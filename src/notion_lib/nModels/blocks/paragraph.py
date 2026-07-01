from notion_lib.nModels.blocks.base_block import register_block, BlockImpl
from notion_lib.nTypes import NRichList
from notion_lib.nTypes.rich_text import simple_rich_text_list, create_rich_list
from notion_lib.utils.constants import NColors


@register_block("paragraph")
class ParagraphBlock(BlockImpl):
    type = "paragraph"
    supports_children = True

    def __init__(self, headers, block_id=None, rich_text: NRichList=None, color="default"):
        super().__init__(headers, block_id)
        self._rich_text = rich_text or NRichList
        self._color = color

    @classmethod
    def from_data(cls, headers, data, block_id):
        p = data["paragraph"]
        obj = cls(
            headers=headers,
            block_id=block_id,
            rich_text=create_rich_list(p.get("rich_text", [])),
            color=p.get("color", "default")
        )
        obj._data = data
        return obj

    @classmethod
    def create(cls, text: str, color="default"):
        return cls(
            headers=None,
            rich_text=simple_rich_text_list(text),
            color=color
        )

    def to_payload(self):
        return {
            "paragraph": {
                "rich_text": self._rich_text.to_dict(),
                "color": self._color
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


