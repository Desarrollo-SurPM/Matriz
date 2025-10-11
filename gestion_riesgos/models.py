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
    
    class Meta:
        unique_together = ('matriz', 'nombre')

    def __str__(self):
        return self.nombre

class Tarea(models.Model):
    proceso = models.ForeignKey(Proceso, on_delete=models.CASCADE, related_name="tareas")
    puesto_trabajo = models.CharField(max_length=255, help_text="Ej: Soldador Calificado")
    descripcion = models.CharField(max_length=255, help_text="Ej: Cortar planchas de metal")
    es_rutinaria = models.BooleanField(default=True)
    
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

    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE, related_name="riesgos")
    peligro = models.ForeignKey(Peligro, on_delete=models.PROTECT, related_name="riesgos_asociados")
    consecuencias = models.TextField(blank=True, help_text="Ej: Golpes, fracturas")

    # --- EVALUACIÓN INHERENTE POR CATEGORÍA ---
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


    # --- EVALUACIÓN RESIDUAL (GENERAL) ---
    probabilidad_residual = models.PositiveIntegerField(choices=Probabilidad.choices, null=True, blank=True)
    consecuencia_residual = models.PositiveIntegerField(choices=Consecuencia.choices, null=True, blank=True)

    # --- MÉTODOS PRIVADOS DE CÁLCULO ---
    def _calcular_vep(self, probabilidad, consecuencia):
        if probabilidad and consecuencia:
            return probabilidad * consecuencia
        return None

    def _clasificar_riesgo(self, vep):
        if vep is None: return "No evaluado"
        if vep >= 9: return "Intolerable"
        if vep >= 5: return "Importante"
        if vep >= 3: return "Moderado"
        return "Tolerable"

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

    def __str__(self):
        return str(self.peligro)

class MedidaControl(models.Model):
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