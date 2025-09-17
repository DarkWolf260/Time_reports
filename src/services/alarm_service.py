# src/services/alarm_service.py
"""
Servicio para gestionar la programación de alarmas nativas de Android.
Utiliza jnius para interactuar con las APIs de Android.
"""
import datetime
import time
from models import Alarm

# Comprobación para evitar errores en entornos no Android
try:
    from jnius import autoclass, cast
    IS_ANDROID = True
except ImportError:
    IS_ANDROID = False

# Clases de Android que se utilizarán
if IS_ANDROID:
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Context = autoclass('android.content.Context')
    Intent = autoclass('android.content.Intent')
    PendingIntent = autoclass('android.app.PendingIntent')
    AlarmManager = autoclass('android.app.AlarmManager')
    Calendar = autoclass('java.util.Calendar')

class AlarmService:
    """
    Gestiona la programación y cancelación de alarmas nativas.
    """
    def __init__(self):
        if IS_ANDROID:
            self.context = PythonActivity.mActivity
            self.alarm_manager = cast(AlarmManager, self.context.getSystemService(Context.ALARM_SERVICE))
        else:
            self.context = None
            self.alarm_manager = None

    def _create_pending_intent(self, alarm: Alarm, is_for_service: bool = True) -> PendingIntent:
        """
        Crea un PendingIntent para una alarma específica.
        Puede crear un intent para un Service o un BroadcastReceiver.
        """
        if is_for_service:
            # Intent para iniciar directamente el servicio de Python
            service_name = "NotificationService" # Debe coincidir con el nombre en buildozer.spec
            service_class_name = f"org.kivy.android.PythonService"

            intent = Intent(self.context, autoclass(service_class_name))
            intent.setAction(service_name) # Identificador único para el servicio

        else:
            # Intent para un BroadcastReceiver (ej. para BOOT_COMPLETED)
            # El action debe ser único para el receiver que definiremos en buildozer.spec
            intent = Intent("com.rubenroy.reportes.BOOT_COMPLETED_RECEIVER")

        intent.putExtra("alarm_id", alarm.id)
        intent.putExtra("alarm_time", alarm.time)
        intent.putExtra("alarm_type", alarm.alarm_type)

        request_code = int(alarm.id.replace('-', '')[:8], 16)

        if is_for_service:
            return PendingIntent.getService(
                self.context,
                request_code,
                intent,
                PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT
            )
        else:
            return PendingIntent.getBroadcast(
                self.context,
                request_code,
                intent,
                PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT
            )

    def schedule_alarm(self, alarm: Alarm):
        """Programa una alarma nativa en el sistema."""
        if not IS_ANDROID or not self.alarm_manager:
            print("INFO: AlarmService: No se puede programar la alarma (no es Android).")
            return

        try:
            pending_intent = self._create_pending_intent(alarm)

            # Calcular la hora de la alarma en milisegundos
            hour, minute = map(int, alarm.time.split(':'))

            calendar = Calendar.getInstance()
            calendar.set(Calendar.HOUR_OF_DAY, hour)
            calendar.set(Calendar.MINUTE, minute)
            calendar.set(Calendar.SECOND, 0)
            calendar.set(Calendar.MILLISECOND, 0)

            # Si la hora ya pasó hoy, programarla para mañana
            if calendar.getTimeInMillis() <= System.currentTimeMillis():
                calendar.add(Calendar.DAY_OF_YEAR, 1)

            trigger_at_millis = calendar.getTimeInMillis()

            # Usar setExactAndAllowWhileIdle para precisión incluso en modo Doze
            self.alarm_manager.setExactAndAllowWhileIdle(
                AlarmManager.RTC_WAKEUP,
                trigger_at_millis,
                pending_intent
            )

            print(f"INFO: Alarma programada para {alarm.time} con ID {alarm.id}")

        except Exception as e:
            print(f"ERROR: No se pudo programar la alarma: {e}")

    def cancel_alarm(self, alarm: Alarm):
        """Cancela una alarma nativa previamente programada."""
        if not IS_ANDROID or not self.alarm_manager:
            print("INFO: AlarmService: No se puede cancelar la alarma (no es Android).")
            return

        try:
            pending_intent = self._create_pending_intent(alarm)
            self.alarm_manager.cancel(pending_intent)
            print(f"INFO: Alarma cancelada para {alarm.time} con ID {alarm.id}")
        except Exception as e:
            print(f"ERROR: No se pudo cancelar la alarma: {e}")

# Para poder probar la lógica de tiempo sin depender de Android
if __name__ == '__main__':
    class MockAlarm:
        def __init__(self, time, id):
            self.time = time
            self.id = id

    alarm = MockAlarm("22:00", "12345")
    hour, minute = map(int, alarm.time.split(':'))

    calendar = Calendar.getInstance()
    calendar.set(Calendar.HOUR_OF_DAY, hour)
    calendar.set(Calendar.MINUTE, minute)

    print(f"Hora de la alarma: {calendar.getTime()}")

    if calendar.getTimeInMillis() < time.time() * 1000:
        calendar.add(Calendar.DAY_OF_YEAR, 1)
        print("La hora ya pasó, se programa para mañana.")

    print(f"Hora de disparo final: {calendar.getTime()}")
