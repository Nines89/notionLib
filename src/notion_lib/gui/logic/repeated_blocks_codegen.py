"""Generatore codice per automazione di blocchi ripetuti."""

import re


def generate_repeated_blocks_code(cfg: dict, target_label: str) -> str:
    cls = re.sub(r"[^A-Za-z0-9]", "", cfg["name"].title().replace(" ", "")) or "RepeatedBlocksAutomation"
    custom_titles = cfg.get("custom_titles") or []

    return f'''\
"""
Automazione: {cfg["name"]}
Destinazione: {target_label}
"""

import json
import sys
sys.path.insert(0, ".")

from client.auth import NotionApiClient
from nModels.datasources import DataSourceFactory
from nModels.blocks.heading import Heading1, Heading2, Heading3
from nModels.blocks.list_blocks import ToDo, BulletedListItem, NumberedListItem, Toggle
from nModels.blocks.paragraph import ParagraphBlock
from nModels.blocks.special_blocks import DividerBlock, CalloutBlock, BreadcrumbBlock, QuoteBlock
from nModels.blocks.table import TableBlock, TableRowBlock
from nTypes.icons import NEmoji
from nTypes.rich_text import simple_rich_text_list


class {cls}:
    TARGET_DS = "{cfg['target_id']}"

    def __init__(self, api_key: str):
        self.api = NotionApiClient(key=api_key)

    def _title_items(self):
        mode = "{cfg['mode']}"
        if mode == "custom":
            titles = {repr(custom_titles)}
            if not titles:
                raise ValueError("Nessun titolo custom configurato")
            return [(i, title) for i, title in enumerate(titles, start=1)]

        template = {repr(cfg['title_template'])}
        start = {cfg['start_index']}
        total = {cfg['count']}
        return [(i, template.format(index=i, title="")) for i in range(start, start + total)]

    def _render(self, text: str, index: int, title: str):
        return (text or "").format(index=index, title=title)

    def _blocks_for(self, blueprint: list, index: int, title: str):
        out = []
        for item in blueprint:
            btype = item.get("type", "paragraph")
            text = self._render(item.get("text", ""), index, title)

            if btype == "heading_1":
                out.append(Heading1.create(text=text))
            elif btype == "heading_2":
                out.append(Heading2.create(text=text))
            elif btype == "heading_3":
                out.append(Heading3.create(text=text))
            elif btype == "paragraph":
                out.append(ParagraphBlock.create(text=text))
            elif btype == "to_do":
                out.append(ToDo.create(text=text, checked=bool(item.get("checked", False))))
            elif btype == "bulleted_list_item":
                out.append(BulletedListItem.create(text=text))
            elif btype == "numbered_list_item":
                out.append(NumberedListItem.create(text=text))
            elif btype == "toggle":
                out.append(Toggle.create(text=text))
            elif btype == "divider":
                out.append(DividerBlock.create())
            elif btype == "callout":
                out.append(CalloutBlock.create(text=text, icon=NEmoji({"emoji": "💡"})))
            elif btype == "breadcrumb":
                out.append(BreadcrumbBlock.create())
            elif btype == "quote":
                out.append(QuoteBlock.create(text=text))
            elif btype == "table":
                columns = item.get("columns") or ["Col 1", "Col 2"]
                rows = int(item.get("rows", 1))
                has_row_header = bool(item.get("has_row_header", False))
                row_header_values = item.get("row_header_values") or []
                header = TableRowBlock.create(cells=[simple_rich_text_list(str(c)) for c in columns])
                total_rows = max(1, rows, len(row_header_values) if has_row_header else 0)
                body = []
                for r_idx in range(total_rows):
                    cells = [simple_rich_text_list("") for _ in columns]
                    if has_row_header and cells:
                        label = row_header_values[r_idx] if r_idx < len(row_header_values) else ""
                        cells[0] = simple_rich_text_list(self._render(str(label), index, title))
                    body.append(TableRowBlock.create(cells=cells))
                out.append(TableBlock.create(
                    table_width=len(columns),
                    has_column_header=True,
                    has_row_header=has_row_header,
                    cells=[header] + body,
                ))
        return out

    def run(self):
        ds = DataSourceFactory.find(self.api.headers, self.TARGET_DS)
        title_prop = "{cfg['title_prop']}"
        blueprint = json.loads({repr(cfg['blocks_blueprint'])})
        if not isinstance(blueprint, list):
            raise ValueError("Il blueprint JSON deve essere una lista")

        title_items = self._title_items()
        for index, title in title_items:
            props = {{title_prop: {{"title": [{{"text": {{"content": title}}}}]}}}}
            page = ds.create_entry(properties=props)
            blocks = self._blocks_for(blueprint, index=index, title=title)
            if blocks:
                page.append_children(blocks)
            print(f"✓ Creata pagina: {{title}}")


if __name__ == "__main__":
    import os
    key = os.environ.get("NOTION_KEY") or input("API Key Notion: ").strip()
    {cls}(key).run()
'''
