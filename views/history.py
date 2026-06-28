"""
GrowLog — Tela de Histórico
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from database.models import Plant, Log
from ui.widgets import make_primary_btn, make_small_btn, make_danger_btn, LogDialog

TYPE_ICONS = {
    'rega':     '💧 Rega',
    'nutricao': '🧪 Nutrição',
    'nota':     '📝 Anotação',
    'fase':     '🔄 Fase',
    'outro':    '📌 Outro',
}


class HistoryView(QWidget):
    logs_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(0)

        # Cabeçalho
        header = QHBoxLayout()
        col = QVBoxLayout()
        lbl = QLabel('Histórico')
        lbl.setObjectName('page_title')
        sub = QLabel('TODOS OS REGISTROS')
        sub.setObjectName('page_subtitle')
        col.addWidget(lbl)
        col.addWidget(sub)
        header.addLayout(col)
        header.addStretch()

        # Filtro por planta
        self.combo_filter = QComboBox()
        self.combo_filter.setMinimumWidth(160)
        self.combo_filter.currentIndexChanged.connect(self.refresh)
        header.addWidget(self.combo_filter)
        header.addSpacing(8)

        self.btn_new = make_primary_btn('+ Registrar')
        self.btn_new.clicked.connect(self.add_log)
        header.addWidget(self.btn_new)
        root.addLayout(header)
        root.addSpacing(20)

        # Tabela
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['Data', 'Planta', 'Tipo', 'Resumo', 'Detalhes'])
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        root.addWidget(self.table)
        root.addSpacing(12)

        # Botão deletar
        actions = QHBoxLayout()
        self.btn_delete = make_danger_btn('🗑 Excluir registro')
        self.btn_delete.clicked.connect(self.delete_log)
        actions.addStretch()
        actions.addWidget(self.btn_delete)
        root.addLayout(actions)

    def refresh(self):
        # Atualiza filtro
        current_pid = self.combo_filter.currentData()

        plants = list(Plant.select())
        self.combo_filter.blockSignals(True)
        self.combo_filter.clear()
        self.combo_filter.addItem('Todas as plantas', None)
        for p in plants:
            self.combo_filter.addItem(f'🌿 {p.name}', p.id)
        # Restaura seleção
        if current_pid:
            idx = self.combo_filter.findData(current_pid)
            if idx >= 0:
                self.combo_filter.setCurrentIndex(idx)
        self.combo_filter.blockSignals(False)

        # Query
        pid = self.combo_filter.currentData()
        query = Log.select(Log, Plant).join(Plant).order_by(Log.date.desc())
        if pid:
            query = query.where(Log.plant_id == pid)
        logs = list(query)

        self.table.setRowCount(len(logs))
        for row, log in enumerate(logs):
            details = self._build_details(log)
            self.table.setItem(row, 0, QTableWidgetItem(log.date.strftime('%d/%m/%Y')))
            self.table.setItem(row, 1, QTableWidgetItem(log.plant.name))
            self.table.setItem(row, 2, QTableWidgetItem(TYPE_ICONS.get(log.log_type, log.log_type)))
            self.table.setItem(row, 3, QTableWidgetItem(log.summary or ''))
            self.table.setItem(row, 4, QTableWidgetItem(details))
            self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, log.id)

    def _build_details(self, log) -> str:
        parts = []
        if log.log_type == 'rega':
            if log.water_amount: parts.append(f'{log.water_amount}L')
            if log.ph:           parts.append(f'pH {log.ph}')
            if log.ec:           parts.append(f'EC {log.ec}')
            if log.runoff_ph:    parts.append(f'Runoff {log.runoff_ph}')
            if log.height:       parts.append(f'📏 {log.height}cm')
        elif log.log_type == 'nutricao':
            if log.product:  parts.append(log.product)
            if log.dose:     parts.append(f'{log.dose}ml/L')
            if log.ph_after: parts.append(f'pH {log.ph_after}')
        elif log.log_type in ('nota', 'fase'):
            if log.content: parts.append(log.content[:80])
        return ' · '.join(parts)

    def _selected_log_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        return self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)

    def add_log(self):
        plants = list(Plant.select())
        if not plants:
            QMessageBox.warning(self, 'Aviso', 'Cadastre uma planta primeiro!')
            return
        dlg = LogDialog(self, plants=plants)
        if dlg.exec():
            data = dlg.get_data()
            plant_id  = data.pop('plant_id')
            new_stage = data.pop('new_stage', None)
            Log.create(plant_id=plant_id, **data)

            # Atualiza plant se for rega ou fase
            plant = Plant.get_by_id(plant_id)
            if data['log_type'] == 'rega':
                plant.last_watered = data['date']
                if data.get('ph'):   plant.current_ph = data['ph']
                if data.get('ec'):   plant.current_ec = data['ec']
                plant.save()
            elif data['log_type'] == 'nutricao':
                plant.last_fertilized = data['date']
                plant.save()
            elif data['log_type'] == 'fase' and new_stage:
                plant.stage = new_stage
                plant.save()

            self.refresh()
            self.logs_changed.emit()

    def delete_log(self):
        lid = self._selected_log_id()
        if not lid:
            QMessageBox.warning(self, 'Aviso', 'Selecione um registro para excluir.')
            return
        reply = QMessageBox.question(
            self, 'Confirmar', 'Excluir este registro?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            Log.delete_by_id(lid)
            self.refresh()
            self.logs_changed.emit()
