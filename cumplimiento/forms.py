# cumplimiento/forms.py

from django import forms
from .models import TareaLegal

class TareaLegalForm(forms.ModelForm):
    class Meta:
        model = TareaLegal
        fields = [
            'nombre_obligacion', 'normativa', 'descripcion', 'fecha_inicio', 
            'frecuencia', 'responsable', 'notificacion_email', 'completada'
        ]
        widgets = {
            'nombre_obligacion': forms.TextInput(attrs={'class': 'form-control'}),
            'normativa': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'frecuencia': forms.Select(attrs={'class': 'form-control'}),
            'responsable': forms.TextInput(attrs={'class': 'form-control'}),
            'notificacion_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'completada': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }