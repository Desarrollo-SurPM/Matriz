from django import forms
from .models import Visita, Recordatorio

# ==========================================
# FORMULARIO DE VISITA
# ==========================================
class VisitaForm(forms.ModelForm):
    class Meta:
        model = Visita
        fields = [
            'empresa', 'tipo_gestion', 'asunto', 'objetivo', 'fecha_hora', 'duracion_minutos',
            'email_solicitud', 'estado', 'resultado', 'proxima_accion', 'fecha_proxima_accion', 'notas'
        ]
        widgets = {
            'fecha_hora': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control-modern'}),
            'fecha_proxima_accion': forms.DateInput(attrs={'type': 'date', 'class': 'form-control-modern'}),
            'objetivo': forms.Textarea(attrs={'rows': 3, 'class': 'form-control-modern', 'placeholder': 'Ej: validar cierre de medidas críticas y acordar evidencias pendientes'}),
            'resultado': forms.Textarea(attrs={'rows': 3, 'class': 'form-control-modern'}),
            'notas': forms.Textarea(attrs={'rows': 3, 'class': 'form-control-modern'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None) # Recibimos el usuario para filtrar empresas
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            current = field.widget.attrs.get('class', '')
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = f'{current} form-control-modern'.strip()
        
        if user:
            # Filtramos empresas asignadas al prevencionista
            from gestion_riesgos.models import Empresa
            self.fields['empresa'].queryset = Empresa.objects.filter(prevencionista=user)

# ==========================================
# FORMULARIO DE RECORDATORIO
# ==========================================
class RecordatorioForm(forms.ModelForm):
    class Meta:
        model = Recordatorio
        fields = ['titulo', 'fecha_hora', 'descripcion', 'completado']
        widgets = {
            'fecha_hora': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }
