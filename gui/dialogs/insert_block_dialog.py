"""
Dialog dinamico per inserire blocchi in una pagina Notion.
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QLineEdit,
    QCheckBox,
    QFormLayout,
    QWidget,
    QPushButton,
)

from utils.constants import NColors, NLanguage
from gui.logic.block_inserter import BLOCK_DEFINITIONS


class InsertBlockDialog(QDialog):
    def __init__(self, page_id: str, parent=None):
        super().__init__(parent)
        self.page_id = page_id
        self._field_widgets: dict[str, QWidget] = {}

        self.setWindowTitle("Inserisci blocco")
        self.setMinimumWidth(480)

        self._build_ui()
        self._rebuild_dynamic_fields()

    @property
    def selected_block_key(self) -> str:
        return self._type_combo.currentData()

    def selected_values(self) -> dict:
        values = {}
        for key, widget in self._field_widgets.items():
            if isinstance(widget, QLineEdit):
                values[key] = widget.text().strip()
            elif isinstance(widget, QComboBox):
                values[key] = widget.currentData()
            elif isinstance(widget, QCheckBox):
                values[key] = widget.isChecked()
        return values

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setSpacing(12)

        subtitle = QLabel(f"Pagina target: {self.page_id}")
        subtitle.setStyleSheet("color: #97A8C7; font-size: 11px;")
        lay.addWidget(subtitle)

        row = QHBoxLayout()
        row.addWidget(QLabel("Tipo blocco:"))
        self._type_combo = QComboBox()
        for key, cfg in BLOCK_DEFINITIONS.items():
            self._type_combo.addItem(f"{cfg['icon']}  {cfg['label']}", key)
        self._type_combo.currentIndexChanged.connect(self._rebuild_dynamic_fields)
        row.addWidget(self._type_combo, 1)
        lay.addLayout(row)

        self._fields_host = QWidget()
        self._fields_form = QFormLayout(self._fields_host)
        self._fields_form.setContentsMargins(0, 0, 0, 0)
        self._fields_form.setSpacing(8)
        lay.addWidget(self._fields_host)

        btns = QHBoxLayout()
        btns.addStretch()
        cancel = QPushButton("Annulla")
        ok = QPushButton("Inserisci")
        cancel.clicked.connect(self.reject)
        ok.clicked.connect(self.accept)
        btns.addWidget(cancel)
        btns.addWidget(ok)
        lay.addLayout(btns)

    def _rebuild_dynamic_fields(self):
        while self._fields_form.rowCount() > 0:
            self._fields_form.removeRow(0)
        self._field_widgets.clear()

        key = self.selected_block_key
        definition = BLOCK_DEFINITIONS.get(key, {})
        for field in definition.get("fields", []):
            widget = self._make_widget_for_field(field)
            self._field_widgets[field["name"]] = widget
            self._fields_form.addRow(field["label"] + ":", widget)

    @staticmethod
    def _make_widget_for_field(field: dict) -> QWidget:
        ftype = field.get("type")

        if ftype == "text":
            w = QLineEdit()
            w.setPlaceholderText("Inserisci testo…")
            return w

        if ftype == "color":
            w = QComboBox()
            for c in NColors:
                w.addItem(c.value, c.value)
            return w

        if ftype == "bool":
            return QCheckBox()

        if ftype == "language":
            w = QComboBox()
            for lang in NLanguage:
                w.addItem(lang.value, lang.value)
            return w

        # fallback sicuro
        return QLineEdit()
