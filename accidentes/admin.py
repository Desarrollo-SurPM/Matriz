from django.contrib import admin
from .models import (
    AlertaAprendizaje,
    DeclaracionAccidente,
    DocumentoMutualAccidente,
    InvestigacionAccidente,
    ReporteAccidente,
)

@admin.register(ReporteAccidente)
class ReporteAccidenteAdmin(admin.ModelAdmin):
    # Actualizado para usar 'severidad_inicial' y 'estado'
    list_display = (
        'id', 
        'tipo_accidente', 
        'empresa', 
        'fecha_accidente', 
        'estado', 
        'severidad_inicial'
    )
    list_filter = ('estado', 'severidad_inicial', 'tipo_accidente', 'empresa')
    search_fields = ('descripcion_evento', 'empresa__razon_social', 'nombre_completo_accidentado')
    readonly_fields = ('fecha_reporte', 'reportado_por')
    
    fieldsets = (
        ('Información General', {
            'fields': ('empresa', 'area_departamento', 'lugar_exacto', 'fecha_accidente', 'estado')
        }),
        ('Afectado', {
            'fields': ('nombre_completo_accidentado', 'rut_accidentado', 'cargo_accidentado')
        }),
        ('Detalle del Evento', {
            'fields': ('descripcion_evento', 'tipo_accidente', 'severidad_inicial', 'tipo_lesion', 'parte_cuerpo_afectada')
        }),
        ('Evidencia', {
            'fields': ('evidencia_fotografica', 'medidas_inmediatas')
        }),
    )

@admin.register(InvestigacionAccidente)
class InvestigacionAccidenteAdmin(admin.ModelAdmin):
    # Actualizado con los nuevos campos 'fecha_plazo' y quitando 'investigador_lider' si no está en el modelo
    list_display = (
        'reporte', 
        'responsable_implementacion', 
        'fecha_plazo', 
        'completada',
        'fecha_cierre'
    )
    list_filter = ('completada', 'fecha_plazo')
    search_fields = ('reporte__empresa__razon_social', 'responsable_implementacion')


@admin.register(DeclaracionAccidente)
class DeclaracionAccidenteAdmin(admin.ModelAdmin):
    list_display = ('reporte', 'nombre_completo', 'tipo_participacion', 'fecha_declaracion', 'confirmada_por_declarante')
    list_filter = ('tipo_participacion', 'confirmada_por_declarante')
    search_fields = ('nombre_completo', 'rut', 'reporte__empresa__razon_social')


@admin.register(DocumentoMutualAccidente)
class DocumentoMutualAccidenteAdmin(admin.ModelAdmin):
    list_display = ('reporte', 'tipo_documento', 'emitido_por', 'fecha_documento', 'subido_en')
    list_filter = ('tipo_documento', 'emitido_por')
    search_fields = ('reporte__empresa__razon_social', 'observacion')


@admin.register(AlertaAprendizaje)
class AlertaAprendizajeAdmin(admin.ModelAdmin):
    list_display = ('reporte', 'titulo', 'revision_privacidad', 'difundida', 'fecha_difusion')
    list_filter = ('revision_privacidad', 'difundida')
    search_fields = ('titulo', 'relato_anonimizado', 'reporte__empresa__razon_social')
