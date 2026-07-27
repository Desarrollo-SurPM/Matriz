# gestion_riesgos/views.py
from django.http import JsonResponse
from django.db.models import Count
from django.utils import timezone
from itertools import chain
from operator import attrgetter

from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from agenda.models import Visita, Recordatorio
from agenda.services import construir_prioridades_clientes
from accidentes.models import ReporteAccidente
from cumplimiento.models import EvaluacionProtocolo, TareaLegal
from .models import Empresa, Matriz, MedidaControl, Normativa, Proceso, Tarea, Riesgo, Documento, Peligro, MatrizIPER, DetalleIPER
from .forms import EmpresaForm, MatrizForm, ProcesoForm, TareaForm, RiesgoForm, DocumentoForm, PeligroForm, RiesgoEvaluarForm, MatrizIPERForm
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.serializers.json import DjangoJSONEncoder

# --- CATALOGO DE RIESGOS (CARGA MANUAL SOLICITADA) ---
CATALOGO_RIESGOS_DATA = [
    # SEGURIDAD - A. Caída de Personas
    {"codigo": "A1", "riesgo": "Caídas al mismo nivel", "familia": "SEGURIDAD", "desc": "Caída en el mismo plano de sustentación."},
    {"codigo": "A2", "riesgo": "Caídas a distinto nivel", "familia": "SEGURIDAD", "desc": "Caída a plano inferior desde menos de 1,8 m."},
    {"codigo": "A3", "riesgo": "Caídas de altura", "familia": "SEGURIDAD", "desc": "Caída a plano inferior desde más de 1,8 m."},
    {"codigo": "A4", "riesgo": "Caídas al agua", "familia": "SEGURIDAD", "desc": "Caída a cursos de agua naturales o estructuras con agua."},
    # SEGURIDAD - B. Contacto con Objetos
    {"codigo": "B1", "riesgo": "Atrapamiento", "familia": "SEGURIDAD", "desc": "Enganche o aprisionamiento del cuerpo por máquinas, equipos, piezas u objetos inestables."},
    {"codigo": "B2", "riesgo": "Caída de objetos", "familia": "SEGURIDAD", "desc": "Caída de materiales, herramientas, estructuras u otros elementos que golpean al trabajador."},
    {"codigo": "B3", "riesgo": "Cortes por objetos/herramientas cortopunzantes", "familia": "SEGURIDAD", "desc": "Cortes o punciones por objetos cortantes, punzantes o abrasivos."},
    {"codigo": "B4", "riesgo": "Choque contra objetos", "familia": "SEGURIDAD", "desc": "Golpe violento del cuerpo contra objetos estén o no en movimiento."},
    # SEGURIDAD - C. Contacto con Seres Vivos
    {"codigo": "C1", "riesgo": "Contacto con personas", "familia": "SEGURIDAD", "desc": "Lesiones por agresiones, golpes, mordidas u otras acciones de personas."},
    {"codigo": "C2", "riesgo": "Contacto con animales y/o insectos", "familia": "SEGURIDAD", "desc": "Lesiones por interacción con animales o insectos."},
    # SEGURIDAD - E. Contactos Térmicos
    {"codigo": "E1", "riesgo": "Contactos térmicos por calor", "familia": "SEGURIDAD", "desc": "Contacto con superficies o sustancias calientes."},
    {"codigo": "E2", "riesgo": "Contactos térmicos por frío", "familia": "SEGURIDAD", "desc": "Contacto con superficies o sustancias frías."},
    # SEGURIDAD - F. Contacto con Energía Eléctrica
    {"codigo": "F1", "riesgo": "Contactos eléctricos directos baja tensión (<1000 V)", "familia": "SEGURIDAD", "desc": ""},
    {"codigo": "F2", "riesgo": "Contactos eléctricos directos alta tensión (>1000 V)", "familia": "SEGURIDAD", "desc": ""},
    {"codigo": "F3", "riesgo": "Contactos eléctricos indirectos baja tensión (<1000 V)", "familia": "SEGURIDAD", "desc": ""},
    {"codigo": "F4", "riesgo": "Contactos eléctricos indirectos alta tensión (>1000 V)", "familia": "SEGURIDAD", "desc": ""},
    # SEGURIDAD - G. Contacto con Sustancias Químicas
    {"codigo": "G1", "riesgo": "Sustancias cáusticas y/o corrosivas", "familia": "SEGURIDAD", "desc": "Contacto con sustancias que causan daño químico en la piel."},
    {"codigo": "G2", "riesgo": "Otras sustancias químicas", "familia": "SEGURIDAD", "desc": "Sustancias no cáusticas que generan lesiones externas."},
    # SEGURIDAD - H. Elementos que se Proyectan
    {"codigo": "H1", "riesgo": "Explosiones", "familia": "SEGURIDAD", "desc": "Liberación brusca de energía (química o física)."},
    {"codigo": "H2", "riesgo": "Proyección de fragmentos o partículas", "familia": "SEGURIDAD", "desc": ""},
    # SEGURIDAD - I. Vehículos en Movimiento
    {"codigo": "I1", "riesgo": "Atropellos o golpes con vehículos", "familia": "SEGURIDAD", "desc": ""},
    {"codigo": "I2", "riesgo": "Choque, colisión o volcamiento de vehículos", "familia": "SEGURIDAD", "desc": ""},
    # SEGURIDAD - J. Incendios
    {"codigo": "J", "riesgo": "Incendios", "familia": "SEGURIDAD", "desc": "Fuego incontrolado con generación de calor, humo o gases tóxicos."},
    # SEGURIDAD - K. Condiciones Atmosféricas
    {"codigo": "K1", "riesgo": "Deficiencia de oxígeno (<19,5%)", "familia": "SEGURIDAD", "desc": ""},
    {"codigo": "K2", "riesgo": "Sustancias químicas tóxicas en la atmósfera", "familia": "SEGURIDAD", "desc": ""},
    # SEGURIDAD - L. Radiaciones (Accidentes)
    {"codigo": "L1", "riesgo": "Radiaciones no ionizantes (UV, IR, etc.)", "familia": "SEGURIDAD", "desc": ""},
    {"codigo": "L2", "riesgo": "Radiaciones ionizantes (rayos X, gamma)", "familia": "SEGURIDAD", "desc": ""},
    # SEGURIDAD - M. Ingesta
    {"codigo": "M", "riesgo": "Ingesta accidental de sustancias nocivas", "familia": "SEGURIDAD", "desc": ""},
    # SEGURIDAD - N. Otros
    {"codigo": "N", "riesgo": "Otros riesgos no clasificados", "familia": "SEGURIDAD", "desc": ""},
    
    # HIGIÉNICOS - O. Químicos
    {"codigo": "O1", "riesgo": "Aerosoles sólidos", "familia": "HIGIENE", "desc": ""},
    {"codigo": "O2", "riesgo": "Aerosoles líquidos", "familia": "HIGIENE", "desc": ""},
    {"codigo": "O3", "riesgo": "Gases y vapores", "familia": "HIGIENE", "desc": ""},
    # HIGIÉNICOS - P. Físicos
    {"codigo": "P1", "riesgo": "Ruido", "familia": "HIGIENE", "desc": ""},
    {"codigo": "P2", "riesgo": "Vibraciones", "familia": "HIGIENE", "desc": ""},
    {"codigo": "P3", "riesgo": "Radiaciones ionizantes", "familia": "HIGIENE", "desc": ""},
    {"codigo": "P4", "riesgo": "Radiaciones no ionizantes", "familia": "HIGIENE", "desc": ""},
    {"codigo": "P5", "riesgo": "Calor ambiental", "familia": "HIGIENE", "desc": ""},
    {"codigo": "P6", "riesgo": "Frío ambiental", "familia": "HIGIENE", "desc": ""},
    {"codigo": "P7", "riesgo": "Altas presiones", "familia": "HIGIENE", "desc": ""},
    {"codigo": "P8", "riesgo": "Bajas presiones", "familia": "HIGIENE", "desc": ""},
    # HIGIÉNICOS - Q. Biológicos
    {"codigo": "Q1", "riesgo": "Transmisión por sangre y fluidos", "familia": "HIGIENE", "desc": ""},
    {"codigo": "Q2", "riesgo": "Transmisión aérea, hídrica o por contacto", "familia": "HIGIENE", "desc": ""},
    
    # MÚSCULO-ESQUELÉTICOS
    {"codigo": "R1", "riesgo": "Manipulación manual de cargas (>3 kg)", "familia": "ERGONOMÍA", "desc": ""},
    {"codigo": "R2", "riesgo": "Manipulación de personas/pacientes", "familia": "ERGONOMÍA", "desc": ""},
    {"codigo": "S1", "riesgo": "Trabajo repetitivo de extremidades superiores", "familia": "ERGONOMÍA", "desc": ""},
    {"codigo": "T1", "riesgo": "Trabajo de pie prolongado", "familia": "ERGONOMÍA", "desc": ""},
    {"codigo": "T2", "riesgo": "Trabajo sentado prolongado", "familia": "ERGONOMÍA", "desc": ""},
    {"codigo": "T3", "riesgo": "Trabajo en cuclillas", "familia": "ERGONOMÍA", "desc": ""},
    {"codigo": "T4", "riesgo": "Trabajo arrodillado", "familia": "ERGONOMÍA", "desc": ""},
    {"codigo": "T5", "riesgo": "Tronco inclinado, torsión o lateralización", "familia": "ERGONOMÍA", "desc": ""},
    {"codigo": "T6", "riesgo": "Trabajo fuera del alcance funcional", "familia": "ERGONOMÍA", "desc": ""},
    {"codigo": "T7", "riesgo": "Otras posturas forzadas", "familia": "ERGONOMÍA", "desc": ""},

    # PSICOSOCIALES
    {"codigo": "D1", "riesgo": "Exigencias psicológicas en el trabajo", "familia": "PSICOSOCIAL", "desc": ""},
    {"codigo": "D2", "riesgo": "Trabajo activo y desarrollo de habilidades", "familia": "PSICOSOCIAL", "desc": ""},
    {"codigo": "D3", "riesgo": "Apoyo social y calidad del liderazgo", "familia": "PSICOSOCIAL", "desc": ""},
    {"codigo": "D4", "riesgo": "Compensaciones (esfuerzo–recompensa)", "familia": "PSICOSOCIAL", "desc": ""},
    {"codigo": "D5", "riesgo": "Doble presencia trabajo–hogar", "familia": "PSICOSOCIAL", "desc": ""},
]


