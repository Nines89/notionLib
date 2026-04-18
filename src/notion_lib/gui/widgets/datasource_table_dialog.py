"""
gui/widgets/datasource_table_dialog.py
Dialog tabellare per visualizzare tutte le entries di un DataSource.

Caricamento asincrono. Tabella read-only con:
- colonne = proprietà schema (tipi visibili nel tooltip)
- righe   = entries del datasource
- barra di ricerca per filtrare righe lato client
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QProgressBar, QLineEdit, QPushButton, QWidget,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor

# ─── Mappatura tipo → badge colore ───────────────────────────────

_TYPE_COLORS: dict[str, str] = {
    "title":          "#3B82F6",
    "rich_text":      "#6366F1",
    "number":         "#F59E0B",
    "checkbox":       "#10B981",
    "select":         "#8B5CF6",
    "multi_select":   "#EC4899",
    "status":         "#14B8A6",
    "date":           "#F97316",
    "url":            "#06B6D4",
    "email":          "#84CC16",
    "phone_number":   "#A78BFA",
    "people":         "#FB7185",
    "relation":       "#94A3B8",
    "files":          "#CBD5E1",
    "formula":        "#FCD34D",
    "rollup":         "#6EE7B7",
    "unique_id":      "#93C5FD",
    "created_time":   "#D1D5DB",
    "last_edited_time": "#D1D5DB",
    "created_by":     "#D1D5DB",
    "last_edited_by": "#D1D5DB",
}

# Tipi che non aggiungono valore nella tabella (nascondibili)
_SKIP_TYPES = frozenset({
    "files", "formula", "rollup", "button",
    "verification", "place", "last_visited_time",
    "location",
})


def _format_value(val) -> str:
    """Converte un valore Python estratto in stringa display."""
    if val is None:
        return ""
    if isinstance(val, bool):
        return "✓" if val else ""
    if isinstance(val, list):
        return ", ".join(str(v) for v in val if v)
    return str(val)


# ─── Worker ──────────────────────────────────────────────────────

class _LoadEntriesWorker(QThread):
    success = pyqtSignal(list, dict)   # entries (raw dicts), schema
    failure = pyqtSignal(str)

    def __init__(self, headers: dict, ds_id: str, schema: dict | None = None):
        super().__init__()
        self._headers = headers
        self._ds_id   = ds_id
        self._schema  = schema  # None → carica nel worker

    def run(self):
        try:
            from src.notion_lib.nModels.datasources import DataSourceFactory
            ds = DataSourceFactory.find(self._headers, self._ds_id)
            schema = self._schema or ds.schema
            entries = ds.all_entries()
            self.success.emit(entries, schema)
        except Exception as e:
            self.failure.emit(str(e))


# ─── Dialog ──────────────────────────────────────────────────────

class DataSourceTableDialog(QDialog):
    """
    Mostra le entries di un DataSource in una QTableWidget.

    Parametri
    ---------
    ds_id       : str  — ID del datasource
    ds_name     : str  — nome display
    headers     : dict — headers API Notion
    schema      : dict | None — se None viene caricato nel worker
    """

    def __init__(self, ds_id: str, ds_name: str,
                 headers: dict, schema: dict | None = None,
                 parent=None):
        super().__init__(parent)
        self._ds_id   = ds_id
        self._ds_name = ds_name
        self._headers = headers
        self._schema  = schema
        self._columns: list[tuple[str, str]] = []  # [(prop_name, prop_type)]
        self._workers: list = []
        self._entry_ids: list[str] = []

        self.setWindowTitle(f"Entries — {ds_name}")
        self.resize(1100, 660)
        self._build_ui()
        self._load()

    # ── Build UI ──────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        header = QWidget()
        header.setFixedHeight(52)
        header.setStyleSheet(
            "background: #0F172A; border-bottom: 1px solid #1E293B;"
        )
        hl = QHBoxLayout(header)
        hl.setContentsMargins(20, 0, 20, 0)
        hl.setSpacing(16)

        title_lbl = QLabel(f"🗂  {self._ds_name}")
        title_lbl.setStyleSheet(
            "font-size: 15px; font-weight: 700; color: #E8EEF9;"
        )
        self._count_lbl = QLabel("Caricamento…")
        self._count_lbl.setStyleSheet("color: #64748B; font-size: 12px;")

        hl.addWidget(title_lbl)
        hl.addStretch()
        hl.addWidget(self._count_lbl)
        root.addWidget(header)

        # Progress bar
        self._progress = QProgressBar()
        self._progress.setRange(0, 0)
        self._progress.setFixedHeight(3)
        self._progress.setTextVisible(False)
        self._progress.setStyleSheet(
            "QProgressBar { border:none; background:#1E293B; }"
            "QProgressBar::chunk { background:#22D3EE; }"
        )
        root.addWidget(self._progress)

        # Toolbar: ricerca + reload
        toolbar = QWidget()
        toolbar.setFixedHeight(48)
        toolbar.setStyleSheet(
            "background: #111827; border-bottom: 1px solid #1E293B;"
        )
        tl = QHBoxLayout(toolbar)
        tl.setContentsMargins(16, 0, 16, 0)
        tl.setSpacing(12)

        search_icon = QLabel("🔍")
        self._search = QLineEdit()
        self._search.setPlaceholderText("Filtra righe…")
        self._search.setFixedHeight(30)
        self._search.setMaximumWidth(320)
        self._search.setStyleSheet("""
            QLineEdit {
                background: #1E293B;
                border: 1px solid #334155;
                border-radius: 6px;
                color: #E2E8F0;
                padding: 0 10px;
                font-size: 13px;
            }
            QLineEdit:focus { border-color: #22D3EE; }
        """)
        self._search.textChanged.connect(self._on_filter)

        self._reload_btn = QPushButton("↺  Ricarica")
        self._reload_btn.setEnabled(False)
        self._reload_btn.setFixedHeight(30)
        self._reload_btn.setStyleSheet("""
            QPushButton {
                background: #1E293B;
                border: 1px solid #334155;
                border-radius: 6px;
                color: #94A3B8;
                font-size: 12px;
                font-weight: 600;
                padding: 0 12px;
            }
            QPushButton:hover:enabled {
                border-color: #475569;
                color: #E2E8F0;
            }
        """)
        self._reload_btn.clicked.connect(self._load)

        tl.addWidget(search_icon)
        tl.addWidget(self._search)
        tl.addStretch()
        tl.addWidget(self._reload_btn)
        root.addWidget(toolbar)

        # Tabella
        self._table = QTableWidget()
        self._table.cellDoubleClicked.connect(self._on_row_double_clicked)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.setSortingEnabled(True)
        self._table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Interactive
        )
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.verticalHeader().setVisible(False)
        self._table.setStyleSheet("""
            QTableWidget {
                background: #111827;
                color: #CBD5E1;
                border: none;
                gridline-color: #1E293B;
                font-size: 13px;
                outline: none;
            }
            QTableWidget::item {
                padding: 6px 10px;
                border: none;
            }
            QTableWidget::item:selected {
                background: #1E3A5F;
                color: #E8EEF9;
            }
            QHeaderView::section {
                background: #0D1628;
                color: #64748B;
                font-size: 11px;
                font-weight: 700;
                padding: 7px 10px;
                border: none;
                border-right: 1px solid #1E293B;
                border-bottom: 2px solid #22D3EE;
                letter-spacing: 0.5px;
            }
            QTableWidget QTableCornerButton::section {
                background: #0D1628;
                border: none;
            }
            QScrollBar:vertical {
                background: transparent; width: 8px;
            }
            QScrollBar::handle:vertical {
                background: #334155; border-radius: 4px; min-height: 20px;
            }
            QScrollBar:horizontal {
                background: transparent; height: 8px;
            }
            QScrollBar::handle:horizontal {
                background: #334155; border-radius: 4px; min-width: 20px;
            }
            QScrollBar::add-line, QScrollBar::sub-line { height:0; width:0; }
        """)
        self._table.setAlternatingRowColors(True)
        self._table.setStyleSheet(
            self._table.styleSheet() +
            "QTableWidget { alternate-background-color: #0D1628; }"
        )
        root.addWidget(self._table, stretch=1)

        # Footer
        footer = QWidget()
        footer.setFixedHeight(48)
        footer.setStyleSheet(
            "background: #0F172A; border-top: 1px solid #1E293B;"
        )
        fl = QHBoxLayout(footer)
        fl.setContentsMargins(20, 0, 20, 0)

        self._filter_lbl = QLabel("")
        self._filter_lbl.setStyleSheet("color: #475569; font-size: 12px;")

        close_btn = QPushButton("Chiudi")
        close_btn.setFixedHeight(32)
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background: #1E293B;
                border: 1px solid #334155;
                border-radius: 8px;
                color: #94A3B8;
                font-size: 13px;
                font-weight: 600;
                padding: 0 18px;
            }
            QPushButton:hover { border-color: #475569; color: #E2E8F0; }
        """)

        fl.addWidget(self._filter_lbl)
        fl.addStretch()
        fl.addWidget(close_btn)
        root.addWidget(footer)

    # ── Caricamento ───────────────────────────────────────────────

    def _load(self):
        self._table.setRowCount(0)
        self._table.setColumnCount(0)
        self._search.setEnabled(False)
        self._reload_btn.setEnabled(False)
        self._entry_ids.clear()
        self._progress.show()
        self._count_lbl.setText("Caricamento…")

        w = _LoadEntriesWorker(self._headers, self._ds_id, self._schema)
        w.success.connect(self._on_loaded)
        w.failure.connect(self._on_error)
        w.finished.connect(lambda worker=w: self._cleanup(worker))
        self._workers.append(w)
        w.start()

    def _on_loaded(self, entries: list, schema: dict):
        self._progress.hide()
        self._reload_btn.setEnabled(True)
        self._search.setEnabled(bool(entries))

        # Costruisce lista colonne (esclude tipi irrilevanti)
        self._columns = [
            (name, meta.get("type", ""))
            for name, meta in schema.items()
            if meta.get("type", "") not in _SKIP_TYPES
        ]

        if not self._columns:
            self._count_lbl.setText("Schema vuoto o non caricato.")
            return

        # Intestazioni
        self._table.setSortingEnabled(False)
        self._table.setColumnCount(len(self._columns))
        header_labels = []
        for name, prop_type in self._columns:
            header_labels.append(f"{name}\n{prop_type}")
        self._table.setHorizontalHeaderLabels(header_labels)

        # Tooltip colorati sulle intestazioni
        for col_idx, (name, prop_type) in enumerate(self._columns):
            item = self._table.horizontalHeaderItem(col_idx)
            if item:
                item.setToolTip(f"{name}  ({prop_type})")
                color = _TYPE_COLORS.get(prop_type, "#64748B")
                item.setForeground(QColor(color))

        # Popola righe
        from src.notion_lib.gui.logic.runner import extract_value

        self._table.setRowCount(len(entries))

        for row_idx, entry in enumerate(entries):
            self._entry_ids.append(entry.get("id", "").replace("-", ""))
            row_vals: list[str] = []
            for col_idx, (name, prop_type) in enumerate(self._columns):
                raw = extract_value(entry, name, prop_type)
                display = _format_value(raw)
                row_vals.append(display)

                cell = QTableWidgetItem(display)
                cell.setFlags(cell.flags() & ~Qt.ItemFlag.ItemIsEditable)

                # Checkbox: allineato al centro
                if prop_type == "checkbox":
                    cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                self._table.setItem(row_idx, col_idx, cell)

        self._table.resizeColumnsToContents()

        # Limita larghezza massima colonna a 320px
        for i in range(self._table.columnCount()):
            if self._table.columnWidth(i) > 320:
                self._table.setColumnWidth(i, 320)

        self._table.setSortingEnabled(True)

        count = len(entries)
        self._count_lbl.setText(
            f"{count} {'entry' if count == 1 else 'entries'}  ·  "
            f"{len(self._columns)} colonne"
        )

    def _on_error(self, error: str):
        self._progress.hide()
        self._reload_btn.setEnabled(True)
        self._count_lbl.setText("⚠  Errore")
        QMessageBox.critical(
            self, "Errore caricamento entries",
            f"Impossibile caricare le entries:\n{error}"
        )

    def _on_row_double_clicked(self, row: int, column: int):
        if row < 0 or row >= len(self._entry_ids):
            return

        page_id = self._entry_ids[row]
        if not page_id:
            return

        # Titolo: prima cella della riga (quasi sempre la colonna title)
        first_cell = self._table.item(row, 0)
        page_title = first_cell.text() if first_cell else page_id

        from src.notion_lib.gui.widgets.page_blocks_dialog import PageBlocksDialog
        dialog = PageBlocksDialog(
            page_id=page_id,
            page_title=page_title,
            headers=self._headers,
            parent=self,
        )
        dialog.exec()

    # ── Filtro client-side ────────────────────────────────────────

    def _on_filter(self, text: str):
        query = text.strip().lower()
        total = self._table.rowCount()
        visible = 0

        for row in range(total):
            if not query:
                self._table.setRowHidden(row, False)
                visible += 1
                continue

            row_text = " ".join(
                (self._table.item(row, col).text()
                 if self._table.item(row, col) else "")
                for col in range(self._table.columnCount())
            )
            match = query in row_text.lower()
            self._table.setRowHidden(row, not match)
            if match:
                visible += 1

        self._filter_lbl.setText(
            f"{visible} / {total} righe visibili" if query else ""
        )

    # ── Cleanup ───────────────────────────────────────────────────

    def _cleanup(self, worker):
        if worker in self._workers:
            self._workers.remove(worker)

    def closeEvent(self, event):
        for w in self._workers:
            w.quit()
            w.wait(300)
        super().closeEvent(event)
