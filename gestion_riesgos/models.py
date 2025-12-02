# gestion_riesgos/models.py

from django.db import models
from django.conf import settings
from django.urls import reverse
import uuid

# --- MÓDULO 1: GESTIÓN DE EMPRESAS Y USUARIOS ---

class Empresa(models.Model):
    """Representa a una empresa cliente del prevencionista."""
    prevencionista = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='empresas_gestionadas')
    razon_social = models.CharField(max_length=255)
    rut = models.CharField(max_length=12, unique=True, help_text="Ej: 76.123.456-7")
    direccion = models.CharField(max_length=255, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.razon_social

    def get_absolute_url(self):
        return reverse('empresa_detail', kwargs={'pk': self.pk})

class Contacto(models.Model):
    """Personas de contacto en cada empresa, por ejemplo, para firmar documentos."""
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='contactos')
    nombre_completo = models.CharField(max_length=255)
    cargo = models.CharField(max_length=100)
    email = models.EmailField()
    telefono = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.nombre_completo} ({self.empresa.razon_social})"

# --- MÓDULO 2: GESTIÓN DE RIESGOS ---

class Peligro(models.Model):
    """Catálogo estandarizado de peligros basado en la normativa."""
    familia_riesgo = models.CharField(max_length=255, help_text="Ej: Riesgos de Seguridad")
    riesgo_especifico = models.CharField(max_length=255, help_text="Ej: Caída de personas")
    definicion = models.TextField(blank=True)
    codigo = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f"{self.riesgo_especifico} ({self.codigo})"

class Matriz(models.Model):
    """La Matriz de Riesgos, que ahora pertenece a una Empresa."""
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='matrices')
    nombre_proyecto = models.CharField(max_length=255, help_text="Nombre del proyecto o área evaluada")
    estado = models.CharField(max_length=50, default='En Elaboración')
    version = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.nombre_proyecto} - {self.empresa.razon_social}"
    
    def get_absolute_url(self):
        return reverse('matriz_detail', kwargs={'pk': self.pk})

class Proceso(models.Model):
    matriz = models.ForeignKey(Matriz, on_delete=models.CASCADE, related_name="procesos")
    nombre = models.CharField(max_length=255, help_text="Ej: Proceso de Soldadura")
    
    # --- CAMPO IPER (Paso 3) ---
    subproceso = models.CharField("Subproceso", max_length=255, blank=True, help_text="Subproceso (Opcional)")

    class Meta:
        unique_together = ('matriz', 'nombre')

    def __str__(self):
        return self.nombre

class Tarea(models.Model):
    proceso = models.ForeignKey(Proceso, on_delete=models.CASCADE, related_name="tareas")
    puesto_trabajo = models.CharField(max_length=255, help_text="Ej: Soldador Calificado")
    descripcion = models.CharField(max_length=255, help_text="Ej: Cortar planchas de metal")
    es_rutinaria = models.BooleanField(default=True)
    
    # --- CAMPOS IPER (Pasos 4 y 5) ---
    herramientas_equipos = models.TextField("Herramientas y Equipos", blank=True, help_text="Equipos y herramientas utilizados")
    genero_hombres = models.PositiveIntegerField("N° Hombres", default=0, help_text="Número de hombres involucrados")
    genero_mujeres = models.PositiveIntegerField("N° Mujeres", default=0, help_text="Número de mujeres involucradas")
    
    def __str__(self):
        return self.descripcion

