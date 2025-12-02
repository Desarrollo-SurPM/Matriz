from django.urls import path
from . import views

urlpatterns = [
    # --- Dashboard y Landing ---
    path('', views.LandingPageView.as_view(), name='landing'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('api/chart-data/', views.dashboard_chart_data, name='dashboard_chart_data'),

    # --- Empresas ---
    path('empresas/', views.EmpresaListView.as_view(), name='empresa_list'), 
    path('empresa/crear/', views.EmpresaCreateView.as_view(), name='empresa_create'),
    path('empresa/<int:pk>/', views.EmpresaDetailView.as_view(), name='empresa_detail'),
    path('empresa/<int:pk>/editar/', views.EmpresaUpdateView.as_view(), name='empresa_update'),
    path('empresa/<int:pk>/eliminar/', views.EmpresaDeleteView.as_view(), name='empresa_delete'),

    # --- GESTIÓN MATRIZ IPER (NUEVO ESTILO EXCEL) ---
    # 1. Ruta para crear (Redirige a la vista Excel)
    path('empresa/<int:empresa_pk>/matriz_iper/nueva/', views.crear_nueva_matriz_iper, name='matriz_iper_create'),
    
    # 2. Vista Principal (Tabla Editable)
    path('matriz_iper/<int:matriz_id>/', views.matriz_riesgos_view, name='matriz_riesgos_view'),
    
    # 3. API para guardar celdas (AJAX)
    path('api/update-iper/', views.update_detalle_iper, name='update_detalle_iper'),

    # --- Configuración (Peligros y Normativas) ---
    path('peligros/', views.PeligroListView.as_view(), name='peligro_list'),
    path('peligros/crear/', views.PeligroCreateView.as_view(), name='peligro_create'),
    path('peligros/<int:pk>/editar/', views.PeligroUpdateView.as_view(), name='peligro_update'),
    path('peligros/<int:pk>/eliminar/', views.PeligroDeleteView.as_view(), name='peligro_delete'),

    path('normativas/', views.NormativaListView.as_view(), name='normativa_list'),
    path('normativas/crear/', views.NormativaCreateView.as_view(), name='normativa_create'),
    path('normativas/<int:pk>/editar/', views.NormativaUpdateView.as_view(), name='normativa_update'),
    path('normativas/<int:pk>/eliminar/', views.NormativaDeleteView.as_view(), name='normativa_delete'),
]