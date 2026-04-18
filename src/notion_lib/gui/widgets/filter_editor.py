"""
gui/widgets/filter_editor.py
FilterRowWidget  — singola riga di filtro
FilterEditor     — contenitore con lista dinamica
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QComboBox,
    QLineEdit, QDoubleSpinBox, QPushButton, QGroupBox, QScrollArea,
)
from PyQt6.QtCore import pyqtSignal, Qt

from src.notion_lib.gui.constants import FILTER_OPS, FILTER_OPS_DEFAULT, NO_VALUE_OPS
from src.notion_lib.gui.state import FilterRow


class FilterRowWidget(QWidget):
    remove_requested = pyqtSignal()

    def __init__(self, columns: list, schema: dict, row: FilterRow, parent=None):
        super().__init__(parent)
        self._schema = schema
        self._row    = row
        self._build_ui(columns)

    def _build_ui(self, columns: list):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 4, 0, 4)
        lay.setSpacing(8)

        self._col_combo = QComboBox()
        self._col_combo.addItems(columns)
        if self._row.col in columns:
            self._col_combo.setCurrentText(self._row.col)
        self._col_combo.setMinimumWidth(160)
        self._col_combo.setFixedHeight(32)
        self._col_combo.currentTextChanged.connect(self._on_col_changed)

        self._op_combo = QComboBox()
        self._op_combo.setMinimumWidth(170)
        self._op_combo.setFixedHeight(32)
        self._op_combo.currentIndexChanged.connect(self._on_op_changed)

        self._text_input = QLineEdit()
        self._text_input.setMinimumWidth(160)
        self._text_input.setFixedHeight(32)
        self._text_input.textChanged.connect(lambda t: setattr(self._row, "val", t))

        self._num_input = QDoubleSpinBox()
        self._num_input.setRange(-1e12, 1e12)
        self._num_input.setDecimals(2)
        self._num_input.setMinimumWidth(160)
        self._num_input.setFixedHeight(32)
        self._num_input.valueChanged.connect(lambda v: setattr(self._row, "val", v))
        self._num_input.hide()

        self._no_val_lbl = QLabel("nessun valore")
        self._no_val_lbl.setStyleSheet("color: #787774; font-style: italic; font-size: 12px;")
        self._no_val_lbl.setMinimumWidth(160)
        self._no_val_lbl.hide()

        rem_btn = QPushButton("✕")
        rem_btn.setObjectName("RemoveBtn")
        rem_btn.setFixedSize(30, 30)
        rem_btn.clicked.connect(self.remove_requested.emit)

        lay.addWidget(self._col_combo)
        lay.addWidget(self._op_combo)
        lay.addWidget(self._text_input)
        lay.addWidget(self._num_input)
        lay.addWidget(self._no_val_lbl)
        lay.addWidget(rem_btn)
        lay.addStretch()

        self._populate_ops()

    def _col_type(self) -> str:
        return self._schema.get(self._col_combo.currentText(), {}).get("type", "rich_text")

    def _populate_ops(self):
        ct  = self._col_type()
        ops = FILTER_OPS.get(ct, FILTER_OPS_DEFAULT)
        self._op_combo.blockSignals(True)
        self._op_combo.clear()
        for label, key in ops:
            self._op_combo.addItem(label, key)
        for i in range(self._op_combo.count()):
            if self._op_combo.itemData(i) == self._row.op:
                self._op_combo.setCurrentIndex(i)
                break
        self._op_combo.blockSignals(False)
        self._update_value_widget()

    def _update_value_widget(self):
        op = self._op_combo.currentData() or ""
        ct = self._col_type()
        self._row.op = op

        if op in NO_VALUE_OPS:
            self._text_input.hide(); self._num_input.hide()
            self._no_val_lbl.show(); self._row.val = None
        elif ct == "number":
            self._text_input.hide(); self._no_val_lbl.hide()
            self._num_input.show()
            try:
                if self._row.val is not None:
                    self._num_input.setValue(float(self._row.val))
            except (TypeError, ValueError):
                pass
        else:
            self._num_input.hide(); self._no_val_lbl.hide()
            self._text_input.show()
            if self._row.val is not None and not isinstance(self._row.val, float):
                self._text_input.setText(str(self._row.val))

    def _on_col_changed(self, col: str):
        self._row.col = col
        self._populate_ops()

    def _on_op_changed(self, _):
        self._update_value_widget()

    def get_row(self) -> FilterRow:
        return self._row


class FilterEditor(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Filtri  (opzionale)", parent)
        self._schema: dict = {}
        self._rows:   list = []
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setSpacing(8)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(200)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        self._container = QWidget()
        self._lay       = QVBoxLayout(self._container)
        self._lay.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._lay.setSpacing(4)
        self._lay.setContentsMargins(0, 0, 0, 0)
        scroll.setWidget(self._container)
        outer.addWidget(scroll)

        self._add_btn = QPushButton("➕  Aggiungi filtro")
        self._add_btn.setEnabled(False)
        self._add_btn.setFixedHeight(32)
        self._add_btn.clicked.connect(self._add_default_row)
        outer.addWidget(self._add_btn)

    def set_schema(self, schema: dict):
        self._schema = schema
        self._clear()
        self._add_btn.setEnabled(bool(schema))

    def get_filter_rows(self) -> list:
        return [w.get_row() for w in self._rows]

    def reset(self):
        self._clear()
        self._schema = {}
        self._add_btn.setEnabled(False)

    def _clear(self):
        for w in self._rows:
            w.setParent(None)
        self._rows.clear()

    def _add_default_row(self):
        cols = list(self._schema.keys())
        if not cols:
            return
        col = cols[0]
        ct  = self._schema.get(col, {}).get("type", "rich_text")
        row = FilterRow(col=col, op=FILTER_OPS.get(ct, FILTER_OPS_DEFAULT)[0][1], val=None)
        self._add_row_widget(row)

    def _add_row_widget(self, row: FilterRow):
        w = FilterRowWidget(list(self._schema.keys()), self._schema, row)
        w.remove_requested.connect(lambda widget=w: self._remove_row(widget))
        self._rows.append(w)
        self._lay.addWidget(w)

    def _remove_row(self, widget):
        if widget in self._rows:
            self._rows.remove(widget)
        widget.setParent(None)
