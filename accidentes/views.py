# accidentes/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
# --- IMPORTACIONES PARA CORREO ---
from django.core.mail import send_mail
from django.conf import settings
import threading # Para enviar en segundo plano y no pegar la web

from .models import (
    AlertaAprendizaje,
    DeclaracionAccidente,
    DocumentoMutualAccidente,
    InvestigacionAccidente,
    ReporteAccidente,
)
from .forms import (
    AlertaAprendizajeForm,
    DeclaracionAccidenteForm,
    DocumentoMutualAccidenteForm,
    InvestigacionAccidenteForm,
    ReporteFlashForm,
    ReporteInmediatoForm,
)

# ==========================================
# 1. CENTRO DE GESTIÓN (LISTADO + DATOS)
# ==========================================
class ReporteAccidenteListView(LoginRequiredMixin, ListView):
    model = ReporteAccidente
    template_name = 'accidentes/reporte_list.html'
    context_object_name = 'reportes'
    paginate_by = 10

    def get_queryset(self):
        qs = ReporteAccidente.objects.por_empresa(self.request.user).select_related('empresa', 'investigacionaccidente')
        estado = self.request.GET.get('estado')
        query = self.request.GET.get('q', '').strip()
        if estado in dict(ReporteAccidente.ESTADO_CHOICES):
            qs = qs.filter(estado=estado)
        if query:
            qs = qs.filter(
                Q(nombre_completo_accidentado__icontains=query)
                | Q(rut_accidentado__icontains=query)
                | Q(empresa__razon_social__icontains=query)
                | Q(descripcion_evento__icontains=query)
            )
        return qs.order_by('-fecha_accidente')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        
        # KPIs
        context['total_casos'] = qs.count()
        context['pendientes_flash'] = qs.filter(estado='reportado').count()
        context['en_investigacion'] = qs.filter(estado__in=['en_investigacion', 'plan_accion']).count()
        context['cerrados'] = qs.filter(estado='cerrado').count()
        context['graves'] = qs.filter(severidad_inicial__in=['grave', 'fatal']).count()
        context['alertas_legales'] = qs.exclude(criterio_gravedad_legal__in=['ninguno', 'por_confirmar']).exclude(tipo_accidente='accidente_trayecto').count()
        context['filtro_estado'] = self.request.GET.get('estado', '')
        context['busqueda'] = self.request.GET.get('q', '')
        
        return context

# ==========================================
# 2. CREACIÓN: REPORTE FLASH (CON EMAIL)
# ==========================================
class ReporteFlashCreateView(LoginRequiredMixin, CreateView):
    model = ReporteAccidente
    form_class = ReporteInmediatoForm
    template_name = 'accidentes/accion_inmediata.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # 1. Configurar datos automáticos
        form.instance.reportado_por = self.request.user
        form.instance.estado = 'reportado'
        
        # 2. Guardar el reporte en BD
        self.object = form.save()
        
        # 3. ENVIAR CORREO (Lógica nueva)
        try:
            destinatarios = self.enviar_alerta_correo(self.object)
            if destinatarios:
                messages.success(
                    self.request,
                    f"Reporte guardado. La notificación a {destinatarios} destinatario(s) quedó en cola.",
                )
            else:
                messages.warning(
                    self.request,
                    "Reporte guardado. La empresa no tiene destinatarios configurados; realiza el aviso por el canal operativo definido.",
                )
        except Exception as e:
            # Si falla el correo, no rompemos el flujo, solo avisamos
            print(f"Error enviando correo: {e}")
            messages.warning(self.request, f"Reporte guardado, pero falló el envío de correo: {e}")

        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('reporte_accidente_detail', args=[self.object.pk])

    def enviar_alerta_correo(self, reporte):
        """
        Envía un correo a los contactos de la empresa configurada.
        """
        # A. Obtener destinatarios desde la Empresa
        if not reporte.empresa.correos_contacto:
            print("AVISO: La empresa no tiene correos de contacto configurados.")
            return 0

        # Convertir string "a@a.com, b@b.com" en lista ['a@a.com', 'b@b.com']
        destinatarios = [email.strip() for email in reporte.empresa.correos_contacto.split(',') if email.strip()]
        
        if not destinatarios:
            return 0

        # B. Construir el mensaje
        asunto = f"⚠️ ALERTA DE ACCIDENTE: {reporte.empresa.razon_social}"
        
        mensaje = f"""
        SISTEMA DE GESTIÓN RISK-BEE
        --------------------------------------------------
        Se ha reportado un nuevo evento de seguridad.

        EMPRESA: {reporte.empresa.razon_social}
        FECHA: {reporte.fecha_accidente}
        TIPO: {reporte.get_tipo_accidente_display()}
        SEVERIDAD: {reporte.get_severidad_inicial_display()}
        
        DESCRIPCIÓN DEL HECHO:
        {reporte.descripcion_evento}

        LUGAR: {reporte.lugar_exacto}
        AFECTADO: {reporte.nombre_completo_accidentado or 'Sin identificar'}
        
        --------------------------------------------------
        Por favor ingrese a la plataforma para iniciar la investigación.
        """

        # C. Enviar (Usando la config de settings.py)
        # Usamos threading para que el usuario no espere a que se envíe el correo
        email_thread = threading.Thread(
            target=send_mail,
            args=(asunto, mensaje, settings.DEFAULT_FROM_EMAIL, destinatarios),
            kwargs={'fail_silently': False}
        )
        email_thread.start()
        return len(destinatarios)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Acción inmediata"
        return context

