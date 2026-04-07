"""
gui/widgets/mapping_editor.py
MappingEditor — mapping colonne sorgente → destinazione.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QGroupBox, QScrollArea, QFrame,
)
from PyQt6.QtCore import Qt

from gui.constants import WRITABLE_TYPES


class MappingEditor(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Mapping colonne", parent)
        self._combos: dict = {}
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setSpacing(10)

        hint = QLabel(
            "Per ogni colonna della destinazione scegli quale colonna della "
            "sorgente copiare.  «— Salta —» per ignorarla."
        )
        hint.setStyleSheet("color: #787774; font-size: 12px;")
        hint.setWordWrap(True)
        outer.addWidget(hint)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #E3E2DE;")
        outer.addWidget(sep)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(280)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        self._container = QWidget()
        self._lay       = QVBoxLayout(self._container)
        self._lay.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._lay.setSpacing(8)
        self._lay.setContentsMargins(0, 4, 0, 4)
        scroll.setWidget(self._container)
        outer.addWidget(scroll)

    def refresh(self, src_schema: dict, tgt_schema: dict):
        self._combos.clear()
        self._clear_layout()

        writable = {k: v for k, v in tgt_schema.items()
                    if v.get("type") in WRITABLE_TYPES}
        src_opts = ["__skip__"] + list(src_schema.keys())

        for tgt_col, tgt_meta in writable.items():
            tgt_type = tgt_meta.get("type", "?")

            row_w = QWidget()
            row_l = QHBoxLayout(row_w)
            row_l.setContentsMargins(0, 0, 0, 0)
            row_l.setSpacing(12)

            # Badge tipo
            type_badge = QLabel(tgt_type)
            type_badge.setFixedWidth(90)
            type_badge.setStyleSheet(
                "background: #F0EFEC; border: 1px solid #E3E2DE; "
                "border-radius: 4px; color: #787774; font-size: 11px; "
                "padding: 2px 6px; font-weight: 500;"
            )
            type_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)

            col_lbl = QLabel(f"<b>{tgt_col}</b>")
            col_lbl.setFixedWidth(180)

            arrow = QLabel("←")
            arrow.setStyleSheet("color: #787774; font-size: 14px;")
            arrow.setFixedWidth(20)

            combo = QComboBox()
            combo.setMinimumWidth(200)
            combo.setFixedHeight(32)
            for opt in src_opts:
                combo.addItem("— Salta —" if opt == "__skip__" else opt, opt)

            self._combos[tgt_col] = combo
            row_l.addWidget(type_badge)
            row_l.addWidget(col_lbl)
            row_l.addWidget(arrow)
            row_l.addWidget(combo)
            row_l.addStretch()
            self._lay.addWidget(row_w)

    def get_col_map(self) -> dict:
        return {tc: combo.currentData() for tc, combo in self._combos.items()}

    def reset(self):
        self._combos.clear()
        self._clear_layout()

    def _clear_layout(self):
        while self._lay.count():
            item = self._lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
