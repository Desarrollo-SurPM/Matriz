from django.contrib import admin
from .models import ReporteAccidente, InvestigacionAccidente

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