from django.urls import path
from . import views

urlpatterns = [
    path('accidentes/', views.ReporteAccidenteListView.as_view(), name='reporte_accidente_list'),
    path('accidentes/reportar/', views.ReporteAccidenteCreateView.as_view(), name='reporte_accidente_create'),
    path('accidentes/reportar/flash/', views.ReporteFlashView.as_view(), name='reporte_flash'), # Nueva URL
    path('accidentes/<int:pk>/', views.ReporteInvestigacionView.as_view(), name='reporte_accidente_detail'),
]