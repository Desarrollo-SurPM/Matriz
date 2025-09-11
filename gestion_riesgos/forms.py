# gestion_riesgos/forms.py

from django import forms
from .models import Proceso, Subproceso, Riesgo

class ProcesoForm(forms.ModelForm):
    class Meta:
        model = Proceso
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
        }

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

class RiesgoForm(forms.ModelForm):
    class Meta:
        model = Riesgo
        fields = ['subproceso', 'riesgo_especifico', 'consecuencias', 'codigo', 'probabilidad', 'consecuencia_valor']
        widgets = {
            'subproceso': forms.Select(attrs={'class': 'form-control'}),
            'riesgo_especifico': forms.TextInput(attrs={'class': 'form-control'}),
            'consecuencias': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'probabilidad': forms.Select(attrs={'class': 'form-control'}),
            'consecuencia_valor': forms.Select(attrs={'class': 'form-control'}),
        }