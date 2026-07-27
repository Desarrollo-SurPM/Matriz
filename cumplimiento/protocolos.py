"""Catálogo editorial para orientar aplicabilidad; no reemplaza evaluación técnica."""

FUENTE_MINSAL = "https://www.minsal.cl/salud-ocupacional/"

PROTOCOLOS_MINSAL = {
    'prexor': {
        'sigla': 'PREXOR',
        'nombre': 'Exposición ocupacional a ruido',
        'icono': 'fa-volume-high',
        'color': 'violet',
        'pregunta': '¿Hay máquinas, herramientas o procesos donde deba elevarse la voz o exista medición de ruido?',
        'accion': 'Caracterizar puestos y fuentes; coordinar evaluación con el organismo administrador y gestionar controles.',
        'fuente': FUENTE_MINSAL,
    },
    'tmert': {
        'sigla': 'TMERT',
        'nombre': 'Trastornos musculoesqueléticos relacionados al trabajo',
        'icono': 'fa-person-walking',
        'color': 'blue',
        'pregunta': '¿Existen repetición, fuerza, posturas mantenidas o ciclos que puedan generar sobrecarga?',
        'accion': 'Identificar tareas críticas, evaluar factores y planificar controles con participación de las personas trabajadoras.',
        'fuente': FUENTE_MINSAL,
    },
    'silice': {
        'sigla': 'Sílice',
        'nombre': 'Exposición a sílice cristalina respirable',
        'icono': 'fa-smog',
        'color': 'amber',
        'pregunta': '¿Se corta, perfora, tritura o manipula material que pueda contener sílice y generar polvo?',
        'accion': 'Identificar fuentes, grupos de exposición similar y coordinar vigilancia ambiental y de salud.',
        'fuente': FUENTE_MINSAL,
    },
    'psicosocial': {
        'sigla': 'Psicosocial',
        'nombre': 'Factores de riesgo psicosocial · CEAL-SM/SUSESO',
        'icono': 'fa-brain',
        'color': 'rose',
        'pregunta': '¿La organización cuenta con su ciclo de evaluación y gestión psicosocial vigente y trazable?',
        'accion': 'Planificar participación, aplicación del instrumento vigente, análisis y medidas por unidad de trabajo.',
        'fuente': FUENTE_MINSAL,
    },
    'uv_solar': {
        'sigla': 'UV solar',
        'nombre': 'Exposición ocupacional a radiación ultravioleta solar',
        'icono': 'fa-sun',
        'color': 'orange',
        'pregunta': '¿Hay personas que realizan labores al aire libre con exposición directa a radiación solar?',
        'accion': 'Identificar puestos expuestos y documentar controles de ingeniería, administrativos y protección personal.',
        'fuente': FUENTE_MINSAL,
    },
    'mmc': {
        'sigla': 'MMC',
        'nombre': 'Manejo o manipulación manual de carga',
        'icono': 'fa-box',
        'color': 'green',
        'pregunta': '¿Se levantan, sostienen, transportan, empujan o arrastran cargas o personas?',
        'accion': 'Identificar tareas, evaluar condiciones y priorizar rediseño, ayudas mecánicas y organización del trabajo.',
        'fuente': FUENTE_MINSAL,
    },
    'hipobaria': {
        'sigla': 'Hipobaria',
        'nombre': 'Hipobaria intermitente crónica por gran altitud',
        'icono': 'fa-mountain-sun',
        'color': 'cyan',
        'pregunta': '¿Se realizan turnos o tareas en gran altitud geográfica con exposición intermitente?',
        'accion': 'Caracterizar exposición, verificar aptitud y coordinar vigilancia conforme a la guía técnica aplicable.',
        'fuente': FUENTE_MINSAL,
    },
}
