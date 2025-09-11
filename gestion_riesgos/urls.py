# gestion_riesgos/urls.py

from django.urls import path
from .views import (
    welcome_page,
    MatrizRiesgosView,
    ProcesoListView, ProcesoCreateView, ProcesoUpdateView, ProcesoDeleteView,
    SubprocesoListView, SubprocesoCreateView, SubprocesoUpdateView, SubprocesoDeleteView,
    RiesgoCreateView, RiesgoUpdateView, RiesgoDeleteView,
)

urlpatterns = [
    # Rutas principales
    path('', welcome_page, name='welcome'),
    path('matriz/', MatrizRiesgosView.as_view(), name='matriz_riesgos'),

    # Rutas para Procesos
    path('procesos/', ProcesoListView.as_view(), name='proceso_list'),
    path('procesos/nuevo/', ProcesoCreateView.as_view(), name='proceso_create'),
    path('procesos/<int:pk>/editar/', ProcesoUpdateView.as_view(), name='proceso_update'),
    path('procesos/<int:pk>/eliminar/', ProcesoDeleteView.as_view(), name='proceso_delete'),

    # Rutas para Subprocesos
    path('subprocesos/', SubprocesoListView.as_view(), name='subproceso_list'),
    path('subprocesos/nuevo/', SubprocesoCreateView.as_view(), name='subproceso_create'),
    path('subprocesos/<int:pk>/editar/', SubprocesoUpdateView.as_view(), name='subproceso_update'),
    path('subprocesos/<int:pk>/eliminar/', SubprocesoDeleteView.as_view(), name='subproceso_delete'),

    # Rutas para Riesgos
    path('riesgos/nuevo/', RiesgoCreateView.as_view(), name='riesgo_create'),
    path('riesgos/<int:pk>/editar/', RiesgoUpdateView.as_view(), name='riesgo_update'),
    path('riesgos/<int:pk>/eliminar/', RiesgoDeleteView.as_view(), name='riesgo_delete'),
]