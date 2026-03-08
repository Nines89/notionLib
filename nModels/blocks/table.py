from nModels.blocks.base_block import register_block, BlockImpl
from nTypes import NRichList, IconFactory, NEmoji
from nTypes.rich_text import simple_rich_text_list, create_rich_list, NRichText
from utils.constants import NColors, NLanguage
from nModels import NObj


@register_block("table_row")
class TableRowBlock(BlockImpl):
    type = "table_row"
    supports_children = False

    def __init__(self,
                 headers,
                 block_id=None,
                 cells: list[NRichList()] = None):
        super().__init__(headers, block_id)
        self._cells = [
            cell if isinstance(cell, NRichList) else create_rich_list(cell)
            for cell in cells
        ]

    @classmethod
    def from_data(cls, headers, data, block_id):
        p = data["table_row"]
        obj = cls(
            headers=headers,
            block_id=block_id,
            cells=p.get("cells", [NRichList()]),
        )
        obj._data = data
        return obj

    @classmethod
    def create(cls,
               cells: list[NRichList]):
        return cls(
            headers=None,
            cells=cells
        )

    def cell(self, column: int):
        return self._cells[column-1].text

    def to_payload(self):
        cell_payload = [cell.to_dict() for cell in self._cells]
        return {
            "table_row": {
                "cells": cell_payload
            }
        }

    def __len__(self):
        return len(self._cells)

@register_block("table")
class TableBlock(BlockImpl):
    type = "table"
    supports_children = True

    def __init__(self,
                 headers,
                 block_id=None,
                 table_width: int = None,
                 has_column_header: bool = None,
                 has_row_header: bool = None,
                 cells: [TableRowBlock] = None):
        super().__init__(headers, block_id)
        self._block_id = block_id
        self._table_width = table_width
        self._has_column_header = has_column_header
        self._has_row_header = has_row_header
        if block_id:
            self._cells = self.get_children()
        else:
            self._cells = cells

    @classmethod
    def from_data(cls, headers, data, block_id):
        p = data["table"]
        obj = cls(
            headers=headers,
            block_id=block_id,
            table_width=p.get("table_width", 1),
            has_column_header=p.get("has_column_header", False),
            has_row_header=p.get("has_row_header", False)
        )
        obj._data = data
        return obj

    @classmethod
    def create(cls,
               table_width: int,
               has_column_header: bool,
               has_row_header: bool,
               cells: [TableRowBlock] = None):
        for idx, c in enumerate(cells):
            if len(c) != table_width:
                raise ArithmeticError(f"Number of columns of the row {idx+1} is {len(c)} instead of {table_width}")
        return cls(
            headers=None,
            table_width=table_width,
            has_column_header=has_column_header,
            has_row_header=has_row_header,
            cells=cells
        )

    def cell(self, row: int, column: int):
        return self._cells[row-1].cell(column)

    def to_payload(self):

        payload = {
            "has_column_header": self._has_column_header,
            "has_row_header": self._has_row_header,
        }

        if self.block_id is None:
            payload["table_width"] = self._table_width
            payload["children"] = [row.to_payload() for row in self._cells]

        return {
            "type": "table",
            "table": payload
        }

    @property
    def has_column_header(self):
        return self._has_column_header

    @has_column_header.setter
    def has_column_header(self, value: bool):
        self._has_column_header = value

    @property
    def has_row_header(self):
        return self._has_row_header

    @has_row_header.setter
    def has_row_header(self, value: bool):
        self._has_row_header = value


if __name__ == "__main__":
    import sys
    import os

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
    from client.auth import NotionApiClient
    from nModels.blocks.base_block import NFactory

    api = NotionApiClient(key="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")

    obj_toggle = "https://www.notion.so/color-A2DCEE-textbf-API-Integration-2a7b7a8f729480b3b420f8736c4116d7?source=copy_link#304b7a8f729480ff8cccedd17c271fd9"
    father = NFactory.find(api.headers, obj_toggle)

    obj_table = "https://www.notion.so/color-A2DCEE-textbf-API-Integration-2a7b7a8f729480b3b420f8736c4116d7?source=copy_link#31cb7a8f729480a79acdd38d9ccae328"

    children = []
    table_blk = NFactory.find(api.headers, obj_table)
    print(table_blk.to_payload())
    table_blk.has_column_header = True
    table_blk.has_row_header = True
    table_blk.update()

    cell_to_read = (1, 1)
    print(table_blk.cell(*cell_to_read))

    rows = []
    for r in range(1, 3):
        rows.append(TableRowBlock.create([simple_rich_text_list(f"tit {r} 1"),
                                          simple_rich_text_list(f"tit {r} 2")]))

    table = TableBlock.create(2, False, True, cells=rows)
    father.append_children([table])

    # guarda la fine di questa conversazione, valuta get e set item per leggere la tabella oltre che il cells
    pass
