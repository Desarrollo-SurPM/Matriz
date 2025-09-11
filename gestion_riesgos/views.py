# gestion_riesgos/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Proceso, Subproceso, Riesgo
from .forms import ProcesoForm, SubprocesoForm, RiesgoForm

# --- Vistas Principales ---

def welcome_page(request):
    return render(request, 'welcome.html')

class MatrizRiesgosView(ListView):
    model = Riesgo
    template_name = 'matriz_riesgos.html'
    context_object_name = 'riesgos'

    def get_queryset(self):
        return Riesgo.objects.select_related('subproceso__proceso').all().order_by('subproceso__proceso__nombre', 'subproceso__tarea')

# --- Vistas para PROCESOS ---

class ProcesoListView(ListView):
    model = Proceso
    template_name = 'gestion/proceso_list.html'

class ProcesoCreateView(CreateView):
    model = Proceso
    form_class = ProcesoForm
    template_name = 'gestion/generic_form.html'
    success_url = reverse_lazy('proceso_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Crear Nuevo Proceso"
        return context

class ProcesoUpdateView(UpdateView):
    model = Proceso
    form_class = ProcesoForm
    template_name = 'gestion/generic_form.html'
    success_url = reverse_lazy('proceso_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Editar Proceso"
        return context

class ProcesoDeleteView(DeleteView):
    model = Proceso
    template_name = 'gestion/confirm_delete.html'
    success_url = reverse_lazy('proceso_list')

# --- Vistas para SUBPROCESOS ---

class SubprocesoListView(ListView):
    model = Subproceso
    template_name = 'gestion/subproceso_list.html'

class SubprocesoCreateView(CreateView):
    model = Subproceso
    form_class = SubprocesoForm
    template_name = 'gestion/generic_form.html'
    success_url = reverse_lazy('subproceso_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Crear Nueva Tarea/Subproceso"
        return context

class SubprocesoUpdateView(UpdateView):
    model = Subproceso
    form_class = SubprocesoForm
    template_name = 'gestion/generic_form.html'
    success_url = reverse_lazy('subproceso_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Editar Tarea/Subproceso"
        return context

class SubprocesoDeleteView(DeleteView):
    model = Subproceso
    template_name = 'gestion/confirm_delete.html'
    success_url = reverse_lazy('subproceso_list')

# --- Vistas para RIESGOS ---

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
    success_url = reverse_lazy('matriz_riesgos')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Editar Riesgo"
        return context

class RiesgoDeleteView(DeleteView):
    model = Riesgo
    template_name = 'gestion/confirm_delete.html'
    success_url = reverse_lazy('matriz_riesgos')