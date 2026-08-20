from __future__ import annotations
from typing import Optional

from notion_lib.nModels.base_object import NObj
from notion_lib.nEndpoints.pages import (
    get_page,
    update_page,
    trash_page,
    restore_page,
    get_block_children,
)
from notion_lib.nEndpoints.blocks import append_children as _append_children
from notion_lib.nTypes.icons import IconFactory
from notion_lib.nTypes.files import n_file, FileTypeExternal
from notion_lib.nTypes.page_properties import PropertyValue, PropertyFactory
from notion_lib.utils.utils import check_url_or_id, resolve_response


class PageError(Exception):
    pass


# ──────────────────────────────────────────────
# Base
# ──────────────────────────────────────────────

class NPage(NObj):
    def __init__(self, headers: dict, page_id: str):
        super().__init__(headers, page_id)

    def _apply(self, data):
        self._data = resolve_response(data)
        self._applied = True

    def _refresh(self):
        self._data = resolve_response(get_page(self.headers, self.obj_id))
        self._applied = True

    def _ensure_data(self):
        if not self._applied or self._data is None:
            self._refresh()

    # ── shared properties ───────────────────────────

    @property
    def icon(self):
        self._ensure_data()
        raw = self._data.get("icon")
        return IconFactory.find(raw) if raw else None

    @icon.setter
    def icon(self, value):
        self._pending_icon = value.to_payload() if value else None

    @property
    def cover(self):
        self._ensure_data()
        raw = self._data.get("cover")
        return n_file(raw) if raw else None

    @cover.setter
    def cover(self, value: Optional[FileTypeExternal]):
        self._pending_cover = value.to_dict() if value else None

    @property
    def url(self) -> Optional[str]:
        self._ensure_data()
        return self._data.get("url")

    # ── children ────────────────────────────────────

    def get_children(self) -> list:
        from notion_lib.nModels.blocks.base_block import NFactory
        raw_blocks = get_block_children(self.headers, self.obj_id)
        # Children list already has full block payloads — avoid N+1 get_block calls.
        return [NFactory.from_raw(self.headers, blk) for blk in raw_blocks]

    def append_children(self, children: list) -> list:
        payload = [child.to_payload() for child in children]
        return _append_children(self.headers, self.obj_id, payload)

    # ── lifecycle ────────────────────────────────────

    def to_payload(self) -> dict:
        raise NotImplementedError

    def update(self):
        payload = self.to_payload()
        if hasattr(self, "_pending_icon"):
            payload["icon"] = self._pending_icon
            del self._pending_icon
        if hasattr(self, "_pending_cover"):
            payload["cover"] = self._pending_cover
            del self._pending_cover
        result = update_page(self.headers, self.obj_id, payload)
        self._apply(result)
        return result

    def trash(self):
        result = trash_page(self.headers, self.obj_id)
        self._apply(result)
        return result

    def restore(self):
        result = restore_page(self.headers, self.obj_id)
        self._apply(result)
        return result

    def __repr__(self):
        self._ensure_data()
        return f"<{self.__class__.__name__} id={self.obj_id}>"


# ──────────────────────────────────────────────
# SimplePage  (parent = page | workspace | block)
# ──────────────────────────────────────────────

class SimplePage(NPage):
    def __init__(self, headers: dict, page_id: str):
        super().__init__(headers, page_id)
        self._title: str = ""

    def _apply(self, data):
        super()._apply(data)
        try:
            title_items = self._data["properties"]["title"]["title"]
            self._title = "".join(t.get("plain_text", "") for t in title_items)
        except (KeyError, TypeError):
            self._title = ""

    @property
    def title(self) -> str:
        self._ensure_data()
        return self._title

    @title.setter
    def title(self, value: str):
        self._title = value

    def to_payload(self) -> dict:
        from notion_lib.nTypes.rich_text import simple_rich_text_list
        return {
            "properties": {
                "title": {"title": simple_rich_text_list(self._title).to_dict()}
            }
        }

    @classmethod
    def create(cls,
               headers: dict,
               parent_id: str,
               title: str,
               icon=None,
               cover=None) -> "SimplePage":
        from notion_lib.client.https import NPOST
        parent_id = check_url_or_id(parent_id)
        payload: dict = {
            "parent": {"page_id": parent_id},
            "properties": {
                "title": [{"type": "text", "text": {"content": title}}]
            }
        }
        if icon:
            payload["icon"] = icon.to_payload()
        if cover:
            payload["cover"] = cover.to_dict()
        data = NPOST(header=headers, url="https://api.notion.com/v1/pages", data=payload).response
        page = cls(headers, data["id"])
        page._apply(data)
        return page

    def __repr__(self):
        self._ensure_data()
        return f"<SimplePage '{self._title}' id={self.obj_id}>"


# ──────────────────────────────────────────────
# DatabasePage  (parent = database | data_source)
# ──────────────────────────────────────────────

class DatabasePage(NPage):
    def __init__(self, headers: dict, page_id: str):
        super().__init__(headers, page_id)
        self._properties: dict[str, PropertyValue] = {}

    def _apply(self, data):
        # FIX: resolve_response gestisce sia NGET che dict grezzo
        super()._apply(data)
        self._properties = {
            name: PropertyFactory.from_data(name, prop_data)
            for name, prop_data in self._data.get("properties", {}).items()
        }

    @property
    def properties(self) -> dict[str, PropertyValue]:
        self._ensure_data()
        return self._properties

    def prop(self, name: str) -> PropertyValue:
        self._ensure_data()
        if name not in self._properties:
            available = list(self._properties.keys())
            raise KeyError(f"Property '{name}' non trovata. Disponibili: {available}")
        return self._properties[name]

    def set_prop(self, name: str, value) -> "DatabasePage":
        self.prop(name).value = value
        return self

    def title(self) -> str:
        self._ensure_data()
        title_prop = next(
            (p for p in self._properties.values() if p.prop_type == "title"),
            None
        )
        return title_prop.value if title_prop else ""

    def to_payload(self) -> dict:
        props = {}
        for prop in self._properties.values():
            try:
                props.update(prop.to_payload())
            except AttributeError:
                pass  # read-only: skip silenziosamente
        return {"properties": props}

    @classmethod
    def create(cls,
               headers: dict,
               parent_db_id: str,
               properties: dict,
               icon=None,
               cover=None) -> "DatabasePage":
        from notion_lib.client.https import NPOST
        parent_db_id = check_url_or_id(parent_db_id)
        payload: dict = {
            "parent": {"data_source_id": parent_db_id},
            "properties": properties
        }
        if icon:
            payload["icon"] = icon.to_payload()
        if cover:
            payload["cover"] = cover.to_dict()
        data = NPOST(header=headers, url="https://api.notion.com/v1/pages", data=payload).response
        page = cls(headers, data["id"])
        page._apply(data)
        return page

    def __repr__(self):
        self._ensure_data()
        return f"<DatabasePage '{self.title()}' id={self.obj_id}>"


# ──────────────────────────────────────────────
# PageFactory
# ──────────────────────────────────────────────

class PageFactory:
    @staticmethod
    def find(headers: dict, page_id: str) -> NPage:
        page_id = check_url_or_id(page_id)
        raw = resolve_response(get_page(headers, page_id))

        parent_type = raw.get("parent", {}).get("type", "")

        # FIX: aggiunto "database_id" — prima veniva trattato come SimplePage
        if parent_type in ("data_source_id", "database_id"):
            page = DatabasePage(headers, page_id)
        else:
            # page_id, workspace, block_id → SimplePage
            page = SimplePage(headers, page_id)

        page._apply(raw)
        return page


