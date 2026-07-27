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

    SEXO_CHOICES = [
        ('mujer', 'Mujer'),
        ('hombre', 'Hombre'),
        ('intersex', 'Intersex'),
        ('no_informa', 'Prefiere no informar'),
    ]

    CRITERIO_GRAVEDAD_CHOICES = [
        ('ninguno', 'No activa criterio legal grave/fatal'),
        ('por_confirmar', 'Por confirmar con organismo administrador'),
        ('fatal', 'Fatal: fallecimiento asociado al accidente'),
        ('reanimacion', 'Requirió maniobras de reanimación'),
        ('rescate', 'Requirió maniobras de rescate'),
        ('caida_altura', 'Caída desde una altura superior a 1,8 metros'),
        ('amputacion', 'Provocó amputación o pérdida inmediata de una parte del cuerpo'),
        ('multiple', 'Involucró a varias personas y alteró el desarrollo normal de la faena'),
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
    sexo_accidentado = models.CharField(
        max_length=20,
        choices=SEXO_CHOICES,
        blank=True,
        null=True,
        verbose_name="Sexo de la persona accidentada",
        help_text="Dato mínimo del registro de accidentes del D.S. N.º 44."
    )
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
    criterio_gravedad_legal = models.CharField(
        max_length=30,
        choices=CRITERIO_GRAVEDAD_CHOICES,
        default='ninguno',
        verbose_name="Criterio legal de accidente grave o fatal",
        help_text="Si existe más de un criterio, seleccione el de mayor impacto y detalle los demás en el relato."
    )
    
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

    @property
    def activa_alerta_legal(self):
        return self.tipo_accidente != 'accidente_trayecto' and self.criterio_gravedad_legal not in ['ninguno', 'por_confirmar']


# ==========================================
# 3. MODELO DE INVESTIGACIÓN
# ==========================================

class DeclaracionAccidente(models.Model):
    TIPO_PARTICIPACION = [
        ('accidentado', 'Persona accidentada'),
        ('testigo_directo', 'Testigo directo'),
        ('testigo_indirecto', 'Testigo indirecto'),
        ('supervisor', 'Supervisor/a o jefatura'),
        ('otro', 'Otra persona entrevistada'),
    ]

    RESPUESTA_AVISO = [
        ('si', 'Sí'),
        ('no', 'No'),
        ('no_aplica', 'No aplica / no corresponde'),
    ]

    reporte = models.ForeignKey(
        ReporteAccidente,
        on_delete=models.CASCADE,
        related_name='declaraciones',
    )
    tipo_participacion = models.CharField(max_length=30, choices=TIPO_PARTICIPACION)
    nombre_completo = models.CharField(max_length=255)
    rut = models.CharField(max_length=12, blank=True, verbose_name='RUT')
    cargo = models.CharField(max_length=255, blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    fecha_declaracion = models.DateField(default=timezone.localdate)

    actividad_al_momento = models.TextField(verbose_name='Qué estaba haciendo cuando ocurrió el evento')
    como_ocurrio_lesion = models.TextField(blank=True, verbose_name='Cómo ocurrió la lesión o evento')
    que_provoco_lesion = models.TextField(blank=True, verbose_name='Qué elemento o condición produjo la lesión')
    notifico_mismo_dia = models.CharField(max_length=20, choices=RESPUESTA_AVISO, default='si')
    aviso_a = models.CharField(max_length=255, blank=True, verbose_name='A quién dio aviso')
    testigos_identificados = models.TextField(blank=True, verbose_name='Testigos identificados')
    jefatura_directa = models.CharField(max_length=255, blank=True)
    cargo_jefatura = models.CharField(max_length=255, blank=True)
    relato = models.TextField(
        verbose_name='Relato libre de la persona entrevistada',
        help_text='Registre hechos en primera persona. No complete causas ni conclusiones por la persona.',
    )
    croquis_o_evidencia = models.FileField(
        upload_to='accidentes_declaraciones/',
        blank=True,
        null=True,
        verbose_name='Croquis, fotografía o declaración firmada',
    )
    firma_nombre = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Nombre consignado como firma',
    )
    confirmada_por_declarante = models.BooleanField(
        default=False,
        verbose_name='La persona confirma que el relato representa su declaración',
    )
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['fecha_declaracion', 'creado_en']
        verbose_name = 'Declaración de accidente'
        verbose_name_plural = 'Declaraciones de accidente'

    def __str__(self):
        return f'{self.get_tipo_participacion_display()} - {self.nombre_completo}'


class DocumentoMutualAccidente(models.Model):
    TIPOS = [
        ('reca', 'RECA / resolución de calificación'),
        ('alta_medica', 'Alta médica'),
        ('certificado_atencion', 'Certificado de atención'),
        ('diat_comprobante', 'Comprobante DIAT'),
        ('licencia', 'Licencia u orden de reposo'),
        ('otro', 'Otro antecedente recibido'),
    ]

    reporte = models.ForeignKey(
        ReporteAccidente,
        on_delete=models.CASCADE,
        related_name='documentos_mutual',
    )
    tipo_documento = models.CharField(max_length=30, choices=TIPOS)
    archivo = models.FileField(upload_to='accidentes_mutual/')
    emitido_por = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Organismo o entidad emisora',
    )
    fecha_documento = models.DateField(null=True, blank=True)
    observacion = models.TextField(blank=True)
    subido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    subido_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['tipo_documento', '-subido_en']
        verbose_name = 'Documento de mutualidad'
        verbose_name_plural = 'Documentos de mutualidad'

    def __str__(self):
        return f'{self.get_tipo_documento_display()} - reporte #{self.reporte_id}'


