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

from agenda.models import Visita, Recordatorio
from .models import Empresa, Matriz, MedidaControl, Normativa, Proceso, Tarea, Riesgo, Documento, Peligro
from .forms import EmpresaForm, MatrizForm, ProcesoForm, TareaForm, RiesgoForm, DocumentoForm, PeligroForm, RiesgoEvaluarForm

# --- LANDING PAGE ---
class LandingPageView(TemplateView):
    template_name = 'landing.html'

# --- VISTAS DE EMPRESA (El corazón de la plataforma) ---
# --- VISTA DEL DASHBOARD PRINCIPAL (MODIFICADA) ---
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtenemos la fecha y hora actual
        now = timezone.now()
        
        # Buscamos los próximos eventos
        proximas_visitas = Visita.objects.filter(
            empresa__prevencionista=self.request.user,
            fecha_hora__gte=now
        ).order_by('fecha_hora')
        
        proximos_recordatorios = Recordatorio.objects.filter(
            prevencionista=self.request.user,
            fecha_hora__gte=now
        ).order_by('fecha_hora')
        
        # Combinamos y ordenamos todos los eventos en una sola lista
        eventos_combinados = sorted(
            list(chain(proximas_visitas, proximos_recordatorios)),
            key=attrgetter('fecha_hora')
        )
        
        # Pasamos los 4 eventos más próximos a la plantilla
        context['proximos_eventos'] = eventos_combinados[:4]
        
        return context

def dashboard_chart_data(request):
    """
    Proporciona los datos en formato JSON para los gráficos del dashboard de riesgos.
    """
    user = request.user
    
    # Datos para el gráfico de Clasificación de Riesgos
    clasificacion_data = Riesgo.objects.filter(tarea__proceso__matriz__empresa__prevencionista=user)\
        .values('clasificacion_riesgo_inherente_maximo')\
        .annotate(count=Count('id'))\
        .order_by('clasificacion_riesgo_inherente_maximo')

    # Datos para el gráfico de Jerarquía de Controles (esto es un ejemplo, ajústalo a tu modelo MedidaControl si tienes un campo de tipo)
    # Suponiendo que tu modelo MedidaControl tiene un campo 'jerarquia'
    # Si no lo tienes, puedes adaptarlo o simplemente devolver datos de ejemplo por ahora.
    jerarquia_data = MedidaControl.objects.filter(riesgo__tarea__proceso__matriz__empresa__prevencionista=user)\
        .values('descripcion')\
        .annotate(count=Count('id'))\
        .order_by('-count')[:5] # Top 5 como ejemplo

    data = {
        'clasificacion_labels': [item['clasificacion_riesgo_inherente_maximo'] for item in clasificacion_data],
        'clasificacion_counts': [item['count'] for item in clasificacion_data],
        'jerarquia_labels': [item['descripcion'] for item in jerarquia_data], # Ajustar a tu campo real
        'jerarquia_counts': [item['count'] for item in jerarquia_data],
    }
    return JsonResponse(data)
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

# --- VISTAS DE MATRIZ ---

class MatrizCreateView(LoginRequiredMixin, CreateView):
    model = Matriz
    form_class = MatrizForm
    template_name = 'gestion/generic_form.html'
    def form_valid(self, form):
        empresa = get_object_or_404(Empresa, pk=self.kwargs['empresa_pk'], prevencionista=self.request.user)
        form.instance.empresa = empresa
        return super().form_valid(form)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa = get_object_or_404(Empresa, pk=self.kwargs['empresa_pk'])
        context['titulo'] = f"Crear Matriz para {empresa.razon_social}"
        context['boton_texto'] = "Crear Matriz"
        return context
    def get_success_url(self):
        return reverse('empresa_detail', kwargs={'pk': self.kwargs['empresa_pk']})

class MatrizDetailView(LoginRequiredMixin, DetailView):
    model = Matriz
    template_name = 'matriz_detail.html'
    context_object_name = 'matriz'
    def get_queryset(self):
        return Matriz.objects.filter(empresa__prevencionista=self.request.user)

class MatrizDeleteView(LoginRequiredMixin, DeleteView):
    model = Matriz
    template_name = 'gestion/confirm_delete.html'
    def get_queryset(self):
        return Matriz.objects.filter(empresa__prevencionista=self.request.user)
    def get_success_url(self):
        return reverse('empresa_detail', kwargs={'pk': self.object.empresa.pk})

# --- VISTAS DE PROCESO, TAREA Y RIESGO (FLUJO COMPLETO) ---

