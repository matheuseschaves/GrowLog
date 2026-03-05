"""
GrowLog — Tema escuro em QSS (Qt Style Sheets)
"""

DARK_THEME = """
/* ── Globals ─────────────────────────────────────────── */
QWidget {
    background-color: #0d1a0e;
    color: #d4e8d5;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}

QMainWindow {
    background-color: #0d1a0e;
}

/* ── Sidebar ──────────────────────────────────────────── */
#sidebar {
    background-color: #111f12;
    border-right: 1px solid #2a3f2b;
    min-width: 200px;
    max-width: 200px;
}

#app_title {
    font-size: 16px;
    font-weight: bold;
    color: #4caf6e;
    padding: 20px 16px 8px 16px;
}

#app_subtitle {
    font-size: 10px;
    color: #4a6b4e;
    padding: 0px 16px 20px 16px;
    letter-spacing: 2px;
}

/* Botões da sidebar */
#nav_btn {
    background-color: transparent;
    border: none;
    border-radius: 10px;
    padding: 12px 16px;
    text-align: left;
    color: #7a9e7e;
    font-size: 13px;
    margin: 2px 8px;
}

#nav_btn:hover {
    background-color: rgba(76, 175, 110, 0.1);
    color: #d4e8d5;
}

#nav_btn[active="true"] {
    background-color: rgba(76, 175, 110, 0.15);
    color: #4caf6e;
    border-left: 3px solid #4caf6e;
    padding-left: 13px;
}

/* ── Content area ─────────────────────────────────────── */
#content_area {
    background-color: #0d1a0e;
    padding: 24px;
}

#page_title {
    font-size: 22px;
    font-weight: bold;
    color: #d4e8d5;
    margin-bottom: 4px;
}

#page_subtitle {
    font-size: 11px;
    color: #4a6b4e;
    letter-spacing: 1px;
    margin-bottom: 20px;
}

/* ── Cards ────────────────────────────────────────────── */
#card {
    background-color: #1a2b1b;
    border: 1px solid #2a3f2b;
    border-radius: 14px;
    padding: 18px;
}

#card_title {
    font-size: 10px;
    color: #4a6b4e;
    letter-spacing: 2px;
    text-transform: uppercase;
}

#card_value {
    font-size: 28px;
    font-weight: 300;
    color: #d4e8d5;
}

#card_status_ok    { font-size: 11px; color: #4caf6e; }
#card_status_warn  { font-size: 11px; color: #e8a44a; }
#card_status_info  { font-size: 11px; color: #7a9e7e; }

/* ── Buttons ──────────────────────────────────────────── */
QPushButton {
    background-color: #1a2b1b;
    border: 1px solid #2a3f2b;
    border-radius: 10px;
    padding: 10px 18px;
    color: #d4e8d5;
    font-size: 13px;
}

QPushButton:hover {
    background-color: #243d25;
    border-color: #3a5f3b;
}

QPushButton:pressed {
    background-color: #162018;
}

#btn_primary {
    background-color: #4caf6e;
    border: none;
    color: #0d1a0e;
    font-weight: bold;
    border-radius: 10px;
    padding: 10px 20px;
}

#btn_primary:hover {
    background-color: #6dcc8a;
}

#btn_primary:pressed {
    background-color: #3a9558;
}

#btn_danger {
    background-color: transparent;
    border: 1px solid #e05c5c;
    color: #e05c5c;
    border-radius: 10px;
    padding: 8px 16px;
}

#btn_danger:hover {
    background-color: rgba(224, 92, 92, 0.1);
}

#btn_small {
    background-color: rgba(76, 175, 110, 0.12);
    border: 1px solid rgba(76, 175, 110, 0.3);
    border-radius: 8px;
    padding: 5px 12px;
    color: #6dcc8a;
    font-size: 11px;
}

#btn_small:hover {
    background-color: rgba(76, 175, 110, 0.22);
}

/* ── Inputs ───────────────────────────────────────────── */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #1a2b1b;
    border: 1px solid #2a3f2b;
    border-radius: 10px;
    padding: 10px 14px;
    color: #d4e8d5;
    selection-background-color: #4caf6e;
}

QLineEdit:focus, QTextEdit:focus {
    border-color: #4caf6e;
}

QComboBox {
    background-color: #1a2b1b;
    border: 1px solid #2a3f2b;
    border-radius: 10px;
    padding: 10px 14px;
    color: #d4e8d5;
}

QComboBox:focus { border-color: #4caf6e; }

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #1a2b1b;
    border: 1px solid #2a3f2b;
    border-radius: 8px;
    color: #d4e8d5;
    selection-background-color: rgba(76,175,110,0.2);
}

QDoubleSpinBox, QSpinBox {
    background-color: #1a2b1b;
    border: 1px solid #2a3f2b;
    border-radius: 10px;
    padding: 10px 14px;
    color: #d4e8d5;
}

QDoubleSpinBox:focus, QSpinBox:focus { border-color: #4caf6e; }

QDateEdit {
    background-color: #1a2b1b;
    border: 1px solid #2a3f2b;
    border-radius: 10px;
    padding: 10px 14px;
    color: #d4e8d5;
}

QDateEdit:focus { border-color: #4caf6e; }

QDateEdit::drop-down {
    border: none;
    width: 24px;
}

/* ── Tables ───────────────────────────────────────────── */
QTableWidget {
    background-color: #111f12;
    border: 1px solid #2a3f2b;
    border-radius: 12px;
    gridline-color: #1a2b1b;
    color: #d4e8d5;
    selection-background-color: rgba(76,175,110,0.15);
    alternate-background-color: #162018;
}

QTableWidget::item {
    padding: 10px 14px;
    border: none;
}

QTableWidget::item:selected {
    background-color: rgba(76,175,110,0.2);
    color: #d4e8d5;
}

QHeaderView::section {
    background-color: #162018;
    color: #4a6b4e;
    font-size: 10px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 10px 14px;
    border: none;
    border-bottom: 1px solid #2a3f2b;
}

/* ── Calendar ─────────────────────────────────────────── */
QCalendarWidget QWidget {
    background-color: #111f12;
    color: #d4e8d5;
}

QCalendarWidget QAbstractItemView {
    background-color: #111f12;
    selection-background-color: #4caf6e;
    selection-color: #0d1a0e;
    color: #d4e8d5;
}

QCalendarWidget QToolButton {
    background-color: transparent;
    color: #4caf6e;
    border: none;
    border-radius: 6px;
    padding: 4px 8px;
    font-weight: bold;
}

QCalendarWidget QToolButton:hover {
    background-color: rgba(76,175,110,0.15);
}

QCalendarWidget QMenu {
    background-color: #1a2b1b;
    color: #d4e8d5;
    border: 1px solid #2a3f2b;
}

/* ── Scrollbar ────────────────────────────────────────── */
QScrollBar:vertical {
    background: transparent;
    width: 6px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #2a3f2b;
    border-radius: 3px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover { background: #4caf6e; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

/* ── Dialog ───────────────────────────────────────────── */
QDialog {
    background-color: #111f12;
    border: 1px solid #2a3f2b;
    border-radius: 16px;
}

#dialog_title {
    font-size: 18px;
    font-weight: bold;
    color: #d4e8d5;
    margin-bottom: 16px;
}

#field_label {
    font-size: 10px;
    color: #4a6b4e;
    letter-spacing: 1.5px;
}

/* ── Status bar ───────────────────────────────────────── */
QStatusBar {
    background-color: #111f12;
    border-top: 1px solid #2a3f2b;
    color: #4a6b4e;
    font-size: 11px;
    padding: 4px 12px;
}

/* ── Labels ───────────────────────────────────────────── */
#badge_green {
    background-color: rgba(76,175,110,0.12);
    border: 1px solid rgba(76,175,110,0.3);
    border-radius: 10px;
    padding: 3px 10px;
    color: #6dcc8a;
    font-size: 11px;
}

#badge_amber {
    background-color: rgba(232,164,74,0.12);
    border: 1px solid rgba(232,164,74,0.3);
    border-radius: 10px;
    padding: 3px 10px;
    color: #f5c07a;
    font-size: 11px;
}

#separator {
    background-color: #2a3f2b;
    max-height: 1px;
    margin: 8px 0px;
}
"""
