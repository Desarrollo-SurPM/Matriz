# cumplimiento/forms.py

from django import forms
from .models import EvaluacionProtocolo, TareaLegal

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


class EvaluacionProtocoloForm(forms.ModelForm):
    class Meta:
        model = EvaluacionProtocolo
        fields = [
            'empresa', 'protocolo', 'estado', 'agente_identificado',
            'diagnostico_exposicion', 'personas_expuestas', 'responsable',
            'organismo_administrador', 'fecha_evaluacion', 'proxima_revision',
            'medidas_control', 'evidencia',
        ]
        widgets = {
            'diagnostico_exposicion': forms.Textarea(attrs={'rows': 4}),
            'medidas_control': forms.Textarea(attrs={'rows': 4}),
            'fecha_evaluacion': forms.DateInput(attrs={'type': 'date'}),
            'proxima_revision': forms.DateInput(attrs={'type': 'date'}),
            'agente_identificado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and not user.is_superuser:
            self.fields['empresa'].queryset = self.fields['empresa'].queryset.filter(prevencionista=user)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-control-modern'

    def clean(self):
        cleaned = super().clean()
        estado = cleaned.get('estado')
        diagnostico = (cleaned.get('diagnostico_exposicion') or '').strip()
        if estado == 'NO_APLICA' and len(diagnostico) < 20:
            self.add_error('diagnostico_exposicion', 'Justifique la no aplicabilidad con tareas y evidencia revisada.')
        if estado in ['APLICA', 'IMPLEMENTACION', 'VIGILANCIA', 'CONTROLADO'] and not cleaned.get('agente_identificado'):
            self.add_error('agente_identificado', 'Confirme que el peligro o agente fue identificado para este estado.')
        return cleaned
