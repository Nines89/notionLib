"""
gui/logic/codegen.py
Genera il file .py dell'automazione dalla configurazione corrente.
Funzione pura: input = config dict, output = stringa Python.
"""

import re
import sys
sys.path.insert(0, "")

from src.notion_lib.gui.constants import NO_VALUE_OPS


# ── Helper: factory method Notion per tipo colonna ────────────────────────────

def _filter_factory(col_type: str) -> str:
    """Restituisce il nome del metodo F.<...> corretto per il tipo."""
    return {
        "title":        "rich_text",
        "rich_text":    "rich_text",
        "url":          "rich_text",
        "email":        "rich_text",
        "phone_number": "rich_text",
        "number":       "number",
        "checkbox":     "checkbox",
        "select":       "select",
        "multi_select": "multi_select",
        "status":       "status",
        "date":         "date",
    }.get(col_type, "rich_text")


# ── Helper: riga di filtro ────────────────────────────────────────────────────

def _filter_line(col: str, col_type: str, op: str, val) -> str:
    if op == "equals_true":  return f'F.checkbox("{col}").equals(True)'
    if op == "equals_false": return f'F.checkbox("{col}").equals(False)'
    ff = _filter_factory(col_type)
    if op in NO_VALUE_OPS:   return f'F.{ff}("{col}").{op}()'
    v  = val if col_type == "number" else f'"{val}"'
    return f'F.{ff}("{col}").{op}({v})'


# ── Helper: espressione di estrazione valore ──────────────────────────────────

def _extract_expr(col: str, col_type: str) -> str:
    q = f'entry["properties"].get("{col}", {{}})'
    if col_type == "title":
        return f'({q}.get("title") or [{{}}])[0].get("plain_text","")'
    if col_type == "rich_text":
        return f'({q}.get("rich_text") or [{{}}])[0].get("plain_text","")'
    if col_type == "number":
        return f'{q}.get("number")'
    if col_type == "checkbox":
        return f'{q}.get("checkbox", False)'
    if col_type == "select":
        return f'({q}.get("select") or {{}}).get("name","")'
    if col_type == "multi_select":
        return f'[x.get("name","") for x in {q}.get("multi_select",[])]'
    if col_type == "status":
        return f'({q}.get("status") or {{}}).get("name","")'
    if col_type == "date":
        return f'({q}.get("date") or {{}}).get("start","")'
    return f'{q}.get("{col_type}","")'


# ── Helper: espressione di payload scrittura ──────────────────────────────────

def _payload_expr(col_type: str) -> str:
    if col_type == "title":
        return '{"title": [{"text": {"content": str(val or "")}}]}'
    if col_type == "rich_text":
        return '{"rich_text": [{"text": {"content": str(val or "")}}]}'
    if col_type == "number":
        return '{"number": float(val) if val is not None else None}'
    if col_type == "checkbox":
        return '{"checkbox": bool(val)}'
    if col_type == "select":
        return '{"select": {"name": str(val)} if val else None}'
    if col_type == "multi_select":
        return ('{"multi_select": [{"name": v} for v in '
                '(val if isinstance(val, list) else ([str(val)] if val else []))]}')
    if col_type == "status":
        return '{"status": {"name": str(val)} if val else None}'
    if col_type == "date":
        return '{"date": {"start": str(val)} if val else None}'
    if col_type in ("url", "email", "phone_number"):
        return '{' + f'"{col_type}": str(val) if val else None' + '}'
    return 'None'


# ── Generatore principale ─────────────────────────────────────────────────────

def generate(name: str, src_id: str, tgt_id: str,
             src_label: str, tgt_label: str,
             src_schema: dict, tgt_schema: dict,
             filter_rows: list, sort_rows: list,
             col_map: dict) -> str:
    """
    Genera il codice Python completo dell'automazione.
    filter_rows: list[FilterRow]
    sort_rows:   list[SortRow]
    col_map:     dict  tgt_col -> src_col
    """
    cls = re.sub(r"[^A-Za-z0-9]", "", name.title().replace(" ", "")) or "Automation"
    i8  = "        "   # 8 spazi per il corpo dei metodi

    # ── Blocco filtri ─────────────────────────────────────────────
    if filter_rows:
        flines = [
            _filter_line(
                r.col,
                src_schema.get(r.col, {}).get("type", "rich_text"),
                r.op, r.val,
            )
            for r in filter_rows
        ]
        if len(flines) == 1:
            filter_block = f'{i8}entries = source.filter({{"filter": {flines[0]}}})'
        else:
            joined = (",\n" + i8 + "    ").join(flines)
            filter_block = (
                f'{i8}entries = source.filter({{"filter": F.and_(\n'
                f'{i8}    {joined}\n{i8})}})'
            )
    else:
        filter_block = f"{i8}entries = source.all_entries()"

    # ── Blocco ordinamento ────────────────────────────────────────
    sort_lines = []
    for row in sort_rows:
        ct  = src_schema.get(row.col, {}).get("type", "rich_text")
        rev = str(not row.asc)
        arrow = "↑" if row.asc else "↓"
        sort_lines.append(
            f'{i8}# {arrow} {row.col}\n'
            f'{i8}entries = sorted(entries, '
            f'key=lambda e: ({_extract_expr(row.col, ct)} or ""), '
            f'reverse={rev})'
        )
    sort_block = "\n".join(sort_lines) if sort_lines else f"{i8}# nessun ordinamento"

    # ── Blocco mapping ────────────────────────────────────────────
    map_lines = []
    for tgt_col, src_col in col_map.items():
        if not src_col or src_col == "__skip__":
            continue
        sct = src_schema.get(src_col, {}).get("type", "rich_text")
        tct = tgt_schema.get(tgt_col, {}).get("type", "rich_text")
        map_lines.append(
            f'            # {src_col} ({sct}) → {tgt_col} ({tct})\n'
            f'            val = {_extract_expr(src_col, sct)}\n'
            f'            props["{tgt_col}"] = {_payload_expr(tct)}'
        )
    map_block = "\n".join(map_lines) if map_lines else "            pass  # nessun mapping"

    return f'''\
"""
Automazione: {name}
Generata da Notion Automation GUI.
Sorgente:     {src_label}
Destinazione: {tgt_label}
"""

import sys
sys.path.insert(0, ".")

from client.auth import NotionApiClient
from nModels.datasources import DataSourceFactory
from nTypes.ds_filters import F, S


class {cls}:
    SOURCE_DS = "{src_id}"
    TARGET_DS = "{tgt_id}"

    def __init__(self, api_key: str):
        self.api = NotionApiClient(key=api_key)

    def run(self):
        print("Avvio: {name}")

        # ── 1. Leggi dalla sorgente ───────────────────────────────
        source = DataSourceFactory.find(self.api.headers, self.SOURCE_DS)
{filter_block}
        print(f"Lette {{len(entries)}} entry")

        # ── 2. Ordinamento ────────────────────────────────────────
{sort_block}

        # ── 3. Scrivi nella destinazione ──────────────────────────
        target  = DataSourceFactory.find(self.api.headers, self.TARGET_DS)
        written = 0
        for entry in entries:
            props = {{}}
{map_block}
            try:
                target.create_entry(properties=props)
                written += 1
            except Exception as e:
                print(f"  Errore: {{e}}")

        print(f"Scritte {{written}}/{{len(entries)}} entry.")
        return written


if __name__ == "__main__":
    import os
    key = os.environ.get("NOTION_KEY") or input("API Key Notion: ").strip()
    {cls}(key).run()
'''
