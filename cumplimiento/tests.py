from django.contrib.auth import get_user_model
from django.test import TestCase

from gestion_riesgos.models import DetalleIPER, Empresa, MatrizIPER

from .services import sugerir_protocolos_desde_iper


class ProtocolSuggestionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='protocolos')
        self.empresa = Empresa.objects.create(
            prevencionista=self.user,
            razon_social='Cliente Expuesto SpA',
            rut='76.444.444-4',
        )
        self.matriz = MatrizIPER.objects.create(empresa=self.empresa)

    def test_codes_create_explainable_suggestions(self):
        DetalleIPER.objects.create(
            matriz=self.matriz,
            codigo_riesgo='P1, O1, P4, D2',
            peligro_factor='Ruido, polvo de hormigón y radiación UV solar',
            tarea='Corte al aire libre',
        )
        codigos = {item['codigo'] for item in sugerir_protocolos_desde_iper(self.empresa)}
        self.assertEqual(codigos, {'prexor', 'silice', 'uv_solar', 'psicosocial'})

    def test_generic_aerosol_does_not_assume_silica(self):
        DetalleIPER.objects.create(
            matriz=self.matriz,
            codigo_riesgo='O1',
            peligro_factor='Aerosol sólido sin agente caracterizado',
        )
        codigos = {item['codigo'] for item in sugerir_protocolos_desde_iper(self.empresa)}
        self.assertNotIn('silice', codigos)
