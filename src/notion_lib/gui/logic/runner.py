"""
gui/logic/runner.py
Funzioni pure per l'esecuzione dell'automazione.
Nessuna dipendenza da PyQt6.
"""

import sys
sys.path.insert(0, "")

from src.notion_lib.gui.constants import NO_VALUE_OPS


# ── Estrazione valore da una entry grezza ────────────────────────────────────

def extract_value(entry: dict, col: str, col_type: str):
    """Estrae il valore leggibile di una colonna da una entry API grezza."""
    p = entry.get("properties", {}).get(col, {})
    if col_type == "title":
        return (p.get("title") or [{}])[0].get("plain_text", "")
    if col_type == "rich_text":
        return (p.get("rich_text") or [{}])[0].get("plain_text", "")
    if col_type == "number":
        return p.get("number")
    if col_type == "checkbox":
        return p.get("checkbox", False)
    if col_type == "select":
        return (p.get("select") or {}).get("name", "")
    if col_type == "multi_select":
        return [x.get("name", "") for x in p.get("multi_select", [])]
    if col_type == "status":
        return (p.get("status") or {}).get("name", "")
    if col_type == "date":
        return (p.get("date") or {}).get("start", "")
    if col_type in ("url", "email", "phone_number"):
        return p.get(col_type, "")
    return str(p)


# ── Costruzione payload per la scrittura ─────────────────────────────────────

def build_prop_payload(col_type: str, val):
    """Converte un valore Python nel formato payload Notion per la scrittura."""
    if col_type == "title":
        return {"title": [{"text": {"content": str(val or "")}}]}
    if col_type == "rich_text":
        return {"rich_text": [{"text": {"content": str(val or "")}}]}
    if col_type == "number":
        try:
            return {"number": float(val)} if val is not None else {"number": None}
        except (TypeError, ValueError):
            return {"number": None}
    if col_type == "checkbox":
        return {"checkbox": bool(val)}
    if col_type == "select":
        return {"select": {"name": str(val)} if val else None}
    if col_type == "multi_select":
        items = val if isinstance(val, list) else ([str(val)] if val else [])
        return {"multi_select": [{"name": v} for v in items]}
    if col_type == "status":
        return {"status": {"name": str(val)} if val else None}
    if col_type == "date":
        return {"date": {"start": str(val)} if val else None}
    if col_type in ("url", "email", "phone_number"):
        return {col_type: str(val) if val else None}
    return None


# ── Costruzione filtro Notion da FilterRow ────────────────────────────────────

def build_filter(filter_rows: list, schema: dict):
    """
    Converte una lista di FilterRow in un filtro Notion.
    Restituisce None se non ci sono filtri.
    """
    from src.notion_lib.nTypes.ds_filters import F
    conds = []

    for row in filter_rows:
        col, op, val = row.col, row.op, row.val
        ct = schema.get(col, {}).get("type", "rich_text")
        try:
            if op == "equals_true":
                cond = F.checkbox(col).equals(True)
            elif op == "equals_false":
                cond = F.checkbox(col).equals(False)
            elif ct == "number":
                cond = (getattr(F.number(col), op)() if op in NO_VALUE_OPS
                        else getattr(F.number(col), op)(float(val)))
            elif ct in ("title", "rich_text", "url", "email", "phone_number"):
                cond = (getattr(F.rich_text(col), op)() if op in NO_VALUE_OPS
                        else getattr(F.rich_text(col), op)(str(val)))
            elif ct == "select":
                cond = (getattr(F.select(col), op)() if op in NO_VALUE_OPS
                        else getattr(F.select(col), op)(str(val)))
            elif ct == "multi_select":
                cond = (getattr(F.multi_select(col), op)() if op in NO_VALUE_OPS
                        else getattr(F.multi_select(col), op)(str(val)))
            elif ct == "status":
                cond = getattr(F.status(col), op)(str(val))
            elif ct == "date":
                cond = (getattr(F.date(col), op)() if op in NO_VALUE_OPS
                        else getattr(F.date(col), op)(str(val)))
            else:
                continue
            conds.append(cond)
        except Exception:
            continue

    if not conds:
        return None
    if len(conds) == 1:
        return conds[0]
    from src.notion_lib.nTypes.ds_filters import F as _F
    return _F.and_(*conds)


# ── Esecuzione dell'automazione ───────────────────────────────────────────────

def run_automation(api, src_id: str, tgt_id: str,
                   src_schema: dict, tgt_schema: dict,
                   filter_rows: list, sort_rows: list,
                   col_map: dict) -> list:
    """
    Esegue l'automazione completa:
      1. Legge le entry dalla sorgente (con filtro opzionale)
      2. Ordina (con sort opzionale)
      3. Scrive nella destinazione (con mapping colonne)
    Restituisce una lista di righe di log leggibili.
    """
    from src.notion_lib.nModels.datasources import DataSourceFactory
    log = []

    try:
        # ── Step 1: lettura ────────────────────────────────────────
        source  = DataSourceFactory.find(api.headers, src_id)
        filt    = build_filter(filter_rows, src_schema)
        entries = source.filter({"filter": filt}) if filt else source.all_entries()
        log.append(f"✓ Lette {len(entries)} entry dalla sorgente.")

        # ── Step 2: ordinamento ────────────────────────────────────
        for row in reversed(sort_rows):
            col = row.col
            ct  = src_schema.get(col, {}).get("type", "rich_text")
            entries = sorted(
                entries,
                key=lambda e, c=col, t=ct: (extract_value(e, c, t) or ""),
                reverse=not row.asc,
            )
        if sort_rows:
            log.append(f"✓ Ordinate per: {', '.join(r.col for r in sort_rows)}")

        # ── Step 3: scrittura ──────────────────────────────────────
        target  = DataSourceFactory.find(api.headers, tgt_id)
        written = errors = 0

        for entry in entries:
            props = {}
            for tgt_col, src_col in col_map.items():
                if not src_col or src_col == "__skip__":
                    continue
                sct = src_schema.get(src_col, {}).get("type", "rich_text")
                tct = tgt_schema.get(tgt_col, {}).get("type", "rich_text")
                p   = build_prop_payload(tct, extract_value(entry, src_col, sct))
                if p is not None:
                    props[tgt_col] = p
            try:
                target.create_entry(properties=props)
                written += 1
            except Exception as e:
                errors += 1
                log.append(f"  ⚠ Errore entry: {e}")

        log.append(f"✓ Scritte {written} entry.  Errori: {errors}.")

    except Exception as e:
        log.append(f"✗ Errore fatale: {e}")

    return log
