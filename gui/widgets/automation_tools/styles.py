"""Stili condivisi per i tool di automazione."""

CARD_STYLE = """
QGroupBox {
    background: #FFFFFF;
    border: 2px solid #E2E8F0;
    border-radius: 12px;
    padding: 20px 16px 16px 16px;
    margin-top: 8px;
}
"""

LINE_EDIT_STYLE = """
QLineEdit {
    border: 2px solid #E2E8F0;
    border-radius: 8px;
    padding: 0 12px;
    font-size: 14px;
    background: #FFFFFF;
}
QLineEdit:focus {
    border-color: #3B82F6;
}
"""

COMBO_STYLE = """
QComboBox {
    border: 2px solid #E2E8F0;
    border-radius: 8px;
    padding: 0 12px;
    background: #FFFFFF;
    font-size: 14px;
}
QComboBox:hover {
    border-color: #CBD5E1;
}
QComboBox::drop-down {
    border: none;
    width: 30px;
}
"""

PRIMARY_BUTTON_STYLE = """
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #3B82F6, stop:1 #2563EB);
    border: none;
    border-radius: 10px;
    color: #FFFFFF;
    font-size: 14px;
    font-weight: 700;
}
QPushButton:hover:enabled {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #2563EB, stop:1 #1D4ED8);
}
QPushButton:disabled {
    background: #E2E8F0;
    color: #94A3B8;
}
"""

SECONDARY_BUTTON_STYLE = """
QPushButton {
    background: #F1F5F9;
    border: 2px solid #CBD5E1;
    border-radius: 10px;
    color: #475569;
    font-size: 14px;
    font-weight: 600;
}
QPushButton:hover:enabled {
    background: #E2E8F0;
    border-color: #94A3B8;
}
QPushButton:disabled {
    background: #F8FAFC;
    color: #CBD5E1;
}
"""

DARK_CODE_STYLE = """
QTextEdit {
    background: #1E293B;
    color: #E2E8F0;
    border: none;
    border-radius: 8px;
    padding: 14px;
    font-family: 'Consolas', 'Monaco', monospace;
}
"""

LOG_STYLE = """
QTextEdit {
    background: #F8FAFC;
    border: 2px solid #E2E8F0;
    border-radius: 8px;
    padding: 12px;
    color: #334155;
}
"""
