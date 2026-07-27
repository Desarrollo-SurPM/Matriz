# cumplimiento/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('protocolos-minsal/', views.ProtocolosMinsalView.as_view(), name='protocolos_minsal'),
    path('protocolos-minsal/evaluar/', views.EvaluacionProtocoloCreateView.as_view(), name='protocolo_create'),
    path('protocolos-minsal/<int:pk>/editar/', views.EvaluacionProtocoloUpdateView.as_view(), name='protocolo_update'),
    path('calendario/', views.TareaLegalListView.as_view(), name='calendario_legal'),
    path('calendario/crear/', views.TareaLegalCreateView.as_view(), name='tarea_legal_create'),
    path('calendario/<int:pk>/editar/', views.TareaLegalUpdateView.as_view(), name='tarea_legal_update'),
    path('calendario/<int:pk>/eliminar/', views.TareaLegalDeleteView.as_view(), name='tarea_legal_delete'),
]
