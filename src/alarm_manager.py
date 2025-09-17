import os
from jnius import autoclass
import datetime
import json

def get_activity():
    """Gets the main Flet activity instance."""
    activity_host_class = os.getenv("MAIN_ACTIVITY_HOST_CLASS_NAME")
    if not activity_host_class:
        return None
    activity_host = autoclass(activity_host_class)
    return activity_host.mActivity

def schedule_alarm(alarm_id: int, timestamp: float, title: str, message: str):
    """Schedules an alarm to start the AlarmService."""
    activity = get_activity()
    if not activity:
        print("Not running on Android, cannot schedule alarm.")
        return

    Context = autoclass('android.content.Context')
    AlarmManager = autoclass('android.app.AlarmManager')
    Intent = autoclass('android.content.Intent')
    PendingIntent = autoclass('android.app.PendingIntent')

    # Create an explicit Intent to start the service
    package_name = activity.getPackageName()
    service_class_name = f"{package_name}.ServiceAlarmService" # Guessing the class name
    intent = Intent()
    intent.setClassName(package_name, service_class_name)

    # Pass alarm details to the service via a JSON string in the 'arg' extra
    args = {"title": title, "message": message, "notification_id": alarm_id}
    intent.putExtra("arg", json.dumps(args))

    pending_intent = PendingIntent.getService(
        activity, alarm_id, intent, PendingIntent.FLAG_UPDATE_CURRENT
    )

    alarm_manager = activity.getSystemService(Context.ALARM_SERVICE)
    alarm_time_ms = int(timestamp * 1000)

    # Use setExactAndAllowWhileIdle for more reliability
    if autoclass('android.os.Build$VERSION').SDK_INT >= 23:
        alarm_manager.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, alarm_time_ms, pending_intent)
    else:
        alarm_manager.setExact(AlarmManager.RTC_WAKEUP, alarm_time_ms, pending_intent)

    print(f"Alarm {alarm_id} scheduled for {datetime.datetime.fromtimestamp(timestamp)}")

def cancel_alarm(alarm_id: int):
    """Cancels a previously scheduled alarm."""
    activity = get_activity()
    if not activity:
        print("Not running on Android, cannot cancel alarm.")
        return

    Context = autoclass('android.content.Context')
    AlarmManager = autoclass('android.app.AlarmManager')
    Intent = autoclass('android.content.Intent')
    PendingIntent = autoclass('android.app.PendingIntent')

    package_name = activity.getPackageName()
    service_class_name = f"{package_name}.ServiceAlarmService"
    intent = Intent()
    intent.setClassName(package_name, service_class_name)

    pending_intent = PendingIntent.getService(
        activity, alarm_id, intent, PendingIntent.FLAG_NO_CREATE
    )

    if pending_intent:
        alarm_manager = activity.getSystemService(Context.ALARM_SERVICE)
        alarm_manager.cancel(pending_intent)
        pending_intent.cancel()
        print(f"Cancelled alarm {alarm_id}")
    else:
        print(f"No alarm found with ID {alarm_id} to cancel.")
