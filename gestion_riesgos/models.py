# gestion_riesgos/models.py

from django.db import models

# Los modelos Proceso y Subproceso no cambian
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

# --- Modelo Riesgo ACTUALIZADO ---
class Riesgo(models.Model):
    subproceso = models.ForeignKey(Subproceso, on_delete=models.CASCADE, related_name="riesgos")
    riesgo_especifico = models.CharField(max_length=255, help_text="Ej: Caída de objetos")
    consecuencias = models.TextField(blank=True, help_text="Ej: Golpes, fracturas")
    codigo = models.CharField(max_length=10, blank=True, null=True)

    # --- Evaluación del Riesgo Inherente (Puro) ---
    PROBABILIDAD_CHOICES = [(1, 'Baja (1)'), (2, 'Media (2)'), (4, 'Alta (4)')]
    CONSECUENCIA_CHOICES = [(1, 'Ligeramente Dañino (1)'), (2, 'Dañino (2)'), (4, 'Extremadamente Dañino (4)')]

    probabilidad = models.IntegerField("Probabilidad Inherente", choices=PROBABILIDAD_CHOICES, default=1)
    consecuencia_valor = models.IntegerField("Consecuencia Inherente", choices=CONSECUENCIA_CHOICES, default=1)
    clasificacion_riesgo = models.CharField(max_length=50, blank=True, editable=False)

    # --- NUEVO: Evaluación del Riesgo Residual ---
    probabilidad_residual = models.IntegerField("Probabilidad Residual", choices=PROBABILIDAD_CHOICES, null=True, blank=True)
    consecuencia_residual = models.IntegerField("Consecuencia Residual", choices=CONSECUENCIA_CHOICES, null=True, blank=True)
    clasificacion_riesgo_residual = models.CharField(max_length=50, blank=True, editable=False)

    @property
    def valor_vep(self):
        return self.probabilidad * self.consecuencia_valor

    @property
    def valor_vep_residual(self):
        if self.probabilidad_residual is not None and self.consecuencia_residual is not None:
            return self.probabilidad_residual * self.consecuencia_residual
        return None

    def save(self, *args, **kwargs):
        # Calcula clasificación del riesgo inherente
        vep = self.valor_vep
        if vep == 1: self.clasificacion_riesgo = "Trivial"
        elif vep == 2: self.clasificacion_riesgo = "Tolerable"
        elif vep == 4: self.clasificacion_riesgo = "Moderado"
        elif vep == 8: self.clasificacion_riesgo = "Importante"
        elif vep == 16: self.clasificacion_riesgo = "Intolerable"
        
        # Calcula clasificación del riesgo residual
        vep_res = self.valor_vep_residual
        if vep_res is None:
            self.clasificacion_riesgo_residual = "No evaluado"
        elif vep_res == 1: self.clasificacion_riesgo_residual = "Trivial"
        elif vep_res == 2: self.clasificacion_riesgo_residual = "Tolerable"
        elif vep_res == 4: self.clasificacion_riesgo_residual = "Moderado"
        elif vep_res == 8: self.clasificacion_riesgo_residual = "Importante"
        elif vep_res == 16: self.clasificacion_riesgo_residual = "Intolerable"
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.riesgo_especifico

# --- NUEVO MODELO: Medida de Control ---
class MedidaControl(models.Model):
    TIPO_CONTROL_CHOICES = [
        ('EL', 'Eliminación'),
        ('SU', 'Sustitución'),
        ('CI', 'Control de Ingeniería'),
        ('CA', 'Control Administrativo'),
        ('EP', 'Equipo de Protección Personal'),
    ]
    riesgo = models.ForeignKey(Riesgo, on_delete=models.CASCADE, related_name="medidas_control")
    descripcion = models.TextField(help_text="Describe la medida de control implementada.")
    tipo_control = models.CharField(max_length=2, choices=TIPO_CONTROL_CHOICES)
    responsable = models.CharField(max_length=100, help_text="Cargo o nombre del responsable")
    plazo_implementacion = models.DateField()

    def __str__(self):
        return self.descripcion[:50]