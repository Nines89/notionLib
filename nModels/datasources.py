from __future__ import annotations
from typing import Optional

from nModels.base_object import NObj
from nEndpoints.datasources import (
    get_ds,
    get_ds_templates,
    create_ds,
    update_ds,
    move_ds,
    filter_a_ds,
    sort_a_ds,
    remove_ds_property,
    rename_ds_property,
)
from nTypes.rich_text import simple_rich_text_list
from utils.utils import check_url_or_id, resolve_response


class DataSourceTemplate:
    def __init__(self, data: dict):
        self._id: str = data.get("id", "")
        self._name: str = data.get("name", "")
        self._is_default: bool = data.get("is_default", False)

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_default(self) -> bool:
        return self._is_default

    def __repr__(self):
        tag = " [default]" if self._is_default else ""
        return f"<DataSourceTemplate '{self._name}'{tag} id={self._id}>"


class DataSourceError(Exception):
    pass


class NDataSource(NObj):
    def __init__(self, headers: dict, ds_id: str):
        super().__init__(headers, ds_id)
        self._title: str = ""
        self._schema: dict = {}
        self._parent_db_id: Optional[str] = None
        self._templates: Optional[list[DataSourceTemplate]] = None

    def _apply(self, data):
        # FIX: resolve_response normalizza sia NGET che dict grezzo
        raw = resolve_response(data)
        self._data = raw
        self._applied = True

        title_raw = raw.get("title", [])
        if isinstance(title_raw, list):
            self._title = "".join(t.get("plain_text", "") for t in title_raw)
        else:
            self._title = str(title_raw)

        self._schema = raw.get("properties", {})

        parent = raw.get("database_parent") or raw.get("parent", {})
        if isinstance(parent, dict):
            self._parent_db_id = (
                parent.get("database_id")
                or parent.get("data_source_id")
                or parent.get("page_id")
            )
        self._templates = None  # invalida cache

    def _refresh(self):
        self._apply(get_ds(self.headers, self.obj_id))

    def _ensure_data(self):
        if not self._applied:
            self._refresh()

    @property
    def title(self) -> str:
        self._ensure_data()
        return self._title

    @title.setter
    def title(self, value: str):
        self._title = value

    @property
    def schema(self) -> dict:
        self._ensure_data()
        return self._schema

    @property
    def parent_db_id(self) -> Optional[str]:
        self._ensure_data()
        return self._parent_db_id

    @property
    def templates(self) -> list[DataSourceTemplate]:
        self._ensure_data()
        if self._templates is None:
            raw = resolve_response(get_ds_templates(self.headers, self.obj_id))
            self._templates = [DataSourceTemplate(t) for t in raw.get("templates", [])]
        return self._templates

    @property
    def default_template(self) -> Optional[DataSourceTemplate]:
        return next((t for t in self.templates if t.is_default), None)

    def filter(self, filt: dict) -> list:
        return filter_a_ds(self.headers, self.obj_id, filt)

    def sort(self, sorties: dict) -> list:
        return sort_a_ds(self.headers, self.obj_id, sorties)

    def all_entries(self) -> list:
        return filter_a_ds(self.headers, self.obj_id, {})

    def query(self, filt: dict = None, sorties: dict = None) -> list:
        payload: dict = {}
        if filt:
            payload.update(filt)
        if sorties:
            payload.update(sorties)
        return filter_a_ds(self.headers, self.obj_id, payload)

    def add_property(self, prop_type: str, name: str):
        result = update_ds(self.headers, self.obj_id, prop_schema={prop_type: name})
        self._apply(result)
        return self

    def remove_property(self, prop_id_or_name: str):
        result = remove_ds_property(self.headers, self.obj_id, prop_id_or_name)
        self._apply(result)
        return self

    def rename_property(self, old_name: str, new_name: str):
        result = rename_ds_property(self.headers, self.obj_id, old_name, new_name)
        self._apply(result)
        return self

    def to_payload(self) -> dict:
        return {"title": simple_rich_text_list(self._title).to_dict()}

    def update(self, title: str = None, prop_schema: dict = None):
        if title is not None:
            self._title = title
        result = update_ds(
            self.headers,
            self.obj_id,
            title=self._title if title is not None else None,
            prop_schema=prop_schema,
        )
        self._apply(result)
        return result

    def move(self, new_parent_db_id: str):
        result = move_ds(self.headers, self.obj_id, check_url_or_id(new_parent_db_id))
        self._apply(result)
        return result

    def trash(self):
        result = update_ds(self.headers, self.obj_id, in_trash=True)
        self._apply(result)
        return result

    def restore(self):
        result = update_ds(self.headers, self.obj_id, in_trash=False)
        self._apply(result)
        return result

    def create_entry(self, properties: dict, template_id=None, icon=None, cover=None):
        from nModels.pages import DatabasePage
        from client.https import NPOST

        ds_id = check_url_or_id(self.obj_id)
        if hasattr(template_id, "id"):
            template_id = template_id.id

        payload: dict = {
            "parent": {"data_source_id": ds_id},
            "properties": properties,
        }
        if template_id:
            payload["template"] = {"type": "template_id", "template_id": template_id}
        if icon:
            payload["icon"] = icon.to_payload()
        if cover:
            payload["cover"] = cover.to_dict()

        data = NPOST(header=self.headers, url="https://api.notion.com/v1/pages", data=payload).response
        page = DatabasePage(self.headers, data["id"])
        page._apply(data)
        return page

    @classmethod
    def create(cls, headers: dict, title: str, parent_db_id: str,
               prop_schema: dict = None) -> "NDataSource":
        data = create_ds(headers, title=title, parent_id=parent_db_id, prop_schema=prop_schema)
        raw = resolve_response(data)
        ds = cls(headers, raw["id"])
        ds._apply(data)
        return ds

    def __repr__(self):
        self._ensure_data()
        return f"<NDataSource '{self._title}' id={self.obj_id}>"


