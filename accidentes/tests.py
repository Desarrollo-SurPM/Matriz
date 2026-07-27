from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from gestion_riesgos.models import Empresa

from .models import AlertaAprendizaje, DeclaracionAccidente, ReporteAccidente


class AccidentAccessTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(username='owner', password='pass-12345')
        self.other = user_model.objects.create_user(username='other', password='pass-12345')
        empresa = Empresa.objects.create(prevencionista=self.other, razon_social='Empresa Ajena', rut='76.222.222-2')
        self.reporte = ReporteAccidente.objects.create(
            empresa=empresa,
            reportado_por=self.other,
            area_departamento='Bodega',
            lugar_exacto='Pasillo 2',
            fecha_accidente=timezone.now(),
            descripcion_evento='Incidente de prueba perteneciente a otro usuario.',
            tipo_accidente='incidente',
            severidad_inicial='insignificante',
            medidas_inmediatas='Se aisló el área.',
        )

    def test_user_cannot_open_another_users_investigation(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse('reporte_accidente_detail', args=[self.reporte.pk]))
        self.assertEqual(response.status_code, 404)

    def test_user_cannot_edit_another_users_report(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse('reporte_accidente_update', args=[self.reporte.pk]))
        self.assertEqual(response.status_code, 404)

    def test_user_cannot_add_declaration_to_another_users_report(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse('declaracion_accidente_create', args=[self.reporte.pk]))
        self.assertEqual(response.status_code, 404)


class ImmediateAccidentWorkflowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='mobile', password='pass-12345')
        self.empresa = Empresa.objects.create(
            prevencionista=self.user,
            razon_social='Cliente Móvil SpA',
            rut='76.333.333-3',
        )
        self.client.force_login(self.user)

    def test_minimum_immediate_report_opens_case(self):
        response = self.client.post(reverse('reporte_accidente_create'), {
            'empresa': self.empresa.pk,
            'area_departamento': 'Planta',
            'lugar_exacto': 'Línea 2',
            'fecha_accidente': '2026-07-14T10:30',
            'tipo_accidente': 'incidente',
            'severidad_inicial': 'insignificante',
            'criterio_gravedad_legal': 'ninguno',
            'descripcion_evento': 'Se proyectó material sin alcanzar a una persona.',
            'medidas_inmediatas': 'Se detuvo y aisló el equipo.',
            'nombre_completo_accidentado': '',
        })

        reporte = ReporteAccidente.objects.get()
        self.assertRedirects(response, reverse('reporte_accidente_detail', args=[reporte.pk]))
        self.assertEqual(reporte.estado, 'reportado')
        self.assertFalse(reporte.nombre_completo_accidentado)

    def test_declaration_and_anonymous_learning_alert(self):
        reporte = ReporteAccidente.objects.create(
            empresa=self.empresa,
            reportado_por=self.user,
            area_departamento='Bodega',
            lugar_exacto='Portón norte',
            fecha_accidente=timezone.now(),
            descripcion_evento='Una persona sufrió una salpicadura.',
            tipo_accidente='accidente_trabajo',
            severidad_inicial='leve',
            criterio_gravedad_legal='ninguno',
            medidas_inmediatas='Lavado y derivación.',
            nombre_completo_accidentado='Persona Ejemplo',
            rut_accidentado='12.345.678-9',
        )
        response = self.client.post(reverse('declaracion_accidente_create', args=[reporte.pk]), {
            'tipo_participacion': 'accidentado',
            'nombre_completo': 'Persona Ejemplo',
            'rut': '12.345.678-9',
            'cargo': 'Operador',
            'telefono': '',
            'fecha_declaracion': '2026-07-14',
            'actividad_al_momento': 'Retiraba elementos de protección.',
            'como_ocurrio_lesion': 'Se proyectó una gota.',
            'que_provoco_lesion': 'Residuo líquido.',
            'notifico_mismo_dia': 'si',
            'aviso_a': 'Supervisión',
            'testigos_identificados': '',
            'jefatura_directa': 'Jefatura',
            'cargo_jefatura': 'Supervisor',
            'relato': 'Al retirar el guante observé la proyección.',
            'firma_nombre': 'Persona Ejemplo',
            'confirmada_por_declarante': 'on',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(DeclaracionAccidente.objects.filter(reporte=reporte, confirmada_por_declarante=True).exists())

        response = self.client.post(reverse('alerta_aprendizaje_update', args=[reporte.pk]), {
            'titulo': 'Aprendizaje por salpicaduras',
            'relato_anonimizado': 'Persona Ejemplo retiraba sus guantes.',
            'aprendizaje_clave': 'El retiro también forma parte de la tarea.',
            'medidas_preventivas': 'Rediseñar la secuencia y controlar residuos.',
            'audiencia': 'Operaciones',
            'canales_difusion': 'Charla',
            'revision_privacidad': 'on',
            'difundida': 'on',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'contiene un identificador')
        self.assertFalse(AlertaAprendizaje.objects.filter(reporte=reporte).exists())

        response = self.client.post(reverse('alerta_aprendizaje_update', args=[reporte.pk]), {
            'titulo': 'Aprendizaje por salpicaduras',
            'relato_anonimizado': 'Durante el retiro de guantes se proyectó un residuo líquido.',
            'aprendizaje_clave': 'El retiro también forma parte de la tarea.',
            'medidas_preventivas': 'Rediseñar la secuencia y controlar residuos.',
            'audiencia': 'Operaciones',
            'canales_difusion': 'Charla',
            'revision_privacidad': 'on',
            'difundida': 'on',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(AlertaAprendizaje.objects.get(reporte=reporte).difundida)

# Create your tests here.
