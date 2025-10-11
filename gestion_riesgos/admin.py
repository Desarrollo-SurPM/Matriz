# gestion_riesgos/admin.py
from django.contrib import admin
from .models import (
    Empresa, Contacto, Matriz, Proceso, Tarea, Riesgo, 
    Documento, SolicitudFirma, Normativa, Peligro
)

admin.site.register(Empresa)
admin.site.register(Contacto)
admin.site.register(Matriz)
admin.site.register(Proceso)
admin.site.register(Tarea) # ANTES DECÍA SUBPROCESO
admin.site.register(Riesgo)
admin.site.register(Documento)
admin.site.register(SolicitudFirma)
admin.site.register(Normativa)
admin.site.register(Peligro)