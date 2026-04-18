from __future__ import annotations
from typing import Optional

from src.notion_lib.nModels.base_object import NObj
from src.notion_lib.nEndpoints.databases import (
    get_db,
    get_db_datasources,
    create_db,
    update_db,
    move_db,
)
from src.notion_lib.nTypes.rich_text import simple_rich_text_list
from src.notion_lib.utils.utils import check_url_or_id, resolve_response


class DatabaseError(Exception):
    pass


class NDatabase(NObj):
    def __init__(self, headers: dict, db_id: str):
        super().__init__(headers, db_id)
        self._title: str = ""
        self._is_inline: Optional[bool] = None
        self._is_locked: Optional[bool] = None
        self._raw_datasources: list[dict] = []

    def _apply(self, data):
        # FIX: resolve_response normalizza sia NGET che dict grezzo
        raw = resolve_response(data)
        self._data = raw
        self._applied = True

        title_items = raw.get("title", [])
        self._title = "".join(t.get("plain_text", "") for t in title_items)
        self._is_inline = raw.get("is_inline")
        self._is_locked = raw.get("is_locked")
        self._raw_datasources = raw.get("data_sources", [])

    def _refresh(self):
        self._apply(get_db(self.headers, self.obj_id))

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
    def is_inline(self) -> Optional[bool]:
        self._ensure_data()
        return self._is_inline

    @is_inline.setter
    def is_inline(self, value: bool):
        self._is_inline = value

    @property
    def is_locked(self) -> Optional[bool]:
        self._ensure_data()
        return self._is_locked

    @is_locked.setter
    def is_locked(self, value: bool):
        self._is_locked = value

    @property
    def datasources(self) -> list:
        self._ensure_data()
        from src.notion_lib.nModels.datasources import NDataSource
        return [NDataSource(self.headers, ds["id"]) for ds in self._raw_datasources]

    def to_payload(self) -> dict:
        payload: dict = {"title": simple_rich_text_list(self._title).to_dict()}
        if self._is_inline is not None:
            payload["is_inline"] = self._is_inline
        if self._is_locked is not None:
            payload["is_locked"] = self._is_locked
        return payload

    def update(self):
        result = update_db(
            self.headers,
            self.obj_id,
            title=self._title,
            is_inline=self._is_inline,
            is_locked=self._is_locked,
        )
        self._apply(result)
        return result

    def move(self, new_parent_id: str):
        result = move_db(self.headers, self.obj_id, new_parent_id)
        self._apply(result)
        return result

    def trash(self):
        result = update_db(self.headers, self.obj_id, in_trash=True)
        self._apply(result)
        return result

    def restore(self):
        result = update_db(self.headers, self.obj_id, in_trash=False)
        self._apply(result)
        return result

    def create_datasource(self, title: str, prop_schema: dict = None):
        from src.notion_lib.nEndpoints.datasources import create_ds
        from src.notion_lib.nModels.datasources import NDataSource
        data = create_ds(self.headers, title=title, parent_id=self.obj_id, prop_schema=prop_schema)
        ds = NDataSource(self.headers, resolve_response(data)["id"])
        ds._apply(data)
        self._raw_datasources = get_db_datasources(self.headers, self.obj_id)
        return ds

    @classmethod
    def create(cls, headers: dict, title: str, parent_id: str,
               prop_schema: dict = None, is_inline: bool = True) -> "NDatabase":
        data = create_db(headers, title=title, parent_id=parent_id,
                         prop_schema=prop_schema, is_inline=is_inline)
        raw = resolve_response(data)
        db = cls(headers, raw["id"])
        db._apply(data)
        return db

    def __repr__(self):
        self._ensure_data()
        return f"<NDatabase '{self._title}' id={self.obj_id}>"


class DatabaseFactory:
    @staticmethod
    def find(headers: dict, db_id: str) -> NDatabase:
        db_id = check_url_or_id(db_id)
        data = get_db(headers, db_id)
        db = NDatabase(headers, db_id)
        db._apply(data)
        return db

# ──────────────────────────────────────────────
# Test manuale
# ──────────────────────────────────────────────

if __name__ == "__main__":
    from src.notion_lib.client.auth import NotionApiClient

    api = NotionApiClient(key="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")

    db_url = "https://www.notion.so/2a7b7a8f729481919ac9c1853a813571?v=2a7b7a8f7294819bb426000cf2da4ff8&source=copy_link"

    db = DatabaseFactory.find(api.headers, db_url)
    print(db)
    print("Titolo:", db.title)
    print("Inline:", db.is_inline)
    print("Locked:", db.is_locked)


    print("\nDataSources:")
    for ds in db.datasources:
        print(" ", ds)

    # Aggiornamento
    # db.title = "Titolo aggiornato"
    # db.update()
    #
    # # Crea un DS figlio
    # new_ds = db.create_datasource("Nuovo DS", prop_schema={"url": "Link", "number": "Score"})
    # print("Creato:", new_ds)
