from django.db import models
from django.conf import settings
# Importamos el modelo Empresa (ajusta la ruta si está en otra app)
from gestion_riesgos.models import Empresa 

# ==========================================
# MODELO VISITA
# ==========================================
class Visita(models.Model):
    # Opciones de Estado para el Semáforo/KPIs
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADA', 'Confirmada'),
        ('REALIZADA', 'Realizada'),
        ('CANCELADA', 'Cancelada'),
    ]

    TIPOS_GESTION = [
        ('VISITA', 'Visita en terreno'),
        ('VIDEOLLAMADA', 'Videollamada'),
        ('LLAMADA', 'Llamada telefónica'),
        ('EMAIL', 'Correo de seguimiento'),
    ]

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name="Empresa Cliente")
    asunto = models.CharField(max_length=200, verbose_name="Asunto de la Visita")
    fecha_hora = models.DateTimeField(verbose_name="Fecha y Hora")
    tipo_gestion = models.CharField(
        max_length=20,
        choices=TIPOS_GESTION,
        default='VISITA',
        verbose_name="Canal de gestión"
    )
    objetivo = models.TextField(
        blank=True,
        verbose_name="Objetivo y resultado esperado",
        help_text="Defina qué decisión, evidencia o acuerdo debe obtenerse."
    )
    resultado = models.TextField(blank=True, verbose_name="Resultado o acuerdos")
    proxima_accion = models.CharField(max_length=255, blank=True, verbose_name="Próxima acción acordada")
    fecha_proxima_accion = models.DateField(null=True, blank=True, verbose_name="Fecha de próxima acción")
    duracion_minutos = models.PositiveIntegerField(default=60, verbose_name="Duración estimada (minutos)")
    
    # --- NUEVOS CAMPOS ---
    estado = models.CharField(
        max_length=20, 
        choices=ESTADOS, 
        default='PENDIENTE',
        verbose_name="Estado Actual"
    )
    email_solicitud = models.EmailField(
        verbose_name="Correo de Contacto", 
        blank=True, 
        null=True, 
        help_text="Correo al que se enviará la notificación de solicitud."
    )
    # ---------------------

    notas = models.TextField(blank=True, null=True, verbose_name="Notas Adicionales")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Visita Técnica"
        verbose_name_plural = "Visitas Técnicas"
        ordering = ['-fecha_hora']

    def __str__(self):
        return f"{self.get_tipo_gestion_display()}: {self.asunto} - {self.get_estado_display()}"

# ==========================================
# MODELO RECORDATORIO (Sin cambios mayores)
# ==========================================
class Recordatorio(models.Model):
    prevencionista = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    fecha_hora = models.DateTimeField()
    descripcion = models.TextField(blank=True, null=True)
    completado = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo
