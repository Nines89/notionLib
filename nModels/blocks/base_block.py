# notion_lib/nModels/blocks/base_block.py
from typing import Type, Dict, Optional
from nModels.base_object import NObj
from nEndpoints import blocks as blocks_endpoint
from nTypes.rich_text import NRichList

# forward imports for registration (import only classes, avoid circular heavy imports)
from nModels.blocks.paragraph import Paragraph
from nModels.blocks.heading import Heading1, Heading2, Heading3
from nModels.blocks.list_blocks import ToDo, Toggle, BulletedListItem, NumberedListItem
from nModels.blocks.media import Image, FileBlock, Pdf, Embed
from nModels.blocks.table import Table, TableRow
from nModels.blocks.special_blocks import (
    Callout, SyncedBlock, Breadcrumb, ChildPage, ChildDatabase,
    CodeBlock, Equation, Bookmark, Column, ColumnList, Divider
)


BLOCK_REGISTRY: Dict[str, Type["BaseBlock"]] = {}


def register_block(cls: Type["BaseBlock"]):
    if cls.block_type:
        BLOCK_REGISTRY[cls.block_type] = cls
    return cls


class BaseBlock(NObj):
    block_type: Optional[str] = None

    def __init__(self, session, obj_id: str):
        super().__init__(session, obj_id)
        self._children = None

    @classmethod
    def from_json(cls, session, data: dict):
        # if called directly create instance of cls
        inst = cls(session, data["id"])
        inst._apply(data)
        return inst

    @staticmethod
    def load_from_json(session, data: dict):
        btype = data.get("type")
        cls = BLOCK_REGISTRY.get(btype, BaseBlock)
        return cls.from_json(session, data)

    def refresh(self):
        data = blocks_endpoint.get_block(self.session, self.obj_id)
        self._apply(data)

    def update(self):
        payload = self.to_patch_dict()
        data = blocks_endpoint.update_block(self.session, self.obj_id, payload)
        self._apply(data)

    def delete(self):
        blocks_endpoint.delete_block(self.session, self.obj_id)

    def append(self, children_payload: list[dict]):
        """
        children_payload: list of block spec dicts (already serialised)
        """
        data = blocks_endpoint.append_children(self.session, self.obj_id, children_payload)
        # Notion returns the appended children in 'results'
        return [BaseBlock.load_from_json(self.session, r) for r in data.get("results", [])]

    @property
    def children(self):
        if self._children is None:
            # lazy load children via endpoint
            data = blocks_endpoint.get_block(self.session, f"{self.obj_id}/children")
            results = data.get("results", [])
            self._children = [BaseBlock.load_from_json(self.session, r) for r in results]
        return self._children

    def to_patch_dict(self) -> dict:
        raise NotImplementedError

    def _apply(self, data: dict):
        # store raw data; subclasses should extend this (and call super)
        self._data = data

# Register base classes (these imports ensure registration)
__all__ = ["BaseBlock", "register_block", "BLOCK_REGISTRY"]
