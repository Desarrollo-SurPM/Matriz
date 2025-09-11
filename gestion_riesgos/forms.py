# gestion_riesgos/forms.py

from django import forms
from .models import Proceso, Subproceso, Riesgo, MedidaControl

class ProcesoForm(forms.ModelForm):
    class Meta:
        model = Proceso
        fields = ['nombre']
        widgets = { 'nombre': forms.TextInput(attrs={'class': 'form-control'}), }

class SubprocesoForm(forms.ModelForm):
    class Meta:
        model = Subproceso
        fields = ['proceso', 'puesto_trabajo', 'tarea', 'es_rutinaria']
        widgets = {
            'proceso': forms.Select(attrs={'class': 'form-control'}),
            'puesto_trabajo': forms.TextInput(attrs={'class': 'form-control'}),
            'tarea': forms.TextInput(attrs={'class': 'form-control'}),
            'es_rutinaria': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# --- Formulario de Riesgo ACTUALIZADO ---
class RiesgoForm(forms.ModelForm):
    class Meta:
        model = Riesgo
        fields = [
            'subproceso', 'riesgo_especifico', 'consecuencias', 'codigo', 
            'probabilidad', 'consecuencia_valor',
            'probabilidad_residual', 'consecuencia_residual' # <-- NUEVOS CAMPOS
        ]
        widgets = {
            'subproceso': forms.Select(attrs={'class': 'form-control'}),
            'riesgo_especifico': forms.TextInput(attrs={'class': 'form-control'}),
            'consecuencias': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'probabilidad': forms.Select(attrs={'class': 'form-control'}),
            'consecuencia_valor': forms.Select(attrs={'class': 'form-control'}),
            'probabilidad_residual': forms.Select(attrs={'class': 'form-control'}),
            'consecuencia_residual': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'probabilidad': 'Probabilidad (Inherente)',
            'consecuencia_valor': 'Consecuencia (Inherente)',
            'probabilidad_residual': 'Probabilidad (Residual)',
            'consecuencia_residual': 'Consecuencia (Residual)',
        }

# --- NUEVO Formulario de Medida de Control ---
class MedidaControlForm(forms.ModelForm):
    class Meta:
        model = MedidaControl
        fields = ['descripcion', 'tipo_control', 'responsable', 'plazo_implementacion']
        widgets = {
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tipo_control': forms.Select(attrs={'class': 'form-control'}),
            'responsable': forms.TextInput(attrs={'class': 'form-control'}),
            'plazo_implementacion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }