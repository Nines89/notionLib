# notion_lib/nModels/blocks/list_blocks.py
from notion_lib.nModels.blocks.base_block import register_block, BlockImpl
from notion_lib.nTypes.rich_text import NRichList, create_rich_list, simple_rich_text_list
from notion_lib.utils.constants import NColors


class ParagraphLike(BlockImpl):
    type = "paragraph"
    block_type = "paragraph_like"
    supports_children = False

    def __init__(self,
                 headers,
                 block_id=None,
                 rich_text: NRichList=None,
                 color="default"):
        super().__init__(headers, block_id)
        self._rich_text = rich_text or NRichList
        self._color = color

    @classmethod
    def from_data(cls, headers, data, block_id):
        t = data["type"]
        p = data[t]
        obj = cls(
            headers=headers,
            block_id=block_id,
            rich_text=create_rich_list(p.get("rich_text", [])),
            color=p.get("color", "default")
        )
        obj._data = data
        return obj

    @classmethod
    def create(cls, text: str, color="default", is_toggleable=False):
        return cls(
            headers=None,
            rich_text=simple_rich_text_list(text),
            color=color,
        )

    def to_payload(self):
        return {
            self.block_type: {
                "rich_text": self._rich_text.to_dict(),
                "color": self._color,
            }
        }

    @property
    def rich_text(self):
        return self._rich_text

    @rich_text.setter
    def rich_text(self, value: str):
        self._rich_text = simple_rich_text_list(value)

    @property
    def color(self):
        return NColors(self._color)

    @color.setter
    def color(self, value: NColors):
        self._color = value.value


@register_block("to_do")
class ToDo(ParagraphLike):
    block_type = "to_do"
    supports_children = True

    def __init__(self,
                 headers,
                 block_id=None,
                 rich_text: NRichList=None,
                 color="default",
                 checked=False):
        super().__init__(headers=headers,
                         block_id=block_id,
                         rich_text=rich_text,
                         color=color)
        self._checked = checked

    @classmethod
    def from_data(cls, headers, data, block_id):
        t = data["type"]
        p = data[t]
        obj = cls(
            headers=headers,
            block_id=block_id,
            rich_text=create_rich_list(p.get("rich_text", [])),
            color=p.get("color", "default"),
            checked=p.get("checked", False)
        )
        obj._data = data
        return obj

    @classmethod
    def create(cls, text: str, color="default", is_toggleable=False, checked=False):
        return cls(
            headers=None,
            rich_text=simple_rich_text_list(text),
            color=color,
            checked=checked
        )

    def to_payload(self):
        payload = super().to_payload()
        payload[self.block_type]["checked"] = self._checked
        return payload

    @property
    def checked(self):
        return self._checked

    @checked.setter
    def checked(self, checked: bool):
        self._checked = checked


@register_block("toggle")
class Toggle(ParagraphLike):
    block_type = "toggle"
    supports_children = True


@register_block("bulleted_list_item")
class BulletedListItem(ParagraphLike):
    block_type = "bulleted_list_item"
    supports_children = True


@register_block("numbered_list_item")
class NumberedListItem(ParagraphLike):
    block_type = "numbered_list_item"
    supports_children = True

