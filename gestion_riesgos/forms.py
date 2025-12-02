# gestion_riesgos/forms.py

from django import forms
from .models import Empresa, Matriz, Proceso, Tarea, Riesgo, Documento, Peligro, MatrizIPER

radio_widget = forms.RadioSelect(attrs={'class': 'form-check-input'})
class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['razon_social', 'rut', 'direccion', 'telefono']
        widgets = {
            'razon_social': forms.TextInput(attrs={'class': 'form-control'}),
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }

class MatrizForm(forms.ModelForm):
    class Meta:
        model = Matriz
        fields = ['nombre_proyecto']
        widgets = {
            'nombre_proyecto': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ProcesoForm(forms.ModelForm):
    class Meta:
        model = Proceso
        # --- CAMPO IPER AÑADIDO ---
        fields = ['nombre', 'subproceso']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Soldadura Estructural'}),
            # --- CAMPO IPER AÑADIDO ---
            'subproceso': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Armado de piezas (Opcional)'}),
        }

class TareaForm(forms.ModelForm):
    class Meta:
        model = Tarea
        # --- CAMPOS IPER AÑADIDOS ---
        fields = ['puesto_trabajo', 'descripcion', 'es_rutinaria', 'herramientas_equipos', 'genero_hombres', 'genero_mujeres']
        widgets = {
            'puesto_trabajo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Cortar planchas de metal'}),
            'es_rutinaria': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            # --- CAMPOS IPER AÑADIDOS ---
            'herramientas_equipos': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Ej: Soldadora, Esmeril angular'}),
            'genero_hombres': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'genero_mujeres': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

class RiesgoForm(forms.ModelForm):
    
    # --- NUEVO CAMPO AÑADIDO ---
    medida_control_actual = forms.CharField(
        label="Medida de Control Actual (Existente)",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ej: Uso de guantes de seguridad, Lentes de seguridad...'}),
        required=False,
        help_text="Si ya existe una medida de control para este peligro, descríbala aquí. Puede añadir más desde la vista 'Gestionar'."
    )
    # --- FIN NUEVO CAMPO ---

    class Meta:
        model = Riesgo
        # --- CAMPO IPER AÑADIDO ---
        fields = ['peligro', 'consecuencias', 'identificacion_gema']
        widgets = {
            'peligro': forms.Select(attrs={'class': 'form-control'}),
            'consecuencias': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            # --- CAMPO IPER AÑADIDO ---
            'identificacion_gema': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'peligro': 'Peligro Específico (Codificado)',
        }

    # --- NUEVA FUNCIÓN __init__ ---
    def __init__(self, *args, **kwargs):
        """
        Reordena los campos para que el nuevo campo 'medida_control_actual'
        aparezca al final del formulario.
        """
        super().__init__(*args, **kwargs)
        
        # Define el orden deseado de los campos
        self.order_fields([
            'peligro',
            'consecuencias',
            'identificacion_gema',
            'medida_control_actual' # Mueve el nuevo campo al final
        ])

# --- WIDGETS IPER (Definidos a nivel de MÓDULO para evitar NameError) ---
date_widget = forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
number_widget = forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'style': 'width: 80px;'})
radio_widget = forms.RadioSelect(attrs={'class': 'form-check-input'})


class RiesgoEvaluarForm(forms.ModelForm):
    """Formulario para evaluar el riesgo por categorías y el riesgo residual."""
    
    class Meta:
        model = Riesgo
        # --- CAMPOS IPER AÑADIDOS (PASOS 15-25) ---
        fields = [
            # Evaluación Inherente (Paso 15)
            'probabilidad_seguridad', 'consecuencia_seguridad',
            'probabilidad_higienicos', 'consecuencia_higienicos',
            'probabilidad_psicosociales', 'consecuencia_psicosociales',
            'probabilidad_musculoesqueleticos', 'consecuencia_musculoesqueleticos',
            
            # Gestión y Seguimiento (Pasos 16-21)
            'requisito_legal', 'nueva_medida_control',
            'responsable_gestion', 'fecha_ejecucion',
            'responsable_seguimiento', 'fecha_seguimiento',

            # Evaluación Residual (Paso 22)
            'probabilidad_residual', 'consecuencia_residual',

            # Población Especial (Paso 23)
            'discapacidad_fisica_h', 'discapacidad_fisica_m',
            'discapacidad_cognitiva_h', 'discapacidad_cognitiva_m',
            'discapacidad_sensorial_h', 'discapacidad_sensorial_m',
            'trabajadora_embarazada', 'trabajadora_lactancia',
            'adultos_mayores_h', 'adultos_mayores_m',
            'adolescentes_h', 'adolescentes_m',

            # Medidas Especiales (Paso 24)
            'medidas_control_especiales',
            
            # Evaluación Especial (Paso 25)
            'probabilidad_especial', 'consecuencia_especial'
        ]
        
        widgets = {
            # Evaluación Inherente (usando los widgets definidos a nivel de módulo)
            'probabilidad_seguridad': radio_widget, 
            'consecuencia_seguridad': radio_widget,
            'probabilidad_higienicos': radio_widget, 
            'consecuencia_higienicos': radio_widget,
            'probabilidad_psicosociales': radio_widget, 
            'consecuencia_psicosociales': radio_widget,
            'probabilidad_musculoesqueleticos': radio_widget, 
            'consecuencia_musculoesqueleticos': radio_widget,

            # Gestión y Seguimiento
            'requisito_legal': forms.TextInput(attrs={'class': 'form-control'}),
            'nueva_medida_control': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'responsable_gestion': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_ejecucion': date_widget, # <-- CORREGIDO
            'responsable_seguimiento': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_seguimiento': date_widget, # <-- CORREGIDO

            # Evaluación Residual
            'probabilidad_residual': radio_widget, 
            'consecuencia_residual': radio_widget,

            # Población Especial
            'discapacidad_fisica_h': number_widget, # <-- CORREGIDO
            'discapacidad_fisica_m': number_widget, # <-- CORREGIDO
            'discapacidad_cognitiva_h': number_widget, # <-- CORREGIDO
            'discapacidad_cognitiva_m': number_widget, # <-- CORREGIDO
            'discapacidad_sensorial_h': number_widget, # <-- CORREGIDO
            'discapacidad_sensorial_m': number_widget, # <-- CORREGIDO
            'trabajadora_embarazada': number_widget, # <-- CORREGIDO
            'trabajadora_lactancia': number_widget, # <-- CORREGIDO
            'adultos_mayores_h': number_widget, # <-- CORREGIDO
            'adultos_mayores_m': number_widget, # <-- CORREGIDO
            'adolescentes_h': number_widget, # <-- CORREGIDO
            'adolescentes_m': number_widget, # <-- CORREGIDO

            # Medidas Especiales
            'medidas_control_especiales': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),

            # Evaluación Especial
            'probabilidad_especial': radio_widget, 
            'consecuencia_especial': radio_widget,
        }

class MatrizIPERForm(forms.ModelForm):
    class Meta:
        model = MatrizIPER
        exclude = ['fecha_creacion']
        widgets = {
            'empresa': forms.Select(attrs={'class': 'form-select form-control-modern'}),
            'fecha_documento': forms.DateInput(attrs={'class': 'form-control-modern', 'type': 'date'}),
            # Aplicar estilo moderno a todos los campos de texto
            'departamento_sucursal': forms.TextInput(attrs={'class': 'form-control-modern'}),
            'proyecto': forms.TextInput(attrs={'class': 'form-control-modern'}),
            'codigo_documento': forms.TextInput(attrs={'class': 'form-control-modern'}),
            'version': forms.TextInput(attrs={'class': 'form-control-modern'}),
            'elaborado_por': forms.TextInput(attrs={'class': 'form-control-modern'}),
            'cargo_elabora': forms.TextInput(attrs={'class': 'form-control-modern'}),
            'revisado_por': forms.TextInput(attrs={'class': 'form-control-modern'}),
            'cargo_revisa': forms.TextInput(attrs={'class': 'form-control-modern'}),
            'aprobado_por': forms.TextInput(attrs={'class': 'form-control-modern'}),
            'cargo_aprueba': forms.TextInput(attrs={'class': 'form-control-modern'}),
        }

class PeligroForm(forms.ModelForm):
    class Meta:
        model = Peligro
        fields = ['familia_riesgo', 'riesgo_especifico', 'definicion', 'codigo']
        widgets = {
            'familia_riesgo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Riesgos de Seguridad'}),
            'riesgo_especifico': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Caída de personas a distinto nivel'}),
            'definicion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: SEG-01'}),
        }

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['nombre', 'archivo', 'categoria']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'archivo': forms.FileInput(attrs={'class': 'form-control'}),
            'categoria': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Procedimientos, Charlas'}),
        }