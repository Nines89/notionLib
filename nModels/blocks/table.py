# notion_lib/nModels/blocks/table.py
from nModels.blocks.base_block import BaseBlock, register_block
from nTypes.rich_text import NRichList

@register_block
class Table(BaseBlock):
    block_type = "table"
    def __init__(self, session, obj_id):
        super().__init__(session, obj_id)
        self.table_width = 0
        self.has_column_header = False
        self.has_row_header = False

    def _apply(self, data):
        super()._apply(data)
        t = data.get("table", {})
        self.table_width = t.get("table_width", 0)
        self.has_column_header = t.get("has_column_header", False)
        self.has_row_header = t.get("has_row_header", False)

    def to_patch_dict(self):
        return {"type": "table", "table": {
            "table_width": self.table_width,
            "has_column_header": self.has_column_header,
            "has_row_header": self.has_row_header
        }}

    def get_rows_plaintext(self):
        rows = []
        for child in self.children:
            # child is TableRow
            cells = child.data.get("table_row", {}).get("cells", [])
            row = []
            for cell in cells:
                # cell is list of rich objects
                rr = NRichList([type("T", (), {"to_dict": (lambda self, x=r: r)})() for r in cell])
                row.append(rr.text)
            rows.append(row)
        return rows

@register_block
class TableRow(BaseBlock):
    block_type = "table_row"
    def __init__(self, session, obj_id):
        super().__init__(session, obj_id)
        self.cells = []

    def _apply(self, data):
        super()._apply(data)
        self.cells = data.get("table_row", {}).get("cells", [])

    def to_patch_dict(self):
        return {"type": "table_row", "table_row": {"cells": self.cells}}
