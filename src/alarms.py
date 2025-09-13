# src/alarms.py
"""
Este módulo contiene la funcionalidad de reloj, alarmas y notificaciones.
"""

import flet as ft
from styles import TextStyles, ContainerStyles
import time
from threading import Thread, Lock
import datetime
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
        self.alarms = []  # Lista para almacenar las alarmas activas
        self._active_alarms_lock = Lock()

        # Componentes de la UI
        self.clock_text = ft.Text("", style=TextStyles.headline(self.app_state.is_dark_theme), text_align=ft.TextAlign.CENTER)
        self.alarm_time_input = ft.TextField(label="Hora de alarma (HH:MM)", width=200)
        self.alarm_type = ft.RadioGroup(content=ft.Row([
            ft.Radio(value="sound", label="Sonido"),
            ft.Radio(value="notification", label="Notificación")
        ]), value="sound")
        self.add_alarm_button = ft.ElevatedButton(text="Añadir Alarma", on_click=self.add_alarm_clicked)
        self.alarms_list_view = ft.ListView(spacing=10, padding=20, auto_scroll=True)

        self.audio_player = ft.Audio(src="/assets/alarm.mp3", autoplay=False)

        # Construir la UI directamente en init
        clock_container = ft.Container(
            content=self.clock_text,
            **ContainerStyles.card(self.app_state.is_dark_theme),
            padding=20, width=300, alignment=ft.alignment.center
        )
        alarm_settings_container = ft.Container(
            content=ft.Column([
                ft.Text("Configurar Alarma", style=TextStyles.subtitle(self.app_state.is_dark_theme)),
                self.alarm_time_input, self.alarm_type, self.add_alarm_button
            ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            **ContainerStyles.card(self.app_state.is_dark_theme),
            padding=20, width=300, alignment=ft.alignment.center
        )
        alarms_list_container = ft.Container(
            content=ft.Column([
                ft.Text("Alarmas Activas", style=TextStyles.subtitle(self.app_state.is_dark_theme)),
                self.alarms_list_view
            ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            **ContainerStyles.card(self.app_state.is_dark_theme),
            padding=20, width=300, expand=True
        )

        self.controls.extend([
            clock_container,
            alarm_settings_container,
            alarms_list_container
        ])

    def did_mount(self):
        self.page.overlay.append(self.audio_player)

        self.running = True
        self.page.run_thread(self.update_clock)
        self.page.run_thread(self.alarm_checker)

    def will_unmount(self):
        self.running = False

    def update_clock(self):
        while self.running:
            utc_now = datetime.datetime.now(datetime.timezone.utc)
            hlv_time = utc_now - datetime.timedelta(hours=4)
            self.clock_text.value = f"{hlv_time.strftime('%H:%M:%S')} HLV"
            if self.page:
                self.update()
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

            if alarms_to_remove:
                self.update_alarms_list()

            time.sleep(20)

    def trigger_alarm(self, alarm):
        if alarm["type"] == "sound":
            self.audio_player.play()
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Alarma de sonido a las {alarm['time']}!"), open=True)
        elif alarm["type"] == "notification":
            try:
                plyer_notification.notify(
                    title='Alarma',
                    message=f'Es hora de tu alarma programada a las {alarm["time"]}.',
                    app_name='Weather Report App'
                )
            except Exception as e:
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al enviar notificación: {e}"), open=True)
        if self.page:
            self.page.update()

    def add_alarm_clicked(self, e):
        time_str = self.alarm_time_input.value
        alarm_type = self.alarm_type.value

        try:
            datetime.datetime.strptime(time_str, '%H:%M')
        except ValueError:
            self.page.snack_bar = ft.SnackBar(ft.Text("Formato de hora inválido. Use HH:MM."), open=True)
            self.page.update()
            return

        with self._active_alarms_lock:
            new_alarm = {"time": time_str, "type": alarm_type, "active": True}
            self.alarms.append(new_alarm)

        self.update_alarms_list()
        self.alarm_time_input.value = ""
        self.page.update()

    def remove_alarm(self, alarm):
        with self._active_alarms_lock:
            self.alarms.remove(alarm)
        self.update_alarms_list()
        self.page.update()

    def update_alarms_list(self):
        self.alarms_list_view.controls.clear()
        with self._active_alarms_lock:
            for alarm in self.alarms:
                self.alarms_list_view.controls.append(
                    ft.Row([
                        ft.Icon(ft.icons.ALARM),
                        ft.Text(f"{alarm['time']} ({'Sonido' if alarm['type'] == 'sound' else 'Notificación'})"),
                        ft.IconButton(
                            icon=ft.icons.DELETE,
                            on_click=lambda e, a=alarm: self.remove_alarm(a),
                            tooltip="Eliminar alarma"
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                )
        if self.page:
            self.update()

    def update_theme(self):
        self.clock_text.style = TextStyles.headline(self.app_state.is_dark_theme)
        for control in self.controls:
            if isinstance(control, ft.Container):
                card_style = ContainerStyles.card(self.app_state.is_dark_theme)
                for key, value in card_style.items():
                    setattr(control, key, value)

                if len(control.content.controls) > 1 and hasattr(control.content.controls[0], 'style'):
                     control.content.controls[0].style = TextStyles.subtitle(self.app_state.is_dark_theme)

        self.update()
