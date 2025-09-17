# src/alarms.py
"""
Este módulo contiene la funcionalidad de reloj, alarmas y notificaciones.
Enfoque: Estabilizar y hacer funcionar las notificaciones en primer plano con Plyer.
"""

import flet as ft
from styles import TextStyles, ContainerStyles
import time
from threading import Thread, Lock
import datetime
import json

# Conditional import for Android-specific modules
try:
    from jnius import autoclass
    from plyer import notification as plyer_notification
    IS_ANDROID = True
except ImportError:
    IS_ANDROID = False

def request_notification_permission():
    """
    Checks and requests the POST_NOTIFICATIONS permission at runtime if needed.
    This function should only be called if IS_ANDROID is True.
    """
    activity = autoclass('org.kivy.android.PythonActivity').mActivity
    if not activity:
        return

    Build = autoclass('android.os.Build')
    if Build.VERSION.SDK_INT >= 33: # Android 13 (TIRAMISU)
        ContextCompat = autoclass('androidx.core.content.ContextCompat')
        ActivityCompat = autoclass('androidx.core.app.ActivityCompat')
        PackageManager = autoclass('android.content.pm.PackageManager')

        permission = "android.permission.POST_NOTIFICATIONS"

        if ContextCompat.checkSelfPermission(activity, permission) != PackageManager.PERMISSION_GRANTED:
            ActivityCompat.requestPermissions(activity, [permission], 101)

