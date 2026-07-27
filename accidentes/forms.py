# accidentes/forms.py

from django import forms
from django.utils import timezone

from .models import (
    AlertaAprendizaje,
    DeclaracionAccidente,
    DocumentoMutualAccidente,
    InvestigacionAccidente,
    ReporteAccidente,
)


class ReporteInmediatoForm(forms.ModelForm):
    """Captura solo lo necesario para activar la respuesta y abrir el expediente."""

    class Meta:
        model = ReporteAccidente
        fields = [
            'empresa', 'area_departamento', 'lugar_exacto', 'fecha_accidente',
            'tipo_accidente', 'severidad_inicial', 'criterio_gravedad_legal',
            'descripcion_evento', 'medidas_inmediatas', 'evidencia_fotografica',
            'nombre_completo_accidentado',
        ]
        widgets = {
            'empresa': forms.Select(attrs={'class': 'form-control-modern form-select'}),
            'area_departamento': forms.TextInput(attrs={
                'class': 'form-control-modern',
                'placeholder': 'Ej: Bodega, planta, ruta o sucursal',
                'autocomplete': 'organization-title',
            }),
            'lugar_exacto': forms.TextInput(attrs={
                'class': 'form-control-modern',
                'placeholder': 'Punto exacto y referencia para llegar',
                'autocomplete': 'street-address',
            }),
            'fecha_accidente': forms.DateTimeInput(attrs={
                'class': 'form-control-modern',
                'type': 'datetime-local',
            }, format='%Y-%m-%dT%H:%M'),
            'tipo_accidente': forms.Select(attrs={'class': 'form-control-modern form-select'}),
            'severidad_inicial': forms.Select(attrs={'class': 'form-control-modern form-select'}),
            'criterio_gravedad_legal': forms.Select(attrs={'class': 'form-control-modern form-select'}),
            'descripcion_evento': forms.Textarea(attrs={
                'class': 'form-control-modern',
                'rows': 3,
                'placeholder': 'Qué actividad se realizaba, qué ocurrió y cuál fue la consecuencia visible. Sin buscar culpables.',
            }),
            'medidas_inmediatas': forms.Textarea(attrs={
                'class': 'form-control-modern',
                'rows': 3,
                'placeholder': 'Atención entregada, detención, aislamiento, traslado u otra acción ya ejecutada.',
            }),
            'evidencia_fotografica': forms.FileInput(attrs={
                'class': 'form-control-modern',
                'accept': 'image/*',
                'capture': 'environment',
            }),
            'nombre_completo_accidentado': forms.TextInput(attrs={
                'class': 'form-control-modern',
                'placeholder': 'Opcional en la alerta inicial; completar después',
                'autocomplete': 'name',
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['fecha_accidente'].input_formats = ['%Y-%m-%dT%H:%M']
        if not self.is_bound:
            self.initial.setdefault(
                'fecha_accidente',
                timezone.localtime().strftime('%Y-%m-%dT%H:%M'),
            )
        if user and not user.is_superuser:
            self.fields['empresa'].queryset = self.fields['empresa'].queryset.filter(prevencionista=user)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('severidad_inicial') == 'fatal' and cleaned.get('criterio_gravedad_legal') == 'ninguno':
            self.add_error(
                'criterio_gravedad_legal',
                'Un evento fatal debe activar o dejar por confirmar el criterio legal.',
            )
        return cleaned

class ReporteFlashForm(forms.ModelForm):
    """
    Formulario simplificado para la notificación inmediata.
    Diseñado para llenarse en 2 minutos desde celular o tablet.
    """
    class Meta:
        model = ReporteAccidente
        fields = [
            'empresa', 'area_departamento', 'lugar_exacto', 'supervisor_directo',
            'fecha_accidente', 'turno_accidentado', 'sexo_accidentado',
            'nombre_completo_accidentado', 'rut_accidentado', 'cargo_accidentado', 
            'antiguedad_cargo', 'horas_trabajadas_antes',
            'descripcion_evento', 'tipo_accidente', 'severidad_inicial', 'criterio_gravedad_legal',
            'parte_cuerpo_afectada', 'detalle_parte_afectada', 'tipo_lesion', 'tratamiento_inicial',
            'danio_propiedad', 'detalle_danio_propiedad',
            'danio_medio_ambiente', 'medidas_inmediatas', 'evidencia_fotografica'
        ]
        
        # Widgets con tus clases CSS 'form-control-modern'
        widgets = {
            'empresa': forms.Select(attrs={'class': 'form-control-modern form-select'}),
            'area_departamento': forms.TextInput(attrs={'class': 'form-control-modern', 'placeholder': 'Ej: Bodega Central'}),
            'lugar_exacto': forms.TextInput(attrs={'class': 'form-control-modern'}),
            'supervisor_directo': forms.TextInput(attrs={'class': 'form-control-modern'}),
            
            'fecha_accidente': forms.DateTimeInput(attrs={'class': 'form-control-modern', 'type': 'datetime-local'}),
            'turno_accidentado': forms.Select(attrs={'class': 'form-control-modern form-select'}),
            'sexo_accidentado': forms.Select(attrs={'class': 'form-control-modern form-select'}),
            
            'nombre_completo_accidentado': forms.TextInput(attrs={'class': 'form-control-modern'}),
            'rut_accidentado': forms.TextInput(attrs={'class': 'form-control-modern', 'placeholder': '12.345.678-9'}),
            'cargo_accidentado': forms.TextInput(attrs={'class': 'form-control-modern'}),
            'antiguedad_cargo': forms.TextInput(attrs={'class': 'form-control-modern'}),
            'horas_trabajadas_antes': forms.NumberInput(attrs={'class': 'form-control-modern', 'step': '0.5'}),

            'descripcion_evento': forms.Textarea(attrs={'class': 'form-control-modern', 'rows': 4, 'placeholder': 'Describa objetivamente qué sucedió...'}),
            'tipo_accidente': forms.Select(attrs={'class': 'form-control-modern form-select'}),
            'severidad_inicial': forms.Select(attrs={'class': 'form-control-modern form-select'}),
            'criterio_gravedad_legal': forms.Select(attrs={'class': 'form-control-modern form-select'}),
            
            'tipo_lesion': forms.Select(attrs={'class': 'form-control-modern form-select'}),
            'tratamiento_inicial': forms.Select(attrs={'class': 'form-control-modern form-select'}),
            'parte_cuerpo_afectada': forms.HiddenInput(), # Se llena vía JS (Three.js)
            'detalle_parte_afectada': forms.TextInput(attrs={'class': 'form-control-modern', 'placeholder': 'Ej: dedo índice, falange distal'}),

            'danio_propiedad': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'detalle_danio_propiedad': forms.Textarea(attrs={'class': 'form-control-modern', 'rows': 2}),
            'danio_medio_ambiente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            
            'medidas_inmediatas': forms.Textarea(attrs={'class': 'form-control-modern', 'rows': 3, 'placeholder': 'Acciones tomadas al instante...'}),
            'evidencia_fotografica': forms.FileInput(attrs={'class': 'form-control-modern'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and not user.is_superuser:
            self.fields['empresa'].queryset = self.fields['empresa'].queryset.filter(prevencionista=user)

    def clean(self):
        cleaned = super().clean()
        tipo = cleaned.get('tipo_accidente')
        if tipo in ['accidente_trabajo', 'accidente_trayecto']:
            if not cleaned.get('nombre_completo_accidentado'):
                self.add_error('nombre_completo_accidentado', 'El registro de accidente debe identificar a la persona afectada.')
            if not cleaned.get('sexo_accidentado'):
                self.add_error('sexo_accidentado', 'El D.S. N.º 44 exige registrar el sexo en accidentes del trabajo y de trayecto.')
        if cleaned.get('severidad_inicial') == 'fatal' and cleaned.get('criterio_gravedad_legal') == 'ninguno':
            self.add_error('criterio_gravedad_legal', 'Un evento fatal no puede quedar marcado sin criterio legal; confirma la clasificación.')
        return cleaned

class DeclaracionAccidenteForm(forms.ModelForm):
    class Meta:
        model = DeclaracionAccidente
        exclude = ['reporte', 'registrado_por', 'creado_en']
        widgets = {
            'tipo_participacion': forms.Select(attrs={'class': 'form-control-modern form-select'}),
            'nombre_completo': forms.TextInput(attrs={'class': 'form-control-modern', 'autocomplete': 'name'}),
            'rut': forms.TextInput(attrs={'class': 'form-control-modern', 'placeholder': '12.345.678-9'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control-modern'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control-modern', 'type': 'tel'}),
            'fecha_declaracion': forms.DateInput(attrs={'class': 'form-control-modern', 'type': 'date'}),
            'actividad_al_momento': forms.Textarea(attrs={'class': 'form-control-modern', 'rows': 2}),
            'como_ocurrio_lesion': forms.Textarea(attrs={'class': 'form-control-modern', 'rows': 2}),
            'que_provoco_lesion': forms.Textarea(attrs={'class': 'form-control-modern', 'rows': 2}),
            'notifico_mismo_dia': forms.Select(attrs={'class': 'form-control-modern form-select'}),
            'aviso_a': forms.TextInput(attrs={'class': 'form-control-modern'}),
            'testigos_identificados': forms.Textarea(attrs={'class': 'form-control-modern', 'rows': 2}),
            'jefatura_directa': forms.TextInput(attrs={'class': 'form-control-modern'}),
            'cargo_jefatura': forms.TextInput(attrs={'class': 'form-control-modern'}),
            'relato': forms.Textarea(attrs={
                'class': 'form-control-modern',
                'rows': 5,
                'placeholder': 'Registre el relato en primera persona y con las palabras del declarante.',
            }),
            'croquis_o_evidencia': forms.FileInput(attrs={
                'class': 'form-control-modern',
                'accept': 'image/*,.pdf,.doc,.docx',
            }),
            'firma_nombre': forms.TextInput(attrs={'class': 'form-control-modern'}),
            'confirmada_por_declarante': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('confirmada_por_declarante') and not cleaned.get('firma_nombre'):
            self.add_error('firma_nombre', 'Registre el nombre de quien confirma la declaración.')
        return cleaned


class DocumentoMutualAccidenteForm(forms.ModelForm):
    class Meta:
        model = DocumentoMutualAccidente
        exclude = ['reporte', 'subido_por', 'subido_en']
        widgets = {
            'tipo_documento': forms.Select(attrs={'class': 'form-control-modern form-select'}),
            'archivo': forms.FileInput(attrs={
                'class': 'form-control-modern',
                'accept': '.pdf,.jpg,.jpeg,.png,.doc,.docx',
            }),
            'emitido_por': forms.TextInput(attrs={
                'class': 'form-control-modern',
                'placeholder': 'ACHS, Mutual de Seguridad, IST, ISL u otro',
            }),
            'fecha_documento': forms.DateInput(attrs={'class': 'form-control-modern', 'type': 'date'}),
            'observacion': forms.Textarea(attrs={'class': 'form-control-modern', 'rows': 2}),
        }


class AlertaAprendizajeForm(forms.ModelForm):
    class Meta:
        model = AlertaAprendizaje
        exclude = ['reporte', 'fecha_difusion', 'actualizado_en']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control-modern'}),
            'relato_anonimizado': forms.Textarea(attrs={
                'class': 'form-control-modern',
                'rows': 3,
                'placeholder': 'Describa lo ocurrido sin nombre, RUT, diagnóstico ni otros identificadores.',
            }),
            'aprendizaje_clave': forms.Textarea(attrs={'class': 'form-control-modern', 'rows': 2}),
            'medidas_preventivas': forms.Textarea(attrs={'class': 'form-control-modern', 'rows': 3}),
            'audiencia': forms.TextInput(attrs={'class': 'form-control-modern'}),
            'canales_difusion': forms.TextInput(attrs={
                'class': 'form-control-modern',
                'placeholder': 'Charla, correo, cartelera, mensajería corporativa',
            }),
            'archivo_alerta': forms.FileInput(attrs={
                'class': 'form-control-modern',
                'accept': '.pdf,.jpg,.jpeg,.png,.ppt,.pptx',
            }),
            'revision_privacidad': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'difundida': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned = super().clean()
        reporte = getattr(self.instance, 'reporte', None)
        relato = (cleaned.get('relato_anonimizado') or '').casefold()
        if reporte:
            identificadores = [
                reporte.nombre_completo_accidentado,
                reporte.rut_accidentado,
            ]
            for identificador in identificadores:
                if identificador and identificador.casefold() in relato:
                    self.add_error(
                        'relato_anonimizado',
                        'La alerta contiene un identificador de la persona. Reescriba el relato de forma anónima.',
                    )
                    break
        if cleaned.get('difundida'):
            if not cleaned.get('revision_privacidad'):
                self.add_error('revision_privacidad', 'Revise la privacidad antes de marcar la alerta como difundida.')
            if not cleaned.get('canales_difusion'):
                self.add_error('canales_difusion', 'Indique al menos un canal de difusión utilizado.')
        return cleaned


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

            # Respuesta y trazabilidad legal
            'diat_emitida': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'folio_diat': forms.TextInput(attrs={'class': 'form-control-modern', 'placeholder': 'Folio o comprobante'}),
            'aviso_dt_seremi': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'fecha_aviso_autoridad': forms.DateTimeInput(attrs={'class': 'form-control-modern', 'type': 'datetime-local'}),
            'faena_suspendida': forms.CheckboxInput(attrs={'class': 'form-check-input'}),

            # Participación y evidencia
            'trabajadores_participantes': forms.Textarea(attrs={'class': 'form-control-modern', 'rows': 2}),
            'testigos_entrevistados': forms.Textarea(attrs={'class': 'form-control-modern', 'rows': 2}),
            'antecedentes_recopilados': forms.Textarea(attrs={'class': 'form-control-modern', 'rows': 3}),
            'secuencia_evento': forms.Textarea(attrs={'class': 'form-control-modern', 'rows': 4, 'placeholder': 'Antes → evento → respuesta inmediata'}),
            'consideraciones_genero': forms.Textarea(attrs={'class': 'form-control-modern', 'rows': 3}),
            
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
            'responsable_verificacion': forms.TextInput(attrs={'class': 'form-control-modern'}),
            'verificacion_eficacia': forms.Textarea(attrs={'class': 'form-control-modern', 'rows': 3}),
            'completada': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ['equipo_investigador', 'responsable_implementacion']:
            self.fields[field_name].required = False

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('completada'):
            return cleaned

        required_for_close = {
            'equipo_investigador': 'Debe identificar al equipo investigador antes de cerrar.',
            'trabajadores_participantes': 'Debe registrar la participación de trabajadores o sus representantes.',
            'porque_5': 'Debe documentar una causa raíz antes de cerrar.',
            'responsable_implementacion': 'Debe asignar un responsable de implementación.',
            'verificacion_eficacia': 'Debe registrar evidencia de eficacia antes de cerrar.',
            'responsable_verificacion': 'Debe asignar quién verificó la eficacia.',
        }
        for field, message in required_for_close.items():
            if not cleaned.get(field):
                self.add_error(field, message)

        if not any(cleaned.get(field) for field in ['medida_eliminar', 'medida_ingenieria', 'medida_administrativa', 'medida_epp']):
            self.add_error('medida_eliminar', 'Defina al menos una medida correctiva antes de cerrar.')

        reporte = getattr(self.instance, 'reporte', None)
        if reporte and reporte.activa_alerta_legal:
            if not cleaned.get('aviso_dt_seremi'):
                self.add_error('aviso_dt_seremi', 'Confirme el aviso inmediato a DT y SEREMI para este caso grave/fatal.')
            if not cleaned.get('faena_suspendida'):
                self.add_error('faena_suspendida', 'Confirme la suspensión y control de la faena afectada.')

        if reporte and reporte.tipo_accidente in ['accidente_trabajo', 'accidente_trayecto']:
            if not reporte.declaraciones.filter(confirmada_por_declarante=True).exists():
                self.add_error(
                    None,
                    'Antes de cerrar, incorpore al menos una declaración confirmada por la persona entrevistada.',
                )
            if not AlertaAprendizaje.objects.filter(
                reporte=reporte,
                difundida=True,
                revision_privacidad=True,
            ).exists():
                self.add_error(
                    None,
                    'Antes de cerrar, registre y difunda la alerta de aprendizaje anonimizada.',
                )

        return cleaned
