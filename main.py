"""
GrowLog — Janela Principal com Sidebar + Google Drive Sync
"""
import sys
import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QStackedWidget, QStatusBar,
    QMessageBox
)
from PyQt6.QtCore import Qt, QTimer

from database.models import init_db, Plant, Log, Task
from ui.theme import DARK_THEME
from views.dashboard import DashboardView
from views.plants import PlantsView
from views.history import HistoryView
from views.calendar_view import CalendarView
from views.settings_view import SettingsView
from ui.widgets import LogDialog, PlantDialog
from sync.sync_manager import SyncManager


class NavButton(QPushButton):
    def __init__(self, icon: str, label: str, parent=None):
        super().__init__(f'  {icon}  {label}', parent)
        self.setObjectName('nav_btn')
        self.setCheckable(False)
        self.setFixedHeight(44)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_active(self, active: bool):
        self.setProperty('active', 'true' if active else 'false')
        self.style().unpolish(self)
        self.style().polish(self)


class Sidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('sidebar')
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 16)
        layout.setSpacing(0)

        lbl_title = QLabel('GrowLog')
        lbl_title.setObjectName('app_title')
        lbl_sub = QLabel('✦ CULTIVO')
        lbl_sub.setObjectName('app_subtitle')
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_sub)

        sep = QWidget()
        sep.setObjectName('separator')
        sep.setFixedHeight(1)
        layout.addWidget(sep)
        layout.addSpacing(8)

        self.btn_dashboard = NavButton('📊', 'Dashboard')
        self.btn_plants    = NavButton('🌿', 'Plantas')
        self.btn_logs      = NavButton('💧', 'Registros')
        self.btn_calendar  = NavButton('📅', 'Calendário')
        self.btn_settings  = NavButton('⚙', 'Configurações')

        self.nav_buttons = [
            self.btn_dashboard, self.btn_plants,
            self.btn_logs, self.btn_calendar, self.btn_settings,
        ]

        for btn in self.nav_buttons:
            layout.addWidget(btn)

        layout.addStretch()

        self.lbl_sync = QLabel('Drive: desconectado')
        self.lbl_sync.setStyleSheet(
            'color: #4a6b4e; font-size: 10px; padding: 0 16px 8px 16px;'
        )
        self.lbl_sync.setWordWrap(True)
        layout.addWidget(self.lbl_sync)

        lbl_ver = QLabel('v1.1.0')
        lbl_ver.setObjectName('app_subtitle')
        lbl_ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_ver)

    def set_active(self, index: int):
        for i, btn in enumerate(self.nav_buttons):
            btn.set_active(i == index)

    def set_sync_status(self, msg: str):
        self.lbl_sync.setText(msg)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('GrowLog 🌿')
        self.resize(1100, 700)
        self.setMinimumSize(900, 600)

        self.sync_manager = SyncManager(base_dir='.')

        self._build_ui()
        self._connect_signals()
        self._setup_overdue_timer()
        self.navigate(0)
        self.refresh_all()
        self._silent_auth()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main = QHBoxLayout(central)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        self.sidebar = Sidebar()
        main.addWidget(self.sidebar)

        self.stack = QStackedWidget()
        self.stack.setObjectName('content_area')

        self.view_dashboard = DashboardView()
        self.view_plants    = PlantsView()
        self.view_history   = HistoryView()
        self.view_calendar  = CalendarView()
        self.view_settings  = SettingsView()

        for view in (self.view_dashboard, self.view_plants,
                     self.view_history, self.view_calendar, self.view_settings):
            self.stack.addWidget(view)

        main.addWidget(self.stack, 1)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self._update_status()

    def _connect_signals(self):
        self.sidebar.btn_dashboard.clicked.connect(lambda: self.navigate(0))
        self.sidebar.btn_plants.clicked.connect(lambda: self.navigate(1))
        self.sidebar.btn_logs.clicked.connect(lambda: self.navigate(2))
        self.sidebar.btn_calendar.clicked.connect(lambda: self.navigate(3))
        self.sidebar.btn_settings.clicked.connect(lambda: self.navigate(4))

        self.view_dashboard.request_add_plant.connect(self._add_plant_from_dash)
        self.view_dashboard.request_add_log.connect(self._add_log_from_dash)

        self.view_plants.plants_changed.connect(self.refresh_all)
        self.view_history.logs_changed.connect(self.refresh_all)
        self.view_calendar.tasks_changed.connect(self.refresh_all)

        self.view_settings.request_authenticate.connect(self._authenticate)
        self.view_settings.request_upload.connect(self._force_upload)
        self.view_settings.request_download.connect(self._force_download)
        self.view_settings.request_sync_now.connect(self._sync_now)
        self.view_settings.interval_changed.connect(self._on_interval_changed)

        self.sync_manager.sync_status.connect(self._on_sync_status)
        self.sync_manager.sync_finished.connect(self._on_sync_finished)

        self.view_settings.set_interval_options(
            self.sync_manager.get_interval_options(),
            self.sync_manager.get_interval_label()
        )

    def navigate(self, index: int):
        self.stack.setCurrentIndex(index)
        self.sidebar.set_active(index)
        views = [self.view_dashboard, self.view_plants,
                 self.view_history, self.view_calendar, self.view_settings]
        views[index].refresh()

    def refresh_all(self):
        self.view_dashboard.refresh()
        self.view_plants.refresh()
        self.view_history.refresh()
        self.view_calendar.refresh()
        self._update_status()

    def _update_status(self):
        plant_count = Plant.select().count()
        pending     = Task.select().where(Task.completed == False).count()
        overdue     = Task.select().where(
            (Task.completed == False) &
            (Task.due_date < datetime.date.today())
        ).count()
        msg = f'🌿 Plantas: {plant_count}  |  🔔 Pendentes: {pending}'
        if overdue:
            msg += f'  |  ⚠ {overdue} atrasadas'
        self.status.showMessage(msg)

    # ─── Sync ─────────────────────────────────────────────────────────────────

    def _silent_auth(self):
        from pathlib import Path
        if Path('token.json').exists():
            ok = self.sync_manager.authenticate()
            self.view_settings.set_authenticated(ok)
            if ok:
                self.sync_manager.start()
                self.view_settings.set_timer_running(True)

    def _authenticate(self):
        self.status.showMessage('🔑 Abrindo autenticação Google...')
        ok = self.sync_manager.authenticate()
        self.view_settings.set_authenticated(ok)
        if ok:
            self.sync_manager.start()
            self.view_settings.set_timer_running(True)
            QMessageBox.information(
                self, 'Conectado!',
                '✅ Google Drive conectado!\n'
                f'Sync automático a cada {self.sync_manager.get_interval_label()}.'
            )
        else:
            QMessageBox.warning(
                self, 'Erro',
                '❌ Não foi possível conectar.\n'
                'Verifique se o credentials.json está na pasta do app.'
            )

    def _force_upload(self):
        result = self.sync_manager.force_upload()
        if result['success']:
            self.view_settings.set_last_sync(result['message'])

    def _force_download(self):
        result = self.sync_manager.force_download()
        if result['success']:
            self.view_settings.set_last_sync(result['message'])
            init_db('growlog.db')
            self.refresh_all()

    def _sync_now(self):
        self.sync_manager.run_sync()

    def _on_interval_changed(self, label: str):
        if label == '__stop__':
            self.sync_manager.stop()
            self.view_settings.set_timer_running(False)
        else:
            self.sync_manager.set_interval(label)
            if not self.sync_manager.is_running():
                self.sync_manager.start()
            self.view_settings.set_timer_running(True)

    def _on_sync_status(self, msg: str):
        self.sidebar.set_sync_status(msg)
        self.status.showMessage(msg, 4000)

    def _on_sync_finished(self, success: bool, message: str):
        self.view_settings.set_last_sync(message)
        if not success:
            self.status.showMessage(f'⚠ {message}', 5000)

    def _add_plant_from_dash(self):
        dlg = PlantDialog(self)
        if dlg.exec():
            Plant.create(**dlg.get_data())
            self.refresh_all()

    def _add_log_from_dash(self):
        plants = list(Plant.select())
        if not plants:
            QMessageBox.warning(self, 'Aviso', 'Cadastre uma planta primeiro!')
            return
        dlg = LogDialog(self, plants=plants)
        if dlg.exec():
            data      = dlg.get_data()
            plant_id  = data.pop('plant_id')
            new_stage = data.pop('new_stage', None)
            Log.create(plant_id=plant_id, **data)
            plant = Plant.get_by_id(plant_id)
            if data['log_type'] == 'rega':
                plant.last_watered = data['date']
                if data.get('ph'): plant.current_ph = data['ph']
                if data.get('ec'): plant.current_ec = data['ec']
                plant.save()
            elif data['log_type'] == 'fase' and new_stage:
                plant.stage = new_stage
                plant.save()
            self.refresh_all()

    def _setup_overdue_timer(self):
        self.overdue_timer = QTimer(self)
        self.overdue_timer.timeout.connect(self._check_overdue)
        self.overdue_timer.start(60 * 60 * 1000)

    def _check_overdue(self):
        count = Task.select().where(
            (Task.completed == False) &
            (Task.due_date < datetime.date.today())
        ).count()
        if count:
            self.status.showMessage(f'⚠️ {count} tarefa(s) atrasada(s)!', 5000)

    def closeEvent(self, event):
        """Faz upload automático ao fechar o app."""
        if self.sync_manager.is_authenticated():
            self.status.showMessage('⬆ Salvando no Drive...')
            self.sync_manager.force_upload()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_THEME)
    app.setStyle('Fusion')

    init_db('growlog.db')

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()