"""Tool automazione per creare pagine ripetute con contenuto altamente personalizzabile."""

import json
import re

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, QGroupBox,
    QScrollArea, QPushButton, QTextEdit, QHBoxLayout, QSpinBox,
    QCheckBox, QFileDialog, QFrame
)

# --- STILE QSS ---
from .styles import STYLESHEET, _SectionCard, cp_ds_sections



class RepeatedBlocksTool(QWidget):
    schema_needed = pyqtSignal(str)
    run_requested = pyqtSignal(dict)
    generate_requested = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._schemas = {}
        self._block_rows = []
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setStyleSheet(STYLESHEET)

        content = QWidget()
        lay = QVBoxLayout(content)
        lay.setContentsMargins(28, 24, 28, 28)
        lay.setSpacing(20)

        name_card = _SectionCard("🔁", "Template ripetitivo")
        self._name_input = QLineEdit("Settimane Annuali")
        self._name_input.setFixedHeight(40)
        self._name_input.setStyleSheet(STYLESHEET)
        name_card.add_content(self._name_input)
        lay.addWidget(name_card)

        target_card = _SectionCard("🎯", "Destinazione")
        target_inner = QWidget()
        ti_lay = QVBoxLayout(target_inner)
        ti_lay.setSpacing(10)

        self._target_combo = QComboBox()
        self._target_combo.setFixedHeight(40)
        self._target_combo.setStyleSheet(STYLESHEET)
        self._target_combo.currentIndexChanged.connect(self._on_target_changed)

        self._title_prop_combo = QComboBox()
        self._title_prop_combo.setFixedHeight(38)
        self._title_prop_combo.setStyleSheet(STYLESHEET)

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
        self._mode_combo.setStyleSheet(STYLESHEET)
        self._mode_combo.addItem("Intervallo dinamico", "range")
        self._mode_combo.addItem("Lista titoli personalizzata", "custom")
        self._mode_combo.currentIndexChanged.connect(self._refresh_mode_ui)

        self._title_template = QLineEdit("Settimana {index:02d}")
        self._title_template.setStyleSheet(STYLESHEET)

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
            "Componi i blocchi con l'editor visuale (drag & drop non richiesto). "
            "Tipi supportati: heading_1, heading_2, heading_3, paragraph, table."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #64748B; font-size: 12px;")

        builder_actions = QWidget()
        ba_lay = QHBoxLayout(builder_actions)
        ba_lay.setContentsMargins(0, 0, 0, 0)
        ba_lay.setSpacing(8)

        add_h1 = QPushButton("＋ H1")
        add_h1.clicked.connect(lambda: self._add_block_row({"type": "heading_1", "text": "{title}"}))
        add_h2 = QPushButton("＋ H2")
        add_h2.clicked.connect(lambda: self._add_block_row({"type": "heading_2", "text": ""}))
        add_h3 = QPushButton("＋ H3")
        add_h3.clicked.connect(lambda: self._add_block_row({"type": "heading_3", "text": ""}))
        add_par = QPushButton("＋ Paragrafo")
        add_par.clicked.connect(lambda: self._add_block_row({"type": "paragraph", "text": ""}))
        add_table = QPushButton("＋ Tabella")
        add_table.clicked.connect(
            lambda: self._add_block_row({"type": "table", "columns": ["Col 1", "Col 2"], "rows": 3})
        )
        clear_btn = QPushButton("🗑 Svuota")
        clear_btn.clicked.connect(self._clear_block_rows)

        for btn in (add_h1, add_h2, add_h3, add_par, add_table, clear_btn):
            btn.setStyleSheet(STYLESHEET)
            ba_lay.addWidget(btn)
        ba_lay.addStretch()

        self._blocks_rows_host = QWidget()
        self._blocks_rows_lay = QVBoxLayout(self._blocks_rows_host)
        self._blocks_rows_lay.setContentsMargins(0, 0, 0, 0)
        self._blocks_rows_lay.setSpacing(8)

        row_hint = QLabel("Placeholder supportati: {index}, {title}.")
        row_hint.setStyleSheet("color: #64748B; font-size: 12px;")

        blocks_card.add_content(info)
        blocks_card.add_content(builder_actions)
        blocks_card.add_content(self._blocks_rows_host)
        blocks_card.add_content(row_hint)
        lay.addWidget(blocks_card)

        action_card = _SectionCard("⚡", "Esecuzione")
        btn_row = QWidget()
        br = QHBoxLayout(btn_row)
        br.setContentsMargins(0, 0, 0, 0)
        br.setSpacing(12)

        self._gen_btn = QPushButton("💾  Genera codice")
        self._gen_btn.setEnabled(False)
        self._gen_btn.setFixedHeight(44)
        self._gen_btn.setStyleSheet(STYLESHEET)
        self._gen_btn.clicked.connect(lambda: self.generate_requested.emit(self.get_config()))

        self._run_btn = QPushButton("▶  Crea pagine")
        self._run_btn.setEnabled(False)
        self._run_btn.setFixedHeight(44)
        self._run_btn.setStyleSheet(STYLESHEET)
        self._run_btn.clicked.connect(lambda: self.run_requested.emit(self.get_config()))

        br.addWidget(self._gen_btn)
        br.addWidget(self._run_btn)
        action_card.add_content(btn_row)
        lay.addWidget(action_card)

        code_card = _SectionCard("</>", "Codice generato")
        self._code_edit = QTextEdit()
        self._code_edit.setFont(QFont("Consolas", 10))
        self._code_edit.setMinimumHeight(200)
        self._code_edit.setStyleSheet(STYLESHEET)
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
        self._log_edit.setStyleSheet(STYLESHEET)
        log_card.add_content(self._log_edit)
        lay.addWidget(log_card)

        lay.addStretch()
        scroll.setWidget(content)
        outer.addWidget(scroll)
        self._load_default_blueprint_rows()
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
            "blocks_blueprint": json.dumps(self._collect_blocks_from_rows(), ensure_ascii=False),
        }

    def _default_blueprint(self) -> list:
        return [
            {"type": "heading_1", "text": "{title}"},
            {"type": "paragraph", "text": "Contenuto della pagina {index}."},
        ]

    def _load_default_blueprint_rows(self):
        self._load_block_rows(self._default_blueprint())

    def _clear_block_rows(self):
        while self._block_rows:
            row = self._block_rows.pop()
            row["frame"].deleteLater()

    def _load_block_rows(self, blocks: list):
        self._clear_block_rows()
        for block in blocks:
            self._add_block_row(block)

    def _add_block_row(self, block: dict):
        row_frame = QFrame()
        row_frame.setFrameShape(QFrame.Shape.StyledPanel)
        row_frame.setStyleSheet("QFrame { border: 1px solid #334155; border-radius: 8px; }")

        lay = QVBoxLayout(row_frame)
        lay.setContentsMargins(10, 8, 10, 8)
        lay.setSpacing(6)

        top = QWidget()
        top_l = QHBoxLayout(top)
        top_l.setContentsMargins(0, 0, 0, 0)
        top_l.setSpacing(8)

        type_combo = QComboBox()
        type_combo.addItem("Titolo H1", "heading_1")
        type_combo.addItem("Titolo H2", "heading_2")
        type_combo.addItem("Titolo H3", "heading_3")
        type_combo.addItem("Paragrafo", "paragraph")
        type_combo.addItem("Tabella", "table")
        type_combo.setStyleSheet(STYLESHEET)

        remove_btn = QPushButton("Rimuovi")
        remove_btn.setStyleSheet(STYLESHEET)
        remove_btn.setFixedHeight(28)

        top_l.addWidget(QLabel("Tipo blocco"))
        top_l.addWidget(type_combo)
        top_l.addStretch()
        top_l.addWidget(remove_btn)

        text_input = QLineEdit(block.get("text", ""))
        text_input.setPlaceholderText("Testo blocco")
        text_input.setStyleSheet(STYLESHEET)

        table_cfg = QWidget()
        tc_l = QHBoxLayout(table_cfg)
        tc_l.setContentsMargins(0, 0, 0, 0)
        tc_l.setSpacing(8)
        columns_input = QLineEdit(", ".join(block.get("columns", ["Col 1", "Col 2"])))
        columns_input.setPlaceholderText("Colonna 1, Colonna 2, ...")
        columns_input.setStyleSheet(STYLESHEET)
        rows_spin = QSpinBox()
        rows_spin.setRange(1, 100)
        rows_spin.setValue(max(1, int(block.get("rows", 1))))
        rows_spin.setStyleSheet(STYLESHEET)
        tc_l.addWidget(QLabel("Colonne"))
        tc_l.addWidget(columns_input, 1)
        tc_l.addWidget(QLabel("Righe"))
        tc_l.addWidget(rows_spin)

        title_col_check = QCheckBox("Colonna titolo")
        title_col_check.setChecked(bool(block.get("has_row_header")))
        tc_l.addWidget(title_col_check)

        row_header_values = QTextEdit()
        row_header_values.setPlaceholderText("Valori colonna titolo (uno per riga oppure separati da virgole)")
        row_header_values.setMaximumHeight(90)
        row_header_values.setStyleSheet(STYLESHEET)
        row_header_values.setPlainText("\n".join(block.get("row_header_values", [])))

        lay.addWidget(top)
        lay.addWidget(text_input)
        lay.addWidget(table_cfg)
        lay.addWidget(row_header_values)

        row = {
            "frame": row_frame,
            "type_combo": type_combo,
            "text_input": text_input,
            "table_cfg": table_cfg,
            "columns_input": columns_input,
            "rows_spin": rows_spin,
            "title_col_check": title_col_check,
            "row_header_values": row_header_values,
        }
        self._block_rows.append(row)
        self._blocks_rows_lay.addWidget(row_frame)

        block_type = block.get("type", "paragraph")
        idx = max(0, type_combo.findData(block_type))
        type_combo.setCurrentIndex(idx)
        self._refresh_block_row_visibility(row)

        type_combo.currentIndexChanged.connect(lambda _=None, r=row: self._refresh_block_row_visibility(r))
        title_col_check.stateChanged.connect(lambda _=None, r=row: self._refresh_block_row_visibility(r))
        remove_btn.clicked.connect(lambda _=None, r=row: self._remove_block_row(r))

    def _remove_block_row(self, row: dict):
        if row not in self._block_rows:
            return
        self._block_rows.remove(row)
        row["frame"].deleteLater()

    def _refresh_block_row_visibility(self, row: dict):
        is_table = row["type_combo"].currentData() == "table"
        row["text_input"].setVisible(not is_table)
        row["table_cfg"].setVisible(is_table)
        row["row_header_values"].setVisible(is_table and row["title_col_check"].isChecked())

    def _collect_blocks_from_rows(self) -> list:
        blocks = []
        for row in self._block_rows:
            btype = row["type_combo"].currentData() or "paragraph"
            if btype == "table":
                columns = [c.strip() for c in row["columns_input"].text().split(",") if c.strip()]
                blocks.append({
                    "type": "table",
                    "columns": columns or ["Col 1", "Col 2"],
                    "rows": row["rows_spin"].value(),
                    "has_row_header": row["title_col_check"].isChecked(),
                    "row_header_values": self._parse_row_header_values(row["row_header_values"].toPlainText()),
                })
            else:
                blocks.append({
                    "type": btype,
                    "text": row["text_input"].text().strip(),
                })
        return blocks

    @staticmethod
    def _parse_row_header_values(raw: str) -> list[str]:
        return [v.strip() for v in re.split(r"[\n,;]+", raw or "") if v.strip()]

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
