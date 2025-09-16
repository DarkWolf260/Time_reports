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
from plyer import notification as plyer_notification

class AlarmsTab(ft.Column):
    """
    Un control de Columna que contiene el reloj, la configuración de alarmas y notificaciones.
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

        # --- Componentes de la UI ---
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


        # --- Construcción de la UI ---
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

        # Cargar alarmas guardadas
        if self.page.client_storage.contains_key("alarms"):
            try:
                saved_alarms = json.loads(self.page.client_storage.get("alarms"))
                if isinstance(saved_alarms, list):
                    self.alarms = saved_alarms
                    self.update_alarms_list()
            except (json.JSONDecodeError, TypeError):
                self.alarms = [] # Iniciar con lista vacía si hay error

        self.running = True
        self.page.run_thread(self.update_clock)
        self.page.run_thread(self.alarm_checker)

    def will_unmount(self):
        self.running = False

    def _save_alarms(self):
        """Guarda la lista de alarmas en el almacenamiento del cliente."""
        self.page.client_storage.set("alarms", json.dumps(self.alarms))

    def time_picker_changed(self, e):
        time_obj = datetime.datetime.strptime(e.data, "%H:%M").time()
        self.selected_alarm_time = time_obj.strftime("%H:%M")
        self.selected_time_text.value = self.selected_alarm_time
        self.update()

    def update_clock(self):
        while self.running:
            utc_now = datetime.datetime.now(datetime.timezone.utc)
            hlv_time = utc_now - datetime.timedelta(hours=4)
            self.clock_text.value = f"{hlv_time.strftime('%H:%M:%S')} HLV"
            if self.page: self.update()
            time.sleep(1)

    def alarm_checker(self):
        while self.running:
            now = datetime.datetime.now()
            current_time_str = now.strftime('%H:%M')

            with self._active_alarms_lock:
                alarms_to_remove = []
                for alarm in self.alarms:
                    if alarm["time"] == current_time_str and alarm["active"]:
                        self.trigger_alarm(alarm)
                        alarm["active"] = False
                        alarms_to_remove.append(alarm)

            if alarms_to_remove: self.update_alarms_list()

            seconds_until_next_minute = 60 - datetime.datetime.now().second
            time.sleep(seconds_until_next_minute)

    def trigger_alarm(self, alarm):
        if alarm["type"] == "sound":
            self.audio_player.src = "assets/alarm.mp3"
            self.audio_player.play()
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Alarma de sonido a las {alarm['time']}!"), open=True)
        elif alarm["type"] == "notification":
            self.audio_player.src = "assets/notification.mp3"
            self.audio_player.play()
            try:
                plyer_notification.notify(
                    title='Alarma',
                    message=f"Recuerda enviar el reporte de las {alarm['time']}",
                    app_name='Reporte del tiempo',
                    app_icon='assets/icon.png'
                )
            except Exception as e:
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al enviar notificación: {e}"), open=True)
        if self.page:
            self.audio_player.update()
            self.page.update()

    def add_alarm_clicked(self, e):
        if not self.selected_alarm_time:
            self.page.snack_bar = ft.SnackBar(ft.Text("Por favor, seleccione una hora para la alarma."), open=True)
            self.page.update()
            return

        alarm_type = self.alarm_type.value
        with self._active_alarms_lock:
            new_alarm = {"time": self.selected_alarm_time, "type": alarm_type, "active": True}
            self.alarms.append(new_alarm)

        self._save_alarms()
        self.update_alarms_list()
        self.page.update()

    def remove_alarm(self, alarm):
        with self._active_alarms_lock:
            self.alarms.remove(alarm)
        self._save_alarms()
        self.update_alarms_list()

    def update_alarms_list(self):
        self.alarms_list_view.controls.clear()
        with self._active_alarms_lock:
            for alarm in self.alarms:
                self.alarms_list_view.controls.append(
                    ft.Row([
                        ft.Icon(ft.Icons.ALARM),
                        ft.Text(f"{alarm['time']} ({'Sonido' if alarm['type'] == 'sound' else 'Notificación'})"),
                        ft.IconButton(icon=ft.Icons.DELETE, on_click=lambda e, a=alarm: self.remove_alarm(a), tooltip="Eliminar alarma")
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
