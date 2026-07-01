from __future__ import annotations
from typing import Optional

from notion_lib.nModels.base_object import NObj
from notion_lib.nEndpoints.datasources import (
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
from notion_lib.nTypes.rich_text import simple_rich_text_list
from notion_lib.utils.utils import check_url_or_id, resolve_response


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
        from notion_lib.nModels.pages import DatabasePage
        from notion_lib.client.https import NPOST

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

