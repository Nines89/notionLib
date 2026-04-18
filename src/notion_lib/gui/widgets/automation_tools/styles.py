from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel


# --- CONFIGURAZIONE DESIGN SYSTEM ---
STYLESHEET = """
/* ... (resto del codice precedente) ... */

QComboBox, QLineEdit {
    background-color: #1E293B; /* Leggermente più chiaro dello sfondo card per contrasto */
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 6px 12px;
    color: #F1F5F9;
    font-size: 13px;
    min-height: 32px; /* Garantisce che il testo non venga tagliato */
}

QComboBox:hover, QLineEdit:focus {
    border: 1px solid #6366F1;
    background-color: #262F45;
}

/* Gestione specifica del menu a tendina della Combo */
QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox::down-arrow {
    image: none; /* Rimuoviamo la freccia standard brutta */
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #94A3B8; /* Freccia minimalista */
    margin-right: 10px;
}

/* Questo è fondamentale per la leggibilità del testo dentro le combo */
QComboBox QAbstractItemView {
    background-color: #1E293B;
    border: 1px solid #334155;
    selection-background-color: #6366F1;
    selection-color: white;
    outline: none;
    padding: 4px;
}

/* Stile per il bottone "Aggiungi filtro" */
QPushButton#AddFilterBtn {
    background-color: rgba(99, 102, 241, 0.1);
    border: 1px dashed #6366F1;
    color: #818CF8;
    border-radius: 8px;
    padding: 10px;
    font-weight: 600;
}

QPushButton#AddFilterBtn:hover {
    background-color: rgba(99, 102, 241, 0.2);
    color: #A5B4FC;
}
"""

cp_ds_sections = "color: #6366F1; font-weight: bold;"

class _SectionCard(QFrame):
    def __init__(self, icon: str, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(30, 30, 30, 30)  # Padding interno generoso
        self._layout.setSpacing(20)

        header = QHBoxLayout()
        header.setSpacing(12)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 18px; background: transparent;")

        title_lbl = QLabel(title)
        title_lbl.setObjectName("SectionTitle")

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #2D3748; max-height: 1px;")

        header.addWidget(icon_lbl)
        header.addWidget(title_lbl)
        header.addWidget(line, 1)

        self._layout.addLayout(header)

    def add_content(self, widget):
        self._layout.addWidget(widget)