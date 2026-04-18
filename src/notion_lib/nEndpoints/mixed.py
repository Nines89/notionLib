from notion_lib.client.errors import ValidationError, ObjectNotFound


# Ordine di lookup ottimizzato: page prima (caso più comune), poi data_source,
# poi database, poi block. Ogni chiamata HTTP ha costo → minimizziamo i tentativi.
_LOOKUP_ORDER = ["page", "data_source", "database", "block"]


def find_parent_type(headers: dict, _id: str) -> str:
    """
    Determina il tipo di oggetto Notion dato un ID.

    Ritorna una stringa tra: 'page', 'data_source', 'database', 'block'.
    Solleva ObjectNotFound se nessun endpoint riconosce l'ID.

    Nota: questa funzione esegue fino a 4 chiamate HTTP in cascata.
    Usarla con parsimonia; preferire il tipo esplicito dove noto.
    """
    from notion_lib.nEndpoints.pages import get_page
    from notion_lib.nEndpoints.databases import get_db
    from notion_lib.nEndpoints.blocks import get_block
    from notion_lib.nEndpoints.datasources import get_ds

    lookups = {
        "page":        get_page,
        "data_source": get_ds,
        "database":    get_db,
        "block":       get_block,
    }

    last_exc = None
    for obj_type in _LOOKUP_ORDER:
        try:
            result = lookups[obj_type](headers, _id)
            # Alcuni endpoint restituiscono NGET; normalizza
            obj = result.response if hasattr(result, "response") else result
            return obj.get("object", obj_type)
        except (ObjectNotFound, ValidationError, Exception) as e:
            last_exc = e
            continue

    raise ObjectNotFound(
        f"Nessun oggetto Notion trovato per l'ID '{_id}'. "
        f"Ultimo errore: {last_exc}"
    )


def is_there_more(response: dict) -> bool:
    """Controlla se la risposta paginata ha ulteriori risultati."""
    return bool(response.get("has_more", False))


if __name__ == "__main__":
    from notion_lib.client.auth import NotionApiClient

    api = NotionApiClient(key="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")

    page_id = "2a7b7a8f729480b3b420f8736c4116d7"
    db_id = "2a7b7a8f7294801ab914e1f063fab45a"
    blk_id = "2a7b7a8f729481c2997effc3c4da56ce"
    page_from_ws_id = "28bb7a8f729480bca147c206032d9273"

    parent_type = find_parent_type(api.headers, blk_id)
    print(parent_type)
