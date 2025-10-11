# cumplimiento/views.py

from django import forms
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from .models import TareaLegal
from .forms import TareaLegalForm
from gestion_riesgos.models import Empresa

class TareaLegalListView(LoginRequiredMixin, ListView):
    model = TareaLegal
    template_name = 'cumplimiento/calendario_legal.html'
    context_object_name = 'tareas'

    def get_queryset(self):
        # Filtra las tareas para que solo muestre las de las empresas del prevencionista logueado
        return TareaLegal.objects.filter(empresa__prevencionista=self.request.user).order_by('proxima_fecha_vencimiento')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['empresas'] = Empresa.objects.filter(prevencionista=self.request.user)
        return context

class TareaLegalCreateView(LoginRequiredMixin, CreateView):
    model = TareaLegal
    form_class = TareaLegalForm
    template_name = 'gestion/generic_form.html'
    success_url = reverse_lazy('calendario_legal')

    def form_valid(self, form):
        # Asigna la empresa correcta a la tarea antes de guardarla
        empresa_pk = self.request.POST.get('empresa')
        empresa = get_object_or_404(Empresa, pk=empresa_pk, prevencionista=self.request.user)
        form.instance.empresa = empresa
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Añadir Nueva Obligación Legal"
        # Necesitamos pasar las empresas al formulario para poder seleccionarlas
        context['form'].fields['empresa'] = forms.ModelChoiceField(
            queryset=Empresa.objects.filter(prevencionista=self.request.user),
            widget=forms.Select(attrs={'class': 'form-control'})
        )
        return context

class TareaLegalUpdateView(LoginRequiredMixin, UpdateView):
    model = TareaLegal
    form_class = TareaLegalForm
    template_name = 'gestion/generic_form.html'
    success_url = reverse_lazy('calendario_legal')

    def get_queryset(self):
        return TareaLegal.objects.filter(empresa__prevencionista=self.request.user)

class TareaLegalDeleteView(LoginRequiredMixin, DeleteView):
    model = TareaLegal
    template_name = 'gestion/confirm_delete.html'
    success_url = reverse_lazy('calendario_legal')

    def get_queryset(self):
        return TareaLegal.objects.filter(empresa__prevencionista=self.request.user)