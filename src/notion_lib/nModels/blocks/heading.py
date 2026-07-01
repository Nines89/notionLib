# notion_lib/nModels/blocks/heading.py
from notion_lib.nModels.blocks.base_block import register_block, BlockImpl
from notion_lib.nTypes.rich_text import NRichList, create_rich_list, simple_rich_text_list
from notion_lib.utils.constants import NColors


class BaseHeading(BlockImpl):
    type = "heading"
    block_type = "heading"
    supports_children = False

    def __init__(self,
                 headers,
                 block_id=None,
                 rich_text: NRichList=None,
                 color="default",
                 is_toggleable=False):
        super().__init__(headers, block_id)
        self._rich_text = rich_text or NRichList
        self._color = color
        self._is_toggleable = is_toggleable
        if self._is_toggleable:
            self.supports_children = True

    @classmethod
    def from_data(cls, headers, data, block_id):
        t = data["type"]
        p = data[t]
        obj = cls(
            headers=headers,
            block_id=block_id,
            rich_text=create_rich_list(p.get("rich_text", [])),
            color=p.get("color", "default"),
            is_toggleable=p.get("is_toggleable", False)
        )
        obj._data = data
        return obj

    @classmethod
    def create(cls, text: str, color="default", is_toggleable=False):
        return cls(
            headers=None,
            rich_text=simple_rich_text_list(text),
            color=color,
            is_toggleable=is_toggleable
        )

    def to_payload(self):
        return {
            self.block_type: {
                "rich_text": self._rich_text.to_dict(),
                "color": self._color,
                "is_toggleable": self._is_toggleable
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

    @property
    def is_toggleable(self):
        return  self._is_toggleable

    @is_toggleable.setter
    def is_toggleable(self, value: bool):
        self._is_toggleable = value
        if self.is_toggleable:
            self.supports_children = True


@register_block("heading_1")
class Heading1(BaseHeading):
    block_type = "heading_1"

@register_block("heading_2")
class Heading2(BaseHeading):
    block_type = "heading_2"

@register_block("heading_3")
class Heading3(BaseHeading):
    block_type = "heading_3"

