"""
gui/style.py
Stylesheet globale dell'applicazione.
Un unico posto da modificare per cambiare look & feel.
"""

# Palette colori
C_BG        = "#F7F7F5"       # sfondo principale (bianco caldo)
C_SURFACE   = "#FFFFFF"       # superfici card/groupbox
C_BORDER    = "#E3E2DE"       # bordi leggeri
C_ACCENT    = "#2F80ED"       # blu azione (pulsanti primari)
C_ACCENT_HO = "#1A6DD4"       # hover accent
C_DANGER    = "#EB5757"       # rosso rimozione
C_SUCCESS   = "#27AE60"       # verde ok
C_TEXT      = "#1A1A1A"       # testo principale
C_MUTED     = "#787774"       # testo secondario
C_SIDEBAR   = "#F0EFEC"       # sfondo sidebar
C_HOVER     = "#EBEBEA"       # hover generico
C_SEL       = "#E8F0FD"       # sfondo selezione/focus


STYLESHEET = f"""

/* ─── Finestra & sfondo ─────────────────────────────────────────── */

QMainWindow, QWidget {{
    background-color: {C_BG};
    color: {C_TEXT};
    font-family: "Segoe UI", "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
}}


/* ─── Sidebar ────────────────────────────────────────────────────── */

#Sidebar {{
    background-color: {C_SIDEBAR};
    border-right: 1px solid {C_BORDER};
    border-radius: 0px;
}}


/* ─── Tab widget ──────────────────────────────────────────────────── */

QTabWidget::pane {{
    border: 1px solid {C_BORDER};
    border-radius: 8px;
    background: {C_SURFACE};
    padding: 4px;
}}

QTabBar::tab {{
    background: transparent;
    color: {C_MUTED};
    padding: 8px 20px;
    margin-right: 2px;
    border-bottom: 2px solid transparent;
    font-size: 13px;
    font-weight: 500;
}}

QTabBar::tab:selected {{
    color: {C_ACCENT};
    border-bottom: 2px solid {C_ACCENT};
    background: transparent;
}}

QTabBar::tab:hover:!selected {{
    color: {C_TEXT};
    background: {C_HOVER};
    border-radius: 6px 6px 0 0;
}}


/* ─── GroupBox ────────────────────────────────────────────────────── */

QGroupBox {{
    background-color: {C_SURFACE};
    border: 1px solid {C_BORDER};
    border-radius: 8px;
    margin-top: 14px;
    padding: 16px 14px 14px 14px;
    font-weight: 600;
    font-size: 12px;
    color: {C_MUTED};
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    top: -1px;
    padding: 0 6px;
    background-color: {C_BG};
    color: {C_MUTED};
    font-size: 11px;
    font-weight: 600;
}}


/* ─── Pulsanti ────────────────────────────────────────────────────── */

QPushButton {{
    background-color: {C_HOVER};
    color: {C_TEXT};
    border: 1px solid {C_BORDER};
    border-radius: 6px;
    padding: 6px 14px;
    font-size: 13px;
    font-weight: 500;
    min-height: 28px;
}}

QPushButton:hover {{
    background-color: {C_BORDER};
}}

QPushButton:pressed {{
    background-color: #D8D7D3;
}}

QPushButton:disabled {{
    color: {C_MUTED};
    background-color: {C_HOVER};
    border-color: {C_BORDER};
}}

/* Pulsante primario (Connetti, Genera, Esegui) */
QPushButton#PrimaryBtn {{
    background-color: {C_ACCENT};
    color: white;
    border: none;
    font-weight: 600;
}}

QPushButton#PrimaryBtn:hover {{
    background-color: {C_ACCENT_HO};
}}

QPushButton#PrimaryBtn:disabled {{
    background-color: #A8C4E8;
    color: white;
}}

/* Pulsante rimozione ✕ */
QPushButton#RemoveBtn {{
    background-color: transparent;
    border: none;
    color: {C_MUTED};
    font-size: 14px;
    padding: 2px 6px;
    min-height: 24px;
}}

QPushButton#RemoveBtn:hover {{
    color: {C_DANGER};
    background-color: #FDF0F0;
    border-radius: 4px;
}}


/* ─── Input ───────────────────────────────────────────────────────── */

QLineEdit, QTextEdit, QDoubleSpinBox {{
    background-color: {C_SURFACE};
    border: 1px solid {C_BORDER};
    border-radius: 6px;
    padding: 6px 10px;
    color: {C_TEXT};
    selection-background-color: {C_SEL};
}}

QLineEdit:focus, QTextEdit:focus, QDoubleSpinBox:focus {{
    border: 1.5px solid {C_ACCENT};
    background-color: {C_SURFACE};
}}

QLineEdit::placeholder {{
    color: {C_MUTED};
}}


/* ─── ComboBox ────────────────────────────────────────────────────── */

QComboBox {{
    background-color: {C_SURFACE};
    border: 1px solid {C_BORDER};
    border-radius: 6px;
    padding: 5px 10px;
    color: {C_TEXT};
    min-height: 28px;
}}

QComboBox:hover {{
    border-color: #BDBDBD;
}}

QComboBox:focus {{
    border: 1.5px solid {C_ACCENT};
}}

QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid {C_MUTED};
    margin-right: 6px;
}}

QComboBox QAbstractItemView {{
    background-color: {C_SURFACE};
    border: 1px solid {C_BORDER};
    border-radius: 6px;
    selection-background-color: {C_SEL};
    selection-color: {C_TEXT};
    padding: 4px;
}}


/* ─── Tree / List ─────────────────────────────────────────────────── */

QTreeWidget {{
    background-color: {C_SURFACE};
    border: 1px solid {C_BORDER};
    border-radius: 8px;
    alternate-background-color: #FAFAF8;
    outline: none;
}}

QTreeWidget::item {{
    padding: 5px 4px;
    border-radius: 4px;
}}

QTreeWidget::item:selected {{
    background-color: {C_SEL};
    color: {C_TEXT};
}}

QTreeWidget::item:hover {{
    background-color: {C_HOVER};
}}

QHeaderView::section {{
    background-color: {C_BG};
    border: none;
    border-bottom: 1px solid {C_BORDER};
    padding: 6px 8px;
    font-weight: 600;
    font-size: 12px;
    color: {C_MUTED};
}}


/* ─── ScrollArea / ScrollBar ──────────────────────────────────────── */

QScrollArea {{
    border: none;
    background: transparent;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: {C_BORDER};
    border-radius: 4px;
    min-height: 24px;
}}

QScrollBar::handle:vertical:hover {{
    background: #BDBDBD;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    height: 8px;
    background: transparent;
}}

QScrollBar::handle:horizontal {{
    background: {C_BORDER};
    border-radius: 4px;
    min-width: 24px;
}}


/* ─── Label ───────────────────────────────────────────────────────── */

QLabel {{
    background: transparent;
    color: {C_TEXT};
}}

QLabel#Title {{
    font-size: 20px;
    font-weight: 700;
    color: {C_TEXT};
    padding-bottom: 4px;
}}

QLabel#Muted {{
    color: {C_MUTED};
    font-size: 12px;
}}

QLabel#Success {{
    color: {C_SUCCESS};
    font-weight: 600;
}}

QLabel#Error {{
    color: {C_DANGER};
    font-size: 12px;
}}


/* ─── Radio button ────────────────────────────────────────────────── */

QRadioButton {{
    spacing: 6px;
    color: {C_TEXT};
}}

QRadioButton::indicator {{
    width: 16px;
    height: 16px;
    border-radius: 8px;
    border: 2px solid {C_BORDER};
    background: {C_SURFACE};
}}

QRadioButton::indicator:checked {{
    background: {C_ACCENT};
    border-color: {C_ACCENT};
}}


/* ─── StatusBar ───────────────────────────────────────────────────── */

QStatusBar {{
    background-color: {C_SIDEBAR};
    border-top: 1px solid {C_BORDER};
    color: {C_MUTED};
    font-size: 12px;
    padding: 2px 8px;
}}


/* ─── Splitter ────────────────────────────────────────────────────── */

QSplitter::handle {{
    background: {C_BORDER};
    width: 1px;
}}

"""


def apply(app):
    """Applica lo stylesheet globale a QApplication."""
    app.setStyleSheet(STYLESHEET)
