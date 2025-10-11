# gestion_riesgos/forms.py

from django import forms
from .models import Empresa, Matriz, Proceso, Tarea, Riesgo, Documento, Peligro

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['razon_social', 'rut', 'direccion', 'telefono']
        widgets = {
            'razon_social': forms.TextInput(attrs={'class': 'form-control'}),
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }

class MatrizForm(forms.ModelForm):
    class Meta:
        model = Matriz
        fields = ['nombre_proyecto']
        widgets = {
            'nombre_proyecto': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ProcesoForm(forms.ModelForm):
    class Meta:
        model = Proceso
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Soldadura Estructural'}),
        }

class TareaForm(forms.ModelForm):
    class Meta:
        model = Tarea
        fields = ['puesto_trabajo', 'descripcion', 'es_rutinaria']
        widgets = {
            'puesto_trabajo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Cortar planchas de metal'}),
            'es_rutinaria': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class RiesgoForm(forms.ModelForm):
    class Meta:
        model = Riesgo
        fields = ['peligro', 'consecuencias']
        widgets = {
            'peligro': forms.Select(attrs={'class': 'form-control'}),
            'consecuencias': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'peligro': 'Peligro Específico (Codificado)',
        }

class RiesgoEvaluarForm(forms.ModelForm):
    """Formulario para evaluar el riesgo por categorías y el riesgo residual."""
    class Meta:
        model = Riesgo
        fields = [
            'probabilidad_seguridad', 'consecuencia_seguridad',
            'probabilidad_higienicos', 'consecuencia_higienicos',
            'probabilidad_psicosociales', 'consecuencia_psicosociales',
            'probabilidad_musculoesqueleticos', 'consecuencia_musculoesqueleticos',
            'probabilidad_residual', 'consecuencia_residual'
        ]
        # Usamos RadioSelect para una mejor experiencia de usuario
        radio_widget = forms.RadioSelect(attrs={'class': 'form-check-input'})
        widgets = {
            'probabilidad_seguridad': radio_widget, 'consecuencia_seguridad': radio_widget,
            'probabilidad_higienicos': radio_widget, 'consecuencia_higienicos': radio_widget,
            'probabilidad_psicosociales': radio_widget, 'consecuencia_psicosociales': radio_widget,
            'probabilidad_musculoesqueleticos': radio_widget, 'consecuencia_musculoesqueleticos': radio_widget,
            'probabilidad_residual': radio_widget, 'consecuencia_residual': radio_widget,
        }


class PeligroForm(forms.ModelForm):
    class Meta:
        model = Peligro
        fields = ['familia_riesgo', 'riesgo_especifico', 'definicion', 'codigo']
        widgets = {
            'familia_riesgo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Riesgos de Seguridad'}),
            'riesgo_especifico': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Caída de personas a distinto nivel'}),
            'definicion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: SEG-01'}),
        }

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['nombre', 'archivo', 'categoria']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'archivo': forms.FileInput(attrs={'class': 'form-control'}),
            'categoria': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Procedimientos, Charlas'}),
        }