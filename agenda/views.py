# agenda/views.py

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages

# --- IMPORTACIONES PARA CORREO ---
from django.core.mail import send_mail
from django.conf import settings
import threading 

# Importación de modelos
from cumplimiento.models import TareaLegal
from .models import Visita, Recordatorio
from .forms import RecordatorioForm, VisitaForm
from .services import construir_prioridades_clientes

# ==========================================
# 1. API DE EVENTOS (FULLCALENDAR)
# ==========================================
@login_required
def all_events(request):
    """
    Retorna un JSON con todos los eventos para el FullCalendar.
    """
    events = []
    user = request.user

    # Colores por Estado (Estilo Risk-Bee)
    colores_estado = {
        'PENDIENTE': '#ffc107',  # Amarillo
        'CONFIRMADA': '#198754', # Verde
        'REALIZADA': '#0d6efd',  # Azul
        'CANCELADA': '#dc3545',  # Rojo
    }

    # --- A. VISITAS ---
    try:
        # Filtramos visitas de las empresas del prevencionista
        visitas = Visita.objects.filter(empresa__prevencionista=user)
        for v in visitas:
            color_fondo = colores_estado.get(v.estado, '#6c757d')
            
            events.append({
                'title': f"{v.get_tipo_gestion_display()}: {v.asunto} ({v.get_estado_display()})",
                'start': v.fecha_hora.isoformat() if v.fecha_hora else '',
                'color': color_fondo,      
                'textColor': '#000000',
                'url': reverse('visita_update', args=[v.id]), 
                'className': 'fc-event-no-underline' 
            })
    except Exception as e:
        print(f"Error cargando visitas: {e}")

    # --- B. TAREAS LEGALES ---
    try:
        tareas = TareaLegal.objects.filter(empresa__prevencionista=user)
        for t in tareas:
            events.append({
                'title': f"Vence: {t.nombre_obligacion}",
                'start': t.proxima_fecha_vencimiento.isoformat() if t.proxima_fecha_vencimiento else '',
                'allDay': True,
                'color': '#dc3545',     
                'textColor': '#ffffff', 
                'url': reverse('tarea_legal_update', args=[t.id]) if hasattr(t, 'id') else '#'
            })
    except Exception as e:
        print(f"Error cargando tareas: {e}")

    # --- C. RECORDATORIOS ---
    try:
        recs = Recordatorio.objects.filter(prevencionista=user)
        for r in recs:
            events.append({
                'title': f"Recordar: {r.titulo}",
                'start': r.fecha_hora.isoformat() if r.fecha_hora else '',
                'color': '#0dcaf0',     
                'textColor': '#000000', 
                'url': reverse('recordatorio_update', args=[r.id]),
                'className': 'fc-event-no-underline'
            })
    except Exception as e:
        print(f"Error cargando recordatorios: {e}")
        
    return JsonResponse(events, safe=False)


# ==========================================
# 2. GESTIÓN DE VISITAS (CRUD + EMAIL)
# ==========================================

class VisitaListView(LoginRequiredMixin, ListView):
    model = Visita
    template_name = 'agenda/visita_list.html'
    context_object_name = 'visitas'

    def get_queryset(self):
        return Visita.objects.filter(empresa__prevencionista=self.request.user).select_related('empresa').order_by('-fecha_hora')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        context['prioridades'] = construir_prioridades_clientes(self.request.user)
        context['pendientes'] = qs.filter(estado='PENDIENTE').count()
        context['confirmadas'] = qs.filter(estado='CONFIRMADA').count()
        context['realizadas'] = qs.filter(estado='REALIZADA').count()
        context['total_gestiones'] = qs.count()
        return context

