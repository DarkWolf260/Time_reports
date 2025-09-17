import os
from jnius import autoclass
import json

def get_service_and_intent():
    """Gets the running service instance and the intent that started it."""
    PythonService = autoclass('org.kivy.android.PythonService')
    service = PythonService.mService

    # This is a guess. The intent might be stored in a field.
    intent = service.getIntent() if hasattr(service, 'getIntent') else None

    return service, intent

def run_service():
    """
    This is the main entry point for the service.
    """
    service, intent = get_service_and_intent()

    if intent is None:
        # Cannot proceed without an intent
        if service:
            service.stopSelf()
        return

    arg_json = intent.getStringExtra("arg")
    if arg_json:
        try:
            args = json.loads(arg_json)
        except json.JSONDecodeError:
            args = {}
    else:
        args = {}

    title = args.get("title", "Alarma")
    message = args.get("message", "Es hora.")
    notification_id = args.get("notification_id", 0)

    # Android API classes
    Context = autoclass('android.content.Context')
    NotificationManager = autoclass('android.app.NotificationManager')
    NotificationChannel = autoclass('android.app.NotificationChannel')
    NotificationBuilder = autoclass('android.app.Notification$Builder')

    # Get the notification service
    notification_service = service.getSystemService(Context.NOTIFICATION_SERVICE)

    # Create a notification channel
    channel_id = "alarm_channel"
    channel_name = "Alarm Notifications"
    importance = NotificationManager.IMPORTANCE_DEFAULT
    channel = NotificationChannel(channel_id, channel_name, importance)
    notification_service.createNotificationChannel(channel)

    # Build the notification
    builder = NotificationBuilder(service, channel_id)
    builder.setContentTitle(autoclass('java.lang.String')(title))
    builder.setContentText(autoclass('java.lang.String')(message))
    builder.setSmallIcon(service.getApplicationInfo().icon)
    builder.setAutoCancel(True)

    # Add an intent to open the app when the notification is clicked
    app_context = service.getApplication().getApplicationContext()
    package_name = app_context.getPackageName()

    main_activity_class_name = f"{package_name}.MainActivity"
    try:
        main_activity_class = autoclass(main_activity_class_name)
        main_intent = autoclass('android.content.Intent')(app_context, main_activity_class)
        pending_main_intent = autoclass('android.app.PendingIntent').getActivity(app_context, 0, main_intent, 0)
        builder.setContentIntent(pending_main_intent)
    except Exception:
        pass

    # Display the notification
    notification = builder.build()
    notification_service.notify(notification_id, notification)

    # The service should stop itself after firing the notification
    service.stopSelf()

if __name__ == "__main__":
    run_service()
