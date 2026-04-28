from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QScrollArea,
    QPushButton,
    QTextEdit,
    QHBoxLayout,
    QFileDialog,
    QListWidget,
    QListWidgetItem,
    QButtonGroup,
    QRadioButton,
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
        self._mode = "datasource"
        self._selected_todo_block_id = ""
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

        mode_row = QWidget()
        mode_lay = QHBoxLayout(mode_row)
        mode_lay.setContentsMargins(0, 0, 0, 0)
        mode_lay.setSpacing(10)
        self._mode_ds_btn = QPushButton("🧩 DataSource")
        self._mode_pg_btn = QPushButton("📄 Pagina")
        for btn in (self._mode_ds_btn, self._mode_pg_btn):
            btn.setCheckable(True)
            btn.setMinimumHeight(40)
            btn.setObjectName("SecondaryBtn")
        self._mode_ds_btn.clicked.connect(lambda: self._set_mode("datasource"))
        self._mode_pg_btn.clicked.connect(lambda: self._set_mode("page"))
        mode_lay.addWidget(self._mode_ds_btn)
        mode_lay.addWidget(self._mode_pg_btn)

        self._ds_combo = QComboBox()
        self._ds_combo.setMinimumHeight(44)
        self._ds_combo.currentIndexChanged.connect(self._on_ds_changed)

        self._todo_prop_combo = QComboBox()
        self._todo_prop_combo.setMinimumHeight(42)
        self._todo_prop_combo.currentIndexChanged.connect(self._refresh_action_btns)

        self._entry_list = QListWidget()
        self._entry_list.setMinimumHeight(150)
        self._entry_list.itemSelectionChanged.connect(self._refresh_action_btns)

        self._page_list = QListWidget()
        self._page_list.setMinimumHeight(180)
        self._page_list.itemSelectionChanged.connect(self._on_page_changed)

        self._todo_scroll = QScrollArea()
        self._todo_scroll.setWidgetResizable(True)
        self._todo_scroll.setMinimumHeight(180)
        self._todo_container = QWidget()
        self._todo_lay = QVBoxLayout(self._todo_container)
        self._todo_lay.setContentsMargins(8, 8, 8, 8)
        self._todo_lay.setSpacing(8)
        self._todo_scroll.setWidget(self._todo_container)
        self._todo_group = QButtonGroup(self)
        self._todo_group.setExclusive(True)
        self._todo_group.buttonClicked.connect(self._on_todo_selected)

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
        cfg_card.add_content(mode_row)

        self._ds_label = QLabel("DataSource:")
        cfg_card.add_content(self._ds_label)
        cfg_card.add_content(self._ds_combo)
        cfg_card.add_content(self._schema_lbl)

        self._prop_label = QLabel("Proprietà To-Do (checkbox):")
        cfg_card.add_content(self._prop_label)
        cfg_card.add_content(self._todo_prop_combo)

        self._entry_label = QLabel("Entry da tenere checkata:")
        cfg_card.add_content(self._entry_label)
        cfg_card.add_content(self._entry_list)
        cfg_card.add_content(self._entries_lbl)

        self._page_label = QLabel("Pagine disponibili:")
        cfg_card.add_content(self._page_label)
        cfg_card.add_content(self._page_list)

        self._todo_label = QLabel("Checkbox To-Do (selezionane una):")
        cfg_card.add_content(self._todo_label)
        cfg_card.add_content(self._todo_scroll)
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
        self._set_mode("datasource")

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
        self._page_list.clear()
        for page in pages:
            item = QListWidgetItem(f"📄 {page.get('title') or 'Pagina senza titolo'}")
            item.setData(256, page.get("id"))
            self._page_list.addItem(item)
        if self._page_list.count() > 0:
            self._page_list.setCurrentRow(0)
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
        if self._normalize_id(self._selected_page_id()) == self._normalize_id(page_id):
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
        return {
            "name": self._name_input.text().strip() or "Radio To-Do",
            "mode": self._mode,
            "ds_id": self._ds_combo.currentData(),
            "todo_prop": self._todo_prop_combo.currentData(),
            "entry_id": self._selected_entry_id(),
            "page_id": self._selected_page_id(),
            "todo_block_id": self._selected_todo_block_id,
        }

    def selected_entry_label(self) -> str:
        if self._mode == "page":
            btn = self._todo_group.checkedButton()
            return btn.text().strip() if btn else "—"
        item = self._entry_list.currentItem()
        return item.text().strip() if item else "—"

    def selected_target_label(self) -> str:
        if self._mode == "page":
            item = self._page_list.currentItem()
            return (item.text().replace("📄", "").strip() if item else "—")
        return self._ds_combo.currentText().strip() or "—"

    def _set_mode(self, mode: str):
        self._mode = mode
        is_ds = mode == "datasource"
        self._mode_ds_btn.setChecked(is_ds)
        self._mode_pg_btn.setChecked(not is_ds)

        self._ds_label.setVisible(is_ds)
        self._ds_combo.setVisible(is_ds)
        self._schema_lbl.setVisible(is_ds)
        self._prop_label.setVisible(is_ds)
        self._todo_prop_combo.setVisible(is_ds)
        self._entry_label.setVisible(is_ds)
        self._entry_list.setVisible(is_ds)
        self._entries_lbl.setVisible(is_ds)

        self._page_label.setVisible(not is_ds)
        self._page_list.setVisible(not is_ds)
        self._todo_label.setVisible(not is_ds)
        self._todo_scroll.setVisible(not is_ds)
        self._page_todos_lbl.setVisible(not is_ds)

        if is_ds:
            self._on_ds_changed()
        else:
            self._on_page_changed()
        self._refresh_action_btns()

    def _selected_entry_id(self):
        item = self._entry_list.currentItem()
        return item.data(256) if item else ""

    def _selected_page_id(self):
        item = self._page_list.currentItem()
        return item.data(256) if item else ""

    def _on_ds_changed(self, _=None):
        if self._mode != "datasource":
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
        if self._mode != "page":
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
        self._entry_list.clear()
        for row in rows:
            item = QListWidgetItem(f"🗂️ {row.get('title') or 'Senza titolo'}")
            item.setData(256, row.get("id"))
            self._entry_list.addItem(item)
        if self._entry_list.count() > 0:
            self._entry_list.setCurrentRow(0)
        self._entries_lbl.setText(f"Entry caricate: {len(rows)}")

    def _request_page_todos(self):
        page_id = self._selected_page_id()
        if page_id:
            self.page_todos_needed.emit(page_id)

    def _on_todo_selected(self, button):
        self._selected_todo_block_id = button.property("todo_id") or ""
        self._refresh_action_btns()

    def _refresh_page_todos_ui(self):
        while self._todo_lay.count():
            item = self._todo_lay.takeAt(0)
            widget = item.widget()
            if widget is not None:
                self._todo_group.removeButton(widget)
                widget.deleteLater()

        page_id = self._normalize_id(self._selected_page_id())
        rows = self._page_todos.get(page_id, [])
        self._selected_todo_block_id = ""

        for idx, row in enumerate(rows):
            label = row.get("label") or "To-Do senza testo"
            btn = QRadioButton(f"{label}")
            btn.setProperty("todo_id", row.get("id"))
            if row.get("checked") and not self._selected_todo_block_id:
                self._selected_todo_block_id = row.get("id")
            self._todo_group.addButton(btn)
            self._todo_lay.addWidget(btn)
            if idx == 0 and not self._selected_todo_block_id:
                self._selected_todo_block_id = row.get("id")

        for btn in self._todo_group.buttons():
            if btn.property("todo_id") == self._selected_todo_block_id:
                btn.setChecked(True)
                break

        self._todo_lay.addStretch(1)
        self._page_todos_lbl.setText(f"Checkbox To-Do caricate: {len(rows)}")

    def _reload_current_mode(self):
        if self._mode == "page":
            self._request_page_todos()
            return
        self._request_entries()

    def _refresh_action_btns(self):
        if self._mode == "page":
            ready = bool(self._selected_page_id() and self._selected_todo_block_id)
        else:
            ready = bool(
                self._ds_combo.currentData()
                and self._todo_prop_combo.currentData()
                and self._selected_entry_id()
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
