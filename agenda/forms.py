from django import forms
from .models import Recordatorio, Visita
from gestion_riesgos.models import Empresa

class VisitaForm(forms.ModelForm):
    class Meta:
        model = Visita
        fields = ['empresa', 'asunto', 'descripcion', 'fecha_hora', 'estado']
        widgets = {
            'empresa': forms.Select(attrs={'class': 'form-control'}),
            'asunto': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fecha_hora': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        # Filtramos el queryset del campo 'empresa' para mostrar solo las del usuario logueado.
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['empresa'].queryset = Empresa.objects.filter(prevencionista=user)

class RecordatorioForm(forms.ModelForm):
    class Meta:
        model = Recordatorio
        fields = ['titulo', 'descripcion', 'fecha_hora']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fecha_hora': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }