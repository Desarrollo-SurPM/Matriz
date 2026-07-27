from django.urls import path
from .views import (
    AlertaAprendizajeUpdateView,
    DeclaracionAccidenteCreateView,
    DocumentoMutualCreateView,
    ReporteAccidenteListView,
    ReporteFlashCreateView,
    ReporteInvestigacionView,
    ReporteUpdateView,
)

urlpatterns = [
    # Dashboard / Lista
    path('', ReporteAccidenteListView.as_view(), name='reporte_accidente_list'),
    
    # CORRECCIÓN AQUÍ: Cambiamos name='reporte_flash' por name='reporte_accidente_create'
    path('nuevo/', ReporteFlashCreateView.as_view(), name='reporte_accidente_create'),
    
    # Detalle e Investigación
    path('detalle/<int:pk>/', ReporteInvestigacionView.as_view(), name='reporte_accidente_detail'),
    path('detalle/<int:pk>/declaracion/', DeclaracionAccidenteCreateView.as_view(), name='declaracion_accidente_create'),
    path('detalle/<int:pk>/documento-mutual/', DocumentoMutualCreateView.as_view(), name='documento_mutual_create'),
    path('detalle/<int:pk>/alerta/', AlertaAprendizajeUpdateView.as_view(), name='alerta_aprendizaje_update'),
    
    # Edición (si se requiere)
    path('editar/<int:pk>/', ReporteUpdateView.as_view(), name='reporte_accidente_update'),
]
