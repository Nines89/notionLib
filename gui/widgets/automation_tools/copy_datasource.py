from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox,
    QScrollArea, QPushButton, QTextEdit,
    QFileDialog, QMessageBox, QHBoxLayout,
)
from PyQt6.QtCore import pyqtSignal

# Mantengo i tuoi import originali
from gui.widgets.filter_editor import FilterEditor
from gui.widgets.sort_editor import SortEditor
from gui.widgets.mapping_editor import MappingEditor

# --- STILE QSS ---
from .styles import STYLESHEET, _SectionCard, cp_ds_sections


class CopyDatasourceTool(QWidget):
    schema_needed = pyqtSignal(str)
    run_requested = pyqtSignal(dict)
    generate_requested = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._schemas: dict = {}
        # Applichiamo lo stile importato
        self.setStyleSheet(STYLESHEET)
        self._build_ui()

    def _build_ui(self):
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content = QWidget()
        lay = QVBoxLayout(content)
        lay.setContentsMargins(40, 40, 40, 40)
        lay.setSpacing(30)

        # 1. NOME
        name_card = _SectionCard("✏️", "Nome Automazione")
        self._name_input = QLineEdit("Copia DataSource")
        self._name_input.setMinimumHeight(45)
        name_card.add_content(self._name_input)
        lay.addWidget(name_card)

        # 2. SORGENTE
        src_card = _SectionCard("📥", "Sorgente Dati")
        self._src_combo = QComboBox()
        self._src_combo.setMinimumHeight(45)
        self._src_combo.currentIndexChanged.connect(self._on_src_changed)

        self._src_schema_lbl = QLabel("Schema: —")
        self._src_schema_lbl.setStyleSheet(cp_ds_sections)

        self._filter_editor = FilterEditor()
        self._filter_editor.setMinimumHeight(300)  # Più spazio per filtri

        self._sort_editor = SortEditor()
        self._sort_editor.setMinimumHeight(200)

        src_card.add_content(self._src_combo)
        src_card.add_content(self._src_schema_lbl)
        src_card.add_content(self._filter_editor)
        src_card.add_content(self._sort_editor)
        lay.addWidget(src_card)

        # 3. DESTINAZIONE
        tgt_card = _SectionCard("📤", "Destinazione")
        self._tgt_combo = QComboBox()
        self._tgt_combo.setMinimumHeight(45)
        self._tgt_combo.currentIndexChanged.connect(self._on_tgt_changed)

        self._tgt_schema_lbl = QLabel("Schema: —")
        self._tgt_schema_lbl.setStyleSheet(cp_ds_sections)

        self._mapping_editor = MappingEditor()
        self._mapping_editor.setMinimumHeight(450)  # Molto spazio per il mapping

        tgt_card.add_content(self._tgt_combo)
        tgt_card.add_content(self._tgt_schema_lbl)
        tgt_card.add_content(self._mapping_editor)
        lay.addWidget(tgt_card)

        # 4. AZIONI
        btn_layout = QHBoxLayout()
        self._gen_btn = QPushButton("💾 GENERA CODICE")
        self._gen_btn.setObjectName("SecondaryBtn")
        self._gen_btn.setMinimumHeight(55)
        self._gen_btn.clicked.connect(self._on_generate)

        self._run_btn = QPushButton("▶ ESEGUI ORA")
        self._run_btn.setObjectName("PrimaryBtn")
        self._run_btn.setMinimumHeight(55)
        self._run_btn.clicked.connect(self._on_run)

        btn_layout.addStretch()
        btn_layout.addWidget(self._gen_btn, 1)
        btn_layout.addWidget(self._run_btn, 1)
        lay.addLayout(btn_layout)

        # 5. CONSOLE
        code_card = _SectionCard("⚡", "Console Output")
        self._code_edit = QTextEdit()
        self._code_edit.setMinimumHeight(300)
        self._save_btn = QPushButton("⬇ SALVA .PY")
        self._save_btn.setObjectName("SecondaryBtn")
        self._save_btn.clicked.connect(self._on_save)

        self._log_edit = QTextEdit()
        self._log_edit.setMinimumHeight(150)
        self._log_edit.setReadOnly(True)

        code_card.add_content(QLabel("PYTHON CODE:"))
        code_card.add_content(self._code_edit)
        code_card.add_content(self._save_btn)
        code_card.add_content(QLabel("LOGS:"))
        code_card.add_content(self._log_edit)
        lay.addWidget(code_card)

        lay.addStretch()
        scroll.setWidget(content)
        main_lay.addWidget(scroll)

    # --- SOTTO MANTENGO TUTTI I TUOI METODI ORIGINALI ---
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
        self._run_btn.setText("⏳ Esecuzione..." if running else "▶ Esegui ora")

    def set_code(self, code: str):
        self._code_edit.setPlainText(code)
        self._save_btn.setEnabled(bool(code))

    def get_config(self) -> dict:
        src_id = self._src_combo.currentData()
        tgt_id = self._tgt_combo.currentData()
        return {
            "name": self._name_input.text().strip() or "Automazione",
            "src_id": src_id, "tgt_id": tgt_id,
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
            QMessageBox.warning(self, "Mapping mancante", "Configura il mapping.")
            return
        self.generate_requested.emit(self.get_config())

    def _on_run(self):
        col_map = self._mapping_editor.get_col_map()
        if not any(v != "__skip__" for v in col_map.values()):
            QMessageBox.warning(self, "Mapping mancante", "Configura il mapping.")
            return
        self.run_requested.emit(self.get_config())

    def _on_save(self):
        code = self._code_edit.toPlainText()
        path, _ = QFileDialog.getSaveFileName(self, "Salva", "automazione.py", "Python (*.py)")
        if path:
            with open(path, "w", encoding="utf-8") as f: f.write(code)

    def _refresh_src_ui(self):
        ds_id = self._src_combo.currentData()
        schema = self._schemas.get(ds_id, {})
        if schema:
            self._src_schema_lbl.setText(f"Schema caricato ({len(schema)} colonne)")
            self._filter_editor.set_schema(schema)
            self._sort_editor.set_schema(schema)
        else:
            self._src_schema_lbl.setText("Schema: caricamento…")

    def _refresh_tgt_ui(self):
        ds_id = self._tgt_combo.currentData()
        schema = self._schemas.get(ds_id, {})
        self._tgt_schema_lbl.setText(f"Schema caricato ({len(schema)} colonne)" if schema else "Schema: caricamento…")

    def _try_refresh_mapping(self):
        ss = self._schemas.get(self._src_combo.currentData(), {})
        ts = self._schemas.get(self._tgt_combo.currentData(), {})
        if ss and ts: self._mapping_editor.refresh(ss, ts)

    def _refresh_action_btns(self):
        src_ok = bool(self._src_combo.currentData() and self._schemas.get(self._src_combo.currentData()))
        tgt_ok = bool(self._tgt_combo.currentData() and self._schemas.get(self._tgt_combo.currentData()))
        self._gen_btn.setEnabled(src_ok and tgt_ok)
        self._run_btn.setEnabled(src_ok and tgt_ok)