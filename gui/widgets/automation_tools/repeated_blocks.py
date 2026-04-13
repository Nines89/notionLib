"""Tool automazione per creare pagine ripetute con blocchi omogenei."""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, QGroupBox,
    QScrollArea, QPushButton, QTextEdit, QHBoxLayout, QSpinBox,
    QCheckBox, QFileDialog
)

from gui.widgets.automation_tools.styles import (
    CARD_STYLE,
    LINE_EDIT_STYLE,
    COMBO_STYLE,
    PRIMARY_BUTTON_STYLE,
    SECONDARY_BUTTON_STYLE,
    DARK_CODE_STYLE,
    LOG_STYLE,
)


class _SectionCard(QGroupBox):
    def __init__(self, icon: str, title: str, parent=None):
        super().__init__(parent)
        self.setTitle("")
        self.setStyleSheet(CARD_STYLE)

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(14)

        header = QWidget()
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(0, 0, 0, 0)
        h_lay.setSpacing(10)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 20px;")
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 15px; font-weight: 700; color: #1E293B;")

        h_lay.addWidget(icon_lbl)
        h_lay.addWidget(title_lbl)
        h_lay.addStretch()
        self._layout.addWidget(header)

    def add_content(self, widget):
        self._layout.addWidget(widget)


class RepeatedBlocksTool(QWidget):
    schema_needed = pyqtSignal(str)
    run_requested = pyqtSignal(dict)
    generate_requested = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._schemas = {}
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

        name_card = _SectionCard("🔁", "Template ripetitivo")
        self._name_input = QLineEdit("Settimane Annuali")
        self._name_input.setFixedHeight(40)
        self._name_input.setStyleSheet(LINE_EDIT_STYLE)
        name_card.add_content(self._name_input)
        lay.addWidget(name_card)

        target_card = _SectionCard("🎯", "Destinazione")
        target_inner = QWidget()
        ti_lay = QVBoxLayout(target_inner)
        ti_lay.setSpacing(10)

        self._target_combo = QComboBox()
        self._target_combo.setFixedHeight(40)
        self._target_combo.setStyleSheet(COMBO_STYLE)
        self._target_combo.currentIndexChanged.connect(self._on_target_changed)

        self._title_prop_combo = QComboBox()
        self._title_prop_combo.setFixedHeight(38)
        self._title_prop_combo.setStyleSheet(COMBO_STYLE)

        self._schema_lbl = QLabel("Schema: —")
        self._schema_lbl.setStyleSheet("color: #94A3B8; font-size: 12px;")

        ti_lay.addWidget(QLabel("DataSource di destinazione:"))
        ti_lay.addWidget(self._target_combo)
        ti_lay.addWidget(QLabel("Proprietà titolo da valorizzare:"))
        ti_lay.addWidget(self._title_prop_combo)
        ti_lay.addWidget(self._schema_lbl)
        target_card.add_content(target_inner)
        lay.addWidget(target_card)

        pattern_card = _SectionCard("📅", "Pattern pagine")
        pattern_inner = QWidget()
        pi_lay = QVBoxLayout(pattern_inner)
        pi_lay.setSpacing(10)

        self._prefix_input = QLineEdit("Settimana")
        self._prefix_input.setFixedHeight(38)
        self._prefix_input.setStyleSheet(LINE_EDIT_STYLE)

        row = QWidget()
        row_lay = QHBoxLayout(row)
        row_lay.setContentsMargins(0, 0, 0, 0)

        self._start_week = QSpinBox()
        self._start_week.setRange(1, 53)
        self._start_week.setValue(1)

        self._weeks_count = QSpinBox()
        self._weeks_count.setRange(1, 200)
        self._weeks_count.setValue(52)

        row_lay.addWidget(QLabel("Settimana iniziale"))
        row_lay.addWidget(self._start_week)
        row_lay.addSpacing(12)
        row_lay.addWidget(QLabel("Numero pagine"))
        row_lay.addWidget(self._weeks_count)
        row_lay.addStretch()

        self._table_check = QCheckBox("Aggiungi tabella giorni in ogni pagina")
        self._table_check.setChecked(True)

        self._days_input = QLineEdit("Lunedì, Martedì, Mercoledì, Giovedì, Venerdì, Sabato, Domenica")
        self._days_input.setStyleSheet(LINE_EDIT_STYLE)
        self._days_input.setFixedHeight(38)

        pi_lay.addWidget(QLabel("Prefisso titolo pagina:"))
        pi_lay.addWidget(self._prefix_input)
        pi_lay.addWidget(row)
        pi_lay.addWidget(self._table_check)
        pi_lay.addWidget(QLabel("Giorni (separati da virgola):"))
        pi_lay.addWidget(self._days_input)
        pattern_card.add_content(pattern_inner)
        lay.addWidget(pattern_card)

        action_card = _SectionCard("⚡", "Esecuzione")
        btn_row = QWidget()
        br = QHBoxLayout(btn_row)
        br.setContentsMargins(0, 0, 0, 0)
        br.setSpacing(12)

        self._gen_btn = QPushButton("💾  Genera codice")
        self._gen_btn.setEnabled(False)
        self._gen_btn.setFixedHeight(44)
        self._gen_btn.setStyleSheet(SECONDARY_BUTTON_STYLE)
        self._gen_btn.clicked.connect(lambda: self.generate_requested.emit(self.get_config()))

        self._run_btn = QPushButton("▶  Crea pagine")
        self._run_btn.setEnabled(False)
        self._run_btn.setFixedHeight(44)
        self._run_btn.setStyleSheet(PRIMARY_BUTTON_STYLE)
        self._run_btn.clicked.connect(lambda: self.run_requested.emit(self.get_config()))

        br.addWidget(self._gen_btn)
        br.addWidget(self._run_btn)
        action_card.add_content(btn_row)
        lay.addWidget(action_card)

        code_card = _SectionCard("</>", "Codice generato")
        self._code_edit = QTextEdit()
        self._code_edit.setFont(QFont("Consolas", 10))
        self._code_edit.setMinimumHeight(200)
        self._code_edit.setStyleSheet(DARK_CODE_STYLE)
        self._save_btn = QPushButton("⬇️  Salva come .py")
        self._save_btn.setEnabled(False)
        self._save_btn.clicked.connect(self._on_save)
        code_card.add_content(self._code_edit)
        code_card.add_content(self._save_btn)
        lay.addWidget(code_card)

        log_card = _SectionCard("📋", "Log esecuzione")
        self._log_edit = QTextEdit()
        self._log_edit.setReadOnly(True)
        self._log_edit.setMaximumHeight(120)
        self._log_edit.setStyleSheet(LOG_STYLE)
        log_card.add_content(self._log_edit)
        lay.addWidget(log_card)

        lay.addStretch()
        scroll.setWidget(content)
        outer.addWidget(scroll)

    def populate_datasources(self, datasources: list):
        self._target_combo.blockSignals(True)
        self._target_combo.clear()
        for ds in datasources:
            self._target_combo.addItem(f"{ds['name']}  [{ds['db_title']}]", ds["id"])
        self._target_combo.blockSignals(False)
        self._on_target_changed()

    def update_schema(self, ds_id: str, schema: dict):
        self._schemas[ds_id] = schema
        self._refresh_schema_ui()
        self._refresh_action_btns()

    def set_code(self, code: str):
        self._code_edit.setPlainText(code)
        self._save_btn.setEnabled(bool(code))

    def show_log(self, lines: list):
        self._log_edit.setPlainText("\n".join(lines))

    def set_running(self, running: bool):
        self._run_btn.setEnabled(not running)
        self._run_btn.setText("⏳ Creazione in corso…" if running else "▶  Crea pagine")

    def get_config(self) -> dict:
        days = [d.strip() for d in self._days_input.text().split(",") if d.strip()]
        return {
            "name": self._name_input.text().strip() or "Automazione ripetitiva",
            "target_id": self._target_combo.currentData(),
            "title_prop": self._title_prop_combo.currentData() or "Name",
            "title_prefix": self._prefix_input.text().strip() or "Settimana",
            "start_week": self._start_week.value(),
            "weeks_count": self._weeks_count.value(),
            "with_table": self._table_check.isChecked(),
            "days": days,
        }

    def _on_target_changed(self, _=None):
        ds_id = self._target_combo.currentData()
        if ds_id and ds_id not in self._schemas:
            self.schema_needed.emit(ds_id)
        self._refresh_schema_ui()
        self._refresh_action_btns()

    def _refresh_schema_ui(self):
        ds_id = self._target_combo.currentData()
        schema = self._schemas.get(ds_id, {})
        self._title_prop_combo.clear()
        if schema:
            preview = ", ".join(f"{k} ({v.get('type', '?')})" for k, v in list(schema.items())[:3])
            self._schema_lbl.setText(f"Schema: {preview}{'…' if len(schema) > 3 else ''}")
            title_props = [k for k, v in schema.items() if v.get("type") == "title"]
            if not title_props:
                title_props = list(schema.keys())[:1]
            for prop in title_props:
                self._title_prop_combo.addItem(prop, prop)
        else:
            self._schema_lbl.setText("Schema: caricamento…")

    def _refresh_action_btns(self):
        ds_id = self._target_combo.currentData()
        enabled = bool(ds_id and self._schemas.get(ds_id))
        self._gen_btn.setEnabled(enabled)
        self._run_btn.setEnabled(enabled)

    def _on_save(self):
        code = self._code_edit.toPlainText()
        if not code:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Salva automazione", "automazione_ripetitiva.py", "Python files (*.py)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(code)
