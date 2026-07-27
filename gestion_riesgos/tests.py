from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accidentes.models import ReporteAccidente

from .models import DetalleIPER, Empresa, MatrizIPER


class ProductInterfaceSmokeTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='prevencion', password='test-pass-123')
        self.empresa = Empresa.objects.create(
            prevencionista=self.user,
            razon_social='Cliente de Prueba SpA',
            rut='76.111.111-1',
        )
        self.client.force_login(self.user)

    def test_main_authenticated_surfaces_render(self):
        names = [
            'dashboard',
            'empresa_list',
            'reporte_accidente_list',
            'visita_list',
            'protocolos_minsal',
            'calendario_legal',
            'reporte_accidente_create',
            'visita_create',
            'protocolo_create',
            'tarea_legal_create',
        ]
        for name in names:
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200)

    def test_public_surfaces_render(self):
        self.client.logout()
        self.assertEqual(self.client.get(reverse('landing')).status_code, 200)
        self.assertEqual(self.client.get(reverse('login')).status_code, 200)

    def test_guided_investigation_renders(self):
        reporte = ReporteAccidente.objects.create(
            empresa=self.empresa,
            reportado_por=self.user,
            area_departamento='Operaciones',
            lugar_exacto='Zona de carga',
            fecha_accidente=timezone.now(),
            descripcion_evento='La persona perdió el equilibrio durante una maniobra.',
            tipo_accidente='accidente_trabajo',
            severidad_inicial='leve',
            criterio_gravedad_legal='ninguno',
            medidas_inmediatas='Se detuvo la tarea y se aisló el sector.',
        )
        response = self.client.get(reverse('reporte_accidente_detail', args=[reporte.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Respuesta inmediata y trazabilidad legal')

    def test_risk_map_is_linked_to_iper_and_stales_after_row_change(self):
        matriz = MatrizIPER.objects.create(
            empresa=self.empresa,
            mapa_riesgos_archivo='mapas_riesgo/mapa.pdf',
            mapa_publicado=True,
            mapa_actualizado_en=timezone.now() - timedelta(days=1),
        )
        DetalleIPER.objects.create(matriz=matriz, codigo_riesgo='P1')
        self.assertTrue(matriz.mapa_requiere_revision)

        response = self.client.get(reverse('matriz_riesgos_view', args=[matriz.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mapa de riesgos asociado a esta IPER')

        otro = get_user_model().objects.create_user(username='otro-prevencionista')
        self.client.force_login(otro)
        response = self.client.get(reverse('matriz_riesgos_view', args=[matriz.pk]))
        self.assertEqual(response.status_code, 404)

# Create your tests here.
