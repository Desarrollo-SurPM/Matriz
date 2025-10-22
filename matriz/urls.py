from django.conf import settings # <-- Añade esta línea
from django.conf.urls.static import static #
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

# Endpoint de healthcheck ultraligero
def healthz(request):
    return HttpResponse("ok")

urlpatterns = [
    path('healthz/', healthz, name='healthz'),
    path('admin/', admin.site.urls),
    path('', include('gestion_riesgos.urls')),
    path('accounts/', include('django.contrib.auth.urls')), # ¡Añade esta línea!
    path('', include('cumplimiento.urls')),
    path('', include('agenda.urls')),
    path('', include('accidentes.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)