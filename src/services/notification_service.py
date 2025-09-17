# src/services/notification_service.py
"""
Este servicio se ejecuta cuando una alarma se dispara.
Muestra una notificación o reproduce un sonido según el tipo de alarma.
"""
import os
import json
from plyer import notification

# Comprobación para evitar errores en entornos no Android
try:
    from jnius import autoclass, cast
    IS_ANDROID = True
except ImportError:
    IS_ANDROID = False

def get_intent_extras():
    """
    Recupera los extras del Intent que inició el servicio.
    En python-for-android, los extras se pasan como variables de entorno.
    """
    argument = os.environ.get('PYTHON_SERVICE_ARGUMENT', '{}')
    try:
        # El argumento suele ser un JSON string, lo parseamos.
        # En nuestro caso, no lo estamos pasando como JSON, sino como extras directos.
        # La forma de recuperarlos es a través de la actividad actual.
        if IS_ANDROID:
            PythonService = autoclass('org.kivy.android.PythonService')
            service = PythonService.mService
            intent = service.getIntent()

            return {
                "alarm_id": intent.getStringExtra("alarm_id"),
                "alarm_time": intent.getStringExtra("alarm_time"),
                "alarm_type": intent.getStringExtra("alarm_type")
            }
    except Exception as e:
        print(f"NotificationService: Error recuperando extras del intent: {e}")

    return {}

def trigger_notification(alarm_time: str):
    """Muestra una notificación del sistema."""
    try:
        notification.notify(
            title='Alarma de Reporte',
            message=f"Es hora de enviar el reporte de las {alarm_time}.",
            app_name='Reporte del Tiempo',
            app_icon='assets/icon.png' # La ruta debe ser accesible desde el APK
        )
        print(f"NotificationService: Notificación mostrada para la alarma de las {alarm_time}.")
    except Exception as e:
        print(f"NotificationService: Error al mostrar la notificación: {e}")

def trigger_sound():
    """Reproduce el sonido de la alarma."""
    if not IS_ANDROID:
        print("NotificationService: No se puede reproducir sonido (no es Android).")
        return

    try:
        MediaPlayer = autoclass('android.media.MediaPlayer')
        Uri = autoclass('android.net.Uri')
        File = autoclass('java.io.File')

        # La ruta al archivo de audio dentro del APK
        # Necesitamos obtener la ruta absoluta
        context = autoclass('org.kivy.android.PythonActivity').mActivity
        app_path = context.getFilesDir().getAbsolutePath()
        sound_path = os.path.join(app_path, '..', 'app', 'assets', 'alarm.mp3') # Ajustar según estructura del APK

        sound_file = File(sound_path)
        if not sound_file.exists():
             # Fallback a la notificación por defecto si no se encuentra el mp3
            sound_uri = autoclass('android.provider.Settings$System').DEFAULT_ALARM_ALERT_URI
        else:
            sound_uri = Uri.fromFile(sound_file)

        media_player = MediaPlayer()
        media_player.setDataSource(context, sound_uri)
        media_player.prepare()
        media_player.start()
        print("NotificationService: Sonido de alarma reproducido.")

        # Liberar recursos después de que termine de sonar
        # Esto es más complejo, requeriría un listener. Para una alarma corta, omitimos por simplicidad.

    except Exception as e:
        print(f"NotificationService: Error al reproducir sonido: {e}")

if __name__ == '__main__':
    print("NotificationService: Servicio iniciado.")

    extras = get_intent_extras()

    alarm_id = extras.get("alarm_id")
    alarm_time = extras.get("alarm_time", "HH:MM")
    alarm_type = extras.get("alarm_type", "notification")

    print(f"NotificationService: Procesando alarma ID {alarm_id} a las {alarm_time} de tipo {alarm_type}.")

    if alarm_type == 'notification':
        trigger_notification(alarm_time)
    elif alarm_type == 'sound':
        trigger_sound()
    else:
        print(f"NotificationService: Tipo de alarma desconocido '{alarm_type}'.")

    # Desactivar la alarma para que no se reprograme en el próximo reinicio
    try:
        from models import AlarmManager
        alarm_manager = AlarmManager()
        alarm = alarm_manager.buscar_por_id(alarm_id)
        if alarm:
            alarm.active = False
            alarm_manager.guardar_alarmas()
            print(f"NotificationService: Alarma {alarm_id} desactivada.")
    except Exception as e:
        print(f"NotificationService: Error al desactivar la alarma: {e}")

    print("NotificationService: Servicio finalizado.")
