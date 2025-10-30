# cumplimiento/management/commands/enviar_alertas.py

import datetime
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from cumplimiento.models import TareaLegal

class Command(BaseCommand):
    help = 'Envía alertas por correo sobre tareas legales próximas a vencer.'

    def handle(self, *args, **options):
        hoy = datetime.date.today()
        # Define el umbral de días para las alertas (ej. 7 días)
        limite_alerta = hoy + datetime.timedelta(days=7)

        # Filtra las tareas que no están completadas y cuya fecha de vencimiento está dentro del umbral
        tareas_a_notificar = TareaLegal.objects.filter(
            proxima_fecha_vencimiento__lte=limite_alerta,
            completada=False
        )

        for tarea in tareas_a_notificar:
            if tarea.notificacion_email:
                asunto = f"Alerta de Vencimiento: {tarea.nombre_obligacion}"
                mensaje = (
                    f"Hola,\n\n"
                    f"Te recordamos que la obligación '{tarea.nombre_obligacion}' para la empresa '{tarea.empresa.razon_social}' "
                    f"vence el {tarea.proxima_fecha_vencimiento.strftime('%d-%m-%Y')}.\n\n"
                    f"Por favor, asegúrate de completarla a tiempo.\n\n"
                    f"Saludos,\nEl equipo de Risk-Bee"
                )
                
                send_mail(
                    asunto,
                    mensaje,
                    settings.DEFAULT_FROM_EMAIL,
                    [tarea.notificacion_email],
                    fail_silently=False,
                )
                self.stdout.write(self.style.SUCCESS(f"Alerta enviada para la tarea: '{tarea.nombre_obligacion}'"))

        self.stdout.write(self.style.SUCCESS('Proceso de envío de alertas finalizado.'))