# src/alarms.py
"""
Módulo refactorizado para la pestaña de Alarmas.
Utiliza la biblioteca flet_notifications para una implementación más simple.
"""
import flet as ft
import datetime
from models import AppState
from styles import TextStyles, ContainerStyles, ButtonStyles
from ui_components import AlarmCard
from flet_notifications import LocalNotifications

class AlarmsTab(ft.Column):
    """
    Pestaña de UI para la gestión de alarmas.
    """
    def __init__(self, app_state: AppState):
        super().__init__(
            expand=True,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            scroll=ft.ScrollMode.ADAPTIVE
        )
        self.app_state = app_state
        self.selected_alarm_time = None

        # Inicializar el control de notificaciones
        self.notifications = LocalNotifications()

        # --- Componentes de UI ---
        self._create_components()
        self._build_layout()

    def _create_components(self):
        """Crea los componentes de la interfaz de usuario."""
        self.clock_text = ft.Text("00:00:00", style=TextStyles.title(self.app_state.is_dark_theme), text_align=ft.TextAlign.CENTER)
        self.time_picker = ft.TimePicker(on_change=self._on_time_picker_change, confirm_text="Confirmar", cancel_text="Cancelar", help_text="Seleccione la hora para la alarma", time_picker_entry_mode=ft.TimePickerEntryMode.INPUT)
        self.selected_time_text = ft.Text("HH:MM", size=20, weight=ft.FontWeight.BOLD)
        self.pick_time_button = ft.IconButton(icon=ft.icons.EDIT_CALENDAR_OUTLINED, tooltip="Seleccionar hora", on_click=lambda _: self.page.open(self.time_picker))
        self.alarm_type_radio = ft.RadioGroup(content=ft.Row([ft.Radio(value="notification", label="Notificación"), ft.Radio(value="sound", label="Sonido")]), value="notification")
        self.add_alarm_button = ft.ElevatedButton(text="Añadir Alarma", on_click=self._add_alarm_clicked, style=ButtonStyles.primary())
        self.alarms_list_view = ft.ListView(spacing=10, padding=10, auto_scroll=True)
        self.audio_player = ft.Audio(src="assets/alarm.mp3", autoplay=False)

    def _build_layout(self):
        """Construye el diseño de la pestaña de alarmas."""
        clock_container = ft.Container(content=self.clock_text, **ContainerStyles.card(self.app_state.is_dark_theme), width=300, alignment=ft.alignment.center)
        time_selection_row = ft.Row([ft.Text("Hora:", size=16), self.selected_time_text, self.pick_time_button], alignment=ft.MainAxisAlignment.CENTER)
        settings_card = ft.Container(content=ft.Column([ft.Text("Configurar Alarma", style=TextStyles.subtitle(self.app_state.is_dark_theme)), time_selection_row, self.alarm_type_radio, self.add_alarm_button], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER), **ContainerStyles.card(self.app_state.is_dark_theme), width=350, padding=15)
        list_card = ft.Container(content=ft.Column([ft.Text("Alarmas Activas", style=TextStyles.subtitle(self.app_state.is_dark_theme)), ft.Divider(), self.alarms_list_view], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER), **ContainerStyles.card(self.app_state.is_dark_theme), width=350, padding=15, expand=True)
        self.controls = [clock_container, settings_card, list_card]

    async def did_mount(self):
        """Se llama cuando el control se añade a la página."""
        self.page.overlay.extend([self.time_picker, self.notifications, self.audio_player])

        # Solicitar permisos para notificaciones
        await self.notifications.request_permissions()

        self.running = True
        self.page.run_thread(self._update_clock)
        self._update_alarms_list()

    def will_unmount(self):
        self.running = False

    def _update_clock(self):
        import time
        while self.running and self.page:
            now = datetime.datetime.now().strftime('%H:%M:%S')
            self.clock_text.value = now
            try:
                self.update()
            except Exception:
                break
            time.sleep(1)

    def _on_time_picker_change(self, e):
        if e.data:
            time_obj = datetime.datetime.strptime(e.data, "%H:%M").time()
            self.selected_alarm_time = time_obj.strftime("%H:%M")
            self.selected_time_text.value = self.selected_alarm_time
        else:
            self.selected_alarm_time = None
            self.selected_time_text.value = "HH:MM"
        self.update()

    async def _add_alarm_clicked(self, e):
        if not self.selected_alarm_time:
            self._show_snackbar("Por favor, seleccione una hora.")
            return

        alarm_type = self.alarm_type_radio.value
        new_alarm = self.app_state.alarm_manager.agregar_alarma(self.selected_alarm_time, alarm_type)

        if new_alarm:
            hour, minute = map(int, new_alarm.time.split(':'))
            now = datetime.datetime.now()
            scheduled_date = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if scheduled_date < now:
                scheduled_date += datetime.timedelta(days=1)

            if alarm_type == "notification":
                await self.notifications.schedule_notification(
                    id=new_alarm.notification_id,
                    title="Alarma de Reporte",
                    body=f"Es hora de enviar el reporte de las {new_alarm.time}.",
                    scheduled_date=scheduled_date
                )
            # El tipo "sound" se manejará de forma diferente

            self._show_snackbar(f"Alarma para las {self.selected_alarm_time} añadida.")
            self._update_alarms_list()
        else:
            self._show_snackbar("Ya existe una alarma con esa hora y tipo.")

        self.page.update()

    async def _delete_alarm_clicked(self, alarm_id: str):
        deleted_alarm = self.app_state.alarm_manager.eliminar_alarma(alarm_id)
        if deleted_alarm:
            if deleted_alarm.alarm_type == "notification":
                # Corregido según la revisión del código
                await self.notifications.cancel_notification(deleted_alarm.notification_id)

            self._show_snackbar(f"Alarma de las {deleted_alarm.time} eliminada.")
            self._update_alarms_list()

        self.page.update()

    def _update_alarms_list(self):
        self.alarms_list_view.controls.clear()
        alarms = self.app_state.alarm_manager.obtener_alarmas()

        if not alarms:
            self.alarms_list_view.controls.append(ft.Text("No hay alarmas programadas.", text_align=ft.TextAlign.CENTER, italic=True))
        else:
            for alarm in sorted(alarms, key=lambda x: x.time):
                self.alarms_list_view.controls.append(AlarmCard(alarm=alarm, on_delete=self._delete_alarm_clicked))
        self.update()

    def _show_snackbar(self, message: str):
        self.page.snack_bar = ft.SnackBar(ft.Text(message), open=True)
        self.page.update()

    def update_theme(self):
        is_dark = self.app_state.is_dark_theme
        self.clock_text.style = TextStyles.title(is_dark)
        for control in self.controls:
            if isinstance(control, ft.Container):
                style = ContainerStyles.card(is_dark)
                for key, value in style.items():
                    setattr(control, key, value)
                if control.content and isinstance(control.content.controls[0], ft.Text):
                    control.content.controls[0].style = TextStyles.subtitle(is_dark)
        self.update()