class DataSourceFactory:
    @staticmethod
    def find(headers: dict, ds_id: str) -> NDataSource:
        ds_id = check_url_or_id(ds_id)
        data = get_ds(headers, ds_id)
        ds = NDataSource(headers, ds_id)
        ds._apply(data)
        return ds

# ──────────────────────────────────────────────
# Test manuale
# ──────────────────────────────────────────────

if __name__ == "__main__":
    from client.auth import NotionApiClient
    from nTypes.ds_filters import F, S

    api = NotionApiClient(key="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")

    db_url = "https://www.notion.so/2a7b7a8f729481919ac9c1853a813571?v=2a7b7a8f7294819bb426000cf2da4ff8&source=copy_link"

    # ── Carica DB e recupera DS tramite NDatabase ──
    from nModels.databases import DatabaseFactory
    db = DatabaseFactory.find(api.headers, db_url)
    print(db)

    ds_list = db.datasources
    if not ds_list:
        print("Nessun DS trovato.")
    else:
        ds = ds_list[0]
        print("\n--- DataSource ---")
        print(ds)
        print("Parent DB:", ds.parent_db_id)

        print("\nSchema:")
        for col_name, col_data in ds.schema.items():
            print(f"  {col_name!r:30} type={col_data.get('type')}")

        print("\nTemplates:", ds.templates)

        # ── Query ──────────────────────────────────
        # Tutte le entry
        all_e = ds.all_entries()
        print(f"\nTotale entry: {len(all_e)}")

        # Filtra per checkbox
        results = ds.filter({"filter": F.checkbox("check").equals(True)})
        print(f"Entry 'check': {len(results)}")

        # Ordina per nome
        sorted_e = ds.sort(S().get(("Name", True)))
        print(f"Sorted: {len(sorted_e)}")

        # Combina filtro + ordinamento
        combined = ds.query(
            filt={"filter": F.checkbox("check").equals(False)},
            sorties=S().get(("Name", True))
        )

        # ── Schema management ───────────────────────
        ds.add_property("select", "Categoria")
        ds.rename_property("Categoria", "Category")
        ds.remove_property("Category")

        # ── Crea entry ─────────────────────────────
        entry = ds.create_entry(
            properties={"Name": {"title": [{"text": {"content": "Test entry"}}]}},
            template_id=ds.default_template,
        )
        print("Entry creata:", entry)

        # ── Sposta DS sotto altro DB ────────────────
        ds_list[1].move("https://www.notion.so/ad506059a56f4626b7a4c4ee5a1f4430?v=e589b1d587604016ba6e9b840da871b3&source=copy_link")

        # ── Aggiorna titolo ─────────────────────────
        ds.update(title="Nuovo Titolo DS da ds e non da db")
