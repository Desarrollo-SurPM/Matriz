from django.urls import path
from .views import ReporteAccidenteListView, ReporteFlashCreateView, ReporteInvestigacionView, ReporteUpdateView

urlpatterns = [
    # Dashboard / Lista
    path('', ReporteAccidenteListView.as_view(), name='reporte_accidente_list'),
    
    # CORRECCIÓN AQUÍ: Cambiamos name='reporte_flash' por name='reporte_accidente_create'
    path('nuevo/', ReporteFlashCreateView.as_view(), name='reporte_accidente_create'),
    
    # Detalle e Investigación
    path('detalle/<int:pk>/', ReporteInvestigacionView.as_view(), name='reporte_accidente_detail'),
    
    # Edición (si se requiere)
    path('editar/<int:pk>/', ReporteUpdateView.as_view(), name='reporte_accidente_update'),
]