# --- MODELO RIESGO ACTUALIZADO CON LÓGICA DE EVALUACIÓN POR CATEGORÍAS (SIN ABREVIACIONES) ---
class Riesgo(models.Model):
    class Probabilidad(models.IntegerChoices):
        BAJA = 1, 'Baja'
        MEDIA = 2, 'Media'
        ALTA = 4, 'Alta'

    class Consecuencia(models.IntegerChoices):
        BAJA = 1, 'Baja'
        MEDIA = 2, 'Media'
        ALTA = 4, 'Alta'
    
    # --- CAMPOS IPER (Paso 13) ---
    class Gema(models.TextChoices):
        GENTE = 'G', 'Gente'
        EQUIPO = 'E', 'Equipo'
        MATERIAL = 'M', 'Material'
        AMBIENTE = 'A', 'Ambiente'
        NO_APLICA = 'N/A', 'No Aplica'

    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE, related_name="riesgos")
    peligro = models.ForeignKey(Peligro, on_delete=models.PROTECT, related_name="riesgos_asociados")
    consecuencias = models.TextField(blank=True, help_text="Ej: Golpes, fracturas")
    
    # --- CAMPO IPER (Paso 13) ---
    identificacion_gema = models.CharField("GEMA", max_length=10, choices=Gema.choices, default=Gema.NO_APLICA)

    # --- EVALUACIÓN INHERENTE POR CATEGORÍA (Paso 15) ---
    # Seguridad y Emergencias
    probabilidad_seguridad = models.PositiveIntegerField("Probabilidad S&E", choices=Probabilidad.choices, null=True, blank=True)
    consecuencia_seguridad = models.PositiveIntegerField("Consecuencia S&E", choices=Consecuencia.choices, null=True, blank=True)

    # Higiénicos
    probabilidad_higienicos = models.PositiveIntegerField("Probabilidad Higiene", choices=Probabilidad.choices, null=True, blank=True)
    consecuencia_higienicos = models.PositiveIntegerField("Consecuencia Higiene", choices=Consecuencia.choices, null=True, blank=True)
    
    # Psicosociales
    probabilidad_psicosociales = models.PositiveIntegerField("Probabilidad Psicosocial", choices=Probabilidad.choices, null=True, blank=True)
    consecuencia_psicosociales = models.PositiveIntegerField("Consecuencia Psicosocial", choices=Consecuencia.choices, null=True, blank=True)

    # Músculo-esqueléticos
    probabilidad_musculoesqueleticos = models.PositiveIntegerField("Probabilidad M-E", choices=Probabilidad.choices, null=True, blank=True)
    consecuencia_musculoesqueleticos = models.PositiveIntegerField("Consecuencia M-E", choices=Consecuencia.choices, null=True, blank=True)

    # --- CAMPOS IPER (Pasos 16-21): GESTIÓN DE MEDIDAS PROPUESTAS ---
    requisito_legal = models.CharField("Requisito Legal", max_length=255, blank=True, help_text="Requisito legal asociado a la medida de control")
    nueva_medida_control = models.TextField("Nueva Medida de Control", blank=True, help_text="Nueva medida de control o eliminación (Opcional)")
    responsable_gestion = models.CharField("Responsable Gestión", max_length=255, blank=True, help_text="Persona o departamento responsable de gestionar")
    fecha_ejecucion = models.DateField("Fecha Ejecución", null=True, blank=True)
    responsable_seguimiento = models.CharField("Responsable Seguimiento", max_length=255, blank=True, help_text="Responsable del seguimiento MIPER")
    fecha_seguimiento = models.DateField("Fecha Seguimiento", null=True, blank=True)

    # --- EVALUACIÓN RESIDUAL (Paso 22) ---
    probabilidad_residual = models.PositiveIntegerField(choices=Probabilidad.choices, null=True, blank=True)
    consecuencia_residual = models.PositiveIntegerField(choices=Consecuencia.choices, null=True, blank=True)

    # --- CAMPOS IPER (Paso 23): POBLACIÓN ESPECIAL ---
    discapacidad_fisica_h = models.PositiveIntegerField("Disc. Física Hombres", default=0, null=True, blank=True)
    discapacidad_fisica_m = models.PositiveIntegerField("Disc. Física Mujeres", default=0, null=True, blank=True)
    discapacidad_cognitiva_h = models.PositiveIntegerField("Disc. Cognitiva Hombres", default=0, null=True, blank=True)
    discapacidad_cognitiva_m = models.PositiveIntegerField("Disc. Cognitiva Mujeres", default=0, null=True, blank=True)
    discapacidad_sensorial_h = models.PositiveIntegerField("Disc. Sensorial Hombres", default=0, null=True, blank=True)
    discapacidad_sensorial_m = models.PositiveIntegerField("Disc. Sensorial Mujeres", default=0, null=True, blank=True)
    trabajadora_embarazada = models.PositiveIntegerField("Trab. Embarazada", default=0, null=True, blank=True)
    trabajadora_lactancia = models.PositiveIntegerField("Trab. Lactancia", default=0, null=True, blank=True)
    adultos_mayores_h = models.PositiveIntegerField("Adultos Mayores H", default=0, null=True, blank=True)
    adultos_mayores_m = models.PositiveIntegerField("Adultos Mayores M", default=0, null=True, blank=True)
    adolescentes_h = models.PositiveIntegerField("Adolescentes H", default=0, null=True, blank=True)
    adolescentes_m = models.PositiveIntegerField("Adolescentes M", default=0, null=True, blank=True)

    # --- CAMPOS IPER (Paso 24) ---
    medidas_control_especiales = models.TextField("Medidas Control Especiales", blank=True, help_text="Medidas para grupos con discapacidades o condiciones especiales")

    # --- CAMPOS IPER (Paso 25): EVALUACIÓN ESPECIAL ---
    probabilidad_especial = models.PositiveIntegerField("Probabilidad Especial", choices=Probabilidad.choices, null=True, blank=True)
    consecuencia_especial = models.PositiveIntegerField("Consecuencia Especial", choices=Consecuencia.choices, null=True, blank=True)

    # --- MÉTODOS PRIVADOS DE CÁLCULO ---
    def _calcular_vep(self, probabilidad, consecuencia):
        if probabilidad and consecuencia:
            return probabilidad * consecuencia
        return None

    def _clasificar_riesgo(self, vep):
        if vep is None: return "No evaluado"
        # Valores actualizados según la lógica P(1,2,4) * C(1,2,4) -> Max 16
        if vep >= 9: return "Intolerable" # 4x4, 4x3(no existe), 3x4(no existe), 3x3(no existe) -> 16, 12, 9
        if vep >= 5: return "Importante" # -> 8, 6
        if vep >= 3: return "Moderado" # -> 4, 3
        return "Tolerable" # -> 2, 1

    # --- PROPIEDADES PARA CÁLCULOS DE SEGURIDAD Y EMERGENCIAS ---
    @property
    def valor_vep_seguridad(self):
        return self._calcular_vep(self.probabilidad_seguridad, self.consecuencia_seguridad)

    @property
    def clasificacion_riesgo_seguridad(self):
        return self._clasificar_riesgo(self.valor_vep_seguridad)

    # --- PROPIEDADES PARA CÁLCULOS HIGIÉNICOS ---
    @property
    def valor_vep_higienicos(self):
        return self._calcular_vep(self.probabilidad_higienicos, self.consecuencia_higienicos)

    @property
    def clasificacion_riesgo_higienicos(self):
        return self._clasificar_riesgo(self.valor_vep_higienicos)

    # --- PROPIEDADES PARA CÁLCULOS PSICOSOCIALES ---
    @property
    def valor_vep_psicosociales(self):
        return self._calcular_vep(self.probabilidad_psicosociales, self.consecuencia_psicosociales)
    
    @property
    def clasificacion_riesgo_psicosociales(self):
        return self._clasificar_riesgo(self.valor_vep_psicosociales)

    # --- PROPIEDADES PARA CÁLCULOS MÚSCULO-ESQUELÉTICOS ---
    @property
    def valor_vep_musculoesqueleticos(self):
        return self._calcular_vep(self.probabilidad_musculoesqueleticos, self.consecuencia_musculoesqueleticos)

    @property
    def clasificacion_riesgo_musculoesqueleticos(self):
        return self._clasificar_riesgo(self.valor_vep_musculoesqueleticos)

    # --- PROPIEDADES PARA EL RIESGO INHERENTE MÁXIMO ---
    @property
    def valor_vep_inherente_maximo(self):
        """Devuelve el VEP inherente más alto de todas las categorías."""
        veps = [
            self.valor_vep_seguridad, 
            self.valor_vep_higienicos, 
            self.valor_vep_psicosociales, 
            self.valor_vep_musculoesqueleticos
        ]
        valid_veps = [v for v in veps if v is not None]
        return max(valid_veps) if valid_veps else None

    @property
    def clasificacion_riesgo_inherente_maximo(self):
        return self._clasificar_riesgo(self.valor_vep_inherente_maximo)

    # --- PROPIEDADES PARA EL RIESGO RESIDUAL ---
    @property
    def valor_vep_residual(self):
        return self._calcular_vep(self.probabilidad_residual, self.consecuencia_residual)

    @property
    def clasificacion_riesgo_residual(self):
        return self._clasificar_riesgo(self.valor_vep_residual)
    
    # --- PROPIEDADES PARA EL RIESGO ESPECIAL (Paso 25/26) ---
    @property
    def valor_vep_especial(self):
        return self._calcular_vep(self.probabilidad_especial, self.consecuencia_especial)

    @property
    def clasificacion_riesgo_especial(self):
        return self._clasificar_riesgo(self.valor_vep_especial)

    def __str__(self):
        return str(self.peligro)

