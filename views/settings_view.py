"""
GrowLog — Tela de Configurações e Sync
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QGroupBox, QMessageBox, QFormLayout, QSpinBox, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal

from ui.widgets import make_primary_btn, make_small_btn, make_danger_btn, field_label


class SettingsView(QWidget):
    """Tela de configurações com controle de sync."""

    request_authenticate = pyqtSignal()
    request_upload       = pyqtSignal()
    request_download     = pyqtSignal()
    request_sync_now     = pyqtSignal()
    interval_changed     = pyqtSignal(str)
    preferences_saved    = pyqtSignal(int)   # watering_interval_days

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        # Layout externo — só contém o scroll
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        outer.addWidget(scroll)

        # Widget interno que vai dentro do scroll
        inner = QWidget()
        scroll.setWidget(inner)

        root = QVBoxLayout(inner)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(20)
        root.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Título
        lbl = QLabel('Configurações')
        lbl.setObjectName('page_title')
        sub = QLabel('SYNC E PREFERÊNCIAS')
        sub.setObjectName('page_subtitle')
        root.addWidget(lbl)
        root.addWidget(sub)

        # ── Grupo: Google Drive ──────────────────────────────────────────────
        group_drive = QGroupBox('☁ Google Drive Sync')
        group_drive.setStyleSheet("""
            QGroupBox {
                border: 1px solid #2a3f2b;
                border-radius: 12px;
                margin-top: 12px;
                padding: 16px;
                color: #7a9e7e;
                font-size: 11px;
                letter-spacing: 1px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
            }
        """)
        drive_layout = QVBoxLayout(group_drive)
        drive_layout.setSpacing(14)

        # Status de conexão
        status_row = QHBoxLayout()
        lbl_status_label = QLabel('Status:')
        lbl_status_label.setStyleSheet('color: #4a6b4e; font-size: 11px;')
        self.lbl_status = QLabel('Não conectado')
        self.lbl_status.setObjectName('badge_amber')
        status_row.addWidget(lbl_status_label)
        status_row.addWidget(self.lbl_status)
        status_row.addStretch()
        drive_layout.addLayout(status_row)

        # Botão de autenticação
        self.btn_auth = make_primary_btn('🔑 Conectar conta Google')
        self.btn_auth.clicked.connect(self.request_authenticate)
        drive_layout.addWidget(self.btn_auth)

        # Intervalo de sync
        interval_row = QHBoxLayout()
        lbl_interval = QLabel('Sync automático:')
        lbl_interval.setStyleSheet('color: #7a9e7e; font-size: 13px;')
        self.combo_interval = QComboBox()
        self.combo_interval.setMinimumWidth(160)
        self.combo_interval.currentTextChanged.connect(self.interval_changed)
        interval_row.addWidget(lbl_interval)
        interval_row.addWidget(self.combo_interval)
        interval_row.addStretch()
        drive_layout.addLayout(interval_row)

        # Status do timer
        timer_row = QHBoxLayout()
        lbl_timer_label = QLabel('Timer:')
        lbl_timer_label.setStyleSheet('color: #4a6b4e; font-size: 11px;')
        self.lbl_timer = QLabel('Inativo')
        self.lbl_timer.setStyleSheet('color: #4a6b4e; font-size: 11px;')
        self.btn_toggle_timer = make_small_btn('▶ Iniciar')
        self.btn_toggle_timer.clicked.connect(self._toggle_timer)
        timer_row.addWidget(lbl_timer_label)
        timer_row.addWidget(self.lbl_timer)
        timer_row.addStretch()
        timer_row.addWidget(self.btn_toggle_timer)
        drive_layout.addLayout(timer_row)

        # Último sync
        self.lbl_last_sync = QLabel('Último sync: —')
        self.lbl_last_sync.setStyleSheet('color: #4a6b4e; font-size: 11px;')
        drive_layout.addWidget(self.lbl_last_sync)

        # Ações manuais
        manual_row = QHBoxLayout()
        lbl_manual = QLabel('Manual:')
        lbl_manual.setStyleSheet('color: #7a9e7e;')
        self.btn_upload   = make_small_btn('⬆ Enviar agora')
        self.btn_download = make_small_btn('⬇ Baixar agora')
        self.btn_sync_now = make_small_btn('🔄 Smart Sync')
        self.btn_upload.clicked.connect(self.request_upload)
        self.btn_download.clicked.connect(self._confirm_download)
        self.btn_sync_now.clicked.connect(self.request_sync_now)
        manual_row.addWidget(lbl_manual)
        manual_row.addWidget(self.btn_upload)
        manual_row.addWidget(self.btn_download)
        manual_row.addWidget(self.btn_sync_now)
        manual_row.addStretch()
        drive_layout.addLayout(manual_row)

        root.addWidget(group_drive)

        # ── Grupo: Preferências de Cultivo ───────────────────────────────────
        group_prefs = QGroupBox('🌿 Preferências de Cultivo')
        group_prefs.setStyleSheet(group_drive.styleSheet())
        prefs_layout = QFormLayout(group_prefs)
        prefs_layout.setSpacing(14)

        from PyQt6.QtWidgets import QSpinBox
        self.spin_water_interval = QSpinBox()
        self.spin_water_interval.setRange(1, 30)
        self.spin_water_interval.setSuffix(' dias')
        self.spin_water_interval.setValue(3)
        self.spin_water_interval.setToolTip(
            'Usado para plantas novas sem histórico de rega suficiente.'
        )

        lbl_interval_help = QLabel(
            'Intervalo padrão para plantas sem histórico (mínimo 3 regas para cálculo automático).'
        )
        lbl_interval_help.setStyleSheet('color: #4a6b4e; font-size: 11px;')
        lbl_interval_help.setWordWrap(True)

        btn_save_prefs = make_primary_btn('💾 Salvar Preferências')
        btn_save_prefs.clicked.connect(self._save_preferences)

        prefs_layout.addRow(field_label('Intervalo de rega padrão'), self.spin_water_interval)
        prefs_layout.addRow('', lbl_interval_help)
        prefs_layout.addRow('', btn_save_prefs)

        root.addWidget(group_prefs)
        group_about = QGroupBox('ℹ Sobre')
        group_about.setStyleSheet(group_drive.styleSheet())
        about_layout = QVBoxLayout(group_about)
        about_layout.setSpacing(6)

        for text in [
            '🌿  GrowLog v1.2.0',
            '🐍  Python + PyQt6 + Peewee',
            '☁   Google Drive API v3',
        ]:
            lbl = QLabel(text)
            lbl.setStyleSheet('color: #7a9e7e; font-size: 12px;')
            about_layout.addWidget(lbl)

        root.addWidget(group_about)
        root.addStretch()

        # Estado inicial dos botões
        self._set_connected(False)

        # Controle interno do timer
        self._timer_running = False

    # ─── Estado da UI ─────────────────────────────────────────────────────────

    def _set_connected(self, connected: bool):
        self.lbl_status.setText('✓ Conectado' if connected else 'Não conectado')
        self.lbl_status.setObjectName('badge_green' if connected else 'badge_amber')
        self.lbl_status.style().unpolish(self.lbl_status)
        self.lbl_status.style().polish(self.lbl_status)
        self.btn_auth.setText('✓ Reconectar' if connected else '🔑 Conectar conta Google')
        self.btn_upload.setEnabled(connected)
        self.btn_download.setEnabled(connected)
        self.btn_sync_now.setEnabled(connected)
        self.btn_toggle_timer.setEnabled(connected)
        self.combo_interval.setEnabled(connected)

    def set_authenticated(self, authenticated: bool):
        self._set_connected(authenticated)

    def set_interval_options(self, options: list, current: str):
        self.combo_interval.blockSignals(True)
        self.combo_interval.clear()
        for opt in options:
            self.combo_interval.addItem(opt)
        idx = self.combo_interval.findText(current)
        if idx >= 0:
            self.combo_interval.setCurrentIndex(idx)
        self.combo_interval.blockSignals(False)

    def set_timer_running(self, running: bool):
        self._timer_running = running
        self.lbl_timer.setText('🟢 Ativo' if running else '⚫ Inativo')
        self.btn_toggle_timer.setText('⏸ Pausar' if running else '▶ Iniciar')

    def set_last_sync(self, message: str):
        self.lbl_last_sync.setText(f'Último sync: {message}')

    # ─── Ações ────────────────────────────────────────────────────────────────

    def _toggle_timer(self):
        if self._timer_running:
            self.set_timer_running(False)
            # Emite sinal para o main parar o timer
            self.interval_changed.emit('__stop__')
        else:
            self.set_timer_running(True)
            self.interval_changed.emit(self.combo_interval.currentText())

    def _confirm_download(self):
        reply = QMessageBox.question(
            self,
            'Confirmar Download',
            'Baixar o banco do Drive vai SUBSTITUIR os dados locais.\n'
            'Um backup local (.db.bak) será criado automaticamente.\n\n'
            'Deseja continuar?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.request_download.emit()

    def _save_preferences(self):
        interval = self.spin_water_interval.value()
        self.preferences_saved.emit(interval)
        QMessageBox.information(self, 'Salvo', '✅ Preferências salvas!')

    def load_preferences(self, watering_interval: int):
        self.spin_water_interval.setValue(watering_interval)

    def refresh(self):
        pass  # Não precisa recarregar dados do banco
