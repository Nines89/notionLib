"""
gui/logic/connector.py
Funzioni pure per connessione API ed esplorazione workspace.
Nessuna dipendenza da PyQt6.

Struttura reale verificata sull'API:
  search(None) restituisce:  pagine + data_source  (i database NON compaiono)
  data_source.parent.database_id   → ID del database parent
  data_source.database_parent.page_id → ID della pagina nonno (già in search)
  data_source.name → lista rich-text: name[0]['plain_text']
"""

import sys
sys.path.insert(0, "")


def connect(api_key: str):
    """
    Connette all'API Notion e restituisce:
      (api, bot_name, databases, datasources, pages)

    pages:       dict  page_id -> {id, title}
    databases:   dict  db_id   -> {id, title, parent_page_id}
    datasources: list  [{id, name, db_id, page_id}]
    """
    from src.notion_lib.client.auth import NotionApiClient
    from src.notion_lib.nEndpoints.users import get_bot_token
    from src.notion_lib.nEndpoints.searches import search_by_title
    from src.notion_lib.nEndpoints.databases import get_db

    api      = NotionApiClient(key=api_key)
    bot_name = get_bot_token(api.headers).response.get("name", "Bot")

    # ── Step 1: carica tutto ciò che l'integrazione vede ─────────
    raw_results = []
    try:
        raw_results = search_by_title(api.headers).response.get("results", [])
    except Exception as e:
        raise RuntimeError(f"Errore nella search: {e}")

    # ── Step 2: separa pagine e datasource ────────────────────────
    pages_raw = [r for r in raw_results if r.get("object") == "page"]
    ds_raw    = [r for r in raw_results if r.get("object") == "data_source"]

    # Indicizza le pagine per ID (senza trattini)
    pages: dict = {}
    for pg in pages_raw:
        pid   = pg["id"].replace("-", "")
        title = _page_title(pg)
        pages[pid] = {"id": pid, "title": title}

    # ── Step 3: carica i database unici dai datasource ────────────
    # Il database NON compare nella search → get_db per ognuno
    db_ids_needed = set()
    for ds in ds_raw:
        db_id = _ds_parent_db_id(ds)
        if db_id:
            db_ids_needed.add(db_id.replace("-", ""))

    databases: dict = {}   # db_id (no trattini) -> {id, title, parent_page_id}
    for db_id in db_ids_needed:
        try:
            raw = get_db(api.headers, db_id)
            obj = raw.response if hasattr(raw, "response") else raw
            clean_id       = obj["id"].replace("-", "")
            title          = _db_title(obj)
            parent_page_id = _db_parent_page_id(obj)
            databases[clean_id] = {
                "id":             clean_id,
                "title":          title,
                "parent_page_id": parent_page_id,
            }
        except Exception:
            pass

    # ── Step 4: normalizza datasource ─────────────────────────────
    datasources = []
    for ds in ds_raw:
        ds_id    = ds["id"].replace("-", "")
        db_id    = (_ds_parent_db_id(ds) or "").replace("-", "")
        page_id  = (_ds_grandparent_page_id(ds) or "").replace("-", "")
        name     = _ds_name(ds)
        db_title = databases.get(db_id, {}).get("title", "?")
        datasources.append({
            "id":       ds_id,
            "name":     name,
            "db_id":    db_id,
            "db_title": db_title,
            "page_id":  page_id,
        })

    return api, bot_name, databases, datasources, pages


def load_schema(api, ds_id: str) -> dict:
    """Restituisce il dizionario delle proprietà di un datasource."""
    from src.notion_lib.nModels.datasources import DataSourceFactory
    return DataSourceFactory.find(api.headers, ds_id).schema


# ── Helpers privati ───────────────────────────────────────────────

def _ds_parent_db_id(ds: dict) -> str:
    """ID del database parent di un datasource (da parent.database_id)."""
    return ds.get("parent", {}).get("database_id", "")


def _ds_grandparent_page_id(ds: dict) -> str:
    """ID della pagina nonno (da database_parent.page_id)."""
    return ds.get("database_parent", {}).get("page_id", "")


def _ds_name(ds: dict) -> str:
    """
    Il campo title di un datasource è una lista rich-text.
    Verificato sull'API reale: ds['title'][0]['plain_text']
    """
    title = ds.get("title")
    if isinstance(title, list) and title:
        return title[0].get("plain_text", "?")
    if isinstance(title, str):
        return title or "?"
    return "?"


def _page_title(pg: dict) -> str:
    """Estrae il titolo da un oggetto pagina grezzo."""
    props = pg.get("properties", {})
    for prop in props.values():
        if prop.get("type") == "title":
            items = prop.get("title", [])
            if items:
                return items[0].get("plain_text", "") or "Pagina senza titolo"
    return "Pagina senza titolo"


def _db_title(db: dict) -> str:
    """Estrae il titolo da un oggetto database grezzo."""
    t = db.get("title", [])
    return t[0].get("plain_text", "?") if t else "?"


def _db_parent_page_id(db: dict) -> str:
    """
    ID della pagina parent di un database.
    parent.type può essere 'page_id', 'workspace', 'block_id'.
    """
    p = db.get("parent", {})
    if p.get("type") == "page_id":
        return p.get("page_id", "").replace("-", "")
    return ""
