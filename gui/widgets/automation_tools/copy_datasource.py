"""
gui/widgets/automation_tools/copy_datasource.py
Tool: Copia DataSource → DataSource

Contiene tutta la UI di configurazione + esecuzione + codice
in un unico widget verticale scrollabile.
Nessuna dipendenza da altri tab.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox,
    QGroupBox, QScrollArea, QPushButton, QTextEdit,
    QFileDialog, QMessageBox, QFrame, QHBoxLayout,
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont

from gui.widgets.filter_editor  import FilterEditor
from gui.widgets.sort_editor    import SortEditor
from gui.widgets.mapping_editor import MappingEditor


class CopyDatasourceTool(QWidget):
    """
    Segnali verso MainWindow:
      schema_needed(ds_id)   — richiesta caricamento schema
      run_requested(config)  — richiesta esecuzione automazione
      generate_requested(config) — richiesta generazione codice
    """
    schema_needed      = pyqtSignal(str)
    run_requested      = pyqtSignal(dict)
    generate_requested = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._schemas: dict = {}
        self._build_ui()

    # ── Costruzione UI ────────────────────────────────────────────

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll  = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        content = QWidget()
        lay     = QVBoxLayout(content)
        lay.setContentsMargins(24, 20, 24, 24)
        lay.setSpacing(16)

        # ── Nome ──────────────────────────────────────────────────
        lay.addWidget(self._section("Nome automazione"))
        self._name_input = QLineEdit("Copia DataSource")
        self._name_input.setFixedHeight(36)
        lay.addWidget(self._name_input)

        lay.addWidget(self._divider())

        # ── Sorgente ──────────────────────────────────────────────
        lay.addWidget(self._section("📥  Sorgente"))
        src_box = QGroupBox()
        sb = QVBoxLayout(src_box)
        sb.setSpacing(8)
        self._src_combo = QComboBox()
        self._src_combo.setFixedHeight(36)
        self._src_schema_lbl = QLabel("Schema: —")
        self._src_schema_lbl.setStyleSheet("color: #787774; font-size: 12px;")
        self._src_combo.currentIndexChanged.connect(self._on_src_changed)
        sb.addWidget(QLabel("DataSource sorgente:"))
        sb.addWidget(self._src_combo)
        sb.addWidget(self._src_schema_lbl)
        lay.addWidget(src_box)

        self._filter_editor = FilterEditor()
        lay.addWidget(self._filter_editor)

        self._sort_editor = SortEditor()
        lay.addWidget(self._sort_editor)

        lay.addWidget(self._divider())

        # ── Destinazione ──────────────────────────────────────────
        lay.addWidget(self._section("📤  Destinazione"))
        tgt_box = QGroupBox()
        tb = QVBoxLayout(tgt_box)
        tb.setSpacing(8)
        self._tgt_combo = QComboBox()
        self._tgt_combo.setFixedHeight(36)
        self._tgt_schema_lbl = QLabel("Schema: —")
        self._tgt_schema_lbl.setStyleSheet("color: #787774; font-size: 12px;")
        self._tgt_combo.currentIndexChanged.connect(self._on_tgt_changed)
        tb.addWidget(QLabel("DataSource destinazione:"))
        tb.addWidget(self._tgt_combo)
        tb.addWidget(self._tgt_schema_lbl)
        lay.addWidget(tgt_box)

        self._mapping_editor = MappingEditor()
        lay.addWidget(self._mapping_editor)

        lay.addWidget(self._divider())

        # ── Azioni ────────────────────────────────────────────────
        btn_row = QWidget()
        br = QHBoxLayout(btn_row)
        br.setContentsMargins(0, 0, 0, 0)
        br.setSpacing(10)

        self._gen_btn = QPushButton("💾  Genera codice")
        self._gen_btn.setFixedHeight(38)
        self._gen_btn.setEnabled(False)
        self._gen_btn.clicked.connect(self._on_generate)

        self._run_btn = QPushButton("▶  Esegui ora")
        self._run_btn.setObjectName("PrimaryBtn")
        self._run_btn.setFixedHeight(38)
        self._run_btn.setEnabled(False)
        self._run_btn.clicked.connect(self._on_run)

        br.addWidget(self._gen_btn)
        br.addWidget(self._run_btn)
        lay.addWidget(btn_row)

        lay.addWidget(self._divider())

        # ── Codice generato ───────────────────────────────────────
        lay.addWidget(self._section("Codice generato"))
        self._code_edit = QTextEdit()
        self._code_edit.setFont(QFont("Consolas", 10))
        self._code_edit.setMinimumHeight(220)
        self._code_edit.setStyleSheet(
            "background: #1E1E1E; color: #D4D4D4; "
            "border-radius: 8px; border: none; padding: 12px;"
        )
        self._code_edit.setPlaceholderText(
            "Il codice apparirà qui dopo aver cliccato  💾 Genera codice."
        )
        lay.addWidget(self._code_edit)

        self._save_btn = QPushButton("⬇️  Salva .py")
        self._save_btn.setEnabled(False)
        self._save_btn.setFixedHeight(32)
        self._save_btn.clicked.connect(self._on_save)
        lay.addWidget(self._save_btn)

        lay.addWidget(self._divider())

        # ── Log ───────────────────────────────────────────────────
        lay.addWidget(self._section("Log esecuzione"))
        self._log_edit = QTextEdit()
        self._log_edit.setReadOnly(True)
        self._log_edit.setMaximumHeight(120)
        self._log_edit.setFont(QFont("Consolas", 10))
        self._log_edit.setStyleSheet(
            "background: #F7F7F5; border: 1px solid #E3E2DE; "
            "border-radius: 8px; padding: 10px; color: #1A1A1A;"
        )
        lay.addWidget(self._log_edit)

        lay.addStretch()
        scroll.setWidget(content)
        outer.addWidget(scroll)

    # ── Helpers UI ────────────────────────────────────────────────

    @staticmethod
    def _section(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(
            "font-size: 12px; font-weight: 700; color: #1A1A1A; "
            "text-transform: uppercase; letter-spacing: 0.4px; padding-top: 4px;"
        )
        return lbl

    @staticmethod
    def _divider() -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #E3E2DE; margin: 2px 0;")
        return line

    # ── API pubblica (chiamata da MainWindow) ─────────────────────

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
            "Esecuzione in corso…" if running else "▶  Esegui ora"
        )

    def set_code(self, code: str):
        self._code_edit.setPlainText(code)
        self._save_btn.setEnabled(bool(code))

    def get_config(self) -> dict:
        src_id = self._src_combo.currentData()
        tgt_id = self._tgt_combo.currentData()
        return {
            "name":        self._name_input.text().strip() or "Automazione",
            "src_id":      src_id,
            "tgt_id":      tgt_id,
            "src_schema":  self._schemas.get(src_id, {}),
            "tgt_schema":  self._schemas.get(tgt_id, {}),
            "filter_rows": self._filter_editor.get_filter_rows(),
            "sort_rows":   self._sort_editor.get_sort_rows(),
            "col_map":     self._mapping_editor.get_col_map(),
        }

    # ── Slot privati ──────────────────────────────────────────────

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
        ds_id  = self._src_combo.currentData()
        schema = self._schemas.get(ds_id, {})
        if schema:
            preview = ", ".join(
                f"{k} ({v.get('type','?')})"
                for k, v in list(schema.items())[:4]
            )
            if len(schema) > 4:
                preview += "…"
            self._src_schema_lbl.setText(f"Schema: {preview}")
            self._filter_editor.set_schema(schema)
            self._sort_editor.set_schema(schema)
        else:
            self._src_schema_lbl.setText("Schema: caricamento in corso…")

    def _refresh_tgt_ui(self):
        ds_id  = self._tgt_combo.currentData()
        schema = self._schemas.get(ds_id, {})
        if schema:
            preview = ", ".join(
                f"{k} ({v.get('type','?')})"
                for k, v in list(schema.items())[:4]
            )
            if len(schema) > 4:
                preview += "…"
            self._tgt_schema_lbl.setText(f"Schema: {preview}")
        else:
            self._tgt_schema_lbl.setText("Schema: caricamento in corso…")

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
