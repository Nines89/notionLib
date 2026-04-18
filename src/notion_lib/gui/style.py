"""
gui/style.py
Stylesheet globale dell'applicazione.
Un unico posto da modificare per cambiare look & feel.
"""

# Palette colori
C_BG          = "#111827"     # sfondo principale (più chiaro)
C_SURFACE     = "#1A2438"     # superfici card/groupbox
C_BORDER      = "#344866"     # bordi leggeri
C_BORDER_SOFT = "#27364E"     # bordi secondari
C_ACCENT      = "#22D3EE"     # cyan moderno
C_ACCENT_HO   = "#06B6D4"     # hover accent
C_ACCENT_SOFT = "#163648"     # focus delicato
C_DANGER      = "#F87171"     # rosso rimozione
C_SUCCESS     = "#34D399"     # verde ok
C_TEXT        = "#E8EEF9"     # testo principale
C_MUTED       = "#97A3BA"     # testo secondario
C_SIDEBAR     = "#162033"     # sfondo sidebar
C_HOVER       = "#23324C"     # hover generico
C_SEL         = "#214158"     # sfondo selezione/focus


STYLESHEET = f"""

/* ─── Finestra & sfondo ─────────────────────────────────────────── */

QMainWindow, QWidget {{
    background-color: {C_BG};
    color: {C_TEXT};
    font-family: "Segoe UI", "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
}}

#ContentArea {{
    background-color: #121B2C;
}}


/* ─── Sidebar ────────────────────────────────────────────────────── */

#Sidebar {{
    background-color: {C_SIDEBAR};
    border-right: 1px solid {C_BORDER_SOFT};
    border-radius: 0px;
}}


/* ─── Tab widget ──────────────────────────────────────────────────── */

QTabWidget::pane {{
    border: 1px solid {C_BORDER};
    border-radius: 14px;
    background: {C_SURFACE};
    padding: 10px;
}}

QTabBar::tab {{
    background: {C_HOVER};
    color: {C_MUTED};
    padding: 9px 18px;
    margin-right: 6px;
    border: 1px solid {C_BORDER};
    border-radius: 10px;
    font-size: 13px;
    font-weight: 600;
}}

QTabBar::tab:selected {{
    color: {C_ACCENT};
    border: 1px solid #356277;
    background: {C_ACCENT_SOFT};
}}

QTabBar::tab:hover:!selected {{
    color: {C_TEXT};
    background: #273B5A;
    border-color: #4A6B93;
}}


/* ─── GroupBox ────────────────────────────────────────────────────── */

QGroupBox {{
    background-color: {C_SURFACE};
    border: 1px solid {C_BORDER};
    border-radius: 12px;
    margin-top: 16px;
    padding: 18px 16px 16px 16px;
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
    background-color: {C_SURFACE};
    color: {C_TEXT};
    border: 1px solid {C_BORDER};
    border-radius: 10px;
    padding: 7px 14px;
    font-size: 13px;
    font-weight: 600;
    min-height: 28px;
}}

QPushButton:hover {{
    background-color: {C_HOVER};
    border-color: #D6DDEA;
}}

QPushButton:pressed {{
    background-color: #21314F;
}}

QPushButton:disabled {{
    color: {C_MUTED};
    background-color: {C_HOVER};
    border-color: {C_BORDER};
}}

/* Pulsante primario (Connetti, Genera, Esegui) */
QPushButton#PrimaryBtn {{
    background-color: {C_ACCENT};
    color: #07121E;
    border: 1px solid {C_ACCENT};
    font-weight: 600;
}}

QPushButton#PrimaryBtn:hover {{
    background-color: {C_ACCENT_HO};
}}

QPushButton#PrimaryBtn:disabled {{
    background-color: #2F7986;
    color: #0D1B2B;
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
    background-color: #351A28;
    border-radius: 4px;
}}


/* ─── Input ───────────────────────────────────────────────────────── */

QLineEdit, QTextEdit, QDoubleSpinBox {{
    background-color: {C_SURFACE};
    border: 1px solid {C_BORDER};
    border-radius: 10px;
    padding: 6px 10px;
    color: {C_TEXT};
    selection-background-color: {C_SEL};
}}

QLineEdit:focus, QTextEdit:focus, QDoubleSpinBox:focus {{
    border: 1.5px solid {C_ACCENT};
    background-color: #1C2B44;
}}

QLineEdit::placeholder {{
    color: {C_MUTED};
}}


/* ─── ComboBox ────────────────────────────────────────────────────── */

QComboBox {{
    background-color: {C_SURFACE};
    border: 1px solid {C_BORDER};
    border-radius: 10px;
    padding: 5px 10px;
    color: {C_TEXT};
    min-height: 28px;
}}

QComboBox:hover {{
    border-color: #40628E;
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
    border-radius: 12px;
    alternate-background-color: #141D31;
    outline: none;
}}

QTreeWidget::item {{
    padding: 7px 6px;
    border-radius: 6px;
}}

QTreeWidget::item:selected {{
    background-color: {C_SEL};
    color: {C_TEXT};
}}

QTreeWidget::item:hover {{
    background-color: {C_HOVER};
}}

QHeaderView::section {{
    background-color: #162135;
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
    background: #355179;
    border-radius: 4px;
    min-height: 24px;
}}

QScrollBar::handle:vertical:hover {{
    background: #4A6C9C;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    height: 8px;
    background: transparent;
}}

QScrollBar::handle:horizontal {{
    background: #355179;
    border-radius: 4px;
    min-width: 24px;
}}


/* ─── Label ───────────────────────────────────────────────────────── */

QLabel {{
    background: transparent;
    color: {C_TEXT};
}}

QLabel#Title {{
    font-size: 22px;
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
    background-color: #0D1628;
    border-top: 1px solid {C_BORDER_SOFT};
    color: {C_MUTED};
    font-size: 12px;
    padding: 2px 8px;
}}


/* ─── Splitter ────────────────────────────────────────────────────── */

QSplitter::handle {{
    background: {C_BORDER_SOFT};
    width: 1px;
}}

"""


def apply(app):
    """Applica lo stylesheet globale a QApplication."""
    app.setStyleSheet(STYLESHEET)
