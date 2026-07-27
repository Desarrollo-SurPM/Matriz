# cumplimiento/views.py

from django import forms
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import EvaluacionProtocolo, TareaLegal
from .forms import EvaluacionProtocoloForm, TareaLegalForm
from .protocolos import PROTOCOLOS_MINSAL
from .services import sugerir_protocolos_desde_iper
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
        qs = self.get_queryset()
        hoy = timezone.localdate()
        context['hoy'] = hoy
        context['vencidas'] = qs.filter(completada=False, proxima_fecha_vencimiento__lt=hoy).count()
        context['pendientes'] = qs.filter(completada=False).count()
        context['completadas'] = qs.filter(completada=True).count()
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


class ProtocolosMinsalView(LoginRequiredMixin, TemplateView):
    template_name = 'cumplimiento/protocolos_minsal.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresas = Empresa.objects.filter(prevencionista=self.request.user).order_by('razon_social')
        evaluaciones = EvaluacionProtocolo.objects.filter(
            empresa__prevencionista=self.request.user
        ).select_related('empresa')
        empresa_id = self.request.GET.get('empresa')
        empresa_obj = None
        if empresa_id and empresas.filter(pk=empresa_id).exists():
            empresa_obj = empresas.get(pk=empresa_id)
            evaluaciones = evaluaciones.filter(empresa_id=empresa_id)
            context['empresa_seleccionada'] = int(empresa_id)

        tarjetas = []
        for codigo, datos in PROTOCOLOS_MINSAL.items():
            registros = evaluaciones.filter(protocolo=codigo)
            tarjetas.append({
                'codigo': codigo,
                **datos,
                'total': registros.count(),
                'activos': registros.filter(estado__in=['APLICA', 'IMPLEMENTACION', 'VIGILANCIA']).count(),
            })

        total_posible = empresas.count() * len(PROTOCOLOS_MINSAL)
        registradas = EvaluacionProtocolo.objects.filter(empresa__prevencionista=self.request.user).count()
        sugerencias_iper = sugerir_protocolos_desde_iper(empresa_obj) if empresa_obj else []
        evaluados_empresa = set(evaluaciones.values_list('protocolo', flat=True)) if empresa_obj else set()
        for sugerencia in sugerencias_iper:
            sugerencia['evaluado'] = sugerencia['codigo'] in evaluados_empresa
        context.update({
            'empresas': empresas,
            'evaluaciones': evaluaciones.order_by('empresa__razon_social', 'protocolo'),
            'protocolos': tarjetas,
            'cobertura': round(registradas / total_posible * 100) if total_posible else 0,
            'registradas': registradas,
            'requieren_accion': EvaluacionProtocolo.objects.filter(
                empresa__prevencionista=self.request.user,
                estado__in=['APLICA', 'IMPLEMENTACION'],
            ).count(),
            'revisiones_vencidas': EvaluacionProtocolo.objects.filter(
                empresa__prevencionista=self.request.user,
                proxima_revision__lt=timezone.localdate(),
            ).exclude(estado='NO_APLICA').count(),
            'empresa_obj': empresa_obj,
            'sugerencias_iper': sugerencias_iper,
        })
        return context


class EvaluacionProtocoloCreateView(LoginRequiredMixin, CreateView):
    model = EvaluacionProtocolo
    form_class = EvaluacionProtocoloForm
    template_name = 'cumplimiento/protocolo_form.html'
    success_url = reverse_lazy('protocolos_minsal')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        protocolo = self.request.GET.get('protocolo')
        empresa = self.request.GET.get('empresa')
        if protocolo in PROTOCOLOS_MINSAL:
            initial['protocolo'] = protocolo
        if empresa and Empresa.objects.filter(pk=empresa, prevencionista=self.request.user).exists():
            initial['empresa'] = empresa
        return initial

    def form_valid(self, form):
        messages.success(self.request, 'Evaluación de protocolo guardada con trazabilidad.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Evaluar aplicabilidad de protocolo'
        context['catalogo'] = PROTOCOLOS_MINSAL
        return context


class EvaluacionProtocoloUpdateView(LoginRequiredMixin, UpdateView):
    model = EvaluacionProtocolo
    form_class = EvaluacionProtocoloForm
    template_name = 'cumplimiento/protocolo_form.html'
    success_url = reverse_lazy('protocolos_minsal')

    def get_queryset(self):
        return EvaluacionProtocolo.objects.filter(empresa__prevencionista=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Seguimiento del protocolo actualizado.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Actualizar protocolo MINSAL'
        context['catalogo'] = PROTOCOLOS_MINSAL
        return context
