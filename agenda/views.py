from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin

from cumplimiento.models import TareaLegal
from .models import Visita, Recordatorio
from .forms import RecordatorioForm, VisitaForm

@login_required
def all_events(request):
    events = []
    user = request.user

    # 1. Tareas Legales (de la app cumplimiento)
    tareas_legales = TareaLegal.objects.filter(empresa__prevencionista=user)
    for tarea in tareas_legales:
        events.append({
            'title': f"Vence: {tarea.nombre_obligacion}",
            'start': tarea.proxima_fecha_vencimiento.isoformat(),
            'allDay': True,
            'color': '#dc3545',
            'url': reverse('tarea_legal_update', args=[tarea.id]) # <-- LÍNEA CLAVE
        })

    # 2. Visitas Agendadas (de la app agenda)
    visitas = Visita.objects.filter(empresa__prevencionista=user)
    for visita in visitas:
        events.append({
            'title': f"Visita: {visita.asunto} ({visita.empresa.razon_social})",
            'start': visita.fecha_hora.isoformat(),
            'color': '#0d6efd',
            'url': reverse('visita_update', args=[visita.id]) # <-- LÍNEA CLAVE
        })

    # 3. Recordatorios Personales (de la app agenda)
    recordatorios = Recordatorio.objects.filter(prevencionista=user)
    for recordatorio in recordatorios:
        events.append({
            'title': f"Recordar: {recordatorio.titulo}",
            'start': recordatorio.fecha_hora.isoformat(),
            'color': '#198754',
            'url': reverse('recordatorio_update', args=[recordatorio.id]) # <-- LÍNEA CLAVE
        })
        
    return JsonResponse(events, safe=False)
# --- VISTAS PARA LA GESTIÓN DE VISITAS ---

class VisitaListView(LoginRequiredMixin, ListView):
    model = Visita
    template_name = 'agenda/visita_list.html' # Crearemos este template
    context_object_name = 'visitas'

    def get_queryset(self):
        return Visita.objects.filter(empresa__prevencionista=self.request.user).order_by('-fecha_hora')

class VisitaCreateView(LoginRequiredMixin, CreateView):
    model = Visita
    form_class = VisitaForm
    template_name = 'gestion/generic_form.html' # Reutilizamos el formulario genérico
    success_url = reverse_lazy('dashboard') # Redirige al dashboard para ver el calendario actualizado

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Agendar Nueva Visita"
        context['boton_texto'] = "Agendar Visita"
        return context

class VisitaUpdateView(LoginRequiredMixin, UpdateView):
    model = Visita
    form_class = VisitaForm
    template_name = 'gestion/generic_form.html'
    success_url = reverse_lazy('dashboard')

    def get_queryset(self):
        return Visita.objects.filter(empresa__prevencionista=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Editar Visita Agendada"
        return context

class VisitaDeleteView(LoginRequiredMixin, DeleteView):
    model = Visita
    template_name = 'gestion/confirm_delete.html' # Reutilizamos
    success_url = reverse_lazy('dashboard')

    def get_queryset(self):
        return Visita.objects.filter(empresa__prevencionista=self.request.user)
    
# --- VISTAS PARA LA GESTIÓN DE RECORDATORIOS ---

class RecordatorioListView(LoginRequiredMixin, ListView):
    model = Recordatorio
    template_name = 'agenda/recordatorio_list.html' # Crearemos este template
    context_object_name = 'recordatorios'

    def get_queryset(self):
        return Recordatorio.objects.filter(prevencionista=self.request.user).order_by('-fecha_hora')

class RecordatorioCreateView(LoginRequiredMixin, CreateView):
    model = Recordatorio
    form_class = RecordatorioForm
    template_name = 'gestion/generic_form.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        # Asigna el usuario actual como el creador del recordatorio
        form.instance.prevencionista = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Crear Nuevo Recordatorio"
        context['boton_texto'] = "Guardar Recordatorio"
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