# accidentes/models.py

from django.db import models
from django.conf import settings
from gestion_riesgos.models import Empresa

class ReporteAccidente(models.Model):
    TIPO_ACCIDENTE_CHOICES = [
        ('accidente_trabajo', 'Accidente del Trabajo'),
        ('accidente_trayecto', 'Accidente de Trayecto'),
        ('enfermedad_profesional', 'Enfermedad Profesional'),
        ('accidente_sin_incapacidad', 'Accidente ocurrido a causa u ocasión del trabajo sin incapacidad'),
        ('enfermedad_laboral_sin_incapacidad', 'Enfermedad laboral sin incapacidad temporal ni permanente'),
        ('accidente_comun', 'Accidente común'),
        ('enfermedad_comun', 'Enfermedad común'),
    ]

    CLASIFICACION_SEVERIDAD_CHOICES = [
        ('incidente', 'Incidente (Casi Accidente)'),
        ('leve', 'Leve (Sin Tiempo Perdido)'),
        ('grave', 'Grave (Con Tiempo Perdido)'),
        ('fatal', 'Fatal'),
    ]

    TURNO_CHOICES = [
        ('manana', 'Mañana'),
        ('tarde', 'Tarde'),
        ('noche', 'Noche'),
    ]

    TIPO_LESION_CHOICES = [
        ('contusion', 'Contusión'),
        ('corte', 'Corte'),
        ('esguince', 'Esguince'),
        # ... agregar más opciones
    ]

    TRATAMIENTO_INICIAL_CHOICES = [
        ('primeros_auxilios', 'Primeros auxilios'),
        ('derivado_mutual', 'Derivado a mutual'),
        ('hospital', 'Hospital'),
        ('otro', 'Otro'),
    ]

    # 1. Información General
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='reportes_accidentes')
    fecha_reporte = models.DateTimeField(auto_now_add=True)
    reportado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    area_departamento = models.CharField(max_length=255, blank=True, null=True)
    supervisor_responsable = models.CharField(max_length=255, blank=True, null=True)

    # 2. Datos del Accidentado
    nombre_completo_accidentado = models.CharField(max_length=255, blank=True, null=True)
    rut_accidentado = models.CharField(max_length=12, blank=True, null=True)
    cargo_accidentado = models.CharField(max_length=255, blank=True, null=True)
    antiguedad_cargo_accidentado = models.CharField(max_length=255, blank=True, null=True)
    turno_accidentado = models.CharField(max_length=20, choices=TURNO_CHOICES, blank=True, null=True)

    # 3. Descripción Breve del Accidente
    descripcion_evento = models.TextField(help_text="Describe detalladamente qué sucedió.")
    lugar_exacto = models.CharField(max_length=255, help_text="Ej: Taller de soldadura, Bodega 2")
    fecha_accidente = models.DateTimeField()

    # 4. Tipo de Accidente (normativo)
    tipo_accidente = models.CharField(max_length=64, choices=TIPO_ACCIDENTE_CHOICES)
    # Clasificación interna de severidad (no normativa)
    clasificacion_severidad = models.CharField(max_length=16, choices=CLASIFICACION_SEVERIDAD_CHOICES, blank=True, null=True, verbose_name='Clasificación de Severidad (Interna)', help_text='Uso interno, no corresponde a la norma')

    # Dato adicional: daño a la propiedad/equipo
    danio_propiedad = models.BooleanField(default=False, verbose_name='Daño a la propiedad/equipo', help_text='Dato adicional, no es un tipo de accidente')
    detalle_danio_propiedad = models.TextField(blank=True, null=True)

    # 5. Lesión / Daño
    tipo_lesion = models.CharField(max_length=50, choices=TIPO_LESION_CHOICES, blank=True, null=True)
    parte_cuerpo_afectada = models.CharField(max_length=255, blank=True, null=True) # Se almacena la parte del cuerpo seleccionada en el modelo 3D
    tratamiento_inicial = models.CharField(max_length=50, choices=TRATAMIENTO_INICIAL_CHOICES, blank=True, null=True)
    
    # 6. Causas Inmediatas (preliminares)
    causas_inmediatas = models.TextField(blank=True, null=True) # Se almacena como texto, ej: "Falta de orden / limpieza, Acto inseguro del trabajador"

    # 7. Medidas Inmediatas Adoptadas
    medidas_inmediatas = models.TextField(blank=True, null=True)

    # 8. Registro Fotográfico (opcional)
    evidencia_fotografica = models.ImageField(upload_to='accidentes_evidencia/', blank=True, null=True, verbose_name="Evidencia Fotográfica")

    def __str__(self):
        return f"{self.get_tipo_accidente_display()} en {self.empresa.razon_social} - {self.fecha_accidente.strftime('%d-%m-%Y')}"


class InvestigacionAccidente(models.Model):
    reporte = models.OneToOneField(ReporteAccidente, on_delete=models.CASCADE, primary_key=True)
    
    # Análisis de Causas (Metodología común)
    causas_inmediatas = models.TextField(help_text="Condiciones y/o actos subestándares. Ej: Piso resbaladizo, no usar EPP.")
    causas_basicas = models.TextField(help_text="Factores personales y/o de trabajo. Ej: Falta de capacitación, mantenimiento deficiente.")
    
    # Plan de Acción
    medidas_correctivas = models.TextField(help_text="Detalla las medidas a implementar para evitar la recurrencia.")
    responsables_implementacion = models.CharField(max_length=255, help_text="Nombres o cargos de los responsables.")
    fecha_limite_implementacion = models.DateField()
    
    # Seguimiento
    completada = models.BooleanField(default=False)
    fecha_cierre = models.DateField(null=True, blank=True)
    
    investigador_lider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Investigación para reporte {self.reporte.id}"