# ==========================================
# 3. GESTIÓN: DETALLE E INVESTIGACIÓN
# ==========================================
class ReporteInvestigacionView(LoginRequiredMixin, UpdateView):
    model = InvestigacionAccidente
    form_class = InvestigacionAccidenteForm
    template_name = 'accidentes/reporte_detail.html'
    
    def get_object(self, queryset=None):
        reporte_id = self.kwargs.get('pk')
        reporte = get_object_or_404(ReporteAccidente.objects.por_empresa(self.request.user), pk=reporte_id)
        
        investigacion, created = InvestigacionAccidente.objects.get_or_create(
            reporte=reporte,
            defaults={
                'responsable_implementacion': self.request.user.get_full_name() or self.request.user.username,
                'fecha_plazo': timezone.now().date()
            }
        )
        return investigacion

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reporte = self.object.reporte
        declaraciones = reporte.declaraciones.select_related('registrado_por')
        documentos = reporte.documentos_mutual.select_related('subido_por')
        alerta = AlertaAprendizaje.objects.filter(reporte=reporte).first()
        context['reporte'] = reporte
        context['avance'] = self.object.porcentaje_avance
        context['siguiente_paso'] = self.object.siguiente_paso
        context['declaraciones'] = declaraciones
        context['documentos_mutual'] = documentos
        context['declaraciones_confirmadas'] = declaraciones.filter(confirmada_por_declarante=True).count()
        context['alerta_aprendizaje'] = alerta
        context['paso_2_completo'] = declaraciones.filter(confirmada_por_declarante=True).exists()
        context['paso_3_completo'] = bool(self.object.porque_5 and any([
            self.object.medida_eliminar,
            self.object.medida_ingenieria,
            self.object.medida_administrativa,
            self.object.medida_epp,
        ]))
        context['paso_4_completo'] = bool(alerta and alerta.difundida and alerta.revision_privacidad)
        return context

    def form_valid(self, form):
        investigacion = form.save(commit=False)
        if investigacion.completada:
            investigacion.reporte.estado = 'cerrado'
            investigacion.fecha_cierre = timezone.now().date()
            messages.success(self.request, "Caso cerrado exitosamente.")
        else:
            investigacion.reporte.estado = 'en_investigacion'
            messages.info(self.request, "Investigación actualizada.")
        
        investigacion.reporte.save()
        investigacion.save()
        return redirect('reporte_accidente_detail', pk=investigacion.reporte_id)

# ==========================================
# 4. EDICIÓN REPORTE ORIGINAL
# ==========================================
class ReporteExpedienteMixin:
    """Limita cada antecedente al portafolio del usuario autenticado."""

    def get_reporte(self):
        if not hasattr(self, '_reporte'):
            self._reporte = get_object_or_404(
                ReporteAccidente.objects.por_empresa(self.request.user),
                pk=self.kwargs['pk'],
            )
        return self._reporte

    def get_success_url(self):
        return reverse('reporte_accidente_detail', args=[self.get_reporte().pk]) + '#expediente-documental'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reporte'] = self.get_reporte()
        return context


class DeclaracionAccidenteCreateView(ReporteExpedienteMixin, LoginRequiredMixin, CreateView):
    model = DeclaracionAccidente
    form_class = DeclaracionAccidenteForm
    template_name = 'accidentes/expediente_form.html'

    def form_valid(self, form):
        form.instance.reporte = self.get_reporte()
        form.instance.registrado_por = self.request.user
        messages.success(self.request, 'Declaración incorporada al expediente.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'titulo': 'Registrar declaración',
            'eyebrow': 'Paso 2 · antecedentes',
            'descripcion': 'Registra el relato de la persona, permite adjuntar croquis o respaldo y deja constancia de su confirmación.',
            'tipo_formulario': 'declaracion',
        })
        return context


class DocumentoMutualCreateView(ReporteExpedienteMixin, LoginRequiredMixin, CreateView):
    model = DocumentoMutualAccidente
    form_class = DocumentoMutualAccidenteForm
    template_name = 'accidentes/expediente_form.html'

    def form_valid(self, form):
        form.instance.reporte = self.get_reporte()
        form.instance.subido_por = self.request.user
        messages.success(self.request, 'Documento recibido incorporado al expediente.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'titulo': 'Subir documento de mutualidad',
            'eyebrow': 'Paso 2 · respaldo externo',
            'descripcion': 'Adjunta el documento recibido. RiskBee lo conserva, pero no lo genera ni reemplaza al organismo emisor.',
            'tipo_formulario': 'documento',
        })
        return context


class AlertaAprendizajeUpdateView(ReporteExpedienteMixin, LoginRequiredMixin, UpdateView):
    model = AlertaAprendizaje
    form_class = AlertaAprendizajeForm
    template_name = 'accidentes/expediente_form.html'

    def get_object(self, queryset=None):
        reporte = self.get_reporte()
        alerta = AlertaAprendizaje.objects.filter(reporte=reporte).first()
        return alerta or AlertaAprendizaje(reporte=reporte)

    def form_valid(self, form):
        form.instance.reporte = self.get_reporte()
        messages.success(self.request, 'Alerta de aprendizaje actualizada.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'titulo': 'Preparar alerta de aprendizaje',
            'eyebrow': 'Paso 4 · comunicar',
            'descripcion': 'Convierte el caso en una comunicación útil, sin exponer datos personales de la persona involucrada.',
            'tipo_formulario': 'alerta',
        })
        return context


class ReporteUpdateView(LoginRequiredMixin, UpdateView):
    model = ReporteAccidente
    form_class = ReporteFlashForm
    template_name = 'accidentes/reporte_flash.html'

    def get_queryset(self):
        return ReporteAccidente.objects.por_empresa(self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse('reporte_accidente_detail', args=[self.object.pk])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Editar Reporte Original"
        return context