class MedidaControl(models.Model):
    """Medida de control existente (Paso 14)"""
    riesgo = models.ForeignKey(Riesgo, on_delete=models.CASCADE, related_name="medidas_control")
    descripcion = models.TextField()
    
    def __str__(self):
        return self.descripcion[:50]
        
# --- MÓDULO 3: GESTOR DOCUMENTAL Y FIRMAS ---

class Documento(models.Model):
    """Organiza y gestiona documentos por empresa."""
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='documentos')
    nombre = models.CharField(max_length=255)
    archivo = models.FileField(upload_to='documentos_empresa/')
    categoria = models.CharField(max_length=100, blank=True, help_text="Ej: Procedimientos, Charlas, Informes")
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.empresa.razon_social})"

class SolicitudFirma(models.Model):
    """Registra el proceso de envío y firma de un documento."""
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente de Firma'),
        ('firmado', 'Firmado'),
        ('rechazado', 'Rechazado'),
    ]
    documento = models.ForeignKey(Documento, on_delete=models.CASCADE, related_name='solicitudes_firma')
    firmante = models.ForeignKey(Contacto, on_delete=models.PROTECT)
    solicitante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    token_acceso = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    def __str__(self):
        return f"Solicitud a {self.firmante.nombre_completo} para firmar {self.documento.nombre}"