class VisitaCreateView(LoginRequiredMixin, CreateView):
    model = Visita
    form_class = VisitaForm
    template_name = 'agenda/gestion_form.html'
    success_url = reverse_lazy('visita_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        fecha = self.request.GET.get('fecha')
        titulo = self.request.GET.get('titulo')
        empresa = self.request.GET.get('empresa')
        tipo = self.request.GET.get('tipo')
        asunto = self.request.GET.get('asunto')
        
        if fecha:
            initial['fecha_hora'] = f"{fecha} 09:00"
        if titulo:
            initial['asunto'] = titulo
        if empresa:
            initial['empresa'] = empresa
        if tipo in dict(Visita.TIPOS_GESTION):
            initial['tipo_gestion'] = tipo
        if asunto:
            initial['asunto'] = asunto
        
        return initial

    def form_valid(self, form):
        self.object = form.save()
        
        # --- ENVÍO DE CORREO DE SOLICITUD ---
        try:
            self.enviar_correo_solicitud(self.object)
            messages.success(self.request, "Visita agendada y solicitud enviada por correo.")
        except Exception as e:
            print(f"Error enviando correo visita: {e}")
            messages.warning(self.request, "Visita agendada, pero hubo un error enviando el correo.")
            
        return redirect(self.success_url)

    def enviar_correo_solicitud(self, visita):
        """
        Envía notificación al correo específico de la solicitud y a los de la empresa.
        """
        destinatarios = []

        # 1. Correo específico de la solicitud (Prioridad)
        if visita.email_solicitud:
            destinatarios.append(visita.email_solicitud)
        
        # 2. Correos generales de la empresa (Opcional, descomentar si quieres que siempre les llegue)
        # if visita.empresa.correos_contacto:
        #     extras = [e.strip() for e in visita.empresa.correos_contacto.split(',') if e.strip()]
        #     destinatarios.extend(extras)

        # Eliminar duplicados
        destinatarios = list(set(destinatarios))

        if not destinatarios:
            print("No hay destinatarios para la visita.")
            return

        asunto = f"Gestión preventiva: {visita.empresa.razon_social}"
        
        mensaje = f"""
        Estimado/a,

        Se ha generado una nueva gestión preventiva a través de la plataforma Risk-Bee.

        DETALLES DE LA VISITA:
        --------------------------------------------------
        Empresa: {visita.empresa.razon_social}
        Canal: {visita.get_tipo_gestion_display()}
        Asunto: {visita.asunto}
        Fecha y Hora Propuesta: {visita.fecha_hora.strftime('%d/%m/%Y %H:%M')}
        Estado Actual: {visita.get_estado_display()}
        
        NOTAS ADICIONALES:
        {visita.notas or 'Sin notas adicionales.'}

        --------------------------------------------------
        Atentamente,
        Equipo de Prevención
        """

        # Enviar en segundo plano
        email_thread = threading.Thread(
            target=send_mail,
            args=(asunto, mensaje, settings.DEFAULT_FROM_EMAIL, destinatarios),
            kwargs={'fail_silently': False}
        )
        email_thread.start()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Agendar Nueva Visita"
        context['boton_texto'] = "Enviar Solicitud"
        return context

class VisitaUpdateView(LoginRequiredMixin, UpdateView):
    model = Visita
    form_class = VisitaForm
    template_name = 'agenda/gestion_form.html'
    success_url = reverse_lazy('visita_list')

    def get_queryset(self):
        return Visita.objects.filter(empresa__prevencionista=self.request.user)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Detectar si cambió el estado para notificar (Opcional)
        if 'estado' in form.changed_data:
            nuevo_estado = form.cleaned_data['estado']
            # Aquí podrías agregar lógica para enviar correo de "Confirmación" o "Cancelación"
            pass
            
        messages.success(self.request, "Visita actualizada correctamente.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Actualizar Visita"
        context['boton_texto'] = "Guardar Cambios"
        return context

class VisitaDeleteView(LoginRequiredMixin, DeleteView):
    model = Visita
    template_name = 'gestion/confirm_delete.html'
    success_url = reverse_lazy('visita_list')

    def get_queryset(self):
        return Visita.objects.filter(empresa__prevencionista=self.request.user)


# ==========================================
# 3. GESTIÓN DE RECORDATORIOS
# ==========================================

class RecordatorioListView(LoginRequiredMixin, ListView):
    model = Recordatorio
    template_name = 'agenda/recordatorio_list.html'
    context_object_name = 'recordatorios'

    def get_queryset(self):
        return Recordatorio.objects.filter(prevencionista=self.request.user).order_by('-fecha_hora')

class RecordatorioCreateView(LoginRequiredMixin, CreateView):
    model = Recordatorio
    form_class = RecordatorioForm
    template_name = 'gestion/generic_form.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.prevencionista = self.request.user
        messages.success(self.request, "Recordatorio creado.")
        return super().form_valid(form)
        
    def get_initial(self):
        initial = super().get_initial()
        fecha = self.request.GET.get('fecha')
        titulo = self.request.GET.get('titulo')
        if fecha: initial['fecha_hora'] = f"{fecha} 09:00"
        if titulo: initial['titulo'] = titulo
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Crear Nuevo Recordatorio"
        context['boton_texto'] = "Guardar"
        return context

class RecordatorioUpdateView(LoginRequiredMixin, UpdateView):
    model = Recordatorio
    form_class = RecordatorioForm
    template_name = 'gestion/generic_form.html'
    success_url = reverse_lazy('dashboard')

    def get_queryset(self):
        return Recordatorio.objects.filter(prevencionista=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Editar Recordatorio"
        return context

class RecordatorioDeleteView(LoginRequiredMixin, DeleteView):
    model = Recordatorio
    template_name = 'gestion/confirm_delete.html'
    success_url = reverse_lazy('dashboard')

    def get_queryset(self):
        return Recordatorio.objects.filter(prevencionista=self.request.user)