# --- VISTAS ---

class LandingPageView(TemplateView):
    template_name = 'landing.html'


class CentroAyudaView(TemplateView):
    """Guía pública y contextual para incorporación de usuarios."""
    template_name = 'ayuda/centro_ayuda.html'

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # 1. KPIs de Visitas (Semáforo)
        visitas_qs = Visita.objects.filter(empresa__prevencionista=user)
        
        context['kpi_pendientes'] = visitas_qs.filter(estado='PENDIENTE').count()
        context['kpi_confirmadas'] = visitas_qs.filter(estado='CONFIRMADA').count()
        context['kpi_realizadas'] = visitas_qs.filter(estado='REALIZADA').count()
        context['kpi_total_visitas'] = visitas_qs.count()

        # 2. Otros datos para el Dashboard
        context['total_empresas'] = Empresa.objects.filter(prevencionista=user).count()
        hoy = timezone.localdate()
        reportes = ReporteAccidente.objects.por_empresa(user)
        context['accidentes_abiertos'] = reportes.exclude(estado='cerrado').count()
        context['accidentes_alerta'] = reportes.exclude(
            criterio_gravedad_legal__in=['ninguno', 'por_confirmar']
        ).exclude(tipo_accidente='accidente_trayecto').exclude(estado='cerrado').count()
        context['obligaciones_vencidas'] = TareaLegal.objects.filter(
            empresa__prevencionista=user,
            completada=False,
            proxima_fecha_vencimiento__lt=hoy,
        ).count()
        context['protocolos_accion'] = EvaluacionProtocolo.objects.filter(
            empresa__prevencionista=user,
            estado__in=['APLICA', 'IMPLEMENTACION'],
        ).count()
        context['prioridades_clientes'] = construir_prioridades_clientes(user, limit=4)
        context['proximas_gestiones'] = visitas_qs.filter(
            estado__in=['PENDIENTE', 'CONFIRMADA'],
            fecha_hora__gte=timezone.now(),
        ).select_related('empresa').order_by('fecha_hora')[:5]
        
        return context