# --- MÓDULO 4: LEGISLACIÓN ---

class Normativa(models.Model):
    """Una biblioteca de consulta de legislación relevante."""
    nombre = models.CharField(max_length=255, help_text="Ej: D.S. N° 594")
    descripcion = models.TextField(help_text="Reglamento sobre condiciones sanitarias y ambientales básicas...")
    archivo = models.FileField(upload_to='legislacion/', null=True, blank=True)
    fuente = models.URLField(blank=True, help_text="Enlace a fuente oficial.")
    categoria = models.CharField(max_length=100, blank=True, help_text="Ej: Seguridad, Salud Ocupacional")

    def __str__(self):
        return self.nombre
    
class MatrizIPER(models.Model):
    """
    Representa el documento completo (la hoja 'IPER').
    Contiene los campos de la parte superior del Excel.
    """
    empresa = models.ForeignKey('Empresa', on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    # Campos del Encabezado Excel
    departamento_sucursal = models.CharField(max_length=255, verbose_name="Departamento o Sucursal", blank=True, null=True)
    proyecto = models.CharField(max_length=255, blank=True, null=True)
    codigo_documento = models.CharField(max_length=50, verbose_name="Código", blank=True, null=True)
    version = models.CharField(max_length=20, verbose_name="Revisión/Versión", default="1.0")
    fecha_documento = models.DateField(verbose_name="Fecha del Documento", blank=True, null=True)
    
    # Responsables y Firmas
    elaborado_por = models.CharField(max_length=255, verbose_name="Elaborado por", blank=True, null=True)
    cargo_elabora = models.CharField(max_length=255, default="Encargado Prevención de Riesgos", blank=True, null=True)
    
    revisado_por = models.CharField(max_length=255, verbose_name="Revisado por", blank=True, null=True)
    cargo_revisa = models.CharField(max_length=255, default="Gerente de Servicios", blank=True, null=True)
    
    aprobado_por = models.CharField(max_length=255, verbose_name="Aprobado por", blank=True, null=True)
    cargo_aprueba = models.CharField(max_length=255, blank=True, null=True)

    # Logo específico para esta matriz (opcional, si difiere del de la empresa)
    logo_cliente = models.ImageField(upload_to='logos_matrices/', blank=True, null=True, verbose_name="Logo Cliente")

    def __str__(self):
        return f"IPER {self.codigo_documento} - {self.empresa.razon_social}"

# ==========================================
# 2. FILAS DE LA MATRIZ (El "Excel")
# ==========================================
class DetalleIPER(models.Model):
    """
    Cada fila de la matriz IPER.
    Replica exactamente las columnas del archivo CSV 'IPER'.
    """
    matriz = models.ForeignKey(MatrizIPER, on_delete=models.CASCADE, related_name='filas')
    
    # 1. Identificación
    proceso = models.CharField(max_length=255, verbose_name="Proceso", blank=True, null=True)
    genero = models.CharField(max_length=50, verbose_name="Género", blank=True, null=True, help_text="Hombre - Mujer - Ambos - Otro")
    puesto_trabajo = models.CharField(max_length=255, verbose_name="Puesto de Trabajo", blank=True, null=True)
    tarea = models.TextField(verbose_name="Tarea", blank=True, null=True)
    tipo_rutina = models.CharField(max_length=50, verbose_name="Rutinaria/No Rutinaria", blank=True, null=True)
    
    # 2. Peligros y Riesgos
    codigo_riesgo = models.CharField(max_length=50, verbose_name="Cod. Riesgo", blank=True, null=True)
    peligro_factor = models.TextField(verbose_name="Peligro / Factor", blank=True, null=True)
    riesgo = models.TextField(verbose_name="Riesgo", blank=True, null=True)
    consecuencia = models.TextField(verbose_name="Consecuencias", blank=True, null=True)
    gema = models.CharField(max_length=100, verbose_name="GEMA", blank=True, null=True, help_text="Gente, Equipo, Material, Ambiente")
    
    # 3. Evaluación Inicial (Pura)
    medida_control_actual = models.TextField(verbose_name="Medida Control Actual", blank=True, null=True)
    eval_probabilidad = models.IntegerField(verbose_name="P", blank=True, null=True, default=0)
    eval_severidad = models.IntegerField(verbose_name="S", blank=True, null=True, default=0)
    eval_valor = models.IntegerField(verbose_name="Valor Riesgo", blank=True, null=True, default=0)
    eval_clasificacion = models.CharField(max_length=50, verbose_name="Clasificación", blank=True, null=True)
    
    # 4. Gestión
    requisito_legal = models.TextField(verbose_name="Requisito Legal", blank=True, null=True)
    responsable_ejecucion = models.CharField(max_length=255, verbose_name="Resp. Ejecución", blank=True, null=True)
    responsable_seguimiento = models.CharField(max_length=255, verbose_name="Resp. Seguimiento", blank=True, null=True)
    
    # 5. Riesgo Residual (Post-Control)
    residual_probabilidad = models.IntegerField(verbose_name="P (Res)", blank=True, null=True, default=0)
    residual_severidad = models.IntegerField(verbose_name="S (Res)", blank=True, null=True, default=0)
    residual_valor = models.IntegerField(verbose_name="Valor (Res)", blank=True, null=True, default=0)
    residual_clasificacion = models.CharField(max_length=50, verbose_name="Clasificación (Res)", blank=True, null=True)
    
    # 6. Otros
    condicion_especial = models.TextField(verbose_name="Condición Especial", blank=True, null=True, help_text="Si no cuenta con trabajadores...")
    reevaluacion = models.TextField(verbose_name="Reevaluación Especial", blank=True, null=True)

    class Meta:
        ordering = ['id'] # Para mantener el orden de creación