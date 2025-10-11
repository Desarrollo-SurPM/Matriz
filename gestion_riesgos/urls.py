# gestion_riesgos/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('api/chart-data/', views.dashboard_chart_data, name='dashboard_chart_data'),

    # --- Gestión de Empresas (CRUD) ---
    # NUEVO: La lista de empresas ahora vive en su propia URL /empresas/
    path('empresas/', views.EmpresaListView.as_view(), name='empresa_list'), 
    # --- Gestión de Empresas (CRUD) ---
    path('empresa/crear/', views.EmpresaCreateView.as_view(), name='empresa_create'),
    path('empresa/<int:pk>/', views.EmpresaDetailView.as_view(), name='empresa_detail'),
    path('empresa/<int:pk>/editar/', views.EmpresaUpdateView.as_view(), name='empresa_update'),
    path('empresa/<int:pk>/eliminar/', views.EmpresaDeleteView.as_view(), name='empresa_delete'),

    # --- Gestión de Matrices (Anidado dentro de Empresa) ---
    path('empresa/<int:empresa_pk>/matriz/crear/', views.MatrizCreateView.as_view(), name='matriz_create'),
    path('matriz/<int:pk>/', views.MatrizDetailView.as_view(), name='matriz_detail'),
    path('matriz/<int:pk>/eliminar/', views.MatrizDeleteView.as_view(), name='matriz_delete'),

    # --- Gestión de Procesos ---
    path('matriz/<int:matriz_pk>/proceso/crear/', views.ProcesoCreateView.as_view(), name='proceso_create'),
    path('proceso/<int:pk>/editar/', views.ProcesoUpdateView.as_view(), name='proceso_update'),
    path('proceso/<int:pk>/eliminar/', views.ProcesoDeleteView.as_view(), name='proceso_delete'),

    # --- Gestión de Tareas ---
    path('proceso/<int:proceso_pk>/tarea/crear/', views.TareaCreateView.as_view(), name='tarea_create'),
    path('tarea/<int:pk>/editar/', views.TareaUpdateView.as_view(), name='tarea_update'),
    path('tarea/<int:pk>/eliminar/', views.TareaDeleteView.as_view(), name='tarea_delete'),
    
    # --- Gestión de Riesgos ---
    path('tarea/<int:tarea_pk>/riesgo/crear/', views.RiesgoCreateView.as_view(), name='riesgo_create'),
    path('riesgo/<int:pk>/', views.RiesgoDetailView.as_view(), name='riesgo_detail'),
    path('riesgo/<int:pk>/editar/', views.RiesgoUpdateView.as_view(), name='riesgo_update'),
    path('riesgo/<int:pk>/eliminar/', views.RiesgoDeleteView.as_view(), name='riesgo_delete'),

    # --- Gestión de Documentos (Anidado dentro de Empresa) ---
    path('empresa/<int:empresa_pk>/documento/subir/', views.DocumentoCreateView.as_view(), name='documento_create'),
    path('documento/<int:pk>/eliminar/', views.DocumentoDeleteView.as_view(), name='documento_delete'),

     # --- Catálogo de Peligros ---
    path('peligros/', views.PeligroListView.as_view(), name='peligro_list'),
    path('peligros/crear/', views.PeligroCreateView.as_view(), name='peligro_create'),
    path('peligros/<int:pk>/editar/', views.PeligroUpdateView.as_view(), name='peligro_update'),
    path('peligros/<int:pk>/eliminar/', views.PeligroDeleteView.as_view(), name='peligro_delete'),

     # --- Biblioteca de Normativas ---
    path('normativas/', views.NormativaListView.as_view(), name='normativa_list'),
    path('normativas/crear/', views.NormativaCreateView.as_view(), name='normativa_create'),
    path('normativas/<int:pk>/editar/', views.NormativaUpdateView.as_view(), name='normativa_update'),
    path('normativas/<int:pk>/eliminar/', views.NormativaDeleteView.as_view(), name='normativa_delete'),
]