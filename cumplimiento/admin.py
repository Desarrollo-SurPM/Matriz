from django.contrib import admin
from .models import TareaLegal

@admin.register(TareaLegal)
class TareaLegalAdmin(admin.ModelAdmin):
    list_display = ('nombre_obligacion', 'empresa', 'proxima_fecha_vencimiento', 'frecuencia', 'completada')
    list_filter = ('empresa', 'frecuencia', 'completada')
    search_fields = ('nombre_obligacion', 'descripcion', 'empresa__razon_social')
    ordering = ('proxima_fecha_vencimiento',)