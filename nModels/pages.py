from __future__ import annotations
from typing import Optional

from nModels.base_object import NObj
from nEndpoints.pages import (
    get_page,
    update_page,
    trash_page,
    restore_page,
    get_block_children,
)
from nEndpoints.blocks import append_children as _append_children
from nTypes.icons import IconFactory
from nTypes.files import n_file, FileTypeExternal
from nTypes.page_properties import PropertyValue, PropertyFactory
from utils.utils import check_url_or_id


class PageError(Exception):
    pass


# ──────────────────────────────────────────────
# Base
# ──────────────────────────────────────────────

class NPage(NObj):
    """
    Base class for all Notion pages.

    Shared behaviour:
      - icon / cover read + write
      - url, parent (inherited from NObj)
      - get_children() → list[BlockImpl]
      - append_children(children)
      - update(), trash(), restore()

    Subclasses decide how to build to_payload().
    """

    def __init__(self, headers: dict, page_id: str):
        super().__init__(headers, page_id)

    # ── data lifecycle ──────────────────────────────

    def _apply(self, data: dict):
        self._data = data
        self._applied = True

    def _refresh(self):
        self._data = get_page(self.headers, self.obj_id)
        self._apply(self._data)

    def _ensure_data(self):
        if not self._applied:
            self._refresh()

    # ── shared properties ───────────────────────────

    @property
    def icon(self):
        self._ensure_data()
        raw = self._data.response.get("icon")
        return IconFactory.find(raw) if raw else None

    @icon.setter
    def icon(self, value):
        """Pass an NEmoji / NCustomEmoji / FileTypeExternal instance, or None to clear."""
        self._pending_icon = value.to_payload() if value else None

    @property
    def cover(self):
        self._ensure_data()
        raw = self._data.response.get("cover")
        return n_file(raw) if raw else None

    @cover.setter
    def cover(self, value: Optional[FileTypeExternal]):
        """Notion only allows external URLs as covers."""
        self._pending_cover = value.to_dict() if value else None

    @property
    def url(self) -> Optional[str]:
        self._ensure_data()
        return self._data.response.get("url")

    # ── children ────────────────────────────────────

    def get_children(self) -> list:
        from nModels.blocks.base_block import NFactory
        raw_blocks = get_block_children(self.headers, self.obj_id)
        return [NFactory.find(self.headers, blk["id"]) for blk in raw_blocks]

    def append_children(self, children: list) -> list:
        payload = [child.to_payload() for child in children]
        return _append_children(self.headers, self.obj_id, payload)

    # ── lifecycle ────────────────────────────────────

    def to_payload(self) -> dict:
        raise NotImplementedError

    def update(self):
        """
        Builds the properties payload, merges any pending icon / cover,
        and sends a PATCH to the pages endpoint.
        """
        payload = self.to_payload()
        if hasattr(self, "_pending_icon"):
            payload["icon"] = self._pending_icon
            del self._pending_icon
        if hasattr(self, "_pending_cover"):
            payload["cover"] = self._pending_cover
            del self._pending_cover
        result = update_page(self.headers, self.obj_id, payload)
        # Re-apply so the local state stays in sync
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
# SimplePage  (parent = page | workspace)
# ──────────────────────────────────────────────

class SimplePage(NPage):
    """
    A Notion page whose parent is another page or the workspace.
    Only carries a title (no typed DB properties).

    Usage:
        page = PageFactory.find(headers, page_url)
        page.title = "New title"
        page.update()

        page.append_children([ParagraphBlock.create("Hello")])
        blocks = page.get_children()
    """

    def __init__(self, headers: dict, page_id: str):
        super().__init__(headers, page_id)
        self._title: str = ""

    def _apply(self, data: dict):
        super()._apply(data)
        try:
            title_items = data["properties"]["title"]["title"]
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
        from nTypes.rich_text import simple_rich_text_list
        return {
            "properties": {
                "title": {
                    "title": simple_rich_text_list(self._title).to_dict()
                }
            }
        }

    @classmethod
    def create(cls,
               headers: dict,
               parent_id: str,
               title: str,
               icon=None,
               cover=None) -> "SimplePage":
        """
        Create a new simple page and return the hydrated SimplePage object.
        """
        from nEndpoints.pages import create_page as _create_page
        from client.https import NPOST

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

        data = NPOST(
            header=headers,
            url="https://api.notion.com/v1/pages",
            data=payload
        ).response
        page = cls(headers, data["id"])
        page._apply(data)
        return page

    def __repr__(self):
        self._ensure_data()
        return f"<SimplePage '{self._title}' id={self.obj_id}>"


# ──────────────────────────────────────────────
# DatabasePage  (parent = database)
# ──────────────────────────────────────────────

