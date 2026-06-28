"""Logica per automazione "radio button" su proprietà checkbox di un DataSource."""

import sys
sys.path.insert(0, "")


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
    from notion_lib.nModels.datasources import DataSourceFactory

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
    from notion_lib.nModels.datasources import DataSourceFactory
    from notion_lib.nEndpoints.pages import update_page

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


def _extract_todo_text(block: dict) -> str:
    items = block.get("to_do", {}).get("rich_text", [])
    if items:
        return items[0].get("plain_text", "").strip() or "To-Do senza testo"
    return "To-Do senza testo"


def _collect_todo_blocks(headers, block_id: str, out: list[dict]):
    from notion_lib.nEndpoints.blocks import get_block_children

    children = get_block_children(headers, block_id)
    for child in children:
        child_id = (child.get("id") or "").replace("-", "")
        if child.get("type") == "to_do":
            out.append(
                {
                    "id": child_id,
                    "label": _extract_todo_text(child),
                    "checked": bool(child.get("to_do", {}).get("checked", False)),
                }
            )

        if child.get("has_children"):
            _collect_todo_blocks(headers, child_id, out)


def list_page_todos(api, page_id: str) -> list[dict]:
    """Restituisce i blocchi To-Do di una pagina in formato adatto alla UI."""
    rows: list[dict] = []
    _collect_todo_blocks(api.headers, page_id, rows)
    return rows


def run_radio_todo_page(api, page_id: str, selected_block_id: str) -> list[str]:
    """Imposta checked=True solo sul To-Do selezionato e False su tutti gli altri."""
    from notion_lib.nEndpoints.blocks import update_block

    target_id = (selected_block_id or "").replace("-", "")
    if not target_id:
        raise ValueError("Checkbox target mancante.")

    todos = list_page_todos(api, page_id)
    if not todos:
        return ["⚠ Nessun blocco To-Do trovato nella pagina selezionata."]

    existing_ids = {t["id"] for t in todos}
    if target_id not in existing_ids:
        raise ValueError("La checkbox selezionata non esiste più nella pagina.")

    updated = 0
    for block in todos:
        desired = block["id"] == target_id
        if bool(block.get("checked", False)) == desired:
            continue
        update_block(
            api.headers,
            block["id"],
            {"to_do": {"checked": desired}},
        )
        updated += 1

    return [
        f"✓ Radio To-Do applicato su {len(todos)} checkbox.",
        f"✓ Checkbox selezionata: {target_id}",
        f"✓ Record aggiornati: {updated}",
    ]
