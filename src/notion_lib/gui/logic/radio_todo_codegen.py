"""Generatore codice per automazione Radio To-Do."""

import re


def generate_radio_todo_code(cfg: dict, target_label: str, entry_label: str) -> str:
    cls = re.sub(r"[^A-Za-z0-9]", "", cfg["name"].title().replace(" ", "")) or "RadioTodoAutomation"
    mode = cfg.get("mode", "datasource")

    if mode == "page":
        return f'''\
"""
Automazione: {cfg["name"]}
Pagina: {target_label}
Checkbox selezionata: {entry_label}
"""

import os
import sys
sys.path.insert(0, ".")

from client.auth import NotionApiClient
from nEndpoints.blocks import get_block_children, update_block


class {cls}:
    TARGET_PAGE = "{cfg['page_id']}"
    TARGET_TODO = "{cfg['todo_block_id']}"

    def __init__(self, api_key: str):
        self.api = NotionApiClient(key=api_key)

    def _collect_todos(self, block_id: str, out: list):
        for child in get_block_children(self.api.headers, block_id):
            cid = (child.get("id") or "").replace("-", "")
            if child.get("type") == "to_do":
                out.append({{"id": cid, "checked": bool(child.get("to_do", {{}}).get("checked", False))}})
            if child.get("has_children"):
                self._collect_todos(cid, out)

    def run(self):
        todos = []
        self._collect_todos(self.TARGET_PAGE, todos)
        if not todos:
            print("⚠ Nessun blocco To-Do trovato nella pagina.")
            return

        target = self.TARGET_TODO.replace("-", "")
        updated = 0
        for item in todos:
            desired = item["id"] == target
            if bool(item.get("checked", False)) == desired:
                continue
            update_block(self.api.headers, item["id"], {{"to_do": {{"checked": desired}}}})
            updated += 1

        print(f"✓ Radio To-Do applicato su {{len(todos)}} checkbox")
        print(f"✓ Record aggiornati: {{updated}}")


if __name__ == "__main__":
    key = os.environ.get("NOTION_KEY") or input("API Key Notion: ").strip()
    {cls}(key).run()
'''

    return f'''\
"""
Automazione: {cfg["name"]}
DataSource: {target_label}
Proprietà To-Do: {cfg["todo_prop"]}
Entry selezionata: {entry_label}
"""

import os
import sys
sys.path.insert(0, ".")

from client.auth import NotionApiClient
from nModels.datasources import DataSourceFactory
from nEndpoints.pages import update_page


class {cls}:
    TARGET_DS = "{cfg['ds_id']}"
    TODO_PROP = "{cfg['todo_prop']}"
    TARGET_ENTRY = "{cfg['entry_id']}"

    def __init__(self, api_key: str):
        self.api = NotionApiClient(key=api_key)

    def run(self):
        ds = DataSourceFactory.find(self.api.headers, self.TARGET_DS)
        entries = ds.all_entries()
        if not entries:
            print("⚠ Nessuna entry trovata nel datasource.")
            return

        target = self.TARGET_ENTRY.replace("-", "")
        found_ids = {{(e.get("id") or "").replace("-", "") for e in entries}}
        if target not in found_ids:
            raise ValueError("L'entry selezionata non esiste più nel datasource.")

        updated = 0
        for entry in entries:
            eid = (entry.get("id") or "").replace("-", "")
            props = entry.get("properties", {{}})
            if self.TODO_PROP not in props:
                continue

            current = props.get(self.TODO_PROP, {{}}).get("checkbox", False)
            desired = (eid == target)
            if bool(current) == desired:
                continue

            update_page(
                self.api.headers,
                entry.get("id"),
                {{"properties": {{self.TODO_PROP: {{"checkbox": desired}}}}}},
            )
            updated += 1

        print(f"✓ Radio To-Do applicato su {{len(entries)}} entry")
        print(f"✓ Record aggiornati: {{updated}}")


if __name__ == "__main__":
    key = os.environ.get("NOTION_KEY") or input("API Key Notion: ").strip()
    {cls}(key).run()
'''