# --- ESTA ES LA FUNCIÓN QUE FALTABA Y CAUSABA EL ERROR ---
def dashboard_chart_data(request):
    """
    Proporciona los datos en formato JSON para los gráficos del dashboard de riesgos.
    """
    user = request.user
    
    # Datos para el gráfico de Clasificación de Riesgos
    # NOTA: Ajustado para usar el modelo antiguo Riesgo si es necesario, 
    # o podrías necesitar adaptarlo a MatrizIPER si quieres datos de la nueva matriz.
    # Por ahora lo dejo compatible con el código original.
    clasificacion_data = Riesgo.objects.filter(tarea__proceso__matriz__empresa__prevencionista=user)\
        .values('clasificacion_riesgo_inherente_maximo')\
        .annotate(count=Count('id'))\
        .order_by('clasificacion_riesgo_inherente_maximo')

    # Datos para Jerarquía de Controles
    jerarquia_data = MedidaControl.objects.filter(riesgo__tarea__proceso__matriz__empresa__prevencionista=user)\
        .values('descripcion')\
        .annotate(count=Count('id'))\
        .order_by('-count')[:5] 

    data = {
        'clasificacion_labels': [item['clasificacion_riesgo_inherente_maximo'] for item in clasificacion_data],
        'clasificacion_counts': [item['count'] for item in clasificacion_data],
        'jerarquia_labels': [item['descripcion'] for item in jerarquia_data], 
        'jerarquia_counts': [item['count'] for item in jerarquia_data],
    }
    return JsonResponse(data)
