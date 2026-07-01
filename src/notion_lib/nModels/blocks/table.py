from notion_lib.nModels.blocks.base_block import register_block, BlockImpl
from notion_lib.nTypes import NRichList
from notion_lib.nTypes.rich_text import simple_rich_text_list, create_rich_list


@register_block("table_row")
class TableRowBlock(BlockImpl):
    type = "table_row"
    supports_children = False

    def __init__(self,
                 headers,
                 block_id=None,
                 cells: list[NRichList()] = None): # noqa
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
                 cells: [TableRowBlock] = None): # noqa
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
               cells: [TableRowBlock] = None): # noqa
        for idx, c in enumerate(cells): # noqa
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
        return self._cells[row-1].cell(column) # noqa

    def to_payload(self):

        payload = {
            "has_column_header": self._has_column_header,
            "has_row_header": self._has_row_header,
        }

        if self.block_id is None:
            payload["table_width"] = self._table_width
            payload["children"] = [row.to_payload() for row in self._cells]  # noqa

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

    def update(self):
        _ = super().update()
        for row in self._cells: # noqa
            return row.update()

    def __getitem__(self, item):
        if isinstance(item, tuple):
            r, c = item
            return self._cells[r-1].cell(c) # noqa
        return  self._cells[item] # noqa

    def __setitem__(self, item, value):
        if isinstance(item, tuple):
            r, c = item
            self._cells[r-1]._cells[c-1] = simple_rich_text_list(value) # noqa
        return  None



