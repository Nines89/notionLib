"""Generatore codice per automazione di blocchi ripetuti."""

import re


def generate_repeated_blocks_code(cfg: dict, target_label: str) -> str:
    cls = re.sub(r"[^A-Za-z0-9]", "", cfg["name"].title().replace(" ", "")) or "RepeatedBlocksAutomation"
    days = cfg.get("days") or ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
    days_repr = repr(days)

    return f'''\
"""
Automazione: {cfg["name"]}
Destinazione: {target_label}
"""

import sys
sys.path.insert(0, ".")

from client.auth import NotionApiClient
from nModels.datasources import DataSourceFactory
from nModels.blocks.table import TableBlock, TableRowBlock
from nTypes.rich_text import simple_rich_text_list


class {cls}:
    TARGET_DS = "{cfg['target_id']}"

    def __init__(self, api_key: str):
        self.api = NotionApiClient(key=api_key)

    def _make_week_props(self, week_no: int):
        return {{
            "{cfg['title_prop']}": {{
                "title": [{{"text": {{"content": "{cfg['title_prefix']} {{:02d}}".format(week_no)}}}}]
            }}
        }}

    def _build_week_table(self):
        giorni = {days_repr}
        header = TableRowBlock.create(cells=[simple_rich_text_list(g) for g in giorni])
        empty = TableRowBlock.create(cells=[simple_rich_text_list("") for _ in giorni])
        return TableBlock.create(
            table_width=len(giorni),
            has_column_header=True,
            has_row_header=False,
            cells=[header, empty],
        )

    def run(self):
        ds = DataSourceFactory.find(self.api.headers, self.TARGET_DS)
        start = {cfg['start_week']}
        total = {cfg['weeks_count']}
        create_table = {cfg['with_table']}

        for week_no in range(start, start + total):
            page = ds.create_entry(properties=self._make_week_props(week_no))
            if create_table:
                page.append_children([self._build_week_table()])
            print(f"✓ Creata pagina settimana {{week_no:02d}}")


if __name__ == "__main__":
    import os
    key = os.environ.get("NOTION_KEY") or input("API Key Notion: ").strip()
    {cls}(key).run()
'''