class AlarmsTab(ft.Column):
    """
    A Column control that contains the clock, alarm settings, and notifications.
    Uses Plyer for notifications.
    """
    def __init__(self, app_state):
        super().__init__(
            expand=True,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            scroll=ft.ScrollMode.ADAPTIVE
        )

        self.app_state = app_state
        self.alarms = []
        self._active_alarms_lock = Lock()
        self.selected_alarm_time = None

        # --- UI Components ---
        self.clock_text = ft.Text("", style=TextStyles.title(self.app_state.is_dark_theme), text_align=ft.TextAlign.CENTER)
        self.time_picker = ft.TimePicker(
            on_change=self.time_picker_changed,
            confirm_text="Confirmar",
            cancel_text="Cancelar",
            help_text="Seleccione la hora para la alarma",
            time_picker_entry_mode=ft.TimePickerEntryMode.INPUT
        )
        self.selected_time_text = ft.Text("HH:MM", size=20, weight=ft.FontWeight.BOLD)
        self.pick_time_button = ft.IconButton(
            icon=ft.Icons.EDIT_CALENDAR_OUTLINED,
            tooltip="Seleccionar hora",
            on_click=lambda _: self.page.open(self.time_picker)
        )
        self.alarm_type = ft.RadioGroup(content=ft.Row([
            ft.Radio(value="sound", label="Sonido"),
            ft.Radio(value="notification", label="Notificación")
        ]), value="sound")
        self.add_alarm_button = ft.ElevatedButton(text="Añadir Alarma", on_click=self.add_alarm_clicked)
        self.alarms_list_view = ft.ListView(spacing=10, padding=20, auto_scroll=True)
        self.audio_player = ft.Audio(src="assets/alarm.mp3", autoplay=False)

        # --- UI Layout ---
        # (Same as before, so I'm keeping it)
        clock_container = ft.Container(content=self.clock_text, **ContainerStyles.card(self.app_state.is_dark_theme), width=300, alignment=ft.alignment.center)
        time_selection_row = ft.Row([ft.Text("Hora de la alarma:", size=16), self.selected_time_text, self.pick_time_button], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
        alarm_settings_container = ft.Container(content=ft.Column([ft.Text("Configurar Alarma", style=TextStyles.subtitle(self.app_state.is_dark_theme)), time_selection_row, self.alarm_type, self.add_alarm_button], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER), **ContainerStyles.card(self.app_state.is_dark_theme), width=300, alignment=ft.alignment.center)
        alarms_list_container = ft.Container(content=ft.Column([ft.Text("Alarmas Activas", style=TextStyles.subtitle(self.app_state.is_dark_theme)), self.alarms_list_view], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER), **ContainerStyles.card(self.app_state.is_dark_theme), width=300, expand=True)
        self.controls.extend([clock_container, alarm_settings_container, alarms_list_container])

    def did_mount(self):
        self.page.overlay.extend([self.time_picker, self.audio_player])
        self.load_saved_alarms()

        if IS_ANDROID:
            request_notification_permission()

        self.running = True
        self.page.run_thread(self.update_clock)
        self.page.run_thread(self.alarm_checker)

    def will_unmount(self):
        self.running = False

    def load_saved_alarms(self):
        if self.page.client_storage.contains_key("alarms"):
            try:
                self.alarms = json.loads(self.page.client_storage.get("alarms"))
                # Ensure old alarms have an 'active' key
                for alarm in self.alarms:
                    alarm.setdefault('active', True)
                self.update_alarms_list()
            except (json.JSONDecodeError, TypeError):
                self.alarms = []

    def _save_alarms(self):
        self.page.client_storage.set("alarms", json.dumps(self.alarms))

    def time_picker_changed(self, e):
        time_obj = datetime.datetime.strptime(e.data, "%H:%M").time()
        self.selected_alarm_time = time_obj.strftime("%H:%M")
        self.selected_time_text.value = self.selected_alarm_time
        self.update()

    def update_clock(self):
        while self.running:
            now = datetime.datetime.now()
            self.clock_text.value = f"{now.strftime('%H:%M:%S')}"
            if self.page: self.update()
            time.sleep(1)

    def alarm_checker(self):
        while self.running:
            now = datetime.datetime.now()
            current_time_str = now.strftime('%H:%M')

            alarms_to_trigger = []
            with self._active_alarms_lock:
                for alarm in self.alarms:
                    if alarm.get("time") == current_time_str and alarm.get("active", False):
                        alarms_to_trigger.append(alarm)
                        alarm["active"] = False

            for alarm in alarms_to_trigger:
                self.trigger_alarm(alarm)

            if alarms_to_trigger:
                self.update_alarms_list()

            seconds_until_next_minute = 60 - now.second
            time.sleep(seconds_until_next_minute)

    def trigger_alarm(self, alarm):
        alarm_type = alarm.get("type", "sound")
        if alarm_type == "sound":
            self.audio_player.play()
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Alarma de sonido a las {alarm['time']}!"), open=True)
        elif alarm_type == "notification" and IS_ANDROID:
            try:
                plyer_notification.notify(
                    title='Alarma de Reporte',
                    message=f"Es hora de enviar el reporte de las {alarm['time']}.",
                    app_name='Reporte del Tiempo',
                    app_icon='assets/icon.png' # May need adjustment for Android
                )
            except Exception as e:
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Error de notificación: {e}"), open=True)

        if self.page:
            if hasattr(self, 'audio_player'): self.audio_player.update()
            self.page.update()

    def add_alarm_clicked(self, e):
        if not self.selected_alarm_time:
            self.page.snack_bar = ft.SnackBar(ft.Text("Por favor, seleccione una hora."), open=True)
            self.page.update()
            return

        new_alarm = {
            "time": self.selected_alarm_time,
            "type": self.alarm_type.value,
            "active": True
        }

        with self._active_alarms_lock:
            self.alarms.append(new_alarm)

        self._save_alarms()
        self.update_alarms_list()
        self.page.snack_bar = ft.SnackBar(ft.Text(f"Alarma programada para las {self.selected_alarm_time}."), open=True)
        self.page.update()

    def remove_alarm(self, alarm_to_remove):
        with self._active_alarms_lock:
            self.alarms = [a for a in self.alarms if a != alarm_to_remove]
        self._save_alarms()
        self.update_alarms_list()
        self.page.snack_bar = ft.SnackBar(ft.Text(f"Alarma de las {alarm_to_remove['time']} eliminada."), open=True)
        self.page.update()

    def update_alarms_list(self):
        self.alarms_list_view.controls.clear()
        with self._active_alarms_lock:
            for alarm in self.alarms:
                alarm_type_text = "Sonido" if alarm.get("type") == "sound" else "Notificación"
                status_text = " (Activa)" if alarm.get("active", False) else " (Inactiva)"
                self.alarms_list_view.controls.append(
                    ft.Row([
                        ft.Icon(ft.Icons.ALARM),
                        ft.Text(f"{alarm['time']} ({alarm_type_text}){status_text}"),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            on_click=lambda e, a=alarm: self.remove_alarm(a),
                            tooltip="Eliminar alarma"
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                )
        if self.page: self.update()

    def update_theme(self):
        self.clock_text.style = TextStyles.title(self.app_state.is_dark_theme)
        for control in self.controls:
            if isinstance(control, ft.Container):
                card_style = ContainerStyles.card(self.app_state.is_dark_theme)
                for key, value in card_style.items():
                    setattr(control, key, value)
                if hasattr(control.content, 'controls') and len(control.content.controls) > 0:
                    if isinstance(control.content.controls[0], ft.Text):
                        control.content.controls[0].style = TextStyles.subtitle(self.app_state.is_dark_theme)
        self.update()
