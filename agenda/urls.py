from django.urls import path
from . import views

urlpatterns = [
    path('api/all_events/', views.all_events, name='all_events'),

    # --- URLs para Visitas ---
    path('visitas/', views.VisitaListView.as_view(), name='visita_list'),
    path('visitas/agendar/', views.VisitaCreateView.as_view(), name='visita_create'),
    path('visitas/<int:pk>/editar/', views.VisitaUpdateView.as_view(), name='visita_update'),
    path('visitas/<int:pk>/eliminar/', views.VisitaDeleteView.as_view(), name='visita_delete'),

    # --- URLs para Recordatorios ---
    path('recordatorios/', views.RecordatorioListView.as_view(), name='recordatorio_list'),
    path('recordatorios/crear/', views.RecordatorioCreateView.as_view(), name='recordatorio_create'),
    path('recordatorios/<int:pk>/editar/', views.RecordatorioUpdateView.as_view(), name='recordatorio_update'),
    path('recordatorios/<int:pk>/eliminar/', views.RecordatorioDeleteView.as_view(), name='recordatorio_delete'),
]