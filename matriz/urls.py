from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

# Endpoint de healthcheck ultraligero
def healthz(request):
    return HttpResponse("ok")

urlpatterns = [
    path('healthz/', healthz, name='healthz'),
    path('admin/', admin.site.urls),
    
    # 1. Autenticación
    path('accounts/', include('django.contrib.auth.urls')),
    
    # 2. Gestión de Riesgos (Se queda con la raíz para el Dashboard y Home)
    path('', include('gestion_riesgos.urls')), 
    
    # 3. Aplicaciones con Prefijos (CORRECCIÓN AQUÍ)
    # Ahora las URLs serán /cumplimiento/..., /agenda/..., /accidentes/...
    path('cumplimiento/', include('cumplimiento.urls')),
    path('agenda/', include('agenda.urls')),
    path('accidentes/', include('accidentes.urls')), 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)