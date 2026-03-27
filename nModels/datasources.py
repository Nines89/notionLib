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
from utils.utils import check_url_or_id


# ──────────────────────────────────────────────
# Tipi ausiliari
# ──────────────────────────────────────────────

class DataSourceTemplate:
    """Rappresenta un template associato a un DataSource."""

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
        default_tag = " [default]" if self._is_default else ""
        return f"<DataSourceTemplate '{self._name}'{default_tag} id={self._id}>"


# ──────────────────────────────────────────────
# NDataSource
# ──────────────────────────────────────────────

class DataSourceError(Exception):
    pass


class NDataSource(NObj):
    """
    Modello per un Notion DataSource.

    Un DataSource è la "vista tabellare" di un Database: contiene entry
    (pagine) con proprietà tipizzate definite dallo schema.

    Operazioni supportate:
      - Lettura: title, schema, templates, parent_db_id
      - Query: filter(), sort(), all() (senza filtri)
      - Scrittura schema: add_property(), remove_property(), rename_property()
      - Metadati: update(), move(), trash(), restore()
      - Creazione entry: create_entry()

    Esempio base:
        ds = DataSourceFactory.find(headers, ds_id)
        print(ds.title)

        entries = ds.filter({"filter": F.checkbox("Done").equals(True)})
        sorted_entries = ds.sort(S().get(("Name", True)))

        ds.add_property("select", "Priorità")
        ds.rename_property("Priorità", "Priority")
        ds.remove_property("Priority")

    Esempio creazione entry:
        from nModels.pages import DatabasePage
        entry = ds.create_entry(properties={
            "FIRST FIELD": {"title": [{"text": {"content": "Nuova voce"}}]}
        })
    """

    def __init__(self, headers: dict, ds_id: str):
        super().__init__(headers, ds_id)
        self._title: str = ""
        self._schema: dict = {}
        self._parent_db_id: Optional[str] = None
        self._templates: Optional[list[DataSourceTemplate]] = None  # lazy

    # ── lifecycle ────────────────────────────────

    def _apply(self, data: dict):
        self._data = data
        self._applied = True

        # title: può essere una lista rich_text o una stringa diretta
        title_raw = data.response.get("title", [])
        if isinstance(title_raw, list):
            self._title = "".join(t.get("plain_text", "") for t in title_raw)
        else:
            self._title = str(title_raw)

        # schema proprietà (definizioni, NON valori)
        self._schema = data.response.get("properties", {})

        # parent database
        parent = data.response.get("database_parent") or data.response.get("parent", {})
        if isinstance(parent, dict):
            self._parent_db_id = (
                parent.get("database_id")
                or parent.get("data_source_id")
                or parent.get("page_id")
            )

        # invalida la cache dei templates se i dati cambiano
        self._templates = None

    def _refresh(self):
        self._data = get_ds(self.headers, self.obj_id)
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
    def schema(self) -> dict:
        """
        Schema proprietà grezzo: {nome: {id, type, name, ...}}.
        Per una vista tipizzata, usa nModels.databases.SchemaProperty.from_data().
        """
        self._ensure_data()
        return self._schema

    @property
    def parent_db_id(self) -> Optional[str]:
        self._ensure_data()
        return self._parent_db_id

    @property
    def templates(self) -> list[DataSourceTemplate]:
        """Templates associati al DS (lazy load)."""
        self._ensure_data()
        if self._templates is None:
            raw = get_ds_templates(self.headers, self.obj_id)
            self._templates = [
                DataSourceTemplate(t) for t in raw.get("templates", [])
            ]
        return self._templates

    @property
    def default_template(self) -> Optional[DataSourceTemplate]:
        """Ritorna il template di default, o None se non esiste."""
        return next((t for t in self.templates if t.is_default), None)

    # ── query ────────────────────────────────────

    def filter(self, filt: dict) -> list:
        """
        Filtra le entry del DS.

        filt: dizionario filtro Notion, costruibile con nTypes.ds_filters.F
        Ritorna lista di dict (raw page data). Usa all_entries() per oggetti tipizzati.

        Esempio:
            from nTypes.ds_filters import F
            entries = ds.filter({"filter": F.checkbox("Done").equals(True)})
        """
        return filter_a_ds(self.headers, self.obj_id, filt)

    def sort(self, sorties: dict) -> list:
        """
        Ordina le entry del DS.

        sorties: dizionario sort, costruibile con nTypes.ds_filters.S
        Ritorna lista di dict (raw page data).

        Esempio:
            from nTypes.ds_filters import S
            entries = ds.sort(S().get(("Name", True), ("created_time", False)))
        """
        return sort_a_ds(self.headers, self.obj_id, sorties)

    def all_entries(self) -> list:
        """
        Recupera tutte le entry senza filtri.
        Usa la paginazione automatica già gestita dall'endpoint.
        """
        return filter_a_ds(self.headers, self.obj_id, {})

    def query(self, filt: dict = None, sorties: dict = None) -> list:
        """
        Combina filtro e ordinamento in un'unica chiamata.
        Se entrambi None, equivale ad all_entries().

        filt:     {"filter": ...}  oppure None
        sorties:  {"sorts": [...]} oppure None
        """
        payload: dict = {}
        if filt:
            payload.update(filt)
        if sorties:
            payload.update(sorties)
        return filter_a_ds(self.headers, self.obj_id, payload)

    # ── gestione schema ───────────────────────────

    def add_property(self, prop_type: str, name: str):
        """
        Aggiunge una nuova colonna allo schema.

        prop_type: stringa tipo (es. "url", "number", "select", "rich_text")
                   o valore di DbFieldType enum.
        name:      nome della colonna.

        Invalida la cache dello schema locale.
        """
        result = update_ds(
            self.headers,
            self.obj_id,
            prop_schema={prop_type: name},
        )
        self._apply(result)
        return self

    def remove_property(self, prop_id_or_name: str):
        """
        Rimuove una colonna dallo schema per nome o ID.
        Invalida la cache locale.
        """
        result = remove_ds_property(self.headers, self.obj_id, prop_id_or_name)
        self._apply(result)
        return self

    def rename_property(self, old_name: str, new_name: str):
        """
        Rinomina una colonna. Invalida la cache locale.
        """
        result = rename_ds_property(self.headers, self.obj_id, old_name, new_name)
        self._apply(result)
        return self

    # ── operazioni metadati ───────────────────────

    def to_payload(self) -> dict:
        return {"title": simple_rich_text_list(self._title).to_dict()}

    def update(self, title: str = None, prop_schema: dict = None):
        """
        Aggiorna title e/o aggiunge colonne.

        prop_schema: {tipo: nome}  — aggiunge colonne, NON le sovrascrive.
        """
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
        """Sposta il DS sotto un altro database."""
        result = move_ds(self.headers, self.obj_id, new_parent_db_id)
        self._apply(result)
        return result

    def trash(self):
        """Manda il DS nel cestino."""
        result = update_ds(self.headers, self.obj_id, in_trash=True)
        self._apply(result)
        return result

    def restore(self):
        """Ripristina il DS dal cestino."""
        result = update_ds(self.headers, self.obj_id, in_trash=False)
        self._apply(result)
        return result

    # ── creazione entry ───────────────────────────

    def create_entry(
        self,
        properties: dict,
        template_id: str = None,
        icon=None,
        cover=None,
    ):
        """
        Crea una nuova entry (pagina) nel DataSource.

        properties: dict payload proprietà, es.:
            {"FIRST FIELD": {"title": [{"text": {"content": "Nome"}}]}}
        template_id: ID template opzionale (stringa o DataSourceTemplate.id).
        icon/cover: oggetti NEmoji/FileTypeExternal opzionali.

        Ritorna un DatabasePage idratato.
        """
        from nEndpoints.pages import create_page
        from nModels.pages import DatabasePage
        from client.https import NPOST

        ds_id = check_url_or_id(self.obj_id)

        # Risolvi template_id se viene passato un DataSourceTemplate
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

        data = NPOST(
            header=self.headers,
            url="https://api.notion.com/v1/pages",
            data=payload,
        ).response

        page = DatabasePage(self.headers, data["id"])
        page._apply(data)
        return page

    # ── factory classmethod ───────────────────────

    @classmethod
    def create(
        cls,
        headers: dict,
        title: str,
        parent_db_id: str,
        prop_schema: dict = None,
    ) -> "NDataSource":
        """
        Crea un nuovo DataSource figlio di un database.

        prop_schema: {tipo: nome}, es. {"url": "Link", "status": "Stato"}
        """
        data = create_ds(
            headers,
            title=title,
            parent_id=parent_db_id,
            prop_schema=prop_schema,
        )
        ds = cls(headers, data["id"])
        ds._apply(data)
        return ds

    def __repr__(self):
        self._ensure_data()
        return f"<NDataSource '{self._title}' id={self.obj_id}>"


# ──────────────────────────────────────────────
# DataSourceFactory
# ──────────────────────────────────────────────

class DataSourceFactory:
    """Entry point per caricare un DataSource esistente."""

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

    api = NotionApiClient(key="YOUR_KEY_HERE")

    db_url = "YOUR_DB_URL_HERE"

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
        # all_e = ds.all_entries()
        # print(f"\nTotale entry: {len(all_e)}")

        # Filtra per checkbox
        # results = ds.filter({"filter": F.checkbox("Done").equals(True)})
        # print(f"Entry 'Done': {len(results)}")

        # Ordina per nome
        # sorted_e = ds.sort(S().get(("FIRST FIELD", True)))
        # print(f"Sorted: {len(sorted_e)}")

        # Combina filtro + ordinamento
        # combined = ds.query(
        #     filt={"filter": F.checkbox("Done").equals(False)},
        #     sorties=S().get(("FIRST FIELD", True))
        # )

        # ── Schema management ───────────────────────
        # ds.add_property("select", "Categoria")
        # ds.rename_property("Categoria", "Category")
        # ds.remove_property("Category")

        # ── Crea entry ─────────────────────────────
        # entry = ds.create_entry(
        #     properties={"FIRST FIELD": {"title": [{"text": {"content": "Test entry"}}]}},
        #     template_id=ds.default_template,
        # )
        # print("Entry creata:", entry)

        # ── Sposta DS sotto altro DB ────────────────
        # ds.move("ALTRO_DB_URL")

        # ── Aggiorna titolo ─────────────────────────
        # ds.update(title="Nuovo Titolo DS")
