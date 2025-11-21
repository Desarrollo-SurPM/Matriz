from django.contrib import admin
from .models import ReporteAccidente, InvestigacionAccidente

@admin.register(ReporteAccidente)
class ReporteAccidenteAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'lugar_exacto', 'reportado_por', 'fecha_reporte')
    list_filter = ('tipo_accidente', 'clasificacion_severidad', 'empresa')

@admin.register(InvestigacionAccidente)
class InvestigacionAccidenteAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'investigador_lider', 'completada', 'fecha_limite_implementacion')
    list_filter = ('completada',)