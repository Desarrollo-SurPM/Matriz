from django.db import models
from django.conf import settings
from django.utils import timezone
from gestion_riesgos.models import Empresa

# ==========================================
# 1. MANAGERS
# ==========================================

class ReporteManager(models.Manager):
    def flash_pendientes(self):
        return self.filter(estado='reportado')

    def en_investigacion(self):
        return self.filter(estado='en_investigacion')
    
    def cerrados(self):
        return self.filter(estado='cerrado')

    def por_empresa(self, usuario):
        if usuario.is_superuser:
            return self.all()
        return self.filter(empresa__prevencionista=usuario)

# ==========================================
# 2. MODELO PRINCIPAL: REPORTE FLASH
# ==========================================

class ReporteAccidente(models.Model):
    
    ESTADO_CHOICES = [
        ('reportado', 'Reporte Flash (Pendiente de Investigación)'),
        ('en_investigacion', 'En Proceso de Investigación'),
        ('plan_accion', 'Plan de Acción / Medidas'),
        ('cerrado', 'Caso Cerrado'),
    ]

    TIPO_ACCIDENTE_CHOICES = [
        ('accidente_trabajo', 'Accidente del Trabajo (CTP/STP)'),
        ('accidente_trayecto', 'Accidente de Trayecto'),
        ('enfermedad_profesional', 'Enfermedad Profesional'),
        ('incidente', 'Incidente / Cuasi-Accidente (Sin Lesión)'),
        ('otro', 'Otro'),
    ]

    CLASIFICACION_SEVERIDAD_CHOICES = [
        ('insignificante', '1. Insignificante (Cuasi Accidente)'),
        ('leve', '2. Leve (Primeros Auxilios / STP)'),
        ('seria', '3. Seria (Incapacidad Temporal / CTP)'),
        ('grave', '4. Grave (Invalidez Parcial / Daño Mayor)'),
        ('fatal', '5. Fatal o Catastrófica'),
    ]

    TURNO_CHOICES = [
        ('A', 'Turno A'),
        ('B', 'Turno B'),
        ('C', 'Turno C'),
        ('administrativo', 'Administrativo'),
        ('otro', 'Otro'),
    ]

    TIPO_LESION_CHOICES = [
        ('contusion', 'Contusión / Golpe'),
        ('corte', 'Corte / Laceración'),
        ('esguince', 'Esguince / Torcedura'),
        ('quemadura', 'Quemadura'),
        ('fractura', 'Fractura'),
        ('amputacion', 'Amputación'),
        ('lumbago', 'Lumbago'),
        ('otro', 'Otro'),
    ]

    TRATAMIENTO_INICIAL_CHOICES = [
        ('primeros_auxilios', 'Primeros Auxilios (Faena)'),
        ('policlinico', 'Atención en Policlínico'),
        ('mutual', 'Derivación a Organismo Administrador (Mutual/ACHS/IST/ISL)'),
        ('hospital', 'Traslado Urgencia (Hospital/Clínica)'),
        ('ninguno', 'Sin tratamiento'),
    ]

    # --- 1. Contexto General ---
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='reportes_accidentes')
    fecha_reporte = models.DateTimeField(auto_now_add=True)
    reportado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='reportado', db_index=True)

    area_departamento = models.CharField(max_length=255, verbose_name="Área / Sección")
    lugar_exacto = models.CharField(max_length=255, help_text="Ej: Pasillo 4, Bodega de Insumos")
    supervisor_directo = models.CharField(max_length=255, blank=True, null=True)

    # --- 2. Datos del Afectado ---
    nombre_completo_accidentado = models.CharField(max_length=255, blank=True, null=True)
    rut_accidentado = models.CharField(max_length=12, blank=True, null=True, verbose_name="RUT")
    cargo_accidentado = models.CharField(max_length=255, blank=True, null=True)
    antiguedad_cargo = models.CharField(max_length=100, blank=True, null=True, help_text="Tiempo en el cargo")
    
    turno_accidentado = models.CharField(max_length=20, choices=TURNO_CHOICES, blank=True, null=True)
    horas_trabajadas_antes = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True, 
        verbose_name="Horas trabajadas previo al evento"
    )

    # --- 3. El Evento ---
    fecha_accidente = models.DateTimeField(verbose_name="Fecha y Hora del Accidente")
    descripcion_evento = models.TextField(
        verbose_name="Relato del Hecho", 
        help_text="Describa QUÉ pasó, CÓMO, DÓNDE y CUÁNDO. Sea objetivo."
    )
    
    tipo_accidente = models.CharField(max_length=50, choices=TIPO_ACCIDENTE_CHOICES)
    severidad_inicial = models.CharField(max_length=20, choices=CLASIFICACION_SEVERIDAD_CHOICES)
    
    # --- 4. Lesiones y Daños ---
    # Campo automático del 3D (General)
    parte_cuerpo_afectada = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        help_text="Zona general detectada por el modelo 3D (ej: Mano Derecha)"
    )
    
    # NUEVO CAMPO: Detalle manual específico
    detalle_parte_afectada = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        verbose_name="Detalle Específico",
        help_text="Especifique el detalle (ej: Dedo índice, falange distal)"
    )

    tipo_lesion = models.CharField(max_length=50, choices=TIPO_LESION_CHOICES, blank=True, null=True)
    tratamiento_inicial = models.CharField(max_length=50, choices=TRATAMIENTO_INICIAL_CHOICES, blank=True, null=True)
    
    danio_propiedad = models.BooleanField(default=False, verbose_name="¿Daño a propiedad/equipos?")
    detalle_danio_propiedad = models.TextField(blank=True, null=True)
    
    danio_medio_ambiente = models.BooleanField(default=False, verbose_name="¿Daño al medio ambiente?")
    
    # --- 5. Medidas Inmediatas ---
    medidas_inmediatas = models.TextField(
        verbose_name="Acciones Inmediatas",
        help_text="¿Qué se hizo al instante? (Ej: Detención de faena, primeros auxilios, bloqueo)."
    )
    
    evidencia_fotografica = models.ImageField(upload_to='accidentes_evidencia/', blank=True, null=True)

    objects = ReporteManager()

    def __str__(self):
        return f"{self.get_tipo_accidente_display()} - {self.fecha_accidente.strftime('%d/%m/%Y')}"
    
    @property
    def es_grave(self):
        return self.severidad_inicial in ['grave', 'fatal']


