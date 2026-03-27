from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from nModels.base_object import NObj
from nEndpoints.databases import (
    get_db,
    get_db_datasources,
    create_db,
    update_db,
    move_db,
)
from nTypes.rich_text import simple_rich_text_list, create_rich_list
from utils.utils import check_url_or_id
from utils.constants import DbFieldType


# ──────────────────────────────────────────────
# Schema property (definizione colonna, NON valore)
# ──────────────────────────────────────────────

@dataclass
class SchemaProperty:
    """
    Rappresenta la definizione di una colonna nel DB/DS schema.
    Diversa da PropertyValue (che rappresenta il valore in una pagina).
    """
    name: str
    prop_id: str
    prop_type: str
    config: dict = field(default_factory=dict)   # configurazione specifica del tipo (es. options per select)

    @classmethod
    def from_data(cls, name: str, data: dict) -> "SchemaProperty":
        prop_type = data.response.get("type", "")
        return cls(
            name=name,
            prop_id=data.response.get("id", ""),
            prop_type=prop_type,
            config=data.response.get(prop_type, {}) or {},
        )

    def __repr__(self):
        return f"<SchemaProperty '{self.name}' type={self.prop_type} id={self.prop_id}>"


# ──────────────────────────────────────────────
# NDatabase
# ──────────────────────────────────────────────

class DatabaseError(Exception):
    pass


class NDatabase(NObj):
    """
    Modello per un Notion Database.

    Il Database è un contenitore che definisce uno SCHEMA (proprietà tipizzate).
    Le entry sono DataSource (DS), accessibili via NDatabase.datasources.

    Operazioni supportate:
      - Lettura: title, properties (schema), datasources, is_inline, is_locked
      - Scrittura: update(), move(), trash(), restore()
      - Creazione DS figlio: create_datasource()

    Esempio:
        db = DatabaseFactory.find(headers, db_url)
        print(db.title)
        for name, schema_prop in db.schema.items():
            print(name, schema_prop.prop_type)

        db.title = "Nuovo titolo"
        db.update()

        ds_list = db.datasources          # lista di NDataSource (lazy)
        new_ds = db.create_datasource("DS 1", prop_schema={"url": "Link"})
    """

    def __init__(self, headers: dict, db_id: str):
        super().__init__(headers, db_id)
        self._title: str = ""
        self._schema: dict[str, SchemaProperty] = {}
        self._is_inline: Optional[bool] = None
        self._is_locked: Optional[bool] = None
        self._raw_datasources: list[dict] = []   # [{"id": "...", "name": "..."}]

    # ── lifecycle ────────────────────────────────

    def _apply(self, data: dict):
        self._data = data
        self._applied = True

        # title: lista rich_text
        title_items = data.response.get("title", [])
        self._title = "".join(t.get("plain_text", "") for t in title_items)

        # schema proprietà
        self._schema = {
            name: SchemaProperty.from_data(name, prop_data)
            for name, prop_data in data.response.get("properties", {}).items()
        }

        self._is_inline = data.response.get("is_inline")
        self._is_locked = data.response.get("is_locked")
        self._raw_datasources = data.response.get("data_sources", [])

    def _refresh(self):
        self._data = get_db(self.headers, self.obj_id)
        self._apply(self._data)

    def _ensure_data(self):
        if not self._applied:
            self._refresh()

    # ── proprietà lettura ────────────────────────

    @property
    def title(self) -> str:
        self._ensure_data()
        return self._title

    @title.setter
    def title(self, value: str):
        self._title = value

    @property
    def schema(self) -> dict[str, SchemaProperty]:
        """Schema del database: {nome_colonna: SchemaProperty}"""
        self._ensure_data()
        return self._schema

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
        """
        Ritorna la lista di NDataSource figli (lazy: carica i dati solo alla prima chiamata).
        Importazione locale per evitare import circolare con nModels/datasources.py.
        """
        self._ensure_data()
        from nModels.datasources import NDataSource
        return [NDataSource(self.headers, ds["id"]) for ds in self._raw_datasources]

    # ── operazioni ───────────────────────────────

    def to_payload(self) -> dict:
        payload: dict = {}
        payload["title"] = simple_rich_text_list(self._title).to_dict()
        if self._is_inline is not None:
            payload["is_inline"] = self._is_inline
        if self._is_locked is not None:
            payload["is_locked"] = self._is_locked
        return payload

    def update(self):
        """Aggiorna title, is_inline, is_locked sul database."""
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
        """Sposta il database sotto un nuovo parent (page o workspace)."""
        result = move_db(self.headers, self.obj_id, new_parent_id)
        self._apply(result)
        return result

    def trash(self):
        """Manda il database nel cestino."""
        result = update_db(self.headers, self.obj_id, in_trash=True)
        self._apply(result)
        return result

    def restore(self):
        """Ripristina il database dal cestino."""
        result = update_db(self.headers, self.obj_id, in_trash=False)
        self._apply(result)
        return result

    def create_datasource(self, title: str, prop_schema: dict = None) -> "NDataSource":  # noqa: F821
        """
        Crea un nuovo DataSource figlio di questo database.

        Prop_schema: {tipo_proprietà: nome_colonna}
        Es.: {"url": "Link", "number": "Punteggio"}
        """
        from nEndpoints.datasources import create_ds
        from nModels.datasources import NDataSource

        data = create_ds(self.headers, title=title, parent_id=self.obj_id, prop_schema=prop_schema)
        ds = NDataSource(self.headers, data["id"])
        ds._apply(data)
        # Invalida la cache dei datasources
        self._raw_datasources = get_db_datasources(self.headers, self.obj_id)
        return ds

    # ── factory classmethod ───────────────────────

    @classmethod
    def create(
        cls,
        headers: dict,
        title: str,
        parent_id: str,
        prop_schema: dict = None,
        is_inline: bool = True,
    ) -> "NDatabase":
        """
        Crea un nuovo database.

        prop_schema: {tipo_proprietà: nome_colonna}
        Es.: {"select": "Priorità", "date": "Scadenza"}
        """
        data = create_db(
            headers,
            title=title,
            parent_id=parent_id,
            prop_schema=prop_schema,
            is_inline=is_inline,
        )
        db = cls(headers, data["id"])
        db._apply(data)
        return db

    def __repr__(self):
        self._ensure_data()
        return f"<NDatabase '{self._title}' id={self.obj_id}>"


# ──────────────────────────────────────────────
# DatabaseFactory
# ──────────────────────────────────────────────

class DatabaseFactory:
    """Entry point per caricare un database esistente."""

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
    from client.auth import NotionApiClient

    api = NotionApiClient(key="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")

    db_url = "https://www.notion.so/2a7b7a8f729481919ac9c1853a813571?v=2a7b7a8f7294819bb426000cf2da4ff8&source=copy_link"

    db = DatabaseFactory.find(api.headers, db_url)
    print(db)
    print("Titolo:", db.title)
    print("Inline:", db.is_inline)
    print("Locked:", db.is_locked)

    print("\nSchema:")
    for name, sp in db.schema.items():
        print(f"  {name!r:30} type={sp.prop_type} id={sp.prop_id}")

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
