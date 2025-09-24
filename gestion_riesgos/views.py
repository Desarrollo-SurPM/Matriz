# gestion_riesgos/views.py
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import Proceso, Subproceso, Riesgo, MedidaControl
from .forms import ProcesoForm, SubprocesoForm, RiesgoForm, MedidaControlForm
from django.http import JsonResponse
# --- Vistas Principales ---

def welcome_page(request):
    return render(request, 'welcome.html')

class MatrizRiesgosView(ListView):
    model = Riesgo
    template_name = 'matriz_riesgos.html'
    context_object_name = 'riesgos'

    def get_queryset(self):
        # Usamos prefetch_related para optimizar la carga de medidas de control
        return Riesgo.objects.select_related('subproceso__proceso').prefetch_related('medidas_control').all().order_by('subproceso__proceso__nombre', 'subproceso__tarea')

# --- VISTAS PARA GESTIÓN DE RIESGOS (CON DETALLE) ---

class RiesgoDetailView(DetailView):
    model = Riesgo
    template_name = 'riesgo_detail.html'
    context_object_name = 'riesgo'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['medidas'] = self.object.medidas_control.all()
        # Pasamos el formulario para añadir una nueva medida directamente en la página de detalle
        context['medida_form'] = MedidaControlForm()
        return context

class RiesgoCreateView(CreateView):
    model = Riesgo
    form_class = RiesgoForm
    template_name = 'gestion/generic_form.html'
    success_url = reverse_lazy('matriz_riesgos')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Añadir Nuevo Riesgo a la Matriz"
        return context

class RiesgoUpdateView(UpdateView):
    model = Riesgo
    form_class = RiesgoForm
    template_name = 'gestion/generic_form.html'
    def get_success_url(self):
        return reverse('riesgo_detail', kwargs={'pk': self.object.pk})
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Editar y Re-evaluar Riesgo"
        return context

class RiesgoDeleteView(DeleteView):
    model = Riesgo
    template_name = 'gestion/confirm_delete.html'
    success_url = reverse_lazy('matriz_riesgos')

# --- NUEVAS VISTAS PARA MEDIDAS DE CONTROL ---

class MedidaControlCreateView(CreateView):
    model = MedidaControl
    form_class = MedidaControlForm
    template_name = 'gestion/generic_form.html'

    def form_valid(self, form):
        # Asignamos el riesgo a la medida de control antes de guardarla
        riesgo = get_object_or_404(Riesgo, pk=self.kwargs['riesgo_pk'])
        form.instance.riesgo = riesgo
        return super().form_valid(form)

    def get_success_url(self):
        # Redirigimos de vuelta a la página de detalle del riesgo
        return reverse('riesgo_detail', kwargs={'pk': self.kwargs['riesgo_pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Añadir Medida de Control"
        return context

class MedidaControlUpdateView(UpdateView):
    model = MedidaControl
    form_class = MedidaControlForm
    template_name = 'gestion/generic_form.html'
    def get_success_url(self):
        return reverse('riesgo_detail', kwargs={'pk': self.object.riesgo.pk})
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Editar Medida de Control"
        return context

class MedidaControlDeleteView(DeleteView):
    model = MedidaControl
    template_name = 'gestion/confirm_delete.html'
    def get_success_url(self):
        return reverse('riesgo_detail', kwargs={'pk': self.object.riesgo.pk})


# --- Vistas para PROCESOS y SUBPROCESOS (sin cambios) ---
class ProcesoListView(ListView):
    model = Proceso
    template_name = 'gestion/proceso_list.html'
class ProcesoCreateView(CreateView):
    model = Proceso
    form_class = ProcesoForm
    template_name = 'gestion/generic_form.html'
    success_url = reverse_lazy('proceso_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs); context['titulo'] = "Crear Nuevo Proceso"; return context
class ProcesoUpdateView(UpdateView):
    model = Proceso
    form_class = ProcesoForm
    template_name = 'gestion/generic_form.html'
    success_url = reverse_lazy('proceso_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs); context['titulo'] = "Editar Proceso"; return context
class ProcesoDeleteView(DeleteView):
    model = Proceso
    template_name = 'gestion/confirm_delete.html'
    success_url = reverse_lazy('proceso_list')

class SubprocesoListView(ListView):
    model = Subproceso
    template_name = 'gestion/subproceso_list.html'
class SubprocesoCreateView(CreateView):
    model = Subproceso
    form_class = SubprocesoForm
    template_name = 'gestion/generic_form.html'
    success_url = reverse_lazy('subproceso_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs); context['titulo'] = "Crear Nueva Tarea/Subproceso"; return context
class SubprocesoUpdateView(UpdateView):
    model = Subproceso
    form_class = SubprocesoForm
    template_name = 'gestion/generic_form.html'
    success_url = reverse_lazy('subproceso_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs); context['titulo'] = "Editar Tarea/Subproceso"; return context
class SubprocesoDeleteView(DeleteView):
    model = Subproceso
    template_name = 'gestion/confirm_delete.html'
    success_url = reverse_lazy('subproceso_list')

def dashboard_page(request):
    """Muestra la página principal del dashboard."""
    # Contamos cuántos riesgos hay en cada categoría de clasificación
    riesgos_por_clasificacion = Riesgo.objects.values('clasificacion_riesgo').annotate(total=Count('clasificacion_riesgo')).order_by('total')

    # Contamos los riesgos por tipo de control implementado
    controles_por_tipo = MedidaControl.objects.values('tipo_control').annotate(total=Count('tipo_control')).order_by('total')

    context = {
        'riesgos_por_clasificacion': riesgos_por_clasificacion,
        'controles_por_tipo': controles_por_tipo
    }
    return render(request, 'dashboard.html', context)

def dashboard_chart_data(request):
    """Prepara los datos en formato JSON para los gráficos."""

    # Datos para el gráfico de clasificación de riesgos
    clasificacion_data = (
        Riesgo.objects
        .values('clasificacion_riesgo')
        .annotate(count=Count('id'))
        .order_by('clasificacion_riesgo')
    )

    # Datos para el gráfico de jerarquía de controles
    jerarquia_data = (
        MedidaControl.objects
        .values('tipo_control')
        .annotate(count=Count('id'))
        .order_by('tipo_control')
    )

    # Mapeo de códigos a nombres completos para mayor claridad en el gráfico
    tipo_control_map = dict(MedidaControl.TIPO_CONTROL_CHOICES)

    data = {
        'clasificacion_labels': [item['clasificacion_riesgo'] for item in clasificacion_data],
        'clasificacion_counts': [item['count'] for item in clasificacion_data],
        'jerarquia_labels': [tipo_control_map.get(item['tipo_control'], 'N/A') for item in jerarquia_data],
        'jerarquia_counts': [item['count'] for item in jerarquia_data],
    }

    return JsonResponse(data)