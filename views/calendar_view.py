"""
GrowLog — Tela de Calendário
"""
import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QCalendarWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QTextCharFormat, QColor

from database.models import Plant, Task
from ui.widgets import make_primary_btn, make_small_btn, make_danger_btn, TaskDialog


class CalendarView(QWidget):
    tasks_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._task_dates = {}

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(0)

        # Cabeçalho
        header = QHBoxLayout()
        col = QVBoxLayout()
        lbl = QLabel('Calendário')
        lbl.setObjectName('page_title')
        sub = QLabel('TAREFAS E LEMBRETES')
        sub.setObjectName('page_subtitle')
        col.addWidget(lbl)
        col.addWidget(sub)
        header.addLayout(col)
        header.addStretch()
        self.btn_new = make_primary_btn('+ Nova Tarefa')
        self.btn_new.clicked.connect(self.add_task)
        header.addWidget(self.btn_new)
        root.addLayout(header)
        root.addSpacing(20)

        # Layout lateral: calendário + lista
        content = QHBoxLayout()
        content.setSpacing(20)

        # Calendário
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(False)
        self.calendar.setMaximumWidth(360)
        self.calendar.clicked.connect(self._on_date_clicked)
        content.addWidget(self.calendar)

        # Painel direito: tarefas do dia
        right = QVBoxLayout()
        self.lbl_day = QLabel('Selecione um dia')
        self.lbl_day.setObjectName('page_subtitle')
        self.lbl_day.setStyleSheet('color: #7a9e7e; font-size: 12px;')
        right.addWidget(self.lbl_day)

        self.task_table = QTableWidget()
        self.task_table.setColumnCount(3)
        self.task_table.setHorizontalHeaderLabels(['Planta', 'Tarefa', 'Status'])
        self.task_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.task_table.verticalHeader().setVisible(False)
        self.task_table.setAlternatingRowColors(True)
        self.task_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.task_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        right.addWidget(self.task_table)

        btns = QHBoxLayout()
        self.btn_toggle = make_small_btn('✓ Concluir')
        self.btn_toggle.clicked.connect(self.toggle_task)
        self.btn_edit_task = make_small_btn('✏ Editar')
        self.btn_edit_task.clicked.connect(self.edit_task)
        self.btn_del = make_danger_btn('🗑 Excluir')
        self.btn_del.clicked.connect(self.delete_task)
        btns.addWidget(self.btn_toggle)
        btns.addWidget(self.btn_edit_task)
        btns.addStretch()
        btns.addWidget(self.btn_del)
        right.addLayout(btns)

        content.addLayout(right, 1)
        root.addLayout(content)

        # Todas as tarefas pendentes (abaixo)
        root.addSpacing(20)
        lbl_all = QLabel('TODAS AS TAREFAS PENDENTES')
        lbl_all.setObjectName('page_subtitle')
        root.addWidget(lbl_all)

        self.all_tasks_table = QTableWidget()
        self.all_tasks_table.setColumnCount(4)
        self.all_tasks_table.setHorizontalHeaderLabels(['Data', 'Planta', 'Tarefa', 'Status'])
        self.all_tasks_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.all_tasks_table.verticalHeader().setVisible(False)
        self.all_tasks_table.setAlternatingRowColors(True)
        self.all_tasks_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.all_tasks_table.setMaximumHeight(200)
        root.addWidget(self.all_tasks_table)

    def refresh(self):
        self._task_dates.clear()
        tasks = list(Task.select(Task, Plant).join(Plant).order_by(Task.due_date))

        # Agrupa por data
        for task in tasks:
            d = task.due_date.isoformat()
            self._task_dates.setdefault(d, []).append(task)

        # Atualiza cores no calendário
        self._update_calendar_colors()

        # Recarrega painel do dia atual
        self._on_date_clicked(self.calendar.selectedDate())

        # Tabela geral de pendentes
        pending = [t for t in tasks if not t.completed]
        self.all_tasks_table.setRowCount(len(pending))
        today = datetime.date.today()
        for row, t in enumerate(pending):
            overdue = t.due_date < today
            status  = '⚠ Atrasada' if overdue else '⏳ Pendente'
            self.all_tasks_table.setItem(row, 0, QTableWidgetItem(t.due_date.strftime('%d/%m/%Y')))
            self.all_tasks_table.setItem(row, 1, QTableWidgetItem(t.plant.name))
            self.all_tasks_table.setItem(row, 2, QTableWidgetItem(t.title))
            self.all_tasks_table.setItem(row, 3, QTableWidgetItem(status))
            self.all_tasks_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, t.id)
            if overdue:
                for col in range(4):
                    item = self.all_tasks_table.item(row, col)
                    if item:
                        item.setForeground(QColor('#e05c5c'))

    def _update_calendar_colors(self):
        today = datetime.date.today()
        for date_str, tasks in self._task_dates.items():
            try:
                d = datetime.date.fromisoformat(date_str)
            except ValueError:
                continue
            qd = QDate(d.year, d.month, d.day)
            fmt = QTextCharFormat()
            has_pending = any(not t.completed for t in tasks)
            overdue     = any(not t.completed and d < today for t in tasks)
            if overdue:
                fmt.setBackground(QColor(80, 30, 30))
                fmt.setForeground(QColor('#e05c5c'))
            elif has_pending:
                fmt.setBackground(QColor(60, 50, 20))
                fmt.setForeground(QColor('#e8a44a'))
            else:
                fmt.setBackground(QColor(20, 50, 25))
                fmt.setForeground(QColor('#4caf6e'))
            self.calendar.setDateTextFormat(qd, fmt)

    def _on_date_clicked(self, qdate: QDate):
        d = datetime.date(qdate.year(), qdate.month(), qdate.day())
        self.lbl_day.setText(f'TAREFAS EM {d.strftime("%d/%m/%Y").upper()}')
        tasks = self._task_dates.get(d.isoformat(), [])
        self.task_table.setRowCount(len(tasks))
        for row, t in enumerate(tasks):
            status = '✅ Concluída' if t.completed else '⏳ Pendente'
            self.task_table.setItem(row, 0, QTableWidgetItem(t.plant.name))
            self.task_table.setItem(row, 1, QTableWidgetItem(t.title))
            self.task_table.setItem(row, 2, QTableWidgetItem(status))
            self.task_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, t.id)

    def _selected_task_id(self):
        row = self.task_table.currentRow()
        if row < 0:
            return None
        return self.task_table.item(row, 0).data(Qt.ItemDataRole.UserRole)

    def add_task(self):
        plants = list(Plant.select())
        if not plants:
            QMessageBox.warning(self, 'Aviso', 'Cadastre uma planta primeiro!')
            return
        dlg = TaskDialog(self, plants=plants)
        if dlg.exec():
            data = dlg.get_data()
            Task.create(**data)
            self.refresh()
            self.tasks_changed.emit()

    def toggle_task(self):
        tid = self._selected_task_id()
        if not tid:
            QMessageBox.warning(self, 'Aviso', 'Selecione uma tarefa.')
            return
        task = Task.get_by_id(tid)
        task.completed = not task.completed
        task.save()
        self.refresh()
        self.tasks_changed.emit()

    def edit_task(self):
        tid = self._selected_task_id()
        if not tid:
            QMessageBox.warning(self, 'Aviso', 'Selecione uma tarefa.')
            return
        task   = Task.get_by_id(tid)
        plants = list(Plant.select())
        dlg    = TaskDialog(self, plants=plants, task=task)
        if dlg.exec():
            data = dlg.get_data()
            for k, v in data.items():
                setattr(task, k, v)
            task.save()
            self.refresh()
            self.tasks_changed.emit()

    def delete_task(self):
        tid = self._selected_task_id()
        if not tid:
            QMessageBox.warning(self, 'Aviso', 'Selecione uma tarefa.')
            return
        reply = QMessageBox.question(
            self, 'Confirmar', 'Excluir esta tarefa?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            Task.delete_by_id(tid)
            self.refresh()
            self.tasks_changed.emit()
