"""Reglas explicables que convierten hallazgos IPER en revisiones sugeridas."""

import re

from gestion_riesgos.models import DetalleIPER


PROTOCOLO_LABELS = {
    'prexor': 'PREXOR · ruido',
    'tmert': 'TMERT · sobrecarga musculoesquelética',
    'silice': 'Sílice · exposición a polvo respirable',
    'psicosocial': 'CEAL-SM/SUSESO · factores psicosociales',
    'uv_solar': 'Radiación UV solar',
    'mmc': 'Manejo manual de carga o personas',
    'hipobaria': 'Hipobaria por gran altitud',
}


def _codigos(valor):
    return {
        codigo.upper()
        for codigo in re.findall(r'\b[A-Z]{1,2}\d{0,2}\b', (valor or '').upper())
    }


def sugerir_protocolos_desde_iper(empresa):
    """Devuelve señales, no decisiones automáticas de aplicabilidad."""
    hallazgos = {}
    filas = DetalleIPER.objects.filter(matriz__empresa=empresa).values(
        'codigo_riesgo',
        'peligro_factor',
        'riesgo',
        'tarea',
        'puesto_trabajo',
    )

    def agregar(protocolo, codigo, motivo):
        item = hallazgos.setdefault(protocolo, {
            'codigo': protocolo,
            'nombre': PROTOCOLO_LABELS[protocolo],
            'codigos': set(),
            'motivos': set(),
        })
        item['codigos'].add(codigo)
        item['motivos'].add(motivo)

    for fila in filas:
        codigos = _codigos(fila['codigo_riesgo'])
        texto = ' '.join(str(fila[campo] or '') for campo in [
            'peligro_factor', 'riesgo', 'tarea', 'puesto_trabajo'
        ]).casefold()

        for codigo in codigos:
            if codigo == 'P1':
                agregar('prexor', codigo, 'La IPER registra exposición a ruido.')
            if codigo.startswith('D') and codigo[1:].isdigit():
                agregar(
                    'psicosocial',
                    codigo,
                    'Existe un código psicosocial. Las dimensiones D1–D5 del archivo son históricas; la evaluación debe usar el instrumento vigente.',
                )
            if codigo in {'R1', 'R2'}:
                agregar('mmc', codigo, 'La tarea considera manejo manual de cargas o personas.')
            if codigo == 'S1' or (codigo.startswith('T') and codigo[1:].isdigit()):
                agregar('tmert', codigo, 'La IPER registra repetición o sobrecarga postural.')
            if codigo == 'P8':
                agregar('hipobaria', codigo, 'La IPER registra exposición a bajas presiones.')
            if codigo == 'O1' and any(palabra in texto for palabra in [
                'sílice', 'silice', 'cuarzo', 'polvo mineral', 'hormigón', 'hormigon', 'concreto'
            ]):
                agregar('silice', codigo, 'Aerosol sólido asociado a material que puede contener sílice.')
            if codigo in {'P4', 'L1'} and any(palabra in texto for palabra in [
                'solar', 'ultravioleta', 'radiación uv', 'radiacion uv', 'intemperie', 'aire libre'
            ]):
                agregar('uv_solar', codigo, 'Radiación no ionizante asociada a trabajo al aire libre o UV solar.')

    resultado = []
    for item in hallazgos.values():
        item['codigos'] = ', '.join(sorted(item['codigos']))
        item['motivos'] = ' '.join(sorted(item['motivos']))
        resultado.append(item)
    return sorted(resultado, key=lambda item: item['nombre'])
