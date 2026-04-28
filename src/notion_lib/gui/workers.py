"""
gui/workers.py
Worker QThread per operazioni API bloccanti.
Ogni worker emette success/failure e non tocca mai la UI direttamente.
"""

from PyQt6.QtCore import QThread, pyqtSignal


class ConnectWorker(QThread):
    """Connette all'API e carica database, datasource e pagine parent."""
    success = pyqtSignal(object, str, object, list, object)  # api, bot_name, dbs(dict), dss(list), pages(dict)
    failure = pyqtSignal(str)

    def __init__(self, api_key: str):
        super().__init__()
        self._api_key = api_key

    def run(self):
        try:
            from notion_lib.gui.logic.connector import connect
            api, bot, dbs, dss, pages = connect(self._api_key)
            self.success.emit(api, bot, dbs, dss, pages)
        except Exception as e:
            self.failure.emit(str(e))


class LoadSchemaWorker(QThread):
    """Carica lo schema (proprietà) di un singolo datasource."""
    success = pyqtSignal(str, dict)   # ds_id, schema
    failure = pyqtSignal(str, str)    # ds_id, errore

    def __init__(self, api, ds_id: str):
        super().__init__()
        self._api   = api
        self._ds_id = ds_id

    def run(self):
        try:
            from notion_lib.gui.logic.connector import load_schema
            schema = load_schema(self._api, self._ds_id)
            self.success.emit(self._ds_id, schema)
        except Exception as e:
            self.failure.emit(self._ds_id, str(e))


class LoadEntriesWorker(QThread):
    """Carica le entry di un datasource per selezione in UI."""
    success = pyqtSignal(str, list)   # ds_id, entries
    failure = pyqtSignal(str, str)    # ds_id, errore

    def __init__(self, api, ds_id: str):
        super().__init__()
        self._api = api
        self._ds_id = ds_id

    def run(self):
        try:
            from notion_lib.gui.logic.radio_todo_runner import list_entries
            entries = list_entries(self._api, self._ds_id)
            self.success.emit(self._ds_id, entries)
        except Exception as e:
            self.failure.emit(self._ds_id, str(e))


class RunWorker(QThread):
    """Esegue l'automazione (lettura, filtro, ordinamento, scrittura)."""
    success = pyqtSignal(list)   # righe di log
    failure = pyqtSignal(str)    # errore fatale

    def __init__(self, api, src_id, tgt_id, src_schema, tgt_schema,
                 filter_rows, sort_rows, col_map):
        super().__init__()
        self._api         = api
        self._src_id      = src_id
        self._tgt_id      = tgt_id
        self._src_schema  = src_schema
        self._tgt_schema  = tgt_schema
        self._filter_rows = filter_rows
        self._sort_rows   = sort_rows
        self._col_map     = col_map

    def run(self):
        try:
            from notion_lib.gui.logic.runner import run_automation
            log = run_automation(
                self._api, self._src_id, self._tgt_id,
                self._src_schema, self._tgt_schema,
                self._filter_rows, self._sort_rows, self._col_map,
            )
            self.success.emit(log)
        except Exception as e:
            self.failure.emit(str(e))


class InsertBlockWorker(QThread):
    """Inserisce un blocco in una pagina."""
    success = pyqtSignal(str)   # messaggio successo
    failure = pyqtSignal(str)   # errore

    def __init__(self, api, page_id: str, block):
        super().__init__()
        self._api     = api
        self._page_id = page_id
        self._block   = block

    def run(self):
        try:
            from notion_lib.nModels.pages import PageFactory
            page = PageFactory.find(self._api.headers, self._page_id)
            page.append_children([self._block])
            self.success.emit(f"Blocco '{self._block.type}' inserito con successo!")
        except Exception as e:
            self.failure.emit(str(e))


class CreateDataSourceWorker(QThread):
    """Crea un nuovo datasource con schema."""
    success = pyqtSignal(str, str)   # ds_id, messaggio
    failure = pyqtSignal(str)        # errore

    def __init__(self, api, db_id: str, name: str, prop_schema: dict):
        super().__init__()
        self._api = api
        self._db_id = db_id
        self._name = name
        self._prop_schema = prop_schema

    def run(self):
        try:
            from notion_lib.nModels.datasources import NDataSource
            ds = NDataSource.create(
                headers=self._api.headers,
                title=self._name,
                parent_db_id=self._db_id,
                prop_schema=self._prop_schema
            )
            self.success.emit(
                ds.obj_id,
                f"DataSource '{self._name}' creato con {len(self._prop_schema)} proprietà!"
            )
        except Exception as e:
            self.failure.emit(str(e))


