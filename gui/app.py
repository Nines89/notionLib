"""
gui/app.py
MainWindow — finestra principale.
Assembla sidebar + tabs, gestisce workers, coordina i componenti.
NON contiene logica di business.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QTabWidget,
    QStatusBar, QMessageBox, QFrame, QDialog
)

from gui.state import get_state, reset_state
from gui.workers import ConnectWorker, LoadSchemaWorker, RunWorker, CreateRepeatedBlocksWorker
from gui.logic.codegen import generate

from gui.widgets.sidebar       import SidebarWidget
from gui.widgets.workspace_tab import WorkspaceTab
from gui.widgets.automations_tab import AutomationsTab
from gui.widgets.automation_tools.copy_datasource import CopyDatasourceTool
from gui.widgets.automation_tools.repeated_blocks import RepeatedBlocksTool


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

        # ── Sidebar (di nuovo a sinistra) ─────────────────────────
        self._sidebar = SidebarWidget()
        self._sidebar.connect_requested.connect(self._on_connect)
        self._sidebar.disconnect_requested.connect(self._on_disconnect)
        root.addWidget(self._sidebar)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet("color: #26334E;")
        root.addWidget(sep)

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
        self._ws_tab.action_insert_block.connect(self._on_insert_block_requested)
        self._ws_tab.action_add_ds.connect(self._on_create_datasource_requested)
        self._ws_tab.action_add_ds_page.connect(self._on_create_ds_entry_requested)
        self._ws_tab.action_open_page.connect(self._on_open_page_blocks)
        self._ws_tab.action_open_datasource.connect(self._on_open_datasource)
        self._tabs.addTab(self._ws_tab, "  🪐 Panorama  ")

        # Tab 2: Automazioni (con tile + stack interno)
        self._auto_tab = AutomationsTab()
        self._tabs.addTab(self._auto_tab, "  🤖 Flussi  ")

        # Registra i tool nell'AutomationsTab
        self._copy_tool = CopyDatasourceTool()
        self._auto_tab.register_tool(
            icon="🧠",
            title="Sync DataSource",
            description="Trasforma e sincronizza record tra due datasource con filtri avanzati e mapping intelligente.",
            gradient_start="#6366F1",  # ← NUOVO: indigo
            gradient_end="#8B5CF6",  # ← NUOVO: purple
            tool_widget=self._copy_tool,
        )

        self._repeat_tool = RepeatedBlocksTool()
        self._auto_tab.register_tool(
            icon="🗓️",
            title="Blocchi ripetuti",
            description="Crea serie di pagine con la stessa struttura, ideale per settimane, sprint o checklist periodiche.",
            gradient_start="#0EA5E9",
            gradient_end="#22D3EE",
            tool_widget=self._repeat_tool,
        )

        content_lay.addWidget(self._tabs)
        root.addWidget(content, stretch=1)

        # ── Connessioni segnali ───────────────────────────────────
        self._copy_tool.schema_needed.connect(self._on_schema_needed)
        self._copy_tool.generate_requested.connect(self._on_copy_generate)
        self._copy_tool.run_requested.connect(self._on_copy_run)
        self._repeat_tool.schema_needed.connect(self._on_schema_needed)
        self._repeat_tool.generate_requested.connect(self._on_repeat_generate)
        self._repeat_tool.run_requested.connect(self._on_repeat_run)

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
        self._repeat_tool.populate_datasources(datasources)
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
            self._repeat_tool.update_schema(ds_id, state.ds_schemas[ds_id])
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
        self._repeat_tool.update_schema(ds_id, schema)
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

    # ══════════════════════════════════════════════════════════════
    # Create Block
    # ══════════════════════════════════════════════════════════════

    def _on_insert_block_requested(self, page_id: str):
        """Mostra dialog per inserire un blocco nella pagina."""
        state = get_state()
        page_info = state.pages.get(page_id.replace("-", ""))
        page_title = page_info.get("title", "Pagina") if page_info else "Pagina"

        from gui.widgets.block_insert_dialog import InsertBlockDialog
        dialog = InsertBlockDialog(page_title, parent=self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            block = dialog.get_block()
            if not block:
                return

            self._status.showMessage("Inserimento blocco in corso...")

            from gui.workers import InsertBlockWorker
            w = InsertBlockWorker(state.api, page_id, block)
            w.success.connect(self._on_insert_block_ok)
            w.failure.connect(self._on_insert_block_fail)
            w.finished.connect(lambda worker=w: self._cleanup_worker(worker))
            self._workers.append(w)
            w.start()

    def _on_insert_block_ok(self, msg: str):
        self._status.showMessage(msg)
        QMessageBox.information(self, "Successo", msg)

    def _on_insert_block_fail(self, error: str):
        self._status.showMessage("Inserimento fallito.")
        QMessageBox.critical(self, "Errore", f"Impossibile inserire il blocco:\n{error}")

    def _on_open_page_blocks(self, page_id: str):
        state = get_state()
        if not state.api:
            return
        page_info = state.pages.get(page_id.replace("-", ""))
        page_title = page_info.get("title", "Pagina") if page_info else "Pagina"

        from gui.widgets.page_blocks_dialog import PageBlocksDialog
        dialog = PageBlocksDialog(
            page_id=page_id,
            page_title=page_title,
            headers=state.api.headers,
            parent=self,
        )
        dialog.exec()

    def _on_open_datasource(self, ds_id: str):
        state = get_state()
        if not state.api:
            return

        # Cerca info datasource
        ds_info = next(
            (ds for ds in state.datasources if ds["id"] == ds_id.replace("-", "")),
            None,
        )
        if not ds_info:
            return

        ds_name = f"{ds_info['name']}  [{ds_info['db_title']}]"
        schema = state.ds_schemas.get(ds_id) or state.ds_schemas.get(ds_id.replace("-", ""))

        from gui.widgets.datasource_table_dialog import DataSourceTableDialog
        dialog = DataSourceTableDialog(
            ds_id=ds_id,
            ds_name=ds_name,
            headers=state.api.headers,
            schema=schema,  # None → il worker lo carica internamente
            parent=self,
        )
        dialog.exec()

        # Aggiorna cache schema se il worker l'ha caricato (schema era None)
        # Il worker espone schema via il segnale success; qui lo recuperiamo
        # direttamente dal DataSourceFactory dopo che il dialog è chiuso
        # solo se non era già in cache.
        if not schema and state.api:
            self._start_schema_load(state.api, ds_id)
    # ══════════════════════════════════════════════════════════════
    # Create DataSource
    # ══════════════════════════════════════════════════════════════

    def _on_create_datasource_requested(self, db_id: str):
        """Mostra dialog per creare un datasource."""
        state = get_state()
        db_info = state.databases.get(db_id.replace("-", ""))
        db_title = db_info.get("title", "Database") if db_info else "Database"

        from gui.widgets.datasource_create_dialog import DataSourceCreateDialog
        from PyQt6.QtWidgets import QDialog

        dialog = DataSourceCreateDialog(db_id, db_title, parent=self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            cfg = dialog.get_config()

            self._status.showMessage("Creazione datasource in corso...")

            from gui.workers import CreateDataSourceWorker
            w = CreateDataSourceWorker(
                state.api,
                cfg["db_id"],
                cfg["name"],
                cfg["prop_schema"]
            )
            w.success.connect(self._on_create_datasource_ok)
            w.failure.connect(self._on_create_datasource_fail)
            w.finished.connect(lambda worker=w: self._cleanup_worker(worker))
            self._workers.append(w)
            w.start()

    def _on_create_datasource_ok(self, ds_id: str, msg: str):
        self._status.showMessage(msg)
        QMessageBox.information(self, "Successo", msg)

        # Ricarica workspace per mostrare il nuovo datasource
        self._refresh_workspace()

    def _on_create_datasource_fail(self, error: str):
        self._status.showMessage("Creazione fallita.")
        QMessageBox.critical(self, "Errore", f"Impossibile creare il datasource:\n{error}")

    def _refresh_workspace(self):
        """Ricarica i dati del workspace."""
        state = get_state()
        if not state.api:
            return

        self._status.showMessage("Aggiornamento workspace...")
        w = ConnectWorker(state.api.headers["Authorization"].replace("Bearer ", ""))
        w.success.connect(self._on_connect_ok)
        w.failure.connect(lambda e: self._status.showMessage("Aggiornamento fallito"))
        w.finished.connect(lambda worker=w: self._cleanup_worker(worker))
        self._workers.append(w)
        w.start()

    # ══════════════════════════════════════════════════════════════
    # Create DataSource Page
    # ══════════════════════════════════════════════════════════════

    def _on_create_ds_entry_requested(self, ds_id: str):
        """Mostra dialog per creare una entry nel datasource."""
        state = get_state()

        # Cerca info datasource
        ds_info = None
        for ds in state.datasources:
            if ds["id"] == ds_id.replace("-", ""):
                ds_info = ds
                break

        if not ds_info:
            QMessageBox.warning(self, "Errore", "DataSource non trovato.")
            return

        ds_name = ds_info["name"]

        # Verifica se schema è in cache
        if ds_id not in state.ds_schemas:
            self._on_schema_needed(ds_id)
            QMessageBox.information(
                self, "Caricamento schema",
                "Lo schema del datasource è in caricamento. Riprova tra qualche secondo."
            )
            return

        schema = state.ds_schemas[ds_id]

        from gui.widgets.datasource_entry_dialog import DataSourceEntryDialog
        from PyQt6.QtWidgets import QDialog

        dialog = DataSourceEntryDialog(ds_id, ds_name, schema, parent=self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            props = dialog.get_properties()

            self._status.showMessage("Creazione entry in corso...")

            from gui.workers import CreateDSEntryWorker
            w = CreateDSEntryWorker(state.api, ds_id, props)
            w.success.connect(self._on_create_ds_entry_ok)
            w.failure.connect(self._on_create_ds_entry_fail)
            w.finished.connect(lambda worker=w: self._cleanup_worker(worker))
            self._workers.append(w)
            w.start()

    def _on_create_ds_entry_ok(self, msg: str):
        self._status.showMessage(msg)
        QMessageBox.information(self, "Successo", msg)

    def _on_create_ds_entry_fail(self, error: str):
        self._status.showMessage("Creazione fallita.")
        QMessageBox.critical(self, "Errore", f"Impossibile creare l'entry:\n{error}")

    # ══════════════════════════════════════════════════════════════
    # RepeatedBlocks tool — genera e esegui
    # ══════════════════════════════════════════════════════════════

    def _on_repeat_generate(self, cfg: dict):
        from gui.logic.repeated_blocks_codegen import generate_repeated_blocks_code
        state = get_state()

        def ds_label(ds_id: str) -> str:
            for d in state.datasources:
                if d["id"] == ds_id:
                    return f"{d['name']}  [{d['db_title']}]"
            return ds_id or "—"

        code = generate_repeated_blocks_code(cfg, ds_label(cfg["target_id"]))
        self._repeat_tool.set_code(code)

    def _on_repeat_run(self, cfg: dict):
        state = get_state()
        self._repeat_tool.set_running(True)
        self._status.showMessage("Creazione pagine ripetute in corso…")

        w = CreateRepeatedBlocksWorker(state.api, cfg)
        w.success.connect(self._on_repeat_run_ok)
        w.failure.connect(self._on_repeat_run_fail)
        w.finished.connect(lambda worker=w: self._cleanup_worker(worker))
        self._workers.append(w)
        w.start()

    def _on_repeat_run_ok(self, log: list):
        self._repeat_tool.set_running(False)
        self._repeat_tool.show_log(log)
        self._status.showMessage("Creazione template completata.")

    def _on_repeat_run_fail(self, error: str):
        self._repeat_tool.set_running(False)
        self._repeat_tool.show_log([f"✗ Errore fatale: {error}"])
        self._status.showMessage("Creazione template fallita.")
