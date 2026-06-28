"""
gui/widgets/custom_automation_dialog.py

Dialog per configurare una nuova automazione personalizzata:
  1. Nome e icona emoji
  2. Descrizione
  3. Gradiente tile (preset)
  4. Selezione oggetti da importare nel template (checklist)
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QComboBox, QTextEdit,
    QWidget, QGroupBox, QScrollArea, QMessageBox, QFrame,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from notion_lib.gui.logic.custom_automation_manager import (
    AVAILABLE_OBJECTS,
    GRADIENT_PRESETS,
)


class _GradientPreview(QWidget):
    """Piccolo rettangolo che mostra l'anteprima del gradiente selezionato."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 36)
        self._start = "#6366F1"
        self._end = "#8B5CF6"

    def set_gradient(self, start: str, end: str):
        self._start = start
        self._end = end
        self.setStyleSheet(
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
            f"stop:0 {start}, stop:1 {end}); "
            f"border-radius: 8px;"
        )


class CustomAutomationDialog(QDialog):
    """
    Dialog per creare una nuova automazione personalizzata.

    Dopo accept(), usa get_config() per recuperare i dati.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nuova automazione personalizzata")
        self.resize(580, 640)
        self._checkboxes: dict[str, QCheckBox] = {}
        self._build_ui()

    # ── Build UI ──────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        # Header
        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
            "stop:0 #1E1B4B, stop:1 #1E3A5F); "
            "border-bottom: 1px solid #334155;"
        )
        hl = QHBoxLayout(header)
        hl.setContentsMargins(24, 0, 24, 0)
        title = QLabel("✨  Nuova automazione personalizzata")
        title.setStyleSheet(
            "font-size: 16px; font-weight: 700; color: #E8EEF9;"
        )
        hl.addWidget(title)
        root.addWidget(header)

        # Scroll area per il form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        content = QWidget()
        lay = QVBoxLayout(content)
        lay.setContentsMargins(28, 24, 28, 24)
        lay.setSpacing(20)

        # ── Sezione 1: Identità ───────────────────────────────────
        identity_box = QGroupBox("Identità")
        ib_lay = QVBoxLayout(identity_box)
        ib_lay.setSpacing(10)

        # Nome + emoji su una riga
        row1 = QWidget()
        r1l = QHBoxLayout(row1)
        r1l.setContentsMargins(0, 0, 0, 0)
        r1l.setSpacing(12)

        emoji_col = QWidget()
        ec = QVBoxLayout(emoji_col)
        ec.setContentsMargins(0, 0, 0, 0)
        ec.setSpacing(4)
        ec.addWidget(self._label("Icona (emoji)"))
        self._icon_input = QLineEdit("⚙️")
        self._icon_input.setFixedWidth(70)
        self._icon_input.setFixedHeight(36)
        self._icon_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon_input.setStyleSheet("font-size: 20px;")
        ec.addWidget(self._icon_input)
        r1l.addWidget(emoji_col)

        name_col = QWidget()
        nc = QVBoxLayout(name_col)
        nc.setContentsMargins(0, 0, 0, 0)
        nc.setSpacing(4)
        nc.addWidget(self._label("Nome automazione *"))
        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("Es: Archivia pagine vecchie")
        self._name_input.setFixedHeight(36)
        nc.addWidget(self._name_input)
        r1l.addWidget(name_col, stretch=1)

        ib_lay.addWidget(row1)

        ib_lay.addWidget(self._label("Descrizione"))
        self._desc_input = QTextEdit()
        self._desc_input.setPlaceholderText(
            "Descrivi brevemente cosa fa questa automazione…"
        )
        self._desc_input.setMaximumHeight(72)
        ib_lay.addWidget(self._desc_input)

        lay.addWidget(identity_box)

        # ── Sezione 2: Gradiente tile ─────────────────────────────
        gradient_box = QGroupBox("Colore tile")
        gb_lay = QVBoxLayout(gradient_box)
        gb_lay.setSpacing(10)

        row2 = QWidget()
        r2l = QHBoxLayout(row2)
        r2l.setContentsMargins(0, 0, 0, 0)
        r2l.setSpacing(16)

        self._gradient_combo = QComboBox()
        self._gradient_combo.setFixedHeight(36)
        for preset in GRADIENT_PRESETS:
            self._gradient_combo.addItem(preset["label"], preset)
        self._gradient_combo.currentIndexChanged.connect(self._on_gradient_changed)

        self._gradient_preview = _GradientPreview()
        self._on_gradient_changed(0)

        r2l.addWidget(self._gradient_combo, stretch=1)
        r2l.addWidget(self._gradient_preview)
        gb_lay.addWidget(row2)

        lay.addWidget(gradient_box)

        # ── Sezione 3: Oggetti da importare ───────────────────────
        objects_box = QGroupBox("Oggetti da importare nel template")
        ob_lay = QVBoxLayout(objects_box)
        ob_lay.setSpacing(6)

        hint = QLabel(
            "Seleziona gli oggetti che utilizzerai. "
            "Verranno aggiunti gli import e del codice d'esempio nel template."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #94A3B8; font-size: 11px;")
        ob_lay.addWidget(hint)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #334155;")
        ob_lay.addWidget(sep)

        for key, meta in AVAILABLE_OBJECTS.items():
            row = QWidget()
            rl = QHBoxLayout(row)
            rl.setContentsMargins(4, 2, 4, 2)
            rl.setSpacing(10)

            chk = QCheckBox(meta["label"])
            chk.setFixedHeight(26)
            self._checkboxes[key] = chk

            desc = QLabel(meta["description"])
            desc.setStyleSheet("color: #64748B; font-size: 11px;")

            rl.addWidget(chk)
            rl.addWidget(desc, stretch=1)
            ob_lay.addWidget(row)

        lay.addWidget(objects_box)
        lay.addStretch()

        scroll.setWidget(content)
        root.addWidget(scroll, stretch=1)

        # Footer pulsanti
        footer = QWidget()
        footer.setFixedHeight(56)
        footer.setStyleSheet(
            "background: #0F172A; border-top: 1px solid #1E293B;"
        )
        fl = QHBoxLayout(footer)
        fl.setContentsMargins(24, 0, 24, 0)
        fl.setSpacing(10)

        cancel_btn = QPushButton("Annulla")
        cancel_btn.setFixedHeight(36)
        cancel_btn.clicked.connect(self.reject)

        self._create_btn = QPushButton("✓ Crea automazione")
        self._create_btn.setObjectName("PrimaryBtn")
        self._create_btn.setFixedHeight(36)
        self._create_btn.setDefault(True)
        self._create_btn.clicked.connect(self._on_create)

        fl.addStretch()
        fl.addWidget(cancel_btn)
        fl.addWidget(self._create_btn)
        root.addWidget(footer)

    # ── Slot ──────────────────────────────────────────────────────────────────

    def _on_gradient_changed(self, _index: int):
        preset = self._gradient_combo.currentData()
        if preset:
            self._gradient_preview.set_gradient(preset["start"], preset["end"])

    def _on_create(self):
        name = self._name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Nome mancante", "Inserisci il nome dell'automazione.")
            return

        selected = [k for k, chk in self._checkboxes.items() if chk.isChecked()]
        # Non obbligatorio avere oggetti selezionati, ma avvisiamo
        if not selected:
            reply = QMessageBox.question(
                self,
                "Nessun oggetto selezionato",
                "Non hai selezionato nessun oggetto da importare.\n"
                "Il template sarà quasi vuoto. Vuoi procedere?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        self.accept()

    # ── Getter pubblici ───────────────────────────────────────────────────────

    def get_config(self) -> dict:
        """
        Restituisce la configurazione inserita dall'utente.
        Da chiamare solo dopo accept().
        """
        preset = self._gradient_combo.currentData() or GRADIENT_PRESETS[0]
        return {
            "name":             self._name_input.text().strip(),
            "icon":             self._icon_input.text().strip() or "⚙️",
            "description":      self._desc_input.toPlainText().strip(),
            "gradient_start":   preset["start"],
            "gradient_end":     preset["end"],
            "selected_objects": [k for k, chk in self._checkboxes.items() if chk.isChecked()],
        }

    # ── Helper ────────────────────────────────────────────────────────────────

    @staticmethod
    def _label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(
            "font-size: 11px; font-weight: 700; color: #94A3B8; "
            "letter-spacing: 0.3px;"
        )
        return lbl
