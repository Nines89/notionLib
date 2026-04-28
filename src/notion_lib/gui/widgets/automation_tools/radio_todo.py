from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox,
    QScrollArea, QPushButton, QTextEdit, QHBoxLayout, QFileDialog,
)

from .styles import STYLESHEET, _SectionCard, cp_ds_sections


class RadioTodoTool(QWidget):
    schema_needed = pyqtSignal(str)
    entries_needed = pyqtSignal(str)
    page_todos_needed = pyqtSignal(str)
    generate_requested = pyqtSignal(dict)
    run_requested = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._schemas: dict = {}
        self._entries: dict = {}
        self._pages: list[dict] = []
        self._page_todos: dict = {}
        self.setStyleSheet(STYLESHEET)
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content = QWidget()
        lay = QVBoxLayout(content)
        lay.setContentsMargins(40, 40, 40, 40)
        lay.setSpacing(28)

        name_card = _SectionCard("🎛️", "Nome Automazione")
        self._name_input = QLineEdit("Radio To-Do")
        self._name_input.setMinimumHeight(44)
        name_card.add_content(self._name_input)
        lay.addWidget(name_card)

        cfg_card = _SectionCard("⚙️", "Configurazione radio")
        self._mode_combo = QComboBox()
        self._mode_combo.setMinimumHeight(42)
        self._mode_combo.addItem("DataSource (proprietà checkbox)", "datasource")
        self._mode_combo.addItem("Pagina (blocchi To-Do)", "page")
        self._mode_combo.currentIndexChanged.connect(self._on_mode_changed)

        self._ds_combo = QComboBox()
        self._ds_combo.setMinimumHeight(44)
        self._ds_combo.currentIndexChanged.connect(self._on_ds_changed)

        self._todo_prop_combo = QComboBox()
        self._todo_prop_combo.setMinimumHeight(42)
        self._todo_prop_combo.currentIndexChanged.connect(self._refresh_action_btns)

        self._entry_combo = QComboBox()
        self._entry_combo.setMinimumHeight(42)
        self._entry_combo.currentIndexChanged.connect(self._refresh_action_btns)

        self._page_combo = QComboBox()
        self._page_combo.setMinimumHeight(42)
        self._page_combo.currentIndexChanged.connect(self._on_page_changed)

        self._todo_block_combo = QComboBox()
        self._todo_block_combo.setMinimumHeight(42)
        self._todo_block_combo.currentIndexChanged.connect(self._refresh_action_btns)

        self._schema_lbl = QLabel("Schema: —")
        self._schema_lbl.setStyleSheet(cp_ds_sections)

        self._entries_lbl = QLabel("Entry: —")
        self._entries_lbl.setStyleSheet("color: #94A3B8; font-size: 12px;")

        self._page_todos_lbl = QLabel("Checkbox To-Do: —")
        self._page_todos_lbl.setStyleSheet("color: #94A3B8; font-size: 12px;")

        reload_row = QWidget()
        rr = QHBoxLayout(reload_row)
        rr.setContentsMargins(0, 0, 0, 0)
        self._reload_btn = QPushButton("↻ Ricarica")
        self._reload_btn.setObjectName("SecondaryBtn")
        self._reload_btn.clicked.connect(self._reload_current_mode)
        rr.addStretch()
        rr.addWidget(self._reload_btn)

        cfg_card.add_content(QLabel("Modalità:"))
        cfg_card.add_content(self._mode_combo)
        cfg_card.add_content(QLabel("DataSource:"))
        cfg_card.add_content(self._ds_combo)
        cfg_card.add_content(self._schema_lbl)
        cfg_card.add_content(QLabel("Proprietà To-Do (checkbox):"))
        cfg_card.add_content(self._todo_prop_combo)
        cfg_card.add_content(QLabel("Entry da tenere checkata:"))
        cfg_card.add_content(self._entry_combo)
        cfg_card.add_content(self._entries_lbl)
        cfg_card.add_content(QLabel("Pagina:"))
        cfg_card.add_content(self._page_combo)
        cfg_card.add_content(QLabel("Checkbox To-Do da tenere checkata:"))
        cfg_card.add_content(self._todo_block_combo)
        cfg_card.add_content(self._page_todos_lbl)
        cfg_card.add_content(reload_row)
        lay.addWidget(cfg_card)

        action_card = _SectionCard("🚀", "Esecuzione")
        row = QWidget()
        rl = QHBoxLayout(row)
        rl.setContentsMargins(0, 0, 0, 0)
        self._gen_btn = QPushButton("💾 Genera codice")
        self._gen_btn.setObjectName("SecondaryBtn")
        self._gen_btn.setMinimumHeight(50)
        self._gen_btn.setEnabled(False)
        self._gen_btn.clicked.connect(lambda: self.generate_requested.emit(self.get_config()))
        self._run_btn = QPushButton("▶ Applica radio")
        self._run_btn.setObjectName("PrimaryBtn")
        self._run_btn.setMinimumHeight(50)
        self._run_btn.setEnabled(False)
        self._run_btn.clicked.connect(lambda: self.run_requested.emit(self.get_config()))
        rl.addWidget(self._gen_btn)
        rl.addWidget(self._run_btn)
        action_card.add_content(row)
        lay.addWidget(action_card)

        code_card = _SectionCard("</>", "Codice generato")
        self._code_edit = QTextEdit()
        self._code_edit.setMinimumHeight(240)
        self._save_btn = QPushButton("⬇ Salva .py")
        self._save_btn.setObjectName("SecondaryBtn")
        self._save_btn.setEnabled(False)
        self._save_btn.clicked.connect(self._on_save)
        code_card.add_content(self._code_edit)
        code_card.add_content(self._save_btn)
        lay.addWidget(code_card)

        log_card = _SectionCard("📋", "Log")
        self._log_edit = QTextEdit()
        self._log_edit.setReadOnly(True)
        self._log_edit.setMinimumHeight(180)
        log_card.add_content(self._log_edit)
        lay.addWidget(log_card)

        lay.addStretch()
        scroll.setWidget(content)
        outer.addWidget(scroll)
        self._on_mode_changed()

    def populate_datasources(self, datasources: list):
        self._ds_combo.blockSignals(True)
        self._ds_combo.clear()
        for ds in datasources:
            label = f"{ds['name']}  [{ds['db_title']}]"
            self._ds_combo.addItem(label, ds["id"])
        self._ds_combo.blockSignals(False)
        self._on_ds_changed()

    def populate_pages(self, pages: list):
        self._pages = pages
        self._page_combo.blockSignals(True)
        self._page_combo.clear()
        for page in pages:
            self._page_combo.addItem(page.get("title") or "Pagina senza titolo", page.get("id"))
        self._page_combo.blockSignals(False)
        self._on_page_changed()

    def update_schema(self, ds_id: str, schema: dict):
        self._schemas[ds_id] = schema
        if self._normalize_id(self._ds_combo.currentData()) == self._normalize_id(ds_id):
            self._refresh_schema_ui()
            self._refresh_action_btns()

    def update_entries(self, ds_id: str, entries: list):
        self._entries[self._normalize_id(ds_id)] = entries
        if self._normalize_id(self._ds_combo.currentData()) == self._normalize_id(ds_id):
            self._refresh_entries_ui()
            self._refresh_action_btns()

    def update_page_todos(self, page_id: str, todos: list):
        self._page_todos[self._normalize_id(page_id)] = todos
        if self._normalize_id(self._page_combo.currentData()) == self._normalize_id(page_id):
            self._refresh_page_todos_ui()
            self._refresh_action_btns()

    def show_log(self, lines: list):
        self._log_edit.setPlainText("\n".join(lines))

    def set_code(self, code: str):
        self._code_edit.setPlainText(code)
        self._save_btn.setEnabled(bool(code))

    def set_running(self, running: bool):
        self._run_btn.setEnabled(not running)
        self._run_btn.setText("⏳ Applicazione..." if running else "▶ Applica radio")

    def get_config(self) -> dict:
        mode = self._mode_combo.currentData()
        return {
            "name": self._name_input.text().strip() or "Radio To-Do",
            "mode": mode,
            "ds_id": self._ds_combo.currentData(),
            "todo_prop": self._todo_prop_combo.currentData(),
            "entry_id": self._entry_combo.currentData(),
            "page_id": self._page_combo.currentData(),
            "todo_block_id": self._todo_block_combo.currentData(),
        }

    def selected_entry_label(self) -> str:
        mode = self._mode_combo.currentData()
        if mode == "page":
            return self._todo_block_combo.currentText().strip() or "—"
        return self._entry_combo.currentText().strip() or "—"

    def selected_target_label(self) -> str:
        mode = self._mode_combo.currentData()
        if mode == "page":
            return self._page_combo.currentText().strip() or "—"
        return self._ds_combo.currentText().strip() or "—"

    def _on_ds_changed(self, _=None):
        if self._mode_combo.currentData() != "datasource":
            return
        ds_id = self._ds_combo.currentData()
        if not ds_id:
            return

        norm_id = self._normalize_id(ds_id)
        if norm_id not in self._schemas:
            self.schema_needed.emit(ds_id)

        self._refresh_schema_ui()
        self._request_entries()
        self._refresh_action_btns()

    def _on_page_changed(self, _=None):
        if self._mode_combo.currentData() != "page":
            return
        self._request_page_todos()
        self._refresh_action_btns()

    def _request_entries(self):
        ds_id = self._ds_combo.currentData()
        if ds_id:
            self.entries_needed.emit(ds_id)

    def _refresh_schema_ui(self):
        ds_id = self._normalize_id(self._ds_combo.currentData())
        schema = self._schemas.get(ds_id, {})
        self._todo_prop_combo.clear()

        if not schema:
            self._schema_lbl.setText("Schema: caricamento…")
            return

        checkbox_props = [name for name, meta in schema.items() if meta.get("type") == "checkbox"]
        for prop in checkbox_props:
            self._todo_prop_combo.addItem(prop, prop)

        self._schema_lbl.setText(
            f"Schema caricato ({len(schema)} colonne). To-Do disponibili: {len(checkbox_props)}"
        )

    def _refresh_entries_ui(self):
        ds_id = self._normalize_id(self._ds_combo.currentData())
        rows = self._entries.get(ds_id, [])
        self._entry_combo.clear()
        for row in rows:
            self._entry_combo.addItem(row.get("title") or "Senza titolo", row.get("id"))
        self._entries_lbl.setText(f"Entry caricate: {len(rows)}")

    def _request_page_todos(self):
        page_id = self._page_combo.currentData()
        if page_id:
            self.page_todos_needed.emit(page_id)

    def _refresh_page_todos_ui(self):
        page_id = self._normalize_id(self._page_combo.currentData())
        rows = self._page_todos.get(page_id, [])
        self._todo_block_combo.clear()
        for row in rows:
            prefix = "✅" if row.get("checked") else "⬜"
            self._todo_block_combo.addItem(f"{prefix} {row.get('label')}", row.get("id"))
        self._page_todos_lbl.setText(f"Checkbox To-Do caricate: {len(rows)}")

    def _reload_current_mode(self):
        if self._mode_combo.currentData() == "page":
            self._request_page_todos()
            return
        self._request_entries()

    def _on_mode_changed(self, _=None):
        is_ds = self._mode_combo.currentData() == "datasource"
        self._ds_combo.setVisible(is_ds)
        self._schema_lbl.setVisible(is_ds)
        self._todo_prop_combo.setVisible(is_ds)
        self._entry_combo.setVisible(is_ds)
        self._entries_lbl.setVisible(is_ds)

        self._page_combo.setVisible(not is_ds)
        self._todo_block_combo.setVisible(not is_ds)
        self._page_todos_lbl.setVisible(not is_ds)

        if is_ds:
            self._on_ds_changed()
        else:
            self._on_page_changed()
        self._refresh_action_btns()

    def _refresh_action_btns(self):
        if self._mode_combo.currentData() == "page":
            ready = bool(
                self._page_combo.currentData()
                and self._todo_block_combo.currentData()
            )
        else:
            ready = bool(
                self._ds_combo.currentData()
                and self._todo_prop_combo.currentData()
                and self._entry_combo.currentData()
            )
        self._gen_btn.setEnabled(ready)
        self._run_btn.setEnabled(ready)

    @staticmethod
    def _normalize_id(value):
        return (value or "").replace("-", "")

    def _on_save(self):
        code = self._code_edit.toPlainText()
        if not code:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Salva automazione", "radio_todo_automation.py", "Python files (*.py)"
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(code)
