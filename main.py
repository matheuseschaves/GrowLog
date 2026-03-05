"""
GrowLog — Janela Principal com Sidebar
"""
import sys
import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QStackedWidget, QStatusBar,
    QSizePolicy, QSpacerItem, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from database.models import init_db, Plant, Log, Task
from ui.theme import DARK_THEME
from views.dashboard import DashboardView
from views.plants import PlantsView
from views.history import HistoryView
from views.calendar_view import CalendarView
from ui.widgets import LogDialog, PlantDialog


class NavButton(QPushButton):
    def __init__(self, icon: str, label: str, parent=None):
        super().__init__(f'  {icon}  {label}', parent)
        self.setObjectName('nav_btn')
        self.setCheckable(False)
        self.setFixedHeight(44)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._active = False

    def set_active(self, active: bool):
        self._active = active
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

        # Logo
        lbl_title = QLabel('GrowLog')
        lbl_title.setObjectName('app_title')
        lbl_sub = QLabel('✦ CULTIVO')
        lbl_sub.setObjectName('app_subtitle')
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_sub)

        # Separador
        sep = QWidget()
        sep.setObjectName('separator')
        sep.setFixedHeight(1)
        sep.setContentsMargins(16, 0, 16, 0)
        layout.addWidget(sep)
        layout.addSpacing(8)

        # Nav buttons
        self.btn_dashboard = NavButton('📊', 'Dashboard')
        self.btn_plants    = NavButton('🌿', 'Plantas')
        self.btn_logs      = NavButton('💧', 'Registros')
        self.btn_calendar  = NavButton('📅', 'Calendário')

        self.nav_buttons = [
            self.btn_dashboard,
            self.btn_plants,
            self.btn_logs,
            self.btn_calendar,
        ]

        for btn in self.nav_buttons:
            layout.addWidget(btn)

        layout.addStretch()

        # Versão
        lbl_ver = QLabel('v1.0.0')
        lbl_ver.setObjectName('app_subtitle')
        lbl_ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_ver)

    def set_active(self, index: int):
        for i, btn in enumerate(self.nav_buttons):
            btn.set_active(i == index)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('GrowLog 🌿')
        self.resize(1100, 700)
        self.setMinimumSize(900, 600)
        self._build_ui()
        self._connect_signals()
        self._setup_timer()
        self.navigate(0)
        self.refresh_all()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main = QHBoxLayout(central)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar()
        main.addWidget(self.sidebar)

        # Stacked pages
        self.stack = QStackedWidget()
        self.stack.setObjectName('content_area')

        self.view_dashboard = DashboardView()
        self.view_plants    = PlantsView()
        self.view_history   = HistoryView()
        self.view_calendar  = CalendarView()

        self.stack.addWidget(self.view_dashboard)
        self.stack.addWidget(self.view_plants)
        self.stack.addWidget(self.view_history)
        self.stack.addWidget(self.view_calendar)
        main.addWidget(self.stack, 1)

        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self._update_status()

    def _connect_signals(self):
        # Navegação
        self.sidebar.btn_dashboard.clicked.connect(lambda: self.navigate(0))
        self.sidebar.btn_plants.clicked.connect(lambda: self.navigate(1))
        self.sidebar.btn_logs.clicked.connect(lambda: self.navigate(2))
        self.sidebar.btn_calendar.clicked.connect(lambda: self.navigate(3))

        # Dashboard
        self.view_dashboard.request_add_plant.connect(self._add_plant_from_dash)
        self.view_dashboard.request_add_log.connect(self._add_log_from_dash)

        # Propagação de mudanças
        self.view_plants.plants_changed.connect(self.refresh_all)
        self.view_history.logs_changed.connect(self.refresh_all)
        self.view_calendar.tasks_changed.connect(self.refresh_all)

    def navigate(self, index: int):
        self.stack.setCurrentIndex(index)
        self.sidebar.set_active(index)
        # Atualiza a view ao navegar
        views = [self.view_dashboard, self.view_plants, self.view_history, self.view_calendar]
        views[index].refresh()

    def refresh_all(self):
        """Atualiza todas as views silenciosamente."""
        self.view_dashboard.refresh()
        self.view_plants.refresh()
        self.view_history.refresh()
        self.view_calendar.refresh()
        self._update_status()

    def _update_status(self):
        plant_count   = Plant.select().count()
        pending_tasks = Task.select().where(Task.completed == False).count()
        overdue       = Task.select().where(
            (Task.completed == False) &
            (Task.due_date < datetime.date.today())
        ).count()
        msg = f'🌿 Plantas: {plant_count}  |  🔔 Tarefas pendentes: {pending_tasks}'
        if overdue:
            msg += f'  |  ⚠ {overdue} atrasadas'
        self.status.showMessage(msg)

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

    def _setup_timer(self):
        """Verifica tarefas atrasadas a cada hora."""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._check_overdue)
        self.timer.start(60 * 60 * 1000)

    def _check_overdue(self):
        count = Task.select().where(
            (Task.completed == False) &
            (Task.due_date < datetime.date.today())
        ).count()
        if count:
            self.status.showMessage(f'⚠️ {count} tarefa(s) atrasada(s)!', 5000)


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