# ---------------------------------------------------------

class EmpresaListView(LoginRequiredMixin, ListView):
    model = Empresa
    template_name = 'empresa_list.html'
    context_object_name = 'empresas'
    def get_queryset(self):
        return Empresa.objects.filter(prevencionista=self.request.user).order_by('razon_social')

class EmpresaDetailView(LoginRequiredMixin, DetailView):
    model = Empresa
    template_name = 'empresa_detail.html'
    context_object_name = 'empresa'
    def get_queryset(self):
        return Empresa.objects.filter(prevencionista=self.request.user)

class EmpresaCreateView(LoginRequiredMixin, CreateView):
    model = Empresa
    form_class = EmpresaForm
    template_name = 'gestion/generic_form.html'
    success_url = reverse_lazy('empresa_list')
    def form_valid(self, form):
        form.instance.prevencionista = self.request.user
        return super().form_valid(form)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Añadir Nueva Empresa Cliente"
        context['boton_texto'] = "Guardar Empresa"
        return context

class EmpresaUpdateView(LoginRequiredMixin, UpdateView):
    model = Empresa
    form_class = EmpresaForm
    template_name = 'gestion/generic_form.html'
    def get_queryset(self):
        return Empresa.objects.filter(prevencionista=self.request.user)
    def get_success_url(self):
        return reverse('empresa_detail', kwargs={'pk': self.object.pk})

class EmpresaDeleteView(LoginRequiredMixin, DeleteView):
    model = Empresa
    template_name = 'gestion/confirm_delete.html'
    success_url = reverse_lazy('empresa_list')
    def get_queryset(self):
        return Empresa.objects.filter(prevencionista=self.request.user)

# --- MATRIZ IPER VIEWS (MODIFICADA) ---

