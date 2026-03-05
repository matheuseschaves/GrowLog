"""
GrowLog — Tela de Plantas
"""
import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from database.models import Plant
from ui.widgets import make_primary_btn, make_small_btn, make_danger_btn, PlantDialog


STAGE_LABELS = {
    'germinacao': '🌰 Germinação',
    'seedling':   '🌱 Seedling',
    'vegetativa': '🍃 Vegetativa',
    'floracao':   '🌸 Floração',
    'colheita':   '✂️ Colheita',
}


class PlantsView(QWidget):
    plants_changed = pyqtSignal()

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
        lbl = QLabel('Plantas')
        lbl.setObjectName('page_title')
        sub = QLabel('GERENCIAR PLANTAS')
        sub.setObjectName('page_subtitle')
        col.addWidget(lbl)
        col.addWidget(sub)
        header.addLayout(col)
        header.addStretch()
        self.btn_new = make_primary_btn('+ Nova Planta')
        self.btn_new.clicked.connect(self.add_plant)
        header.addWidget(self.btn_new)
        root.addLayout(header)
        root.addSpacing(20)

        # Tabela
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            'Nome', 'Strain', 'Fase', 'Ambiente', 'Meio', 'Início', 'Dias'
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.doubleClicked.connect(self.edit_plant)
        root.addWidget(self.table)
        root.addSpacing(12)

        # Botões de ação
        actions = QHBoxLayout()
        self.btn_edit   = make_small_btn('✏ Editar')
        self.btn_delete = make_danger_btn('🗑 Excluir')
        self.btn_edit.clicked.connect(self.edit_plant)
        self.btn_delete.clicked.connect(self.delete_plant)
        actions.addStretch()
        actions.addWidget(self.btn_edit)
        actions.addWidget(self.btn_delete)
        root.addLayout(actions)

    def refresh(self):
        plants = list(Plant.select().order_by(Plant.planted_on.desc()))
        self.table.setRowCount(len(plants))
        for row, p in enumerate(plants):
            self.table.setItem(row, 0, QTableWidgetItem(p.name))
            self.table.setItem(row, 1, QTableWidgetItem(p.strain or '—'))
            self.table.setItem(row, 2, QTableWidgetItem(STAGE_LABELS.get(p.stage, p.stage)))
            self.table.setItem(row, 3, QTableWidgetItem(p.environment_type))
            self.table.setItem(row, 4, QTableWidgetItem(p.grow_medium))
            self.table.setItem(row, 5, QTableWidgetItem(p.planted_on.strftime('%d/%m/%Y')))
            self.table.setItem(row, 6, QTableWidgetItem(f'{p.days_since_planted()}d'))
            # Guarda id na coluna oculta via UserRole
            self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, p.id)

    def _selected_plant(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        pid = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        return Plant.get_by_id(pid)

    def add_plant(self):
        dlg = PlantDialog(self)
        if dlg.exec():
            data = dlg.get_data()
            Plant.create(**data)
            self.refresh()
            self.plants_changed.emit()

    def edit_plant(self):
        plant = self._selected_plant()
        if not plant:
            QMessageBox.warning(self, 'Aviso', 'Selecione uma planta para editar.')
            return
        dlg = PlantDialog(self, plant=plant)
        if dlg.exec():
            data = dlg.get_data()
            for k, v in data.items():
                setattr(plant, k, v)
            plant.save()
            self.refresh()
            self.plants_changed.emit()

    def delete_plant(self):
        plant = self._selected_plant()
        if not plant:
            QMessageBox.warning(self, 'Aviso', 'Selecione uma planta para excluir.')
            return
        reply = QMessageBox.question(
            self, 'Confirmar',
            f'Excluir "{plant.name}"?\nTodos os registros e tarefas associados serão removidos.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            plant.delete_instance(recursive=True)
            self.refresh()
            self.plants_changed.emit()
