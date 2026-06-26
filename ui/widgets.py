"""
GrowLog — Componentes reutilizáveis de UI
"""

import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QSizePolicy, QDialog,
    QFormLayout, QLineEdit, QComboBox, QDoubleSpinBox,
    QSpinBox, QTextEdit, QDialogButtonBox, QDateEdit,
    QCheckBox, QMessageBox
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon


# ─── Card de Stat ─────────────────────────────────────────────────────────────

class StatCard(QWidget):
    """Cartão de estatística para o dashboard."""
    clicked = pyqtSignal()

    def __init__(self, icon: str, title: str, value: str,
                 status: str = '', status_type: str = 'info', parent=None):
        super().__init__(parent)
        self.setObjectName('card')
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(120)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(4)

        self.lbl_icon = QLabel(icon)
        self.lbl_icon.setStyleSheet("font-size: 20px; background: transparent; border: none;")

        self.lbl_title = QLabel(title.upper())
        self.lbl_title.setObjectName('card_title')

        self.lbl_value = QLabel(value)
        self.lbl_value.setObjectName('card_value')

        self.lbl_status = QLabel(status)
        self.lbl_status.setObjectName(f'card_status_{status_type}')

        layout.addWidget(self.lbl_icon)
        layout.addWidget(self.lbl_title)
        layout.addWidget(self.lbl_value)
        layout.addWidget(self.lbl_status)
        layout.addStretch()

    def update_data(self, value: str, status: str = '', status_type: str = 'info'):
        self.lbl_value.setText(value)
        self.lbl_status.setText(status)
        self.lbl_status.setObjectName(f'card_status_{status_type}')
        self.lbl_status.style().unpolish(self.lbl_status)
        self.lbl_status.style().polish(self.lbl_status)

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


# ─── Separador ────────────────────────────────────────────────────────────────

class HSeparator(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('separator')
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFixedHeight(1)


# ─── Botão primário ───────────────────────────────────────────────────────────

def make_primary_btn(text: str, parent=None) -> QPushButton:
    btn = QPushButton(text, parent)
    btn.setObjectName('btn_primary')
    btn.setFixedHeight(40)
    return btn

def make_small_btn(text: str, parent=None) -> QPushButton:
    btn = QPushButton(text, parent)
    btn.setObjectName('btn_small')
    return btn

def make_danger_btn(text: str, parent=None) -> QPushButton:
    btn = QPushButton(text, parent)
    btn.setObjectName('btn_danger')
    btn.setFixedHeight(36)
    return btn


# ─── Rótulo de campo ──────────────────────────────────────────────────────────

def field_label(text: str) -> QLabel:
    lbl = QLabel(text.upper())
    lbl.setObjectName('field_label')
    return lbl


# ─── Diálogo: Nova Planta ─────────────────────────────────────────────────────

class PlantDialog(QDialog):
    """Diálogo para criar ou editar uma planta."""

    STAGES = [
        ('germinacao', '🌰 Germinação'),
        ('seedling',   '🌱 Seedling'),
        ('vegetativa', '🍃 Vegetativa'),
        ('floracao',   '🌸 Floração'),
        ('colheita',   '✂️ Colheita'),
    ]

    ENVIRONMENTS = [('indoor', '🏠 Indoor'), ('outdoor', '🌳 Outdoor')]
    MEDIUMS      = [('solo', '🪨 Solo'), ('hidro', '💧 Hidropônico'), ('coco', '🥥 Coco Coir')]

    def __init__(self, parent=None, plant=None):
        super().__init__(parent)
        self.plant = plant
        self.setWindowTitle('Editar Planta' if plant else 'Nova Planta')
        self.setMinimumWidth(420)
        self._build_ui()
        if plant:
            self._fill(plant)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel('Editar Planta' if self.plant else '🌱 Nova Planta')
        title.setObjectName('dialog_title')
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignTop)

        self.edit_name   = QLineEdit(); self.edit_name.setPlaceholderText('ex: Planta 1')
        self.edit_strain = QLineEdit(); self.edit_strain.setPlaceholderText('ex: White Widow')

        self.combo_stage = QComboBox()
        for key, label in self.STAGES:
            self.combo_stage.addItem(label, key)

        self.combo_env = QComboBox()
        for key, label in self.ENVIRONMENTS:
            self.combo_env.addItem(label, key)

        self.combo_medium = QComboBox()
        for key, label in self.MEDIUMS:
            self.combo_medium.addItem(label, key)

        self.date_planted = QDateEdit(QDate.currentDate())
        self.date_planted.setCalendarPopup(True)
        self.date_planted.setDisplayFormat('dd/MM/yyyy')

        self.edit_notes = QTextEdit()
        self.edit_notes.setPlaceholderText('Observações gerais...')
        self.edit_notes.setMaximumHeight(80)

        form.addRow(field_label('Nome *'),          self.edit_name)
        form.addRow(field_label('Strain'),          self.edit_strain)
        form.addRow(field_label('Fase inicial'),    self.combo_stage)
        form.addRow(field_label('Ambiente'),        self.combo_env)
        form.addRow(field_label('Meio de cultivo'), self.combo_medium)
        form.addRow(field_label('Data de início'),  self.date_planted)
        form.addRow(field_label('Observações'),     self.edit_notes)
        layout.addLayout(form)

        btns = QHBoxLayout()
        btn_cancel = QPushButton('Cancelar')
        btn_cancel.clicked.connect(self.reject)
        self.btn_save = make_primary_btn('Salvar')
        self.btn_save.clicked.connect(self._on_save)
        btns.addWidget(btn_cancel)
        btns.addWidget(self.btn_save)
        layout.addLayout(btns)

    def _fill(self, plant):
        self.edit_name.setText(plant.name)
        self.edit_strain.setText(plant.strain or '')
        idx = self.combo_stage.findData(plant.stage)
        if idx >= 0: self.combo_stage.setCurrentIndex(idx)
        idx = self.combo_env.findData(plant.environment_type)
        if idx >= 0: self.combo_env.setCurrentIndex(idx)
        idx = self.combo_medium.findData(plant.grow_medium)
        if idx >= 0: self.combo_medium.setCurrentIndex(idx)
        qd = QDate(plant.planted_on.year, plant.planted_on.month, plant.planted_on.day)
        self.date_planted.setDate(qd)
        self.edit_notes.setPlainText(plant.notes or '')

    def _on_save(self):
        if not self.edit_name.text().strip():
            QMessageBox.warning(self, 'Aviso', 'O nome da planta é obrigatório!')
            return
        self.accept()

    def get_data(self) -> dict:
        pd = self.date_planted.date()
        return {
            'name':             self.edit_name.text().strip(),
            'strain':           self.edit_strain.text().strip() or None,
            'stage':            self.combo_stage.currentData(),
            'environment_type': self.combo_env.currentData(),
            'grow_medium':      self.combo_medium.currentData(),
            'planted_on':       datetime.date(pd.year(), pd.month(), pd.day()),
            'notes':            self.edit_notes.toPlainText().strip() or None,
        }


