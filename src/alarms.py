# src/alarms.py
"""
Este módulo contiene la funcionalidad de reloj y la interfaz para programar alarmas.
La lógica de las alarmas ahora es manejada por el `alarm_manager` nativo de Android.
"""

import flet as ft
from styles import TextStyles, ContainerStyles
import datetime
import json
import time

# Asumiendo que Flet se ejecuta en Android, importamos los módulos específicos.
# En un entorno no-Android, estos imports fallarán.
try:
    import alarm_manager
    from android_alarm_receiver import on_receive
    from android.broadcast import BroadcastReceiver
    IS_ANDROID = True
except ImportError:
    IS_ANDROID = False

class AlarmsTab(ft.Column):
    """
    Un control de Columna que contiene el reloj y la configuración de alarmas.
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
        self.selected_alarm_time = None
        self.br = None # Referencia al BroadcastReceiver

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
        self.add_alarm_button = ft.ElevatedButton(text="Añadir Alarma", on_click=self.add_alarm_clicked)
        self.alarms_list_view = ft.ListView(spacing=10, padding=20, auto_scroll=True)
        self.audio_player = ft.Audio(src="assets/alarm.mp3", autoplay=False) # For sound alarms

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
                ft.Text("Esta alarma usará el sistema nativo de Android."),
                self.add_alarm_button,
            ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            **ContainerStyles.card(self.app_state.is_dark_theme),
            width=300, alignment=ft.alignment.center
        )
        alarms_list_container = ft.Container(
            content=ft.Column([
                ft.Text("Alarmas Programadas", style=TextStyles.subtitle(self.app_state.is_dark_theme)),
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
            # Registrar el BroadcastReceiver para las alarmas
            activity = alarm_manager.get_activity()
            if activity:
                package_name = activity.getPackageName()
                self.br = BroadcastReceiver(on_receive, actions=[f"{package_name}.ALARM"])
                self.br.register()

        self.running = True
        self.page.run_thread(self.update_clock)

    def will_unmount(self):
        self.running = False
        if IS_ANDROID and self.br:
            self.br.unregister()

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

    def add_alarm_clicked(self, e):
        if not self.selected_alarm_time:
            self.page.snack_bar = ft.SnackBar(ft.Text("Por favor, seleccione una hora."), open=True)
            self.page.update()
            return

        if not IS_ANDROID:
            self.page.snack_bar = ft.SnackBar(ft.Text("Las notificaciones solo están soportadas en Android."), open=True)
            self.page.update()
            return

        # Calcular el timestamp de la alarma
        now = datetime.datetime.now()
        hour, minute = map(int, self.selected_alarm_time.split(':'))
        alarm_dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if alarm_dt < now:
            alarm_dt += datetime.timedelta(days=1)

        alarm_id = int(alarm_dt.timestamp())
        timestamp = alarm_dt.timestamp()

        # Programar la alarma nativa
        alarm_manager.schedule_alarm(
            alarm_id=alarm_id,
            timestamp=timestamp,
            title='Alarma de Reporte',
            message=f"Es hora de enviar el reporte de las {self.selected_alarm_time}."
        )

        # Guardar localmente para la UI
        new_alarm = {"id": alarm_id, "time": self.selected_alarm_time}
        self.alarms.append(new_alarm)
        self._save_alarms()
        self.update_alarms_list()
        self.page.snack_bar = ft.SnackBar(ft.Text(f"Alarma programada para las {self.selected_alarm_time}."), open=True)
        self.page.update()

    def remove_alarm(self, alarm):
        if IS_ANDROID:
            alarm_manager.cancel_alarm(alarm['id'])

        self.alarms.remove(alarm)
        self._save_alarms()
        self.update_alarms_list()
        self.page.snack_bar = ft.SnackBar(ft.Text(f"Alarma de las {alarm['time']} eliminada."), open=True)
        self.page.update()

    def update_alarms_list(self):
        self.alarms_list_view.controls.clear()
        for alarm in self.alarms:
            self.alarms_list_view.controls.append(
                ft.Row([
                    ft.Icon(ft.Icons.ALARM),
                    ft.Text(f"{alarm['time']} (Notificación Nativa)"),
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
