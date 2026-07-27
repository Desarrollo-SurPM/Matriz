"""Reglas explicables para priorizar la relación preventiva con clientes."""

from datetime import timedelta

from django.db.models import Q
from django.utils import timezone

from accidentes.models import ReporteAccidente
from cumplimiento.models import TareaLegal
from gestion_riesgos.models import Empresa

from .models import Visita


def _nivel(score):
    if score >= 60:
        return "Crítica", "danger"
    if score >= 35:
        return "Alta", "warning"
    if score >= 15:
        return "Planificar", "info"
    return "Al día", "success"


def construir_prioridades_clientes(user, limit=None):
    """
    Calcula una prioridad reproducible, acotada a 100 puntos y con motivos visibles.

    No predice accidentes ni reemplaza criterio profesional. Ordena señales que ya
    existen en la plataforma para reducir olvidos y preparar mejor cada contacto.
    """
    hoy = timezone.localdate()
    ahora = timezone.now()
    empresas = list(Empresa.objects.filter(prevencionista=user).order_by('razon_social'))
    resultado = []

    for empresa in empresas:
        reportes_abiertos = ReporteAccidente.objects.filter(empresa=empresa).exclude(estado='cerrado')
        graves = reportes_abiertos.filter(
            Q(severidad_inicial__in=['grave', 'fatal'])
            | ~Q(criterio_gravedad_legal__in=['ninguno', 'por_confirmar'])
        ).distinct().count()
        abiertos = reportes_abiertos.count()

        tareas = TareaLegal.objects.filter(empresa=empresa, completada=False)
        vencidas = tareas.filter(proxima_fecha_vencimiento__lt=hoy).count()
        proximas = tareas.filter(
            proxima_fecha_vencimiento__gte=hoy,
            proxima_fecha_vencimiento__lte=hoy + timedelta(days=30),
        ).count()

        ultima = Visita.objects.filter(
            empresa=empresa,
            estado='REALIZADA',
        ).order_by('-fecha_hora').first()
        proxima = Visita.objects.filter(
            empresa=empresa,
            estado__in=['PENDIENTE', 'CONFIRMADA'],
            fecha_hora__gte=ahora,
        ).order_by('fecha_hora').first()

        if ultima:
            dias_sin_contacto = max(0, (hoy - timezone.localtime(ultima.fecha_hora).date()).days)
            recencia = 20 if dias_sin_contacto > 60 else 12 if dias_sin_contacto > 30 else 5 if dias_sin_contacto > 14 else 0
        else:
            dias_sin_contacto = None
            recencia = 25

        score = graves * 30 + max(0, abiertos - graves) * 12 + vencidas * 10 + proximas * 4 + recencia
        if proxima:
            score = max(0, score - 6)
        score = min(100, score)
        nivel, color = _nivel(score)

        motivos = []
        if graves:
            motivos.append(f"{graves} caso(s) grave(s) o con alerta legal")
        if abiertos:
            motivos.append(f"{abiertos} investigación(es) abierta(s)")
        if vencidas:
            motivos.append(f"{vencidas} obligación(es) vencida(s)")
        if proximas:
            motivos.append(f"{proximas} vencimiento(s) en 30 días")
        if dias_sin_contacto is None:
            motivos.append("sin gestiones realizadas registradas")
        elif dias_sin_contacto > 14:
            motivos.append(f"{dias_sin_contacto} días desde la última gestión")
        if proxima:
            motivos.append(f"contacto ya agendado para {timezone.localtime(proxima.fecha_hora):%d/%m}")
        if not motivos:
            motivos.append("sin alertas operativas actuales")

        if graves:
            tipo = 'VISITA'
            accion = 'Revisar respuesta, investigación y controles críticos en terreno'
        elif vencidas:
            tipo = 'VIDEOLLAMADA'
            accion = 'Acordar responsables y evidencias para regularizar vencimientos'
        elif ultima is None or (dias_sin_contacto and dias_sin_contacto > 45):
            tipo = 'LLAMADA'
            accion = 'Realizar diagnóstico breve y acordar el siguiente hito preventivo'
        elif proximas:
            tipo = 'EMAIL'
            accion = 'Enviar recordatorio con documentos y responsables requeridos'
        else:
            tipo = 'LLAMADA'
            accion = 'Mantener seguimiento y validar que no existan nuevos cambios'

        resultado.append({
            'empresa': empresa,
            'score': score,
            'nivel': nivel,
            'color': color,
            'motivos': motivos,
            'accion': accion,
            'tipo': tipo,
            'tipo_label': dict(Visita.TIPOS_GESTION).get(tipo, tipo),
            'proxima': proxima,
        })

    resultado.sort(key=lambda item: (-item['score'], item['empresa'].razon_social.lower()))
    return resultado[:limit] if limit else resultado
