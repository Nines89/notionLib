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
            from gui.logic.connector import connect
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
            from gui.logic.connector import load_schema
            schema = load_schema(self._api, self._ds_id)
            self.success.emit(self._ds_id, schema)
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
            from gui.logic.runner import run_automation
            log = run_automation(
                self._api, self._src_id, self._tgt_id,
                self._src_schema, self._tgt_schema,
                self._filter_rows, self._sort_rows, self._col_map,
            )
            self.success.emit(log)
        except Exception as e:
            self.failure.emit(str(e))
