[app]
title = Reporte del Tiempo
package.name = reportes
package.domain = com.rubenroy
source.dir = src
source.include_exts = py,png,jpg,kv,atlas,mp3,json
version = 0.1
requirements = flet,plyer,jnius
orientation = portrait
icon.filename = %(source.dir)s/assets/icon.png
presplash.filename = %(source.dir)s/assets/splash_android.png
android.permissions = POST_NOTIFICATIONS,RECEIVE_BOOT_COMPLETED,WAKE_LOCK
android.services = NotificationService:services/notification_service.py,BootService:services/boot_service.py
android.meta_data = android.app.Notification.color=0xFF000000

[buildozer]
log_level = 2
warn_on_root = 1
