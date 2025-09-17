# src/services/boot_service.py
"""
Este servicio se ejecuta al iniciar el dispositivo (BOOT_COMPLETED).
Su única función es volver a programar todas las alarmas guardadas.
"""

import os
# Asegurarse de que el directorio de la app esté en el path
# para poder importar los otros módulos.
os.environ['PYTHONPATH'] = os.path.join(os.path.dirname(__file__), '../../')

from models import AlarmManager
from services.alarm_service import AlarmService

def reschedule_alarms():
    """
    Carga las alarmas guardadas y las vuelve a programar.
    """
    print("BootService: Iniciando reprogramación de alarmas.")

    try:
        alarm_manager = AlarmManager()
        alarm_service = AlarmService()

        alarms = alarm_manager.obtener_alarmas()

        if not alarms:
            print("BootService: No hay alarmas para reprogramar.")
            return

        for alarm in alarms:
            if alarm.active:
                print(f"BootService: Reprogramando alarma para las {alarm.time}")
                alarm_service.schedule_alarm(alarm)

        print(f"BootService: Reprogramación completada. {len(alarms)} alarmas procesadas.")

    except Exception as e:
        # Es crucial capturar y registrar cualquier error,
        # ya que los fallos en los servicios en segundo plano son difíciles de depurar.
        print(f"BootService: ERROR CRÍTICO durante la reprogramación: {e}")

if __name__ == '__main__':
    # Este bloque se ejecuta cuando el servicio de Python es iniciado por Android.
    reschedule_alarms()