@login_required
def matriz_riesgos_view(request, matriz_id=None):
    """
    Vista principal de la Matriz IPER. 
    Inyecta el catálogo JSON para autocompletado en JS.
    """
    if matriz_id:
        matriz = get_object_or_404(
            MatrizIPER,
            pk=matriz_id,
            empresa__prevencionista=request.user,
        )
    else:
        matriz = MatrizIPER.objects.filter(empresa__prevencionista=request.user).last()
        if not matriz:
            return redirect('empresa_list')

    if request.method == 'POST' and 'save_header' in request.POST:
        form = MatrizIPERForm(request.POST, request.FILES, instance=matriz)
        if form.is_valid():
            matriz_actualizada = form.save(commit=False)
            if request.FILES.get('mapa_riesgos_archivo'):
                matriz_actualizada.mapa_actualizado_en = timezone.now()
            matriz_actualizada.save()
            return redirect('matriz_riesgos_view', matriz_id=matriz.id)
    else:
        form = MatrizIPERForm(instance=matriz)

    filas = matriz.filas.all()

    return render(request, 'matriz_riesgos.html', {
        'matriz': matriz,
        'form': form,
        'filas': filas,
        # Inyectamos el catálogo definido arriba como JSON
        'catalogo_peligros_json': json.dumps(CATALOGO_RIESGOS_DATA, cls=DjangoJSONEncoder)
    })

@login_required
@require_POST
def update_detalle_iper(request):
    """
    API para actualizar celdas individuales del DetalleIPER.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            row_id = data.get('id')
            field = data.get('field')
            value = data.get('value')

            # Si el ID es 'new', creamos una fila nueva
            if row_id == 'new':
                matriz_id = data.get('matriz_id')
                matriz = MatrizIPER.objects.get(
                    pk=matriz_id,
                    empresa__prevencionista=request.user,
                )
                detalle = DetalleIPER.objects.create(matriz=matriz)
                if hasattr(detalle, field):
                    setattr(detalle, field, value)
                    detalle.save()
                return JsonResponse({'status': 'created', 'id': detalle.id})
            
            # Actualizar fila existente
            detalle = DetalleIPER.objects.get(
                pk=row_id,
                matriz__empresa__prevencionista=request.user,
            )
            if hasattr(detalle, field):
                setattr(detalle, field, value)
                detalle.save()
                return JsonResponse({'status': 'ok'})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
            
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def crear_nueva_matriz_iper(request, empresa_pk):
    empresa = get_object_or_404(Empresa, pk=empresa_pk, prevencionista=request.user)
    nueva_matriz = MatrizIPER.objects.create(
        empresa=empresa,
        codigo_documento="IPER-001",
        version="1.0"
    )
    return redirect('matriz_riesgos_view', matriz_id=nueva_matriz.id)

# --- VISTAS HEREDADAS (Procesos, Tareas, Riesgos Antiguos) ---

class MatrizDetailView(LoginRequiredMixin, DetailView):
    model = Matriz
    template_name = 'matriz_detail.html'
    context_object_name = 'matriz'
    def get_queryset(self):
        return Matriz.objects.filter(empresa__prevencionista=self.request.user)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        matriz = self.get_object()
        context['riesgos'] = Riesgo.objects.filter(tarea__proceso__matriz=matriz)\
            .select_related('tarea__proceso', 'peligro').prefetch_related('medidas_control')\
            .order_by('tarea__proceso__nombre', 'tarea__descripcion', 'peligro__codigo')
        context['procesos'] = matriz.procesos.all().prefetch_related('tareas')
        return context

class MatrizCreateView(LoginRequiredMixin, CreateView):
    model = Matriz
    form_class = MatrizForm
    template_name = 'gestion/generic_form.html'
    def form_valid(self, form):
        empresa = get_object_or_404(Empresa, pk=self.kwargs['empresa_pk'], prevencionista=self.request.user)
        form.instance.empresa = empresa
        return super().form_valid(form)
    def get_success_url(self):
        return reverse('empresa_detail', kwargs={'pk': self.kwargs['empresa_pk']})

class MatrizDeleteView(LoginRequiredMixin, DeleteView):
    model = Matriz
    template_name = 'gestion/confirm_delete.html'
    def get_queryset(self):
        return Matriz.objects.filter(empresa__prevencionista=self.request.user)
    def get_success_url(self):
        return reverse('empresa_detail', kwargs={'pk': self.object.empresa.pk})

class ProcesoCreateView(LoginRequiredMixin, CreateView):
    model = Proceso
    form_class = ProcesoForm
    template_name = 'gestion/generic_form.html'
    def form_valid(self, form):
        matriz = get_object_or_404(Matriz, pk=self.kwargs['matriz_pk'], empresa__prevencionista=self.request.user)
        form.instance.matriz = matriz
        return super().form_valid(form)
    def get_success_url(self):
        return reverse('matriz_detail', kwargs={'pk': self.kwargs['matriz_pk']})
class ProcesoUpdateView(LoginRequiredMixin, UpdateView):
    model = Proceso
    form_class = ProcesoForm
    template_name = 'gestion/generic_form.html'
    def get_queryset(self):
        return Proceso.objects.filter(matriz__empresa__prevencionista=self.request.user)
    def get_success_url(self):
        return reverse('matriz_detail', kwargs={'pk': self.object.matriz.pk})
class ProcesoDeleteView(LoginRequiredMixin, DeleteView):
    model = Proceso
    template_name = 'gestion/confirm_delete.html'
    def get_queryset(self):
        return Proceso.objects.filter(matriz__empresa__prevencionista=self.request.user)
    def get_success_url(self):
        return reverse('matriz_detail', kwargs={'pk': self.object.matriz.pk})
class TareaCreateView(LoginRequiredMixin, CreateView):
    model = Tarea
    form_class = TareaForm
    template_name = 'gestion/generic_form.html'
    def form_valid(self, form):
        proceso = get_object_or_404(Proceso, pk=self.kwargs['proceso_pk'], matriz__empresa__prevencionista=self.request.user)
        form.instance.proceso = proceso
        return super().form_valid(form)
    def get_success_url(self):
        return reverse('matriz_detail', kwargs={'pk': self.object.proceso.matriz.pk})
class TareaUpdateView(LoginRequiredMixin, UpdateView):
    model = Tarea
    form_class = TareaForm
    template_name = 'gestion/generic_form.html'
    def get_queryset(self):
        return Tarea.objects.filter(proceso__matriz__empresa__prevencionista=self.request.user)
    def get_success_url(self):
        return reverse('matriz_detail', kwargs={'pk': self.object.proceso.matriz.pk})
class TareaDeleteView(LoginRequiredMixin, DeleteView):
    model = Tarea
    template_name = 'gestion/confirm_delete.html'
    def get_queryset(self):
        return Tarea.objects.filter(proceso__matriz__empresa__prevencionista=self.request.user)
    def get_success_url(self):
        return reverse('matriz_detail', kwargs={'pk': self.object.proceso.matriz.pk})
class RiesgoCreateView(LoginRequiredMixin, CreateView):
    model = Riesgo
    form_class = RiesgoForm
    template_name = 'gestion/generic_form.html'
    def form_valid(self, form):
        tarea = get_object_or_404(Tarea, pk=self.kwargs['tarea_pk'], proceso__matriz__empresa__prevencionista=self.request.user)
        form.instance.tarea = tarea
        medida_actual_desc = form.cleaned_data.get('medida_control_actual')
        response = super().form_valid(form)
        if medida_actual_desc:
            MedidaControl.objects.create(riesgo=self.object, descripcion=medida_actual_desc)
        return response
    def get_success_url(self):
        return reverse('matriz_detail', kwargs={'pk': self.object.tarea.proceso.matriz.pk})
class RiesgoDetailView(LoginRequiredMixin, UpdateView):
    model = Riesgo
    form_class = RiesgoEvaluarForm
    template_name = 'riesgo_detail.html'
    context_object_name = 'riesgo'
    def get_queryset(self):
        return Riesgo.objects.filter(tarea__proceso__matriz__empresa__prevencionista=self.request.user)
    def get_success_url(self):
        return reverse('matriz_detail', kwargs={'pk': self.object.tarea.proceso.matriz.pk})
class RiesgoUpdateView(LoginRequiredMixin, UpdateView):
    model = Riesgo
    form_class = RiesgoForm
    template_name = 'gestion/generic_form.html'
    def get_queryset(self):
        return Riesgo.objects.filter(tarea__proceso__matriz__empresa__prevencionista=self.request.user)
    def get_success_url(self):
        return reverse('matriz_detail', kwargs={'pk': self.object.tarea.proceso.matriz.pk})
class RiesgoDeleteView(LoginRequiredMixin, DeleteView):
    model = Riesgo
    template_name = 'gestion/confirm_delete.html'
    def get_queryset(self):
        return Riesgo.objects.filter(tarea__proceso__matriz__empresa__prevencionista=self.request.user)
    def get_success_url(self):
        return reverse('matriz_detail', kwargs={'pk': self.object.tarea.proceso.matriz.pk})
class PeligroListView(LoginRequiredMixin, ListView):
    model = Peligro
    template_name = 'peligro_list.html'
    context_object_name = 'peligros'
    ordering = ['familia_riesgo', 'codigo']
class PeligroCreateView(LoginRequiredMixin, CreateView):
    model = Peligro
    form_class = PeligroForm
    template_name = 'gestion/generic_form.html'
    success_url = reverse_lazy('peligro_list')
class PeligroUpdateView(LoginRequiredMixin, UpdateView):
    model = Peligro
    form_class = PeligroForm
    template_name = 'gestion/generic_form.html'
    success_url = reverse_lazy('peligro_list')
class PeligroDeleteView(LoginRequiredMixin, DeleteView):
    model = Peligro
    template_name = 'gestion/confirm_delete.html'
    success_url = reverse_lazy('peligro_list')
class DocumentoCreateView(LoginRequiredMixin, CreateView):
    model = Documento
    form_class = DocumentoForm
    template_name = 'gestion/generic_form.html'
    def form_valid(self, form):
        empresa = get_object_or_404(Empresa, pk=self.kwargs['empresa_pk'], prevencionista=self.request.user)
        form.instance.empresa = empresa
        return super().form_valid(form)
    def get_success_url(self):
        return reverse('empresa_detail', kwargs={'pk': self.kwargs['empresa_pk']})
class DocumentoDeleteView(LoginRequiredMixin, DeleteView):
    model = Documento
    template_name = 'gestion/confirm_delete.html'
    def get_queryset(self):
        return Documento.objects.filter(empresa__prevencionista=self.request.user)
    def get_success_url(self):
        return reverse('empresa_detail', kwargs={'pk': self.object.empresa.pk})
class NormativaListView(LoginRequiredMixin, ListView):
    model = Normativa
    template_name = 'normativa_list.html'
    context_object_name = 'normativas'
    ordering = ['categoria', 'nombre']
class NormativaCreateView(LoginRequiredMixin, CreateView):
    model = Normativa
    fields = ['nombre', 'descripcion', 'archivo', 'fuente', 'categoria']
    template_name = 'gestion/generic_form.html'
    success_url = reverse_lazy('normativa_list')
class NormativaUpdateView(LoginRequiredMixin, UpdateView):
    model = Normativa
    fields = ['nombre', 'descripcion', 'archivo', 'fuente', 'categoria']
    template_name = 'gestion/generic_form.html'
    success_url = reverse_lazy('normativa_list')
class NormativaDeleteView(LoginRequiredMixin, DeleteView):
    model = Normativa
    template_name = 'gestion/confirm_delete.html'
    success_url = reverse_lazy('normativa_list')

@login_required
@require_POST
def delete_detalle_iper(request, fila_id):
    """
    Elimina una fila específica de la matriz IPER.
    """
    try:
        # Aseguramos que la fila pertenezca a una matriz del usuario actual para seguridad
        detalle = get_object_or_404(DetalleIPER, pk=fila_id)
        if detalle.matriz.empresa.prevencionista != request.user:
             return JsonResponse({'status': 'error', 'message': 'No autorizado'}, status=403)

        detalle.delete()
        return JsonResponse({'status': 'ok', 'message': 'Fila eliminada correctamente'})
            
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