# ─── Diálogo: Novo Log ────────────────────────────────────────────────────────

class LogDialog(QDialog):
    """Diálogo para registrar rega, nutrição ou anotação."""

    def __init__(self, parent=None, plants=None, preselect_plant=None, log_type='rega'):
        super().__init__(parent)
        self.plants = plants or []
        self.setWindowTitle('Novo Registro')
        self.setMinimumWidth(440)
        self._build_ui(preselect_plant, log_type)

    def _build_ui(self, preselect_plant, log_type):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel('📋 Novo Registro')
        title.setObjectName('dialog_title')
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)

        # Planta
        self.combo_plant = QComboBox()
        for p in self.plants:
            self.combo_plant.addItem(f'🌿 {p.name}', p.id)
        if preselect_plant:
            idx = self.combo_plant.findData(preselect_plant.id)
            if idx >= 0: self.combo_plant.setCurrentIndex(idx)

        # Tipo
        self.combo_type = QComboBox()
        self.combo_type.addItem('💧 Rega',              'rega')
        self.combo_type.addItem('🧪 Nutrição',         'nutricao')
        self.combo_type.addItem('📝 Anotação',         'nota')
        self.combo_type.addItem('🔄 Fase',             'fase')
        self.combo_type.addItem('🏠 Migração Ambiente','ambiente')
        idx = self.combo_type.findData(log_type)
        if idx >= 0: self.combo_type.setCurrentIndex(idx)
        self.combo_type.currentIndexChanged.connect(self._toggle_fields)

        # Data
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat('dd/MM/yyyy')

        form.addRow(field_label('Planta'),  self.combo_plant)
        form.addRow(field_label('Tipo'),    self.combo_type)
        form.addRow(field_label('Data'),    self.date_edit)
        layout.addLayout(form)

        # ── Campos de Rega ──────────────────────────────
        self.water_group = QWidget()
        wg = QFormLayout(self.water_group)
        wg.setContentsMargins(0, 0, 0, 0)
        wg.setSpacing(10)

        self.spin_volume = QDoubleSpinBox()
        self.spin_volume.setRange(0, 50); self.spin_volume.setSuffix(' L'); self.spin_volume.setValue(1.5)

        self.spin_ph = QDoubleSpinBox()
        self.spin_ph.setRange(0, 14); self.spin_ph.setDecimals(1); self.spin_ph.setValue(6.2)

        self.spin_ec = QDoubleSpinBox()
        self.spin_ec.setRange(0, 10); self.spin_ec.setDecimals(2); self.spin_ec.setSuffix(' mS/cm')

        self.spin_runoff = QDoubleSpinBox()
        self.spin_runoff.setRange(0, 14); self.spin_runoff.setDecimals(1); self.spin_runoff.setValue(6.0)

        wg.addRow(field_label('Volume'),    self.spin_volume)
        wg.addRow(field_label('pH'),        self.spin_ph)
        wg.addRow(field_label('EC'),        self.spin_ec)
        wg.addRow(field_label('Runoff pH'), self.spin_runoff)
        layout.addWidget(self.water_group)

        # ── Campos de Nutrição ──────────────────────────
        self.nutri_group = QWidget()
        ng = QFormLayout(self.nutri_group)
        ng.setContentsMargins(0, 0, 0, 0)
        ng.setSpacing(10)

        self.edit_product = QLineEdit(); self.edit_product.setPlaceholderText('ex: Bloom Booster')
        self.spin_dose = QDoubleSpinBox()
        self.spin_dose.setRange(0, 100); self.spin_dose.setSuffix(' ml/L')
        self.spin_ph_after = QDoubleSpinBox()
        self.spin_ph_after.setRange(0, 14); self.spin_ph_after.setDecimals(1); self.spin_ph_after.setValue(6.3)

        ng.addRow(field_label('Produto'),   self.edit_product)
        ng.addRow(field_label('Dose'),      self.spin_dose)
        ng.addRow(field_label('pH final'),  self.spin_ph_after)
        layout.addWidget(self.nutri_group)

        # ── Campo de Anotação / Fase ────────────────────
        self.note_group = QWidget()
        noteg = QFormLayout(self.note_group)
        noteg.setContentsMargins(0, 0, 0, 0)
        noteg.setSpacing(10)

        self.edit_content = QTextEdit()
        self.edit_content.setPlaceholderText('Descreva sua observação...')
        self.edit_content.setMaximumHeight(100)

        self.combo_new_stage = QComboBox()
        STAGES = [
            ('germinacao', '🌰 Germinação'), ('seedling', '🌱 Seedling'),
            ('vegetativa', '🍃 Vegetativa'), ('floracao', '🌸 Floração'),
            ('colheita', '✂️ Colheita'),
        ]
        for key, label in STAGES:
            self.combo_new_stage.addItem(label, key)

        self.combo_new_env = QComboBox()
        self.combo_new_env.addItem('🏠 Indoor',  'indoor')
        self.combo_new_env.addItem('🌳 Outdoor', 'outdoor')

        noteg.addRow(field_label('Nota'),            self.edit_content)
        noteg.addRow(field_label('Nova fase'),       self.combo_new_stage)
        noteg.addRow(field_label('Novo ambiente'),   self.combo_new_env)
        layout.addWidget(self.note_group)

        # Botões
        btns = QHBoxLayout()
        btn_cancel = QPushButton('Cancelar')
        btn_cancel.clicked.connect(self.reject)
        btn_save = make_primary_btn('Salvar')
        btn_save.clicked.connect(self.accept)
        btns.addWidget(btn_cancel)
        btns.addWidget(btn_save)
        layout.addLayout(btns)

        self._toggle_fields()

    def _toggle_fields(self):
        t = self.combo_type.currentData()
        self.water_group.setVisible(t == 'rega')
        self.nutri_group.setVisible(t == 'nutricao')
        self.note_group.setVisible(t in ('nota', 'fase', 'ambiente'))
        self.combo_new_stage.setVisible(t == 'fase')
        self.combo_new_env.setVisible(t == 'ambiente')
        self.adjustSize()

    def get_data(self) -> dict:
        t   = self.combo_type.currentData()
        qd  = self.date_edit.date()
        date = datetime.date(qd.year(), qd.month(), qd.day())

        data = {
            'plant_id': self.combo_plant.currentData(),
            'log_type': t,
            'date':     date,
        }

        if t == 'rega':
            data.update({
                'water_amount': self.spin_volume.value() or None,
                'ph':           self.spin_ph.value() or None,
                'ec':           self.spin_ec.value() or None,
                'runoff_ph':    self.spin_runoff.value() or None,
                'summary':      f"{self.spin_volume.value()}L · pH {self.spin_ph.value()}"
            })
        elif t == 'nutricao':
            data.update({
                'product':  self.edit_product.text().strip() or None,
                'dose':     self.spin_dose.value() or None,
                'ph_after': self.spin_ph_after.value() or None,
                'summary':  f"{self.edit_product.text()} {self.spin_dose.value()}ml/L"
            })
        elif t == 'fase':
            content = self.edit_content.toPlainText().strip()
            data.update({
                'content':   content or None,
                'new_stage': self.combo_new_stage.currentData(),
                'summary':   f"Fase → {self.combo_new_stage.currentText()}"
            })
        elif t == 'ambiente':
            content = self.edit_content.toPlainText().strip()
            data.update({
                'content':     content or None,
                'new_env':     self.combo_new_env.currentData(),
                'summary':     f"Ambiente → {self.combo_new_env.currentText()}"
            })
        elif t == 'nota':
            content = self.edit_content.toPlainText().strip()
            data.update({
                'content': content or None,
                'summary': content[:60] if content else 'Anotação'
            })

        return data