class DatabasePage(NPage):
    """
    A Notion page whose parent is a database.
    All columns are exposed as typed PropertyValue wrappers.

    Usage — reading:
        page = PageFactory.find(headers, page_url)
        print(page.prop("Status").value)        # "In Progress"
        print(page.prop("Due Date").start)      # NDate(...)
        print(page.prop("Score").value)         # 42.0

    Usage — writing (fluent chain):
        page.set_prop("Status", "Done") \\
            .set_prop("Score", 100) \\
            .update()

    Direct property access:
        page.prop("Tags").value = ["urgent", "feature"]
        page.update()
    """

    def __init__(self, headers: dict, page_id: str):
        super().__init__(headers, page_id)
        self._properties: dict[str, PropertyValue] = {}

    def _apply(self, data: dict):
        super()._apply(data)
        self._properties = {
            name: PropertyFactory.from_data(name, prop_data)
            for name, prop_data in data.response.get("properties", {}).items()
        }

    # ── property access ──────────────────────────

    @property
    def properties(self) -> dict[str, PropertyValue]:
        self._ensure_data()
        return self._properties

    def prop(self, name: str) -> PropertyValue:
        """Return a typed wrapper for the given property name."""
        self._ensure_data()
        if name not in self._properties:
            available = list(self._properties.keys())
            raise KeyError(
                f"Property '{name}' not found. Available: {available}"
            )
        return self._properties[name]

    def set_prop(self, name: str, value) -> "DatabasePage":
        """
        Set a property value by name. Returns self for fluent chaining.
        For DateProperty pass an NDate; for multi-value props pass a list.
        """
        self.prop(name).value = value
        return self

    def title(self) -> str:
        """Convenience: return the text of the title property."""
        self._ensure_data()
        title_prop = next(
            (p for p in self._properties.values() if p.prop_type == "title"),
            None
        )
        return title_prop.value if title_prop else ""

    # ── payload ──────────────────────────────────

    def to_payload(self) -> dict:
        """
        Builds the properties payload skipping read-only ones silently.
        Only properties whose value was actually modified should be included
        for efficiency — for now we send the full writable set.
        """
        props = {}
        for prop in self._properties.values():
            try:
                props.update(prop.to_payload())
            except AttributeError:
                pass  # read-only: skip
        return {"properties": props}

    # ── factory create ───────────────────────────

    @classmethod
    def create(cls,
               headers: dict,
               parent_db_id: str,
               properties: dict,
               icon=None,
               cover=None) -> "DatabasePage":
        """
        Create a new database page.

        properties: dict built with PropertyValue.to_payload() merged together, e.g.
            {
                "Name":   {"title":  [...]},
                "Status": {"status": {"name": "In Progress"}},
                "Score":  {"number": 42},
            }
        Returns the hydrated DatabasePage object.
        """
        from client.https import NPOST

        parent_db_id = check_url_or_id(parent_db_id)
        payload: dict = {
            "parent": {"database_id": parent_db_id},
            "properties": properties
        }
        if icon:
            payload["icon"] = icon.to_payload()
        if cover:
            payload["cover"] = cover.to_dict()

        data = NPOST(
            header=headers,
            url="https://api.notion.com/v1/pages",
            data=payload
        ).response
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
    """
    Entry point for loading any Notion page.

    Returns a SimplePage or DatabasePage depending on the parent type.

    Usage:
        page = PageFactory.find(headers, page_url_or_id)
    """

    @staticmethod
    def find(headers: dict, page_id: str) -> NPage:
        page_id = check_url_or_id(page_id)
        data = get_page(headers, page_id)

        parent_type = data.response.get("parent", {}).get("type", "")
        if parent_type == "data_source_id":
            page = DatabasePage(headers, page_id)
        else:
            # page_id, workspace, block_id → all treated as SimplePage
            page = SimplePage(headers, page_id)

        page._apply(data)
        return page


# ──────────────────────────────────────────────
# Quick manual test
# ──────────────────────────────────────────────

if __name__ == "__main__":
    from client.auth import NotionApiClient
    from nModels.blocks.paragraph import ParagraphBlock
    from nTypes.icons import NEmoji

    api = NotionApiClient(key="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")

    # simple_url = "https://www.notion.so/color-A2DCEE-textbf-API-Integration-2a7b7a8f729480b3b420f8736c4116d7"
    db_page_url = "https://www.notion.so/New-Title-2-The-revenge-2a7b7a8f729481ffadcfe600364f3fd4?source=copy_link"  # replace with a real DB page URL

    # ── SimplePage ──────────────────────────────
    # print("=== SimplePage ===")
    # simple = PageFactory.find(api.headers, simple_url)
    # print(simple)
    # print("Title:", simple.title)
    # print("URL:  ", simple.url)
    # print("Icon: ", simple.icon.emoji)
    # print("Cover:", simple.cover.type)

    # Rename + update
    # simple.title = "\color{#A2DCEE}\textbf{API} Integration - UPDATED per due volte"
    # simple.update()

    # Append a paragraph child
    # simple.append_children([ParagraphBlock.create("Hello from the model!")])

    # ── DatabasePage ────────────────────────────
    # print("\n=== DatabasePage ===")
    # db_page = PageFactory.find(api.headers, db_page_url)
    # print(db_page)
    # print("Title:", db_page.title())
    # for name, prop in db_page.properties.items():
    #     print(f"  {name!r:30} ({prop.prop_type}): {prop.value}")

    # Fluent write + update
    # db_page.set_prop("Status", "Done").set_prop("Phone", "100").update()

    # ── Create a new SimplePage ──────────────────
    # parent_page_id = "2a7b7a8f729480b3b420f8736c4116d7"
    # new_page = SimplePage.create(
    #     headers=api.headers,
    #     parent_id=parent_page_id,
    #     title="Created via NPage model",
    #     icon=NEmoji({"type": "emoji", "emoji": "🚀"})
    # )
    # print("Created:", new_page)

    # ── Create a new DatabasePage ────────────────
    # from nTypes.page_properties import TitleProperty, StatusProperty
    # props = {}
    # props.update(TitleProperty.from_data("Name", "", {"title": []}).to_payload())
    # # ... or build raw dict directly:
    # # props = {
    # #     "Name":   {"title": [{"type": "text", "text": {"content": "New entry"}}]},
    # #     "Status": {"status": {"name": "In Progress"}},
    # # }
    # new_db_page = DatabasePage.create(api.headers, parent_db_id, props)
    # print("Created:", new_db_page)

