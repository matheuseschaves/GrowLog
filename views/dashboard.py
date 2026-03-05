"""
GrowLog — Dashboard
"""
import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QGridLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal

from database.models import Plant, Log, Task
from ui.widgets import StatCard, make_primary_btn, make_small_btn, HSeparator, LogDialog


class DashboardView(QWidget):
    request_add_plant = pyqtSignal()
    request_add_log   = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(0)

        # Cabeçalho
        header = QHBoxLayout()
        col_title = QVBoxLayout()
        lbl_title = QLabel('Dashboard')
        lbl_title.setObjectName('page_title')
        lbl_sub = QLabel('VISÃO GERAL DO SEU CULTIVO')
        lbl_sub.setObjectName('page_subtitle')
        col_title.addWidget(lbl_title)
        col_title.addWidget(lbl_sub)
        header.addLayout(col_title)
        header.addStretch()
        btn_reg = make_primary_btn('+ Registrar')
        btn_reg.clicked.connect(self.request_add_log)
        btn_plant = make_small_btn('+ Planta')
        btn_plant.clicked.connect(self.request_add_plant)
        header.addWidget(btn_plant)
        header.addSpacing(8)
        header.addWidget(btn_reg)
        root.addLayout(header)
        root.addSpacing(20)

        # Cards de stats
        self.card_plants   = StatCard('🌿', 'Plantas',      '—')
        self.card_logs     = StatCard('📋', 'Registros',    '—')
        self.card_watering = StatCard('💧', 'Última Rega',  '—')
        self.card_tasks    = StatCard('🔔', 'Tarefas',      '—')

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(14)
        for card in (self.card_plants, self.card_logs, self.card_watering, self.card_tasks):
            cards_layout.addWidget(card)
        root.addLayout(cards_layout)
        root.addSpacing(24)

        # ── Linha inferior: plantas + histórico recente ──────────────────────
        bottom = QHBoxLayout()
        bottom.setSpacing(16)

        # Tabela de plantas
        left_col = QVBoxLayout()
        lbl_p = QLabel('PLANTAS ATIVAS')
        lbl_p.setObjectName('page_subtitle')
        left_col.addWidget(lbl_p)

        self.plant_table = QTableWidget()
        self.plant_table.setColumnCount(4)
        self.plant_table.setHorizontalHeaderLabels(['Planta', 'Fase', 'Dia', 'Rega'])
        self.plant_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.plant_table.verticalHeader().setVisible(False)
        self.plant_table.setAlternatingRowColors(True)
        self.plant_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.plant_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        left_col.addWidget(self.plant_table)
        bottom.addLayout(left_col, 3)

        # Histórico recente
        right_col = QVBoxLayout()
        lbl_h = QLabel('ATIVIDADE RECENTE')
        lbl_h.setObjectName('page_subtitle')
        right_col.addWidget(lbl_h)

        self.log_table = QTableWidget()
        self.log_table.setColumnCount(3)
        self.log_table.setHorizontalHeaderLabels(['Data', 'Planta', 'Registro'])
        self.log_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.log_table.verticalHeader().setVisible(False)
        self.log_table.setAlternatingRowColors(True)
        self.log_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        right_col.addWidget(self.log_table)
        bottom.addLayout(right_col, 2)

        root.addLayout(bottom)

    def refresh(self):
        """Recarrega todos os dados do dashboard."""
        plants  = list(Plant.select())
        logs    = list(Log.select(Log, Plant).join(Plant).order_by(Log.date.desc()).limit(20))
        pending = Task.select().where(Task.completed == False).count()
        overdue = Task.select().where(
            (Task.completed == False) &
            (Task.due_date < datetime.date.today())
        ).count()

        # Cards
        self.card_plants.update_data(str(len(plants)), f'{len(plants)} no cultivo', 'info')
        self.card_logs.update_data(str(len(logs)), 'últimos registros', 'info')

        # Última rega geral
        last_water = (Log.select()
                      .where(Log.log_type == 'rega')
                      .order_by(Log.date.desc())
                      .first())
        if last_water:
            days = (datetime.date.today() - last_water.date).days
            st   = 'warn' if days >= 2 else 'ok'
            stxt = f'⚠ há {days} dias' if days >= 2 else f'✓ há {days} dias'
            self.card_watering.update_data(f'{days}d', stxt, st)
        else:
            self.card_watering.update_data('—', 'sem registro', 'info')

        st = 'warn' if overdue else ('ok' if pending == 0 else 'info')
        self.card_tasks.update_data(
            str(pending),
            f'⚠ {overdue} atrasadas' if overdue else ('✓ tudo em dia' if pending == 0 else f'{pending} pendentes'),
            st
        )

        # Tabela de plantas
        STAGE_LABELS = {
            'germinacao': '🌰 Germinação', 'seedling': '🌱 Seedling',
            'vegetativa': '🍃 Vegetativa', 'floracao': '🌸 Floração',
            'colheita': '✂️ Colheita',
        }
        self.plant_table.setRowCount(len(plants))
        for row, plant in enumerate(plants):
            days_w = plant.days_since_watered()
            water_txt = f'{days_w}d atrás' if days_w is not None else '—'
            self.plant_table.setItem(row, 0, QTableWidgetItem(plant.name))
            self.plant_table.setItem(row, 1, QTableWidgetItem(STAGE_LABELS.get(plant.stage, plant.stage)))
            self.plant_table.setItem(row, 2, QTableWidgetItem(f'{plant.days_since_planted()}d'))
            self.plant_table.setItem(row, 3, QTableWidgetItem(water_txt))

        # Tabela de logs
        TYPE_ICONS = {'rega': '💧', 'nutricao': '🧪', 'nota': '📝', 'fase': '🔄', 'outro': '📌'}
        self.log_table.setRowCount(len(logs))
        for row, log in enumerate(logs):
            date_str = log.date.strftime('%d/%m')
            icon     = TYPE_ICONS.get(log.log_type, '📌')
            summary  = log.summary or log.log_type
            self.log_table.setItem(row, 0, QTableWidgetItem(date_str))
            self.log_table.setItem(row, 1, QTableWidgetItem(log.plant.name))
            self.log_table.setItem(row, 2, QTableWidgetItem(f'{icon} {summary}'))
