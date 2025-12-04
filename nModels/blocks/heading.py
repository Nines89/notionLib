# notion_lib/nModels/blocks/heading.py
from nModels.blocks.base_block import BaseBlock, register_block
from nTypes.rich_text import NRichList

class BaseHeading(BaseBlock):
    def __init__(self, session, obj_id: str):
        super().__init__(session, obj_id)
        self.rich_text = NRichList()
        self.color = "default"
        self.is_toggleable = False

    def _apply(self, data: dict):
        super()._apply(data)
        h = data.get(self.block_type, {})
        self.rich_text = NRichList([type("T", (), {"to_dict": (lambda self, x=r: x)})() for r in h.get("rich_text", [])])
        self.color = h.get("color", "default")
        self.is_toggleable = bool(h.get("is_toggleable", False))

    def to_patch_dict(self):
        return {
            "type": self.block_type,
            self.block_type: {
                "rich_text": self.rich_text.to_dict(),
                "color": self.color,
                "is_toggleable": self.is_toggleable
            }
        }

@register_block
class Heading1(BaseHeading):
    block_type = "heading_1"

@register_block
class Heading2(BaseHeading):
    block_type = "heading_2"

@register_block
class Heading3(BaseHeading):
    block_type = "heading_3"
