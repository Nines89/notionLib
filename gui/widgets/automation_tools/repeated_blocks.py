"""Tool automazione per creare pagine ripetute con contenuto altamente personalizzabile."""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, QGroupBox,
    QScrollArea, QPushButton, QTextEdit, QHBoxLayout, QSpinBox,
    QFileDialog
)

CARD_STYLE = """
QGroupBox {
    background: #FFFFFF;
    border: 2px solid #E2E8F0;
    border-radius: 12px;
    padding: 20px 16px 16px 16px;
    margin-top: 8px;
}
"""

LINE_EDIT_STYLE = """
QLineEdit {
    border: 2px solid #E2E8F0;
    border-radius: 8px;
    padding: 0 12px;
    font-size: 14px;
    background: #FFFFFF;
}
QLineEdit:focus { border-color: #3B82F6; }
"""

COMBO_STYLE = """
QComboBox {
    border: 2px solid #E2E8F0;
    border-radius: 8px;
    padding: 0 12px;
    background: #FFFFFF;
    font-size: 14px;
}
QComboBox:hover { border-color: #CBD5E1; }
QComboBox::drop-down { border: none; width: 30px; }
"""

PRIMARY_BUTTON_STYLE = """
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3B82F6, stop:1 #2563EB);
    border: none; border-radius: 10px; color: #FFFFFF; font-size: 14px; font-weight: 700;
}
QPushButton:hover:enabled { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563EB, stop:1 #1D4ED8); }
QPushButton:disabled { background: #E2E8F0; color: #94A3B8; }
"""

SECONDARY_BUTTON_STYLE = """
QPushButton {
    background: #F1F5F9; border: 2px solid #CBD5E1; border-radius: 10px;
    color: #475569; font-size: 14px; font-weight: 600;
}
QPushButton:hover:enabled { background: #E2E8F0; border-color: #94A3B8; }
QPushButton:disabled { background: #F8FAFC; color: #CBD5E1; }
"""

DARK_CODE_STYLE = """
QTextEdit {
    background: #1E293B; color: #E2E8F0; border: none; border-radius: 8px;
    padding: 14px; font-family: 'Consolas', 'Monaco', monospace;
}
"""

LOG_STYLE = """
QTextEdit {
    background: #F8FAFC; border: 2px solid #E2E8F0; border-radius: 8px;
    padding: 12px; color: #334155;
}
"""


DEFAULT_BLUEPRINT = """[
  {"type": "heading_2", "text": "Piano {title}"},
  {"type": "paragraph", "text": "Obiettivi della pagina {index}"},
  {
    "type": "table",
    "columns": ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"],
    "rows": 1
  }
]"""


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
        self._name_input = QLineEdit("Pagine ricorrenti")
        self._name_input.setFixedHeight(40)
        self._name_input.setStyleSheet(LINE_EDIT_STYLE)
        name_card.add_content(self._name_input)
        lay.addWidget(name_card)

        target_card = _SectionCard("🎯", "Destinazione")
        self._target_combo = QComboBox()
        self._target_combo.setFixedHeight(40)
        self._target_combo.setStyleSheet(COMBO_STYLE)
        self._target_combo.currentIndexChanged.connect(self._on_target_changed)

        self._title_prop_combo = QComboBox()
        self._title_prop_combo.setFixedHeight(38)
        self._title_prop_combo.setStyleSheet(COMBO_STYLE)

        self._schema_lbl = QLabel("Schema: —")
        self._schema_lbl.setStyleSheet("color: #94A3B8; font-size: 12px;")

        target_card.add_content(QLabel("DataSource di destinazione:"))
        target_card.add_content(self._target_combo)
        target_card.add_content(QLabel("Proprietà titolo da valorizzare:"))
        target_card.add_content(self._title_prop_combo)
        target_card.add_content(self._schema_lbl)
        lay.addWidget(target_card)

        pages_card = _SectionCard("🧩", "Tipo di pagine da creare")
        self._mode_combo = QComboBox()
        self._mode_combo.setStyleSheet(COMBO_STYLE)
        self._mode_combo.addItem("Intervallo dinamico", "range")
        self._mode_combo.addItem("Lista titoli personalizzata", "custom")
        self._mode_combo.currentIndexChanged.connect(self._refresh_mode_ui)

        self._title_template = QLineEdit("Settimana {index:02d}")
        self._title_template.setStyleSheet(LINE_EDIT_STYLE)

        row = QWidget()
        row_l = QHBoxLayout(row)
        row_l.setContentsMargins(0, 0, 0, 0)
        self._start_index = QSpinBox()
        self._start_index.setRange(1, 5000)
        self._start_index.setValue(1)
        self._count = QSpinBox()
        self._count.setRange(1, 5000)
        self._count.setValue(52)
        row_l.addWidget(QLabel("Indice iniziale"))
        row_l.addWidget(self._start_index)
        row_l.addSpacing(12)
        row_l.addWidget(QLabel("Numero pagine"))
        row_l.addWidget(self._count)
        row_l.addStretch()

        self._custom_titles = QTextEdit()
        self._custom_titles.setPlaceholderText("Un titolo per riga (es. Sprint 1, Sprint 2, ...)")
        self._custom_titles.setMinimumHeight(110)

        hint = QLabel("Placeholder disponibili nel titolo template: {index}, {title}")
        hint.setStyleSheet("color: #64748B; font-size: 12px;")

        pages_card.add_content(QLabel("Modalità generazione pagine:"))
        pages_card.add_content(self._mode_combo)
        pages_card.add_content(QLabel("Titolo template (modalità intervallo):"))
        pages_card.add_content(self._title_template)
        pages_card.add_content(row)
        pages_card.add_content(QLabel("Titoli custom (modalità lista):"))
        pages_card.add_content(self._custom_titles)
        pages_card.add_content(hint)
        lay.addWidget(pages_card)

        blocks_card = _SectionCard("🧱", "Contenuto pagina (massima personalizzazione)")
        info = QLabel(
            "Definisci i blocchi in JSON. Tipi supportati: heading_1, heading_2, heading_3, "
            "paragraph, table. Nei testi puoi usare {index} e {title}."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #64748B; font-size: 12px;")

        self._blueprint_edit = QTextEdit()
        self._blueprint_edit.setFont(QFont("Consolas", 10))
        self._blueprint_edit.setMinimumHeight(180)
        self._blueprint_edit.setPlainText(DEFAULT_BLUEPRINT)

        blocks_card.add_content(info)
        blocks_card.add_content(self._blueprint_edit)
        lay.addWidget(blocks_card)

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
        self._refresh_mode_ui()

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
        custom_titles = [r.strip() for r in self._custom_titles.toPlainText().splitlines() if r.strip()]
        return {
            "name": self._name_input.text().strip() or "Automazione ripetitiva",
            "target_id": self._target_combo.currentData(),
            "title_prop": self._title_prop_combo.currentData() or "Name",
            "mode": self._mode_combo.currentData(),
            "title_template": self._title_template.text().strip() or "Pagina {index}",
            "start_index": self._start_index.value(),
            "count": self._count.value(),
            "custom_titles": custom_titles,
            "blocks_blueprint": self._blueprint_edit.toPlainText().strip() or "[]",
        }

    def _refresh_mode_ui(self):
        custom_mode = self._mode_combo.currentData() == "custom"
        self._title_template.setEnabled(not custom_mode)
        self._start_index.setEnabled(not custom_mode)
        self._count.setEnabled(not custom_mode)
        self._custom_titles.setEnabled(custom_mode)

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
        path, _ = QFileDialog.getSaveFileName(
            self, "Salva automazione", "automazione_ripetitiva.py", "Python files (*.py)"
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(code)
