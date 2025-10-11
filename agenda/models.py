# agenda/models.py

from django.db import models
from django.conf import settings
from gestion_riesgos.models import Empresa

class Visita(models.Model):
    ESTADO_CHOICES = [
        ('propuesta', 'Propuesta'),
        ('agendada', 'Agendada'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='visitas')
    asunto = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    fecha_hora = models.DateTimeField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='propuesta')

    def __str__(self):
        return f"Visita a {self.empresa.razon_social} - {self.asunto}"

class Recordatorio(models.Model):
    prevencionista = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=255)
    fecha_hora = models.DateTimeField()
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.titulo