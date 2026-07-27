# cumplimiento/models.py

from django.db import models
from gestion_riesgos.models import Empresa, Normativa

class TareaLegal(models.Model):
    """
    Representa una obligación legal con una fecha de vencimiento y frecuencia.
    """
    FRECUENCIA_CHOICES = [
        ('puntual', 'Puntual'),
        ('mensual', 'Mensual'),
        ('trimestral', 'Trimestral'),
        ('semestral', 'Semestral'),
        ('anual', 'Anual'),
    ]

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='tareas_legales')
    normativa = models.ForeignKey(Normativa, on_delete=models.SET_NULL, null=True, blank=True)
    nombre_obligacion = models.CharField(max_length=255, help_text="Ej: Declaración de Emisiones Atmosféricas")
    descripcion = models.TextField(blank=True)
    fecha_inicio = models.DateField(help_text="Primera fecha en que la obligación debe cumplirse.")
    frecuencia = models.CharField(max_length=20, choices=FRECUENCIA_CHOICES, default='puntual')
    proxima_fecha_vencimiento = models.DateField()
    responsable = models.CharField(max_length=255, blank=True, help_text="Nombre o email del responsable.")
    
    # Campos para el seguimiento
    completada = models.BooleanField(default=False)
    fecha_completada = models.DateField(null=True, blank=True)
    
    # Campo para notificaciones (puedes expandir esto a un modelo de usuarios si lo necesitas)
    notificacion_email = models.EmailField(blank=True, help_text="Email para recibir notificaciones de esta tarea.")

    def __str__(self):
        return f"{self.nombre_obligacion} - {self.empresa.razon_social}"

    def save(self, *args, **kwargs):
        # Si es una nueva tarea, la próxima fecha de vencimiento es la fecha de inicio
        if not self.pk:
            self.proxima_fecha_vencimiento = self.fecha_inicio
        super().save(*args, **kwargs)

    @property
    def esta_vencida(self):
        from django.utils import timezone
        return not self.completada and self.proxima_fecha_vencimiento < timezone.localdate()


class EvaluacionProtocolo(models.Model):
    PROTOCOLOS = [
        ('prexor', 'PREXOR · Exposición ocupacional a ruido'),
        ('tmert', 'TMERT · Trastornos musculoesqueléticos'),
        ('silice', 'Sílice · Vigilancia ambiental y de salud'),
        ('psicosocial', 'Riesgos psicosociales · CEAL-SM/SUSESO'),
        ('uv_solar', 'Radiación UV solar'),
        ('mmc', 'Manejo o manipulación manual de carga'),
        ('hipobaria', 'Hipobaria intermitente crónica por gran altitud'),
    ]

    ESTADOS = [
        ('POR_EVALUAR', 'Por evaluar'),
        ('NO_APLICA', 'No aplica con justificación'),
        ('APLICA', 'Aplica · diagnóstico pendiente'),
        ('IMPLEMENTACION', 'Medidas en implementación'),
        ('VIGILANCIA', 'En vigilancia'),
        ('CONTROLADO', 'Controlado · mantener seguimiento'),
    ]

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='evaluaciones_protocolos')
    protocolo = models.CharField(max_length=30, choices=PROTOCOLOS)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='POR_EVALUAR')
    agente_identificado = models.BooleanField(default=False, verbose_name="Peligro o agente identificado")
    diagnostico_exposicion = models.TextField(
        blank=True,
        verbose_name="Diagnóstico de exposición o justificación",
        help_text="Describa tareas, puestos, fuente, duración y evidencia usada para decidir aplicabilidad."
    )
    personas_expuestas = models.PositiveIntegerField(default=0, verbose_name="Personas potencialmente expuestas")
    responsable = models.CharField(max_length=255, blank=True)
    organismo_administrador = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Organismo administrador Ley N.º 16.744"
    )
    fecha_evaluacion = models.DateField(null=True, blank=True, verbose_name="Fecha de evaluación")
    proxima_revision = models.DateField(null=True, blank=True, verbose_name="Próxima revisión")
    medidas_control = models.TextField(blank=True, verbose_name="Medidas y acciones comprometidas")
    evidencia = models.FileField(upload_to='protocolos_minsal/', blank=True, null=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('empresa', 'protocolo')
        ordering = ['empresa__razon_social', 'protocolo']
        verbose_name = "Evaluación de protocolo MINSAL"
        verbose_name_plural = "Evaluaciones de protocolos MINSAL"

    def __str__(self):
        return f"{self.get_protocolo_display()} · {self.empresa.razon_social}"

    @property
    def esta_vencida(self):
        from django.utils import timezone
        return bool(self.proxima_revision and self.proxima_revision < timezone.localdate())