class ProcesoCreateView(LoginRequiredMixin, CreateView):
    model = Proceso
    form_class = ProcesoForm
    template_name = 'gestion/generic_form.html'
    def form_valid(self, form):
        matriz = get_object_or_404(Matriz, pk=self.kwargs['matriz_pk'], empresa__prevencionista=self.request.user)
        form.instance.matriz = matriz
        return super().form_valid(form)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Añadir Nuevo Proceso"
        context['boton_texto'] = "Guardar Proceso"
        return context
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
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proceso = get_object_or_404(Proceso, pk=self.kwargs['proceso_pk'])
        context['titulo'] = f"Añadir Tarea al Proceso: {proceso.nombre}"
        context['boton_texto'] = "Guardar Tarea"
        return context
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
        return super().form_valid(form)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tarea = get_object_or_404(Tarea, pk=self.kwargs['tarea_pk'])
        context['titulo'] = f"Identificar Riesgo para la Tarea: {tarea.descripcion}"
        context['boton_texto'] = "Guardar Riesgo"
        return context
    def get_success_url(self):
        return reverse('matriz_detail', kwargs={'pk': self.object.tarea.proceso.matriz.pk})

class RiesgoDetailView(LoginRequiredMixin, DetailView):
    model = Riesgo
    template_name = 'riesgo_detail.html'
    context_object_name = 'riesgo'
    def get_queryset(self):
        return Riesgo.objects.filter(tarea__proceso__matriz__empresa__prevencionista=self.request.user)

class RiesgoUpdateView(LoginRequiredMixin, UpdateView):
    model = Riesgo
    form_class = RiesgoForm
    template_name = 'gestion/generic_form.html'
    def get_queryset(self):
        return Riesgo.objects.filter(tarea__proceso__matriz__empresa__prevencionista=self.request.user)
    def get_success_url(self):
        return reverse('riesgo_detail', kwargs={'pk': self.object.pk})

class RiesgoDeleteView(LoginRequiredMixin, DeleteView):
    model = Riesgo
    template_name = 'gestion/confirm_delete.html'
    def get_queryset(self):
        return Riesgo.objects.filter(tarea__proceso__matriz__empresa__prevencionista=self.request.user)
    def get_success_url(self):
        # Redirige a la vista de detalle de la matriz después de eliminar un riesgo
        return reverse_lazy('matriz_detail', kwargs={'pk': self.object.tarea.proceso.matriz.pk})

class RiesgoDetailView(LoginRequiredMixin, UpdateView):
    model = Riesgo
    form_class = RiesgoEvaluarForm # Usamos el formulario de evaluación
    template_name = 'riesgo_detail.html'
    context_object_name = 'riesgo'

    def get_queryset(self):
        return Riesgo.objects.filter(tarea__proceso__matriz__empresa__prevencionista=self.request.user)

    def get_context_data(self, **kwargs):
        # Pasamos el formulario de medidas de control también
        context = super().get_context_data(**kwargs)
        # Aquí iría el formulario para añadir Medidas de Control si lo tuvieras
        # context['medida_form'] = MedidaControlForm() 
        return context

    def get_success_url(self):
        return reverse('riesgo_detail', kwargs={'pk': self.object.pk})


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Añadir Nuevo Peligro al Catálogo"
        context['boton_texto'] = "Guardar Peligro"
        return context

class PeligroUpdateView(LoginRequiredMixin, UpdateView):
    model = Peligro
    form_class = PeligroForm
    template_name = 'gestion/generic_form.html'
    success_url = reverse_lazy('peligro_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Editar Peligro del Catálogo"
        context['boton_texto'] = "Actualizar Peligro"
        return context

class PeligroDeleteView(LoginRequiredMixin, DeleteView):
    model = Peligro
    template_name = 'gestion/confirm_delete.html'
    success_url = reverse_lazy('peligro_list')

# --- VISTAS DEL GESTOR DOCUMENTAL ---

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
    

# --- VISTAS PARA LA BIBLIOTECA DE NORMATIVAS ---

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Añadir Nueva Normativa a la Biblioteca"
        context['boton_texto'] = "Guardar Normativa"
        return context

class NormativaUpdateView(LoginRequiredMixin, UpdateView):
    model = Normativa
    fields = ['nombre', 'descripcion', 'archivo', 'fuente', 'categoria']
    template_name = 'gestion/generic_form.html'
    success_url = reverse_lazy('normativa_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Editar Normativa"
        context['boton_texto'] = "Actualizar"
        return context

class NormativaDeleteView(LoginRequiredMixin, DeleteView):
    model = Normativa
    template_name = 'gestion/confirm_delete.html'
    success_url = reverse_lazy('normativa_list')