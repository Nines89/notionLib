# notion_lib/nModels/blocks/list_blocks.py
from nModels.blocks.base_block import BaseBlock, register_block
from nTypes.rich_text import NRichList


class ParagraphLike(BaseBlock):
    def __init__(self, session, obj_id: str):
        super().__init__(session, obj_id)
        self.rich_text = NRichList()
        self.color = "default"

    def _apply(self, data: dict):
        super()._apply(data)
        p = data.get(self.block_type, {})
        self.rich_text = NRichList(
            [type("T", (), {"to_dict": (lambda self, x=r: x)})() for r in p.get("rich_text", [])])
        self.color = p.get("color", "default")

    def to_patch_dict(self):
        return {
            "type": self.block_type,
            self.block_type: {
                "rich_text": self.rich_text.to_dict(),
                "color": self.color
            }
        }


@register_block
class ToDo(ParagraphLike):
    block_type = "to_do"

    def __init__(self, session, obj_id):
        super().__init__(session, obj_id)
        self.checked = False

    def _apply(self, data: dict):
        super()._apply(data)
        self.checked = data.get(self.block_type, {}).get("checked", False)

    def to_patch_dict(self):
        base = super().to_patch_dict()
        base[self.block_type].update({"checked": self.checked})
        return base


@register_block
class Toggle(ParagraphLike):
    block_type = "toggle"


@register_block
class BulletedListItem(ParagraphLike):
    block_type = "bulleted_list_item"


@register_block
class NumberedListItem(ParagraphLike):
    block_type = "numbered_list_item"