class AlertaAprendizaje(models.Model):
    reporte = models.OneToOneField(
        ReporteAccidente,
        on_delete=models.CASCADE,
        related_name='alerta_aprendizaje',
    )
    titulo = models.CharField(max_length=180)
    relato_anonimizado = models.TextField(
        help_text='No incluya nombre, RUT, datos clínicos ni otros identificadores de la persona.',
    )
    aprendizaje_clave = models.TextField()
    medidas_preventivas = models.TextField()
    audiencia = models.CharField(
        max_length=255,
        default='Personas trabajadoras expuestas a tareas similares',
    )
    canales_difusion = models.CharField(
        max_length=255,
        blank=True,
        help_text='Ej: charla, correo, WhatsApp corporativo, cartelera.',
    )
    archivo_alerta = models.FileField(upload_to='accidentes_alertas/', blank=True, null=True)
    revision_privacidad = models.BooleanField(
        default=False,
        verbose_name='Se revisó que la alerta no identifique a la persona',
    )
    difundida = models.BooleanField(default=False)
    fecha_difusion = models.DateTimeField(null=True, blank=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Alerta de aprendizaje'
        verbose_name_plural = 'Alertas de aprendizaje'

    def save(self, *args, **kwargs):
        if self.difundida and not self.fecha_difusion:
            self.fecha_difusion = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Alerta reporte #{self.reporte_id}: {self.titulo}'


class InvestigacionAccidente(models.Model):
    reporte = models.OneToOneField(ReporteAccidente, on_delete=models.CASCADE, primary_key=True)
    
    fecha_inicio_investigacion = models.DateField(default=timezone.now)
    equipo_investigador = models.TextField(help_text="Nombres y cargos del comité investigador")

    # --- A. RESPUESTA Y TRAZABILIDAD LEGAL ---
    diat_emitida = models.BooleanField(default=False, verbose_name="DIAT enviada al organismo administrador")
    folio_diat = models.CharField(max_length=100, blank=True, verbose_name="Folio o comprobante DIAT")
    aviso_dt_seremi = models.BooleanField(default=False, verbose_name="Aviso inmediato a DT y SEREMI de Salud")
    fecha_aviso_autoridad = models.DateTimeField(null=True, blank=True, verbose_name="Fecha y hora del aviso")
    faena_suspendida = models.BooleanField(default=False, verbose_name="Faena afectada suspendida y controlada")

    # --- B. EVIDENCIA, PARTICIPACIÓN Y SECUENCIA ---
    trabajadores_participantes = models.TextField(
        blank=True,
        verbose_name="Participación de trabajadores y representantes",
        help_text="Personas trabajadoras, Comité Paritario, delegado/a o representantes que participaron."
    )
    testigos_entrevistados = models.TextField(blank=True, verbose_name="Testigos entrevistados")
    antecedentes_recopilados = models.TextField(
        blank=True,
        verbose_name="Antecedentes y evidencias recopiladas",
        help_text="Fotografías, procedimientos, permisos, capacitación, mantención, EPP y otros registros."
    )
    secuencia_evento = models.TextField(
        blank=True,
        verbose_name="Secuencia cronológica del evento",
        help_text="Ordene hechos verificables antes, durante y después del evento; evite atribuir culpa."
    )
    consideraciones_genero = models.TextField(
        blank=True,
        verbose_name="Enfoque de género y diversidad",
        help_text="Considere diseño del trabajo, EPP, tareas, exposición, turnos y condiciones diferenciadas."
    )

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
    responsable_verificacion = models.CharField(max_length=255, blank=True, verbose_name="Responsable de verificar eficacia")
    verificacion_eficacia = models.TextField(
        blank=True,
        verbose_name="Evidencia de eficacia",
        help_text="Indique cómo se comprobó que las medidas controlan la causa y no sólo que fueron ejecutadas."
    )
    completada = models.BooleanField(default=False)
    fecha_cierre = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.completada:
            self.reporte.estado = 'cerrado'
        elif any([self.medida_eliminar, self.medida_ingenieria, self.medida_administrativa, self.medida_epp]):
            self.reporte.estado = 'plan_accion'
        else:
            self.reporte.estado = 'en_investigacion'
        self.reporte.save()
        super().save(*args, **kwargs)

    @property
    def porcentaje_avance(self):
        pasos = [
            bool(self.equipo_investigador and self.trabajadores_participantes),
            bool(self.testigos_entrevistados or self.antecedentes_recopilados) and bool(self.secuencia_evento),
            bool(self.factores_personales or self.factores_trabajo or self.actos_subestandares or self.condiciones_subestandares),
            bool(self.porque_1 and self.porque_5),
            bool(self.medida_eliminar or self.medida_ingenieria or self.medida_administrativa or self.medida_epp),
            bool(self.responsable_implementacion and self.fecha_plazo),
            bool(self.completada and self.verificacion_eficacia),
        ]
        return round(sum(pasos) / len(pasos) * 100)

    @property
    def siguiente_paso(self):
        if not self.equipo_investigador or not self.trabajadores_participantes:
            return "Conformar equipo y registrar participación"
        if not self.secuencia_evento:
            return "Recopilar evidencia y ordenar la secuencia"
        if not any([self.factores_personales, self.factores_trabajo, self.actos_subestandares, self.condiciones_subestandares]):
            return "Analizar causas sin asignar culpas"
        if not self.porque_5:
            return "Profundizar hasta la causa raíz"
        if not any([self.medida_eliminar, self.medida_ingenieria, self.medida_administrativa, self.medida_epp]):
            return "Definir controles según jerarquía"
        if not self.completada:
            return "Implementar y verificar eficacia"
        return "Expediente cerrado"
