from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox,
    QGroupBox, QScrollArea, QPushButton, QTextEdit,
    QFileDialog, QMessageBox, QFrame, QHBoxLayout,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont

# Mantengo i tuoi import originali
from gui.widgets.filter_editor import FilterEditor
from gui.widgets.sort_editor import SortEditor
from gui.widgets.mapping_editor import MappingEditor

# --- STILE QSS ---
STYLESHEET = """
QWidget {
    background-color: #0F172A;
    color: #F1F5F9;
    font-family: 'Inter', 'Segoe UI', sans-serif;
}
QScrollArea { border: none; background-color: #0F172A; }
_SectionCard {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 12px;
}
QLineEdit, QComboBox {
    background-color: #0F172A;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 8px 12px;
    color: #F1F5F9;
}
QLineEdit:focus, QComboBox:focus { border: 2px solid #6366F1; }
QPushButton#PrimaryBtn {
    background-color: #6366F1; color: white; font-weight: bold;
    border-radius: 6px; padding: 10px;
}
QPushButton#SecondaryBtn {
    background-color: transparent; border: 1px solid #334155;
    color: #CBD5E1; border-radius: 6px;
}
QTextEdit {
    background-color: #020617; border: 1px solid #1E293B;
    border-radius: 8px; color: #94A3B8; font-family: 'Consolas';
}
"""

class _SectionCard(QFrame):
    def __init__(self, icon: str, title: str, parent=None):
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(20, 20, 20, 20)
        self._layout.setSpacing(15)

        header = QHBoxLayout()
        title_lbl = QLabel(f"{icon}  {title.upper()}")
        title_lbl.setStyleSheet("font-size: 11px; font-weight: 800; color: #94A3B8; letter-spacing: 1px;")
        header.addWidget(title_lbl)
        header.addStretch()
        self._layout.addLayout(header)

    def add_content(self, widget):
        self._layout.addWidget(widget)

class CopyDatasourceTool(QWidget):
    schema_needed = pyqtSignal(str)
    run_requested = pyqtSignal(dict)
    generate_requested = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._schemas: dict = {}
        self.setStyleSheet(STYLESHEET)
        self._build_ui()

    def _build_ui(self):
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        lay = QVBoxLayout(content)
        lay.setContentsMargins(30, 30, 30, 30)
        lay.setSpacing(25)

        # 1. Nome Automazione
        name_card = _SectionCard("✏️", "Nome Automazione")
        self._name_input = QLineEdit("Copia DataSource")
        name_card.add_content(self._name_input)
        lay.addWidget(name_card)

        # 2. Sorgente
        src_card = _SectionCard("📥", "Sorgente Dati")
        self._src_combo = QComboBox()
        self._src_combo.currentIndexChanged.connect(self._on_src_changed)
        self._src_schema_lbl = QLabel("Schema: —")
        self._src_schema_lbl.setStyleSheet("color: #6366F1; font-size: 11px;")

        src_card.add_content(self._src_combo)
        src_card.add_content(self._src_schema_lbl)

        # Inizializzazione widget custom (CRITICO)
        self._filter_editor = FilterEditor()
        self._sort_editor = SortEditor()
        src_card.add_content(self._filter_editor)
        src_card.add_content(self._sort_editor)
        lay.addWidget(src_card)

        # 3. Destinazione
        tgt_card = _SectionCard("📤", "Destinazione")
        self._tgt_combo = QComboBox()
        self._tgt_combo.currentIndexChanged.connect(self._on_tgt_changed)
        self._tgt_schema_lbl = QLabel("Schema: —")
        self._tgt_schema_lbl.setStyleSheet("color: #6366F1; font-size: 11px;")

        tgt_card.add_content(self._tgt_combo)
        tgt_card.add_content(self._tgt_schema_lbl)

        self._mapping_editor = MappingEditor()
        tgt_card.add_content(self._mapping_editor)
        lay.addWidget(tgt_card)

        # 4. Azioni
        btn_layout = QHBoxLayout()
        self._gen_btn = QPushButton("💾 Genera Codice")
        self._gen_btn.setObjectName("SecondaryBtn")
        self._gen_btn.clicked.connect(self._on_generate)

        self._run_btn = QPushButton("▶ Esegui Ora")
        self._run_btn.setObjectName("PrimaryBtn")
        self._run_btn.clicked.connect(self._on_run)

        btn_layout.addStretch()
        btn_layout.addWidget(self._gen_btn)
        btn_layout.addWidget(self._run_btn)
        lay.addLayout(btn_layout)

        # 5. Codice e Log
        code_card = _SectionCard("⚡", "Output")
        self._code_edit = QTextEdit()
        self._code_edit.setMinimumHeight(200)
        self._save_btn = QPushButton("⬇ Salva .py")
        self._save_btn.setObjectName("SecondaryBtn")
        self._save_btn.clicked.connect(self._on_save)

        self._log_edit = QTextEdit()
        self._log_edit.setMaximumHeight(100)
        self._log_edit.setReadOnly(True)

        code_card.add_content(QLabel("CODICE GENERATO:"))
        code_card.add_content(self._code_edit)
        code_card.add_content(self._save_btn)
        code_card.add_content(QLabel("LOG ESECUZIONE:"))
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