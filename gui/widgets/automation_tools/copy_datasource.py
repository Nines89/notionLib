"""
gui/widgets/automation_tools/copy_datasource.py
Tool: Copia DataSource → DataSource (design moderno)
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox,
    QGroupBox, QScrollArea, QPushButton, QTextEdit,
    QFileDialog, QMessageBox, QFrame, QHBoxLayout,
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont

from gui.widgets.filter_editor import FilterEditor
from gui.widgets.sort_editor import SortEditor
from gui.widgets.mapping_editor import MappingEditor


class _SectionCard(QGroupBox):
    """Card sezione con icona e stile moderno."""

    def __init__(self, icon: str, title: str, parent=None):
        super().__init__(parent)
        self.setTitle("")
        self.setStyleSheet("""
            QGroupBox {
                background: #FFFFFF;
                border: 2px solid #E2E8F0;
                border-radius: 12px;
                padding: 20px 16px 16px 16px;
                margin-top: 8px;
            }
        """)

        # Header interno
        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(14)

        header = QWidget()
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(0, 0, 0, 0)
        h_lay.setSpacing(10)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 20px;")

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(
            "font-size: 15px; font-weight: 700; color: #1E293B;"
        )

        h_lay.addWidget(icon_lbl)
        h_lay.addWidget(title_lbl)
        h_lay.addStretch()

        self._layout.addWidget(header)

    def add_content(self, widget):
        self._layout.addWidget(widget)


class CopyDatasourceTool(QWidget):
    """Tool con design moderno a card."""

    schema_needed = pyqtSignal(str)
    run_requested = pyqtSignal(dict)
    generate_requested = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._schemas: dict = {}
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setStyleSheet("background: #F8FAFC;")

        content = QWidget()
        lay = QVBoxLayout(content)
        lay.setContentsMargins(28, 24, 28, 28)
        lay.setSpacing(20)

        # ── Nome ──────────────────────────────────────────────────
        name_card = _SectionCard("✏️", "Nome automazione")
        self._name_input = QLineEdit("Copia DataSource")
        self._name_input.setFixedHeight(40)
        self._name_input.setStyleSheet("""
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
        """)
        name_card.add_content(self._name_input)
        lay.addWidget(name_card)

        # ── Sorgente ──────────────────────────────────────────────
        src_card = _SectionCard("📥", "Sorgente dati")

        src_inner = QWidget()
        si_lay = QVBoxLayout(src_inner)
        si_lay.setSpacing(10)

        src_label = QLabel("DataSource di partenza:")
        src_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #64748B;")

        self._src_combo = QComboBox()
        self._src_combo.setFixedHeight(40)
        self._src_combo.setStyleSheet("""
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
        """)
        self._src_combo.currentIndexChanged.connect(self._on_src_changed)

        self._src_schema_lbl = QLabel("Schema: —")
        self._src_schema_lbl.setStyleSheet("color: #94A3B8; font-size: 12px;")

        si_lay.addWidget(src_label)
        si_lay.addWidget(self._src_combo)
        si_lay.addWidget(self._src_schema_lbl)

        src_card.add_content(src_inner)
        self._filter_editor = FilterEditor()
        src_card.add_content(self._filter_editor)
        self._sort_editor = SortEditor()
        src_card.add_content(self._sort_editor)
        lay.addWidget(src_card)

        # ── Destinazione ──────────────────────────────────────────
        tgt_card = _SectionCard("📤", "Destinazione")

        tgt_inner = QWidget()
        ti_lay = QVBoxLayout(tgt_inner)
        ti_lay.setSpacing(10)

        tgt_label = QLabel("DataSource di arrivo:")
        tgt_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #64748B;")

        self._tgt_combo = QComboBox()
        self._tgt_combo.setFixedHeight(40)
        self._tgt_combo.setStyleSheet(self._src_combo.styleSheet())
        self._tgt_combo.currentIndexChanged.connect(self._on_tgt_changed)

        self._tgt_schema_lbl = QLabel("Schema: —")
        self._tgt_schema_lbl.setStyleSheet("color: #94A3B8; font-size: 12px;")

        ti_lay.addWidget(tgt_label)
        ti_lay.addWidget(self._tgt_combo)
        ti_lay.addWidget(self._tgt_schema_lbl)

        tgt_card.add_content(tgt_inner)
        self._mapping_editor = MappingEditor()
        tgt_card.add_content(self._mapping_editor)
        lay.addWidget(tgt_card)

        # ── Azioni ────────────────────────────────────────────────
        action_card = _SectionCard("⚡", "Esecuzione")

        btn_row = QWidget()
        br = QHBoxLayout(btn_row)
        br.setContentsMargins(0, 0, 0, 0)
        br.setSpacing(12)

        self._gen_btn = QPushButton("💾  Genera codice")
        self._gen_btn.setFixedHeight(44)
        self._gen_btn.setEnabled(False)
        self._gen_btn.setStyleSheet("""
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
        """)
        self._gen_btn.clicked.connect(self._on_generate)

        self._run_btn = QPushButton("▶  Esegui ora")
        self._run_btn.setFixedHeight(44)
        self._run_btn.setEnabled(False)
        self._run_btn.setStyleSheet("""
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
        """)
        self._run_btn.clicked.connect(self._on_run)

        br.addWidget(self._gen_btn)
        br.addWidget(self._run_btn)

        action_card.add_content(btn_row)
        lay.addWidget(action_card)

        # ── Codice generato ───────────────────────────────────────
        code_card = _SectionCard("</> ", "Codice generato")

        self._code_edit = QTextEdit()
        self._code_edit.setFont(QFont("Consolas", 10))
        self._code_edit.setMinimumHeight(200)
        self._code_edit.setStyleSheet("""
            QTextEdit {
                background: #1E293B;
                color: #E2E8F0;
                border: none;
                border-radius: 8px;
                padding: 14px;
                font-family: 'Consolas', 'Monaco', monospace;
            }
        """)
        self._code_edit.setPlaceholderText(
            "// Il codice apparirà qui dopo aver cliccato 💾 Genera codice"
        )

        self._save_btn = QPushButton("⬇️  Salva come .py")
        self._save_btn.setEnabled(False)
        self._save_btn.setFixedHeight(36)
        self._save_btn.setStyleSheet("""
            QPushButton {
                background: #0F172A;
                border: 1px solid #334155;
                border-radius: 8px;
                color: #94A3B8;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover:enabled {
                background: #1E293B;
                border-color: #475569;
                color: #E2E8F0;
            }
        """)
        self._save_btn.clicked.connect(self._on_save)

        code_card.add_content(self._code_edit)
        code_card.add_content(self._save_btn)
        lay.addWidget(code_card)

        # ── Log ───────────────────────────────────────────────────
        log_card = _SectionCard("📋", "Log esecuzione")

        self._log_edit = QTextEdit()
        self._log_edit.setReadOnly(True)
        self._log_edit.setMaximumHeight(120)
        self._log_edit.setFont(QFont("Consolas", 10))
        self._log_edit.setStyleSheet("""
            QTextEdit {
                background: #F8FAFC;
                border: 2px solid #E2E8F0;
                border-radius: 8px;
                padding: 12px;
                color: #334155;
            }
        """)

        log_card.add_content(self._log_edit)
        lay.addWidget(log_card)

        lay.addStretch()
        scroll.setWidget(content)
        outer.addWidget(scroll)

    # ── Metodi identici al codice precedente ──────────────────────
    # (popolate_datasources, update_schema, etc. rimangono invariati)

    def populate_datasources(self, datasources: list):
        self._src_combo.blockSignals(True)
        self._tgt_combo.blockSignals(True)
        self._src_combo.clear()
        self._tgt_combo.clear()
        for ds in datasources:
            label = f"{ds['name']}  [{ds['db_title']}]"
            self._src_combo.addItem(label, ds["id"])
            self._tgt_combo.addItem(label, ds["id"])
        self._src_combo.blockSignals(False)
        self._tgt_combo.blockSignals(False)
        self._on_src_changed()
        self._on_tgt_changed()

    def update_schema(self, ds_id: str, schema: dict):
        self._schemas[ds_id] = schema
        self._refresh_src_ui()
        self._refresh_tgt_ui()
        self._try_refresh_mapping()
        self._refresh_action_btns()

    def show_log(self, lines: list):
        self._log_edit.setPlainText("\n".join(lines))

    def set_running(self, running: bool):
        self._run_btn.setEnabled(not running)
        self._run_btn.setText(
            "⏳ Esecuzione in corso…" if running else "▶  Esegui ora"
        )

    def set_code(self, code: str):
        self._code_edit.setPlainText(code)
        self._save_btn.setEnabled(bool(code))

    def get_config(self) -> dict:
        src_id = self._src_combo.currentData()
        tgt_id = self._tgt_combo.currentData()
        return {
            "name": self._name_input.text().strip() or "Automazione",
            "src_id": src_id,
            "tgt_id": tgt_id,
            "src_schema": self._schemas.get(src_id, {}),
            "tgt_schema": self._schemas.get(tgt_id, {}),
            "filter_rows": self._filter_editor.get_filter_rows(),
            "sort_rows": self._sort_editor.get_sort_rows(),
            "col_map": self._mapping_editor.get_col_map(),
        }

    def _on_src_changed(self, _=None):
        self._filter_editor.reset()
        self._sort_editor.reset()
        self._mapping_editor.reset()
        ds_id = self._src_combo.currentData()
        if ds_id and ds_id not in self._schemas:
            self.schema_needed.emit(ds_id)
        self._refresh_src_ui()
        self._try_refresh_mapping()
        self._refresh_action_btns()

    def _on_tgt_changed(self, _=None):
        self._mapping_editor.reset()
        ds_id = self._tgt_combo.currentData()
        if ds_id and ds_id not in self._schemas:
            self.schema_needed.emit(ds_id)
        self._refresh_tgt_ui()
        self._try_refresh_mapping()
        self._refresh_action_btns()

    def _on_generate(self):
        col_map = self._mapping_editor.get_col_map()
        if not any(v != "__skip__" for v in col_map.values()):
            QMessageBox.warning(
                self, "Mapping mancante",
                "Configura almeno un mapping di colonne prima di generare."
            )
            return
        self.generate_requested.emit(self.get_config())

    def _on_run(self):
        col_map = self._mapping_editor.get_col_map()
        if not any(v != "__skip__" for v in col_map.values()):
            QMessageBox.warning(
                self, "Mapping mancante",
                "Configura almeno un mapping di colonne prima di eseguire."
            )
            return
        self.run_requested.emit(self.get_config())

    def _on_save(self):
        code = self._code_edit.toPlainText()
        if not code:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Salva automazione", "automazione.py",
            "Python files (*.py)"
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(code)

    def _refresh_src_ui(self):
        ds_id = self._src_combo.currentData()
        schema = self._schemas.get(ds_id, {})
        if schema:
            preview = ", ".join(
                f"{k} ({v.get('type', '?')})"
                for k, v in list(schema.items())[:3]
            )
            if len(schema) > 3:
                preview += "…"
            self._src_schema_lbl.setText(f"Schema: {preview}")
            self._filter_editor.set_schema(schema)
            self._sort_editor.set_schema(schema)
        else:
            self._src_schema_lbl.setText("Schema: caricamento…")

    def _refresh_tgt_ui(self):
        ds_id = self._tgt_combo.currentData()
        schema = self._schemas.get(ds_id, {})
        if schema:
            preview = ", ".join(
                f"{k} ({v.get('type', '?')})"
                for k, v in list(schema.items())[:3]
            )
            if len(schema) > 3:
                preview += "…"
            self._tgt_schema_lbl.setText(f"Schema: {preview}")
        else:
            self._tgt_schema_lbl.setText("Schema: caricamento…")

    def _try_refresh_mapping(self):
        ss = self._schemas.get(self._src_combo.currentData(), {})
        ts = self._schemas.get(self._tgt_combo.currentData(), {})
        if ss and ts:
            self._mapping_editor.refresh(ss, ts)

    def _refresh_action_btns(self):
        src_ok = bool(
            self._src_combo.currentData()
            and self._schemas.get(self._src_combo.currentData())
        )
        tgt_ok = bool(
            self._tgt_combo.currentData()
            and self._schemas.get(self._tgt_combo.currentData())
        )
        enabled = src_ok and tgt_ok
        self._gen_btn.setEnabled(enabled)
        self._run_btn.setEnabled(enabled)