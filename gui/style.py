"""
gui/style.py
Stylesheet globale dell'applicazione.
Un unico posto da modificare per cambiare look & feel.
"""

# Palette colori
C_BG          = "#F4F6FB"     # sfondo principale
C_SURFACE     = "#FFFFFF"     # superfici card/groupbox
C_BORDER      = "#E4E9F2"     # bordi leggeri
C_BORDER_SOFT = "#EEF2F9"     # bordi secondari
C_ACCENT      = "#4F46E5"     # indigo moderno
C_ACCENT_HO   = "#4338CA"     # hover accent
C_ACCENT_SOFT = "#EEF0FF"     # pill/focus delicato
C_DANGER      = "#DC4A56"     # rosso rimozione
C_SUCCESS     = "#1B9C62"     # verde ok
C_TEXT        = "#151B2C"     # testo principale
C_MUTED       = "#6D7487"     # testo secondario
C_SIDEBAR     = "#EEF2F9"     # sfondo sidebar
C_HOVER       = "#F3F6FC"     # hover generico
C_SEL         = "#E8ECFF"     # sfondo selezione/focus


STYLESHEET = f"""

/* ─── Finestra & sfondo ─────────────────────────────────────────── */

QMainWindow, QWidget {{
    background-color: {C_BG};
    color: {C_TEXT};
    font-family: "Segoe UI", "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
}}

#ContentArea {{
    background-color: transparent;
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
    padding: 8px;
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
    border: 1px solid #D9DEFE;
    background: {C_ACCENT_SOFT};
}}

QTabBar::tab:hover:!selected {{
    color: {C_TEXT};
    background: #F8FAFF;
    border-color: #DDE3EF;
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
    background-color: #E9EEF8;
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
    border: 1px solid {C_ACCENT};
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
    border-radius: 10px;
    padding: 6px 10px;
    color: {C_TEXT};
    selection-background-color: {C_SEL};
}}

QLineEdit:focus, QTextEdit:focus, QDoubleSpinBox:focus {{
    border: 1.5px solid {C_ACCENT};
    background-color: #FBFCFF;
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
    border-radius: 12px;
    alternate-background-color: #FAFBFE;
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
    background-color: #F8FAFF;
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
    background: #CCD5E6;
    border-radius: 4px;
    min-height: 24px;
}}

QScrollBar::handle:vertical:hover {{
    background: #B3C0D9;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    height: 8px;
    background: transparent;
}}

QScrollBar::handle:horizontal {{
    background: #CCD5E6;
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
    background-color: #F8FAFF;
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
