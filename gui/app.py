"""
gui/app.py
MainWindow — finestra principale.
Assembla sidebar + tabs, gestisce workers, coordina i componenti.
NON contiene logica di business.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QTabWidget,
    QStatusBar, QMessageBox, QFrame,
)

from gui.state import get_state, reset_state
from gui.workers import ConnectWorker, LoadSchemaWorker, RunWorker
from gui.logic.codegen import generate

from gui.widgets.sidebar       import SidebarWidget
from gui.widgets.workspace_tab import WorkspaceTab
from gui.widgets.automations_tab import AutomationsTab
from gui.widgets.automation_tools.copy_datasource import CopyDatasourceTool


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Notion Automation")
        self.resize(1320, 860)
        self.setMinimumSize(900, 600)
        self._workers: list = []
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Area contenuto principale ─────────────────────────────
        content = QWidget()
        content.setObjectName("ContentArea")
        content_lay = QHBoxLayout(content)
        content_lay.setContentsMargins(20, 18, 20, 14)
        content_lay.setSpacing(0)

        self._tabs = QTabWidget()
        self._tabs.setDocumentMode(True)
        self._tabs.setEnabled(False)

        # Tab 1: Workspace
        self._ws_tab = WorkspaceTab()
        self._tabs.addTab(self._ws_tab, "  🪐 Panorama  ")

        # Tab 2: Automazioni (con tile + stack interno)
        self._auto_tab = AutomationsTab()
        self._tabs.addTab(self._auto_tab, "  🤖 Flussi  ")

        # Registra i tool nell'AutomationsTab
        self._copy_tool = CopyDatasourceTool()
        self._auto_tab.register_tool(
            icon        = "🧠",
            title       = "Sync DataSource",
            description = "Trasforma e sincronizza record tra due datasource con filtri avanzati.",
            tool_widget = self._copy_tool,
        )

        content_lay.addWidget(self._tabs)
        root.addWidget(content, stretch=1)

        # ── Sidebar a destra (layout rinnovato) ───────────────────
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet("color: #1F2A40;")
        root.addWidget(sep)

        self._sidebar = SidebarWidget()
        self._sidebar.connect_requested.connect(self._on_connect)
        self._sidebar.disconnect_requested.connect(self._on_disconnect)
        root.addWidget(self._sidebar)

        # ── Connessioni segnali ───────────────────────────────────
        self._copy_tool.schema_needed.connect(self._on_schema_needed)
        self._copy_tool.generate_requested.connect(self._on_copy_generate)
        self._copy_tool.run_requested.connect(self._on_copy_run)

        # ── Status bar ────────────────────────────────────────────
        self._status = QStatusBar()
        self.setStatusBar(self._status)
        self._status.showMessage("Inserisci la chiave API per iniziare.")

    # ══════════════════════════════════════════════════════════════
    # Connessione
    # ══════════════════════════════════════════════════════════════

    def _on_connect(self, api_key: str):
        self._status.showMessage("Connessione in corso…")
        w = ConnectWorker(api_key)
        w.success.connect(self._on_connect_ok)
        w.failure.connect(self._on_connect_fail)
        w.finished.connect(lambda worker=w: self._cleanup_worker(worker))
        self._workers.append(w)
        w.start()

    def _on_connect_ok(self, api, bot_name: str,
                       databases: dict, datasources: list, pages: dict):
        state             = get_state()
        state.api         = api
        state.bot_name    = bot_name
        state.databases   = databases
        state.datasources = datasources
        state.pages       = pages

        self._sidebar.show_connected(bot_name, len(databases), len(datasources))
        self._ws_tab.refresh(databases, datasources, pages)
        self._copy_tool.populate_datasources(datasources)
        self._tabs.setEnabled(True)
        self._status.showMessage(
            f"Connesso come {bot_name}  ·  "
            f"{len(pages)} pagine, {len(databases)} database, {len(datasources)} datasource"
        )

        # Precarica i primi 2 schemi in background
        for ds in datasources[:2]:
            self._start_schema_load(api, ds["id"])

    def _on_connect_fail(self, error: str):
        self._sidebar.show_error(error)
        self._status.showMessage("Connessione fallita.")

    def _on_disconnect(self):
        reset_state()
        self._sidebar.show_disconnected()
        self._tabs.setEnabled(False)
        self._status.showMessage("Disconnesso.")

    # ══════════════════════════════════════════════════════════════
    # Schema
    # ══════════════════════════════════════════════════════════════

    def _on_schema_needed(self, ds_id: str):
        state = get_state()
        if ds_id and state.api and ds_id not in state.ds_schemas:
            self._start_schema_load(state.api, ds_id)

    def _start_schema_load(self, api, ds_id: str):
        state = get_state()
        if ds_id in state.ds_schemas:
            # Schema già in cache: aggiorna subito i tool
            self._copy_tool.update_schema(ds_id, state.ds_schemas[ds_id])
            return
        w = LoadSchemaWorker(api, ds_id)
        w.success.connect(self._on_schema_ok)
        w.failure.connect(self._on_schema_fail)
        w.finished.connect(lambda worker=w: self._cleanup_worker(worker))
        self._workers.append(w)
        w.start()

    def _on_schema_ok(self, ds_id: str, schema: dict):
        state = get_state()
        state.ds_schemas[ds_id] = schema
        self._copy_tool.update_schema(ds_id, schema)
        self._status.showMessage("Schema caricato.")

    def _on_schema_fail(self, ds_id: str, error: str):
        self._status.showMessage(f"Errore caricamento schema: {error}")

    # ══════════════════════════════════════════════════════════════
    # CopyDatasource tool — genera e esegui
    # ══════════════════════════════════════════════════════════════

    def _on_copy_generate(self, cfg: dict):
        state = get_state()

        def ds_label(ds_id: str) -> str:
            for d in state.datasources:
                if d["id"] == ds_id:
                    return f"{d['name']}  [{d['db_title']}]"
            return ds_id or "—"

        code = generate(
            name        = cfg["name"],
            src_id      = cfg["src_id"],
            tgt_id      = cfg["tgt_id"],
            src_label   = ds_label(cfg["src_id"]),
            tgt_label   = ds_label(cfg["tgt_id"]),
            src_schema  = cfg["src_schema"],
            tgt_schema  = cfg["tgt_schema"],
            filter_rows = cfg["filter_rows"],
            sort_rows   = cfg["sort_rows"],
            col_map     = cfg["col_map"],
        )
        self._copy_tool.set_code(code)

    def _on_copy_run(self, cfg: dict):
        state = get_state()

        src_schema = state.ds_schemas.get(cfg["src_id"], {})
        tgt_schema = state.ds_schemas.get(cfg["tgt_id"], {})

        if not src_schema or not tgt_schema:
            QMessageBox.warning(
                self, "Schema mancante",
                "Lo schema non è ancora caricato. Attendi qualche secondo e riprova."
            )
            return

        self._copy_tool.set_running(True)
        self._status.showMessage("Esecuzione in corso…")

        w = RunWorker(
            api         = state.api,
            src_id      = cfg["src_id"],
            tgt_id      = cfg["tgt_id"],
            src_schema  = src_schema,
            tgt_schema  = tgt_schema,
            filter_rows = cfg["filter_rows"],
            sort_rows   = cfg["sort_rows"],
            col_map     = cfg["col_map"],
        )
        w.success.connect(self._on_copy_run_ok)
        w.failure.connect(self._on_copy_run_fail)
        w.finished.connect(lambda worker=w: self._cleanup_worker(worker))
        self._workers.append(w)
        w.start()

    def _on_copy_run_ok(self, log: list):
        self._copy_tool.set_running(False)
        self._copy_tool.show_log(log)
        self._status.showMessage("Esecuzione completata.")

    def _on_copy_run_fail(self, error: str):
        self._copy_tool.set_running(False)
        self._copy_tool.show_log([f"✗ Errore fatale: {error}"])
        self._status.showMessage("Esecuzione fallita.")

    # ══════════════════════════════════════════════════════════════
    # Utility
    # ══════════════════════════════════════════════════════════════

    def _cleanup_worker(self, worker):
        if worker in self._workers:
            self._workers.remove(worker)
