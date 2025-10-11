from .models import ReporteAccidente, InvestigacionAccidente
from .forms import ReporteAccidenteForm, InvestigacionAccidenteForm, ReporteFlashForm
from django.views.generic import FormView
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.conf import settings

class ReporteAccidenteListView(LoginRequiredMixin, ListView):
    model = ReporteAccidente
    template_name = 'accidentes/reporte_list.html'
    context_object_name = 'reportes'

    def get_queryset(self):
        return ReporteAccidente.objects.filter(empresa__prevencionista=self.request.user).order_by('-fecha_accidente')

class ReporteAccidenteCreateView(LoginRequiredMixin, CreateView):
    model = ReporteAccidente
    form_class = ReporteAccidenteForm
    template_name = 'gestion/generic_form.html' # Reutilizamos la plantilla genérica
    success_url = reverse_lazy('reporte_accidente_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.reportado_por = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Reportar Nuevo Accidente / Incidente"
        context['boton_texto'] = "Guardar Reporte"
        return context
    
# --- VISTA PARA VER DETALLE Y GESTIONAR LA INVESTIGACIÓN ---
class ReporteFlashView(LoginRequiredMixin, CreateView):
    model = ReporteAccidente
    form_class = ReporteFlashForm
    template_name = 'accidentes/reporte_flash.html'
    success_url = reverse_lazy('reporte_accidente_list')

    def form_valid(self, form):
        form.instance.reportado_por = self.request.user
        reporte = form.save()

        # Enviar correo electrónico
        asunto = f"Reporte Flash de Accidente / Incidente en {reporte.empresa.razon_social}"
        mensaje = f"""
        Se ha generado un nuevo reporte flash de accidente / incidente.

        - **Fecha del reporte:** {reporte.fecha_reporte.strftime('%d/%m/%Y - %H:%M')}
        - **Reportado por:** {reporte.reportado_por.get_full_name()}
        - **Empresa:** {reporte.empresa.razon_social}
        - **Descripción:** {reporte.descripcion_evento}

        Para más detalles, revise la plataforma.
        """
        send_mail(
            asunto,
            mensaje,
            settings.DEFAULT_FROM_EMAIL,
            ['destinatario@ejemplo.com'], # Reemplazar con el correo del destinatario
            fail_silently=False,
        )

        return super().form_valid(form)
class ReporteInvestigacionView(LoginRequiredMixin, FormView):
    template_name = 'accidentes/reporte_detail.html'
    form_class = InvestigacionAccidenteForm

    def get_success_url(self):
        return reverse_lazy('reporte_accidente_detail', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reporte = get_object_or_404(ReporteAccidente, pk=self.kwargs['pk'], empresa__prevencionista=self.request.user)
        context['reporte'] = reporte
        
        # Pasamos la instancia de la investigación si ya existe
        try:
            context['form'] = InvestigacionAccidenteForm(instance=reporte.investigacionaccidente)
        except InvestigacionAccidente.DoesNotExist:
            context['form'] = InvestigacionAccidenteForm()
            
        return context

    def form_valid(self, form):
        reporte = get_object_or_404(ReporteAccidente, pk=self.kwargs['pk'])
        
        # Obtenemos o creamos la investigación
        investigacion, created = InvestigacionAccidente.objects.get_or_create(reporte=reporte)
        
        # Actualizamos los datos
        investigacion.causas_inmediatas = form.cleaned_data['causas_inmediatas']
        investigacion.causas_basicas = form.cleaned_data['causas_basicas']
        investigacion.medidas_correctivas = form.cleaned_data['medidas_correctivas']
        investigacion.responsables_implementacion = form.cleaned_data['responsables_implementacion']
        investigacion.fecha_limite_implementacion = form.cleaned_data['fecha_limite_implementacion']
        investigacion.completada = form.cleaned_data['completada']
        investigacion.fecha_cierre = form.cleaned_data['fecha_cierre']
        investigacion.investigador_lider = self.request.user
        investigacion.save()
        
        return super().form_valid(form)