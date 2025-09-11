# gestion_riesgos/models.py

from django.db import models

class Proceso(models.Model):
    nombre = models.CharField(max_length=255, unique=True, help_text="Ej: Proceso de Soldadura")

    def __str__(self):
        return self.nombre

class Subproceso(models.Model):
    proceso = models.ForeignKey(Proceso, on_delete=models.CASCADE, related_name="subprocesos")
    puesto_trabajo = models.CharField(max_length=255, help_text="Ej: Soldador Calificado")
    tarea = models.CharField(max_length=255, help_text="Ej: Cortar planchas de metal")
    es_rutinaria = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.tarea} ({self.proceso.nombre})"

class Riesgo(models.Model):
    subproceso = models.ForeignKey(Subproceso, on_delete=models.CASCADE, related_name="riesgos")
    riesgo_especifico = models.CharField(max_length=255, help_text="Ej: Caída de objetos")
    consecuencias = models.TextField(blank=True, help_text="Ej: Golpes, fracturas")
    codigo = models.CharField(max_length=10, blank=True, null=True)

    PROBABILIDAD_CHOICES = [(1, 'Baja (1)'), (2, 'Media (2)'), (4, 'Alta (4)')]
    CONSECUENCIA_CHOICES = [(1, 'Ligeramente Dañino (1)'), (2, 'Dañino (2)'), (4, 'Extremadamente Dañino (4)')]

    probabilidad = models.IntegerField(choices=PROBABILIDAD_CHOICES, default=1)
    consecuencia_valor = models.IntegerField(choices=CONSECUENCIA_CHOICES, default=1)
    
    clasificacion_riesgo = models.CharField(max_length=50, blank=True, editable=False)

    @property
    def valor_vep(self):
        return self.probabilidad * self.consecuencia_valor

    def save(self, *args, **kwargs):
        vep = self.valor_vep
        if vep == 1: self.clasificacion_riesgo = "Trivial"
        elif vep == 2: self.clasificacion_riesgo = "Tolerable"
        elif vep == 4: self.clasificacion_riesgo = "Moderado"
        elif vep == 8: self.clasificacion_riesgo = "Importante"
        elif vep == 16: self.clasificacion_riesgo = "Intolerable"
        else: self.clasificacion_riesgo = "No evaluado"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.riesgo_especifico