# accidentes/forms.py

from django import forms
from .models import InvestigacionAccidente, ReporteAccidente

class ReporteFlashForm(forms.ModelForm):
    """
    Formulario simplificado para la notificación inmediata.
    Diseñado para llenarse en 2 minutos desde celular o tablet.
    """
    class Meta:
        model = ReporteAccidente
        fields = [
            'empresa', 'area_departamento', 'lugar_exacto', 'supervisor_directo',
            'fecha_accidente', 'turno_accidentado',
            'nombre_completo_accidentado', 'rut_accidentado', 'cargo_accidentado', 
            'antiguedad_cargo', 'horas_trabajadas_antes',
            'descripcion_evento', 'tipo_accidente', 'severidad_inicial',
            'parte_cuerpo_afectada', 'tipo_lesion', 'tratamiento_inicial',
            'danio_propiedad', 'detalle_danio_propiedad',
            'medidas_inmediatas', 'evidencia_fotografica'
        ]
        
        # Widgets con tus clases CSS 'form-control-modern'
        widgets = {
            'empresa': forms.Select(attrs={'class': 'form-control-modern form-select'}),
            'area_departamento': forms.TextInput(attrs={'class': 'form-control-modern', 'placeholder': 'Ej: Bodega Central'}),
            'lugar_exacto': forms.TextInput(attrs={'class': 'form-control-modern'}),
            'supervisor_directo': forms.TextInput(attrs={'class': 'form-control-modern'}),
            
            'fecha_accidente': forms.DateTimeInput(attrs={'class': 'form-control-modern', 'type': 'datetime-local'}),
            'turno_accidentado': forms.Select(attrs={'class': 'form-control-modern form-select'}),
            
            'nombre_completo_accidentado': forms.TextInput(attrs={'class': 'form-control-modern'}),
            'rut_accidentado': forms.TextInput(attrs={'class': 'form-control-modern', 'placeholder': '12.345.678-9'}),
            'cargo_accidentado': forms.TextInput(attrs={'class': 'form-control-modern'}),
            'antiguedad_cargo': forms.TextInput(attrs={'class': 'form-control-modern'}),
            'horas_trabajadas_antes': forms.NumberInput(attrs={'class': 'form-control-modern', 'step': '0.5'}),

            'descripcion_evento': forms.Textarea(attrs={'class': 'form-control-modern', 'rows': 4, 'placeholder': 'Describa objetivamente qué sucedió...'}),
            'tipo_accidente': forms.Select(attrs={'class': 'form-control-modern form-select'}),
            'severidad_inicial': forms.Select(attrs={'class': 'form-control-modern form-select'}),
            
            'tipo_lesion': forms.Select(attrs={'class': 'form-control-modern form-select'}),
            'tratamiento_inicial': forms.Select(attrs={'class': 'form-control-modern form-select'}),
            'parte_cuerpo_afectada': forms.HiddenInput(), # Se llena vía JS (Three.js)

            'danio_propiedad': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'detalle_danio_propiedad': forms.Textarea(attrs={'class': 'form-control-modern', 'rows': 2}),
            
            'medidas_inmediatas': forms.Textarea(attrs={'class': 'form-control-modern', 'rows': 3, 'placeholder': 'Acciones tomadas al instante...'}),
            'evidencia_fotografica': forms.FileInput(attrs={'class': 'form-control-modern'}),
        }

class InvestigacionAccidenteForm(forms.ModelForm):
    """
    Formulario profesional para la investigación.
    Incluye GEMA, 5 Porqués y Jerarquía de Controles.
    """
    class Meta:
        model = InvestigacionAccidente
        exclude = ['reporte', 'fecha_cierre']
        
        widgets = {
            'equipo_investigador': forms.Textarea(attrs={'class': 'form-control-modern', 'rows': 2}),
            'fecha_inicio_investigacion': forms.DateInput(attrs={'class': 'form-control-modern', 'type': 'date'}),
            
            # GEMA / Causalidad
            'factores_personales': forms.Textarea(attrs={'class': 'form-control-modern', 'rows': 3, 'placeholder': 'Ej: Fatiga, falta de experiencia...'}),
            'factores_trabajo': forms.Textarea(attrs={'class': 'form-control-modern', 'rows': 3, 'placeholder': 'Ej: Falta de procedimiento...'}),
            'actos_subestandares': forms.Textarea(attrs={'class': 'form-control-modern', 'rows': 3}),
            'condiciones_subestandares': forms.Textarea(attrs={'class': 'form-control-modern', 'rows': 3}),
            
            # 5 Porqués
            'porque_1': forms.Textarea(attrs={'class': 'form-control-modern', 'rows': 2}),
            'porque_2': forms.Textarea(attrs={'class': 'form-control-modern', 'rows': 2}),
            'porque_3': forms.Textarea(attrs={'class': 'form-control-modern', 'rows': 2}),
            'porque_4': forms.Textarea(attrs={'class': 'form-control-modern', 'rows': 2}),
            'porque_5': forms.Textarea(attrs={'class': 'form-control-modern', 'rows': 2, 'style': 'border: 2px solid var(--accent-primary);'}),
            
            # Jerarquía de Control
            'medida_eliminar': forms.Textarea(attrs={'class': 'form-control-modern', 'rows': 2}),
            'medida_ingenieria': forms.Textarea(attrs={'class': 'form-control-modern', 'rows': 2}),
            'medida_administrativa': forms.Textarea(attrs={'class': 'form-control-modern', 'rows': 2}),
            'medida_epp': forms.Textarea(attrs={'class': 'form-control-modern', 'rows': 2}),
            
            'responsable_implementacion': forms.TextInput(attrs={'class': 'form-control-modern'}),
            'fecha_plazo': forms.DateInput(attrs={'class': 'form-control-modern', 'type': 'date'}),
            'completada': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }