"""Logica per automazione "radio button" su proprietà checkbox di un DataSource."""

import sys
sys.path.insert(0, ".")


def _extract_title(entry: dict) -> str:
    props = entry.get("properties", {})
    for prop in props.values():
        if prop.get("type") == "title":
            items = prop.get("title") or []
            if items:
                return items[0].get("plain_text", "") or "Senza titolo"
            return "Senza titolo"
    return "Senza titolo"


def list_entries(api, ds_id: str) -> list[dict]:
    """Restituisce le entry del datasource in formato adatto alla UI."""
    from nModels.datasources import DataSourceFactory

    ds = DataSourceFactory.find(api.headers, ds_id)
    rows = []
    for entry in ds.all_entries():
        entry_id = (entry.get("id") or "").replace("-", "")
        rows.append({
            "id": entry_id,
            "title": _extract_title(entry),
        })
    return rows


def run_radio_todo(api, ds_id: str, todo_prop: str, selected_entry_id: str) -> list[str]:
    """
    Imposta la checkbox `todo_prop` a True solo sull'entry selezionata,
    e a False su tutte le altre entry del datasource.
    """
    from nModels.datasources import DataSourceFactory
    from nEndpoints.pages import update_page

    target_id = (selected_entry_id or "").replace("-", "")
    if not target_id:
        raise ValueError("Entry target mancante.")

    ds = DataSourceFactory.find(api.headers, ds_id)
    entries = ds.all_entries()
    if not entries:
        return ["⚠ Nessuna entry trovata nel datasource."]

    existing_ids = {(e.get("id") or "").replace("-", "") for e in entries}
    if target_id not in existing_ids:
        raise ValueError("L'entry selezionata non esiste più nel datasource.")

    log = []
    updated = 0

    for entry in entries:
        entry_id = (entry.get("id") or "").replace("-", "")
        props = entry.get("properties", {})

        if todo_prop not in props:
            continue

        current = props.get(todo_prop, {}).get("checkbox", False)
        desired = (entry_id == target_id)

        if bool(current) == desired:
            continue

        update_page(
            api.headers,
            entry.get("id"),
            {"properties": {todo_prop: {"checkbox": desired}}},
        )
        updated += 1

    log.append(f"✓ Radio To-Do applicato su {len(entries)} entry.")
    log.append(f"✓ Entry selezionata: {target_id}")
    log.append(f"✓ Record aggiornati: {updated}")
    return log