class CreateDSEntryWorker(QThread):
    """Crea una nuova entry o template in un datasource."""
    success = pyqtSignal(str)  # messaggio
    failure = pyqtSignal(str)  # errore

    def __init__(self, api, ds_id: str, properties: dict, is_template: bool = False):
        super().__init__()
        self._api = api
        self._ds_id = ds_id
        self._properties = properties
        self._is_template = is_template

    def run(self):
        try:
            from notion_lib.nModels.datasources import DataSourceFactory
            ds = DataSourceFactory.find(self._api.headers, self._ds_id)

            # Crea entry o template
            if self._is_template:
                ds.create_entry(properties=self._properties, is_template=True)
                msg = "Template creato con successo!"
            else:
                ds.create_entry(properties=self._properties)
                msg = "Entry creata con successo!"

            self.success.emit(msg)
        except Exception as e:
            self.failure.emit(str(e))

class CreateRepeatedBlocksWorker(QThread):
    """Crea pagine ripetute usando titolo dinamico + blueprint blocchi JSON."""
    success = pyqtSignal(list)
    failure = pyqtSignal(str)

    def __init__(self, api, cfg: dict):
        super().__init__()
        self._api = api
        self._cfg = cfg

    def _build_title_items(self):
        mode = self._cfg.get("mode", "range")
        if mode == "custom":
            titles = self._cfg.get("custom_titles") or []
            if not titles:
                raise ValueError("Nessun titolo inserito in modalità lista personalizzata.")
            return [(i, title) for i, title in enumerate(titles, start=1)]

        template = self._cfg.get("title_template") or "Pagina {index}"
        start = int(self._cfg.get("start_index") or 1)
        total = int(self._cfg.get("count") or 1)
        out = []
        for idx in range(start, start + total):
            out.append((idx, template.format(index=idx, title="")))
        return out

    @staticmethod
    def _render_text(text: str, index: int, title: str):
        return (text or "").format(index=index, title=title)

    def _build_blocks(self, blueprint: list, index: int, title: str):
        from notion_lib.nModels.blocks.heading import Heading1, Heading2, Heading3
        from notion_lib.nModels.blocks.paragraph import ParagraphBlock
        from notion_lib.nModels.blocks.table import TableBlock, TableRowBlock
        from notion_lib.nTypes.rich_text import simple_rich_text_list

        blocks = []
        for item in blueprint:
            btype = item.get("type", "paragraph")
            text = self._render_text(item.get("text", ""), index, title)

            if btype == "heading_1":
                blocks.append(Heading1.create(text=text))
            elif btype == "heading_2":
                blocks.append(Heading2.create(text=text))
            elif btype == "heading_3":
                blocks.append(Heading3.create(text=text))
            elif btype == "paragraph":
                blocks.append(ParagraphBlock.create(text=text))
            elif btype == "table":
                columns = item.get("columns") or ["Col 1", "Col 2"]
                rows = int(item.get("rows", 1))
                header = TableRowBlock.create(cells=[simple_rich_text_list(str(c)) for c in columns])
                body_rows = [
                    TableRowBlock.create(cells=[simple_rich_text_list("") for _ in columns])
                    for _ in range(max(1, rows))
                ]
                blocks.append(TableBlock.create(
                    table_width=len(columns),
                    has_column_header=True,
                    has_row_header=False,
                    cells=[header] + body_rows,
                ))
        return blocks

    def run(self):
        log = []
        try:
            import json
            from notion_lib.nModels.datasources import DataSourceFactory

            ds = DataSourceFactory.find(self._api.headers, self._cfg["target_id"])
            title_prop = self._cfg["title_prop"]
            title_items = self._build_title_items()

            raw_blueprint = self._cfg.get("blocks_blueprint") or "[]"
            blueprint = json.loads(raw_blueprint)
            if not isinstance(blueprint, list):
                raise ValueError("Il blueprint JSON deve essere una lista di blocchi.")

            for index, title in title_items:
                props = {
                    title_prop: {"title": [{"text": {"content": title}}]}
                }
                page = ds.create_entry(properties=props)
                blocks = self._build_blocks(blueprint, index=index, title=title)
                if blocks:
                    page.append_children(blocks)
                log.append(f"✓ Creata pagina {title} ({len(blocks)} blocchi)")

            log.append(f"✓ Completato: create {len(title_items)} pagine.")
            self.success.emit(log)
        except Exception as e:
            self.failure.emit(str(e))


class RunRadioTodoWorker(QThread):
    """Esegue l'automazione radio-button su una proprietà checkbox."""
    success = pyqtSignal(list)
    failure = pyqtSignal(str)

    def __init__(self, api, cfg: dict):
        super().__init__()
        self._api = api
        self._cfg = cfg

    def run(self):
        try:
            from notion_lib.gui.logic.radio_todo_runner import run_radio_todo
            log = run_radio_todo(
                api=self._api,
                ds_id=self._cfg["ds_id"],
                todo_prop=self._cfg["todo_prop"],
                selected_entry_id=self._cfg["entry_id"],
            )
            self.success.emit(log)
        except Exception as e:
            self.failure.emit(str(e))