# ==========================================
# 3. MODELO DE INVESTIGACIÓN
# ==========================================

class InvestigacionAccidente(models.Model):
    reporte = models.OneToOneField(ReporteAccidente, on_delete=models.CASCADE, primary_key=True)
    
    fecha_inicio_investigacion = models.DateField(default=timezone.now)
    equipo_investigador = models.TextField(help_text="Nombres y cargos del comité investigador")

    # --- A. ANÁLISIS DE CAUSALIDAD (GEMA) ---
    factores_personales = models.TextField(blank=True, verbose_name="Factores Personales")
    factores_trabajo = models.TextField(blank=True, verbose_name="Factores del Trabajo")
    actos_subestandares = models.TextField(blank=True, verbose_name="Actos Subestándares")
    condiciones_subestandares = models.TextField(blank=True, verbose_name="Condiciones Subestándares")

    # --- B. 5 PORQUÉS ---
    porque_1 = models.TextField(verbose_name="1. ¿Por qué ocurrió?", blank=True)
    porque_2 = models.TextField(verbose_name="2. ¿Por qué ocurrió lo anterior?", blank=True)
    porque_3 = models.TextField(verbose_name="3. ¿Por qué ocurrió lo anterior?", blank=True)
    porque_4 = models.TextField(verbose_name="4. ¿Por qué ocurrió lo anterior?", blank=True)
    porque_5 = models.TextField(verbose_name="5. ¿Por qué ocurrió lo anterior (Causa Raíz)?", blank=True)

    # --- C. JERARQUÍA DE CONTROL ---
    medida_eliminar = models.TextField(verbose_name="Eliminar/Sustituir", blank=True)
    medida_ingenieria = models.TextField(verbose_name="Control de Ingeniería", blank=True)
    medida_administrativa = models.TextField(verbose_name="Administrativo", blank=True)
    medida_epp = models.TextField(verbose_name="EPP", blank=True)

    # --- D. CIERRE ---
    responsable_implementacion = models.CharField(max_length=255)
    fecha_plazo = models.DateField()
    completada = models.BooleanField(default=False)
    fecha_cierre = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.completada:
            self.reporte.estado = 'cerrado'
        elif self.reporte.estado == 'reportado':
            self.reporte.estado = 'en_investigacion'
        self.reporte.save()
        super().save(*args, **kwargs)