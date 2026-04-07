"""
gui/widgets/workspace_tab.py
Tab Workspace — albero Pagina → Database → DataSource
con menu contestuale al tasto destro.

Segnali emessi verso MainWindow:
  action_insert_block(page_id)        — inserisci blocco in una pagina
  action_add_datasource(db_id)        — aggiungi datasource a un database
  action_create_db_page(db_id)        — crea pagina con proprietà in un database
  action_add_ds_page(ds_id)           — aggiungi pagina a un datasource
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTreeWidget, QTreeWidgetItem, QFrame, QMenu,
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QFont, QAction


class _MetricCard(QWidget):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            "background: white; border: 1px solid #E3E2DE; border-radius: 10px;"
        )
        self.setFixedSize(130, 72)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(2)
        self._num = QLabel("0")
        self._num.setStyleSheet(
            "font-size: 28px; font-weight: 700; color: #1A1A1A; border: none;"
        )
        lbl = QLabel(title)
        lbl.setStyleSheet(
            "font-size: 11px; font-weight: 600; color: #787774; border: none;"
        )
        lay.addWidget(self._num)
        lay.addWidget(lbl)

    def set_value(self, n: int):
        self._num.setText(str(n))


class WorkspaceTab(QWidget):

    # ── Segnali ───────────────────────────────────────────────────
    action_insert_block  = pyqtSignal(str)   # page_id
    action_add_ds        = pyqtSignal(str)   # db_id
    action_create_db_page = pyqtSignal(str)  # db_id
    action_add_ds_page   = pyqtSignal(str)   # ds_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(20)

        title = QLabel("Workspace")
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #1A1A1A;")
        lay.addWidget(title)

        # ── Metriche ──────────────────────────────────────────────
        metrics = QWidget()
        mlay    = QHBoxLayout(metrics)
        mlay.setContentsMargins(0, 0, 0, 0)
        mlay.setSpacing(12)
        self._pg_card = _MetricCard("Pagine")
        self._db_card = _MetricCard("Database")
        self._ds_card = _MetricCard("DataSource")
        mlay.addWidget(self._pg_card)
        mlay.addWidget(self._db_card)
        mlay.addWidget(self._ds_card)
        mlay.addStretch()
        lay.addWidget(metrics)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #E3E2DE;")
        lay.addWidget(sep)

        tree_lbl = QLabel("Struttura  —  tasto destro per le azioni")
        tree_lbl.setStyleSheet(
            "font-size: 12px; font-weight: 600; color: #787774; "
            "text-transform: uppercase; letter-spacing: 0.5px;"
        )
        lay.addWidget(tree_lbl)

        self._tree = QTreeWidget()
        self._tree.setHeaderLabels(["Nome", "Tipo", "ID"])
        self._tree.setColumnWidth(0, 340)
        self._tree.setColumnWidth(1, 100)
        self._tree.setAlternatingRowColors(True)
        self._tree.setAnimated(True)
        self._tree.setIndentation(22)

        # Abilita menu contestuale custom
        self._tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._on_context_menu)

        lay.addWidget(self._tree)

        hint = QLabel(
            "Se un elemento non appare: in Notion aprilo → ··· → Connetti a → "
            "seleziona l'integrazione."
        )
        hint.setStyleSheet("font-size: 11px; color: #787774;")
        hint.setWordWrap(True)
        lay.addWidget(hint)

    # ── Menu contestuale ──────────────────────────────────────────

    def _on_context_menu(self, pos: QPoint):
        item = self._tree.itemAt(pos)
        if not item:
            return

        obj_type = item.text(1)   # "pagina" | "database" | "datasource"
        obj_id   = item.text(2)

        if not obj_type or not obj_id:
            return   # nodi di raggruppamento (es. "Senza pagina parent")

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background: white;
                border: 1px solid #E3E2DE;
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item {
                padding: 7px 20px;
                border-radius: 4px;
                font-size: 13px;
                color: #1A1A1A;
            }
            QMenu::item:selected {
                background: #F0EFEC;
            }
            QMenu::separator {
                height: 1px;
                background: #E3E2DE;
                margin: 4px 10px;
            }
        """)

        if obj_type == "pagina":
            self._menu_pagina(menu, obj_id, item.text(0).strip())

        elif obj_type == "database":
            self._menu_database(menu, obj_id, item.text(0).strip())

        elif obj_type == "datasource":
            self._menu_datasource(menu, obj_id, item.text(0).strip())

        menu.exec(self._tree.viewport().mapToGlobal(pos))

    def _menu_pagina(self, menu: QMenu, page_id: str, name: str):
        header = QAction(f"🗒  {name}", menu)
        header.setEnabled(False)
        header.setFont(self._header_font())
        menu.addAction(header)
        menu.addSeparator()

        act = QAction("📝  Inserisci blocco", menu)
        act.triggered.connect(lambda: self.action_insert_block.emit(page_id))
        menu.addAction(act)

    def _menu_database(self, menu: QMenu, db_id: str, name: str):
        header = QAction(f"📦  {name}", menu)
        header.setEnabled(False)
        header.setFont(self._header_font())
        menu.addAction(header)
        menu.addSeparator()

        act1 = QAction("🗂  Aggiungi DataSource", menu)
        act1.triggered.connect(lambda: self.action_add_ds.emit(db_id))
        menu.addAction(act1)

        act2 = QAction("📄  Crea pagina con proprietà", menu)
        act2.triggered.connect(lambda: self.action_create_db_page.emit(db_id))
        menu.addAction(act2)

    def _menu_datasource(self, menu: QMenu, ds_id: str, name: str):
        header = QAction(f"🗂  {name}", menu)
        header.setEnabled(False)
        header.setFont(self._header_font())
        menu.addAction(header)
        menu.addSeparator()

        act = QAction("➕  Aggiungi pagina", menu)
        act.triggered.connect(lambda: self.action_add_ds_page.emit(ds_id))
        menu.addAction(act)

    # ── Albero ────────────────────────────────────────────────────

    def refresh(self, databases: dict, datasources: list, pages: dict):
        self._pg_card.set_value(len(pages))
        self._db_card.set_value(len(databases))
        self._ds_card.set_value(len(datasources))
        self._tree.clear()

        bf = self._bold_font()

        ds_by_db: dict = {}
        for ds in datasources:
            ds_by_db.setdefault(ds["db_id"], []).append(ds)

        db_by_page: dict = {}
        for db_id, db_info in databases.items():
            ppid = db_info.get("parent_page_id", "").replace("-", "")
            db_by_page.setdefault(ppid, []).append(db_id)

        placed_db = set()

        for page_id, page_info in pages.items():
            child_db_ids = db_by_page.get(page_id, [])
            if not child_db_ids:
                continue

            pg_item = QTreeWidgetItem(
                self._tree,
                [f"🗒  {page_info['title']}", "pagina", page_id]
            )
            pg_item.setFont(0, bf)
            pg_item.setExpanded(True)

            for db_id in child_db_ids:
                db_info = databases[db_id]
                db_item = QTreeWidgetItem(
                    pg_item,
                    [f"📦  {db_info['title']}", "database", db_id]
                )
                db_item.setExpanded(True)
                placed_db.add(db_id)

                for ds in ds_by_db.get(db_id, []):
                    QTreeWidgetItem(
                        db_item,
                        [f"🗂  {ds['name']}", "datasource", ds["id"]]
                    )

        orphan_dbs = [
            (db_id, db_info) for db_id, db_info in databases.items()
            if db_id not in placed_db
        ]
        if orphan_dbs:
            other = QTreeWidgetItem(self._tree, ["📂  Senza pagina parent", "", ""])
            other.setFont(0, bf)
            other.setExpanded(True)
            for db_id, db_info in orphan_dbs:
                db_item = QTreeWidgetItem(
                    other,
                    [f"📦  {db_info['title']}", "database", db_id]
                )
                db_item.setExpanded(True)
                for ds in ds_by_db.get(db_id, []):
                    QTreeWidgetItem(
                        db_item,
                        [f"🗂  {ds['name']}", "datasource", ds["id"]]
                    )

    # ── Font helpers ──────────────────────────────────────────────

    @staticmethod
    def _bold_font() -> QFont:
        f = QFont()
        f.setBold(True)
        return f

    @staticmethod
    def _header_font() -> QFont:
        f = QFont()
        f.setBold(True)
        f.setPointSize(10)
        return f