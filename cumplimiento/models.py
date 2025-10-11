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