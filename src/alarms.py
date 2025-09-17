# src/alarms.py
"""
Este módulo contiene la funcionalidad de reloj, alarmas y notificaciones.
"""

import flet as ft
from styles import TextStyles, ContainerStyles
import time
from threading import Thread, Lock
import datetime
import json

# Conditional import for Android-specific modules
try:
    import alarm_manager
    IS_ANDROID = True
except ImportError:
    IS_ANDROID = False

class AlarmsTab(ft.Column):
    """
    A Column control that contains the clock, alarm settings, and notifications.
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
            ft.Radio(value="sound", label="Sonido (en app)"),
            ft.Radio(value="notification", label="Notificación (fondo)")
        ]), value="sound")

        self.add_alarm_button = ft.ElevatedButton(text="Añadir Alarma", on_click=self.add_alarm_clicked)
        self.alarms_list_view = ft.ListView(spacing=10, padding=20, auto_scroll=True)
        self.audio_player = ft.Audio(src="assets/alarm.mp3", autoplay=False)

        # --- UI Layout ---
        clock_container = ft.Container(
            content=self.clock_text,
            **ContainerStyles.card(self.app_state.is_dark_theme),
            width=300, alignment=ft.alignment.center
        )

        time_selection_row = ft.Row([
            ft.Text("Hora de la alarma:", size=16),
            self.selected_time_text,
            self.pick_time_button
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)

        alarm_settings_container = ft.Container(
            content=ft.Column([
                ft.Text("Configurar Alarma", style=TextStyles.subtitle(self.app_state.is_dark_theme)),
                time_selection_row,
                self.alarm_type,
                self.add_alarm_button
            ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            **ContainerStyles.card(self.app_state.is_dark_theme),
            width=300, alignment=ft.alignment.center
        )

        alarms_list_container = ft.Container(
            content=ft.Column([
                ft.Text("Alarmas Activas", style=TextStyles.subtitle(self.app_state.is_dark_theme)),
                self.alarms_list_view
            ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            **ContainerStyles.card(self.app_state.is_dark_theme),
            width=300, expand=True
        )

        self.controls.extend([
            clock_container,
            alarm_settings_container,
            alarms_list_container
        ])

    def did_mount(self):
        self.page.overlay.extend([self.time_picker, self.audio_player])
        self.load_saved_alarms()

        if IS_ANDROID:
            alarm_manager.request_notification_permission()

        self.running = True
        self.page.run_thread(self.update_clock)
        self.page.run_thread(self.alarm_checker)

    def will_unmount(self):
        self.running = False

    def load_saved_alarms(self):
        if self.page.client_storage.contains_key("alarms"):
            try:
                self.alarms = json.loads(self.page.client_storage.get("alarms"))
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

            alarms_to_remove = []
            with self._active_alarms_lock:
                for alarm in self.alarms:
                    if alarm.get("type") == "sound" and alarm.get("time") == current_time_str and alarm.get("active", False):
                        self.trigger_sound_alarm(alarm)
                        # Sound alarms are one-shot, mark as inactive
                        alarm["active"] = False
                        alarms_to_remove.append(alarm)

            if alarms_to_remove:
                self.update_alarms_list()

            seconds_until_next_minute = 60 - now.second
            time.sleep(seconds_until_next_minute)

    def trigger_sound_alarm(self, alarm):
        self.audio_player.play()
        self.page.snack_bar = ft.SnackBar(ft.Text(f"Alarma de sonido a las {alarm['time']}!"), open=True)
        if self.page:
            self.audio_player.update()
            self.page.update()

    def add_alarm_clicked(self, e):
        if not self.selected_alarm_time:
            self.page.snack_bar = ft.SnackBar(ft.Text("Por favor, seleccione una hora."), open=True)
            self.page.update()
            return

        alarm_type = self.alarm_type.value

        if alarm_type == "notification" and not IS_ANDROID:
            self.page.snack_bar = ft.SnackBar(ft.Text("Las notificaciones solo están soportadas en Android."), open=True)
            self.page.update()
            return

        now = datetime.datetime.now()
        hour, minute = map(int, self.selected_alarm_time.split(':'))
        alarm_dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if alarm_dt < now:
            alarm_dt += datetime.timedelta(days=1)

        alarm_id = int(alarm_dt.timestamp())

        new_alarm = {
            "id": alarm_id,
            "time": self.selected_alarm_time,
            "type": alarm_type,
            "active": True
        }

        if alarm_type == "notification":
            alarm_manager.schedule_alarm(
                alarm_id=alarm_id,
                timestamp=alarm_dt.timestamp(),
                title='Alarma de Reporte',
                message=f"Es hora de enviar el reporte de las {self.selected_alarm_time}."
            )
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Notificación programada para las {self.selected_alarm_time}."), open=True)
        else: # sound
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Alarma de sonido programada para las {self.selected_alarm_time}."), open=True)

        with self._active_alarms_lock:
            self.alarms.append(new_alarm)

        self._save_alarms()
        self.update_alarms_list()
        self.page.update()

    def remove_alarm(self, alarm_to_remove):
        if alarm_to_remove.get("type") == "notification" and IS_ANDROID:
            alarm_manager.cancel_alarm(alarm_to_remove['id'])

        with self._active_alarms_lock:
            self.alarms = [a for a in self.alarms if a['id'] != alarm_to_remove['id']]

        self._save_alarms()
        self.update_alarms_list()
        self.page.snack_bar = ft.SnackBar(ft.Text(f"Alarma de las {alarm_to_remove['time']} eliminada."), open=True)
        self.page.update()

    def update_alarms_list(self):
        self.alarms_list_view.controls.clear()
        with self._active_alarms_lock:
            for alarm in self.alarms:
                alarm_type_text = "Sonido" if alarm.get("type") == "sound" else "Notificación"
                self.alarms_list_view.controls.append(
                    ft.Row([
                        ft.Icon(ft.Icons.ALARM),
                        ft.Text(f"{alarm['time']} ({alarm_type_text})"),
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
                    subtitle = control.content.controls[0]
                    if isinstance(subtitle, ft.Text):
                        subtitle.style = TextStyles.subtitle(self.app_state.is_dark_theme)
        self.update()
