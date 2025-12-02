# accidentes/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q # <--- IMPORTANTE: Agregar esto

from .models import ReporteAccidente, InvestigacionAccidente
from .forms import ReporteFlashForm, InvestigacionAccidenteForm

# ==========================================
# 1. CENTRO DE GESTIÓN (LISTADO + DATOS)
# ==========================================
class ReporteAccidenteListView(LoginRequiredMixin, ListView):
    model = ReporteAccidente
    template_name = 'accidentes/reporte_list.html'
    context_object_name = 'reportes'
    paginate_by = 10

    def get_queryset(self):
        # Filtra por empresa si no es superusuario
        qs = ReporteAccidente.objects.all().order_by('-fecha_accidente')
        if not self.request.user.is_superuser:
            # qs = qs.filter(empresa__prevencionista=self.request.user) # Descomentar cuando tengas usuarios vinculados
            pass
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        
        # --- CÁLCULO DE DATOS (KPIs) ---
        context['total_casos'] = qs.count()
        context['pendientes_flash'] = qs.filter(estado='reportado').count()
        context['en_investigacion'] = qs.filter(estado='en_investigacion').count()
        context['cerrados'] = qs.filter(estado='cerrado').count()
        
        # Datos para gráficas simples (opcional)
        context['graves'] = qs.filter(severidad_inicial__in=['grave', 'fatal']).count()
        
        return context

# ==========================================
# 2. CREACIÓN: REPORTE FLASH
# ==========================================
class ReporteFlashCreateView(LoginRequiredMixin, CreateView):
    model = ReporteAccidente
    form_class = ReporteFlashForm
    template_name = 'accidentes/reporte_flash.html'
    success_url = reverse_lazy('reporte_accidente_list')

    def form_valid(self, form):
        form.instance.reportado_por = self.request.user
        form.instance.estado = 'reportado'
        response = super().form_valid(form)
        messages.success(self.request, f"¡Reporte Flash registrado! Ahora puede iniciar el seguimiento.")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Nuevo Reporte Flash"
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
        reporte = get_object_or_404(ReporteAccidente, pk=reporte_id)
        
        investigacion, created = InvestigacionAccidente.objects.get_or_create(
            reporte=reporte,
            defaults={
                'responsable_implementacion': self.request.user.get_full_name(),
                'fecha_plazo': timezone.now().date()
            }
        )
        return investigacion

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reporte'] = self.object.reporte 
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
        return redirect('reporte_accidente_list')

# ==========================================
# 4. EDICIÓN FLASH (Correcciones)
# ==========================================
class ReporteUpdateView(LoginRequiredMixin, UpdateView):
    model = ReporteAccidente
    form_class = ReporteFlashForm
    template_name = 'accidentes/reporte_flash.html'
    success_url = reverse_lazy('reporte_accidente_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Editar Reporte Original"
        return context