# accidentes/forms.py

from django import forms
from .models import InvestigacionAccidente, ReporteAccidente
from gestion_riesgos.models import Empresa

class ReporteFlashForm(forms.ModelForm):
    class Meta:
        model = ReporteAccidente
        exclude = ['reportado_por', 'fecha_reporte']
        widgets = {
            'empresa': forms.Select(attrs={'class': 'form-control form-select'}),
            'area_departamento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Producción / Logística'}),
            'supervisor_responsable': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_completo_accidentado': forms.TextInput(attrs={'class': 'form-control'}),
            'rut_accidentado': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 12.345.678-9'}),
            'cargo_accidentado': forms.TextInput(attrs={'class': 'form-control'}),
            'antiguedad_cargo_accidentado': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 2 años y 3 meses'}),
            'turno_accidentado': forms.Select(attrs={'class': 'form-control form-select'}),
            'descripcion_evento': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), # <-- AJUSTE DE ALTURA
            'lugar_exacto': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_accidente': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'tipo_accidente': forms.Select(attrs={'class': 'form-control form-select'}),
            'tipo_lesion': forms.Select(attrs={'class': 'form-control form-select'}),
            'tratamiento_inicial': forms.Select(attrs={'class': 'form-control form-select'}),
            'causas_inmediatas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}), # <-- AJUSTE DE ALTURA
            'medidas_inmediatas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}), # <-- AJUSTE DE ALTURA
            'evidencia_fotografica': forms.FileInput(attrs={'class': 'form-control'}),
        }
class ReporteAccidenteForm(forms.ModelForm):
    class Meta:
        model = ReporteAccidente
        fields = [
            'empresa', 'fecha_accidente', 'lugar_exacto', 'tipo_accidente',
            'descripcion_evento', 
            'evidencia_fotografica'
        ]
        widgets = {
            'empresa': forms.Select(attrs={'class': 'form-control'}),
            'fecha_accidente': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'lugar_exacto': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_accidente': forms.Select(attrs={'class': 'form-control'}),
            'descripcion_evento': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'evidencia_fotografica': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['empresa'].queryset = Empresa.objects.filter(prevencionista=user)

class InvestigacionAccidenteForm(forms.ModelForm):
    class Meta:
        model = InvestigacionAccidente
        fields = [
            'causas_inmediatas', 'causas_basicas', 'medidas_correctivas',
            'responsables_implementacion', 'fecha_limite_implementacion',
            'completada', 'fecha_cierre'
        ]
        widgets = {
            'causas_inmediatas': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'causas_basicas': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'medidas_correctivas': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'responsables_implementacion': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_limite_implementacion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'completada': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'fecha_cierre': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }