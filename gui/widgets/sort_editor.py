"""
gui/widgets/sort_editor.py
SortRowWidget + SortEditor
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QComboBox, QPushButton,
    QGroupBox, QScrollArea, QRadioButton, QButtonGroup,
)
from PyQt6.QtCore import pyqtSignal, Qt

from gui.state import SortRow


class SortRowWidget(QWidget):
    remove_requested = pyqtSignal()

    def __init__(self, columns: list, row: SortRow, parent=None):
        super().__init__(parent)
        self._row = row
        self._build_ui(columns)

    def _build_ui(self, columns: list):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 4, 0, 4)
        lay.setSpacing(12)

        self._col_combo = QComboBox()
        self._col_combo.addItems(columns)
        if self._row.col in columns:
            self._col_combo.setCurrentText(self._row.col)
        self._col_combo.setMinimumWidth(200)
        self._col_combo.setFixedHeight(32)
        self._col_combo.currentTextChanged.connect(
            lambda t: setattr(self._row, "col", t)
        )

        self._asc_btn  = QRadioButton("⬆  Crescente")
        self._desc_btn = QRadioButton("⬇  Decrescente")
        grp = QButtonGroup(self)
        grp.addButton(self._asc_btn)
        grp.addButton(self._desc_btn)
        (self._asc_btn if self._row.asc else self._desc_btn).setChecked(True)
        self._asc_btn.toggled.connect(lambda checked: setattr(self._row, "asc", checked))

        rem_btn = QPushButton("✕")
        rem_btn.setObjectName("RemoveBtn")
        rem_btn.setFixedSize(30, 30)
        rem_btn.clicked.connect(self.remove_requested.emit)

        lay.addWidget(self._col_combo)
        lay.addWidget(self._asc_btn)
        lay.addWidget(self._desc_btn)
        lay.addWidget(rem_btn)
        lay.addStretch()

    def get_row(self) -> SortRow:
        return self._row


class SortEditor(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Ordinamento  (opzionale)", parent)
        self._schema: dict = {}
        self._rows:   list = []
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setSpacing(8)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(160)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        self._container = QWidget()
        self._lay       = QVBoxLayout(self._container)
        self._lay.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._lay.setSpacing(4)
        self._lay.setContentsMargins(0, 0, 0, 0)
        scroll.setWidget(self._container)
        outer.addWidget(scroll)

        self._add_btn = QPushButton("➕  Aggiungi ordinamento")
        self._add_btn.setEnabled(False)
        self._add_btn.setFixedHeight(32)
        self._add_btn.clicked.connect(self._add_default_row)
        outer.addWidget(self._add_btn)

    def set_schema(self, schema: dict):
        self._schema = schema
        self._clear()
        self._add_btn.setEnabled(bool(schema))

    def get_sort_rows(self) -> list:
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
        row = SortRow(col=cols[0], asc=True)
        self._add_row_widget(row)

    def _add_row_widget(self, row: SortRow):
        w = SortRowWidget(list(self._schema.keys()), row)
        w.remove_requested.connect(lambda widget=w: self._remove_row(widget))
        self._rows.append(w)
        self._lay.addWidget(w)

    def _remove_row(self, widget):
        if widget in self._rows:
            self._rows.remove(widget)
        widget.setParent(None)