# ─── Diálogo: Nova Tarefa ─────────────────────────────────────────────────────

class TaskDialog(QDialog):
    def __init__(self, parent=None, plants=None, task=None):
        super().__init__(parent)
        self.plants = plants or []
        self.task = task
        self.setWindowTitle('Editar Tarefa' if task else 'Nova Tarefa')
        self.setMinimumWidth(400)
        self._build_ui()
        if task:
            self._fill(task)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel('Editar Tarefa' if self.task else '📅 Nova Tarefa')
        title.setObjectName('dialog_title')
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)

        self.combo_plant = QComboBox()
        for p in self.plants:
            self.combo_plant.addItem(f'🌿 {p.name}', p.id)

        self.edit_title = QLineEdit()
        self.edit_title.setPlaceholderText('ex: Regar, Fertilizar, Verificar pH...')

        self.date_due = QDateEdit(QDate.currentDate())
        self.date_due.setCalendarPopup(True)
        self.date_due.setDisplayFormat('dd/MM/yyyy')

        self.check_done = QCheckBox('Marcar como concluída')
        self.check_done.setStyleSheet('color: #7a9e7e;')

        self.edit_notes = QTextEdit()
        self.edit_notes.setPlaceholderText('Observações...')
        self.edit_notes.setMaximumHeight(80)

        form.addRow(field_label('Planta'),     self.combo_plant)
        form.addRow(field_label('Tarefa'),     self.edit_title)
        form.addRow(field_label('Vencimento'), self.date_due)
        form.addRow(field_label('Status'),     self.check_done)
        form.addRow(field_label('Notas'),      self.edit_notes)
        layout.addLayout(form)

        btns = QHBoxLayout()
        btn_cancel = QPushButton('Cancelar')
        btn_cancel.clicked.connect(self.reject)
        btn_save = make_primary_btn('Salvar')
        btn_save.clicked.connect(self._on_save)
        btns.addWidget(btn_cancel)
        btns.addWidget(btn_save)
        layout.addLayout(btns)

    def _fill(self, task):
        idx = self.combo_plant.findData(task.plant_id)
        if idx >= 0: self.combo_plant.setCurrentIndex(idx)
        self.edit_title.setText(task.title)
        qd = QDate(task.due_date.year, task.due_date.month, task.due_date.day)
        self.date_due.setDate(qd)
        self.check_done.setChecked(task.completed)
        self.edit_notes.setPlainText(task.notes or '')

    def _on_save(self):
        if not self.edit_title.text().strip():
            QMessageBox.warning(self, 'Aviso', 'O título da tarefa é obrigatório!')
            return
        self.accept()

    def get_data(self) -> dict:
        qd = self.date_due.date()
        return {
            'plant_id':  self.combo_plant.currentData(),
            'title':     self.edit_title.text().strip(),
            'due_date':  datetime.date(qd.year(), qd.month(), qd.day()),
            'completed': self.check_done.isChecked(),
            'notes':     self.edit_notes.toPlainText().strip() or None,
        }
