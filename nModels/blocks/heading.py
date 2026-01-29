# notion_lib/nModels/blocks/heading.py
from nModels.blocks.base_block import register_block, BlockImpl
from nTypes.rich_text import NRichList, create_rich_list, simple_rich_text_list
from utils.constants import NColors


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


if __name__ == "__main__":
    from client.auth import NotionApiClient
    from nModels.blocks.base_block import NFactory

    api = NotionApiClient(key="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")
    obj_h1 = "https://www.notion.so/color-A2DCEE-textbf-API-Integration-2a7b7a8f729480b3b420f8736c4116d7?source=copy_link#2a7b7a8f7294814297b9cc59924601e3"
    obj_h2 = "https://www.notion.so/color-A2DCEE-textbf-API-Integration-2a7b7a8f729480b3b420f8736c4116d7?source=copy_link#2a7b7a8f729481f2a917e1c673fb8cf4"
    obj_h3 = "https://www.notion.so/color-A2DCEE-textbf-API-Integration-2a7b7a8f729480b3b420f8736c4116d7?source=copy_link#2a7b7a8f72948193860fc75f7b83d099"

    # Partendo da un paragrafo bianco, vuoto, normale
    # cambiamo il testo
    # cambiamo il colore di sfondo
    # aggiungiamo un figlio
    # leggiamo tutti i figli

    child = Heading3.create("Title Child for H2")
    children = [child]

    blk_h1 = NFactory.find(api.headers, obj_h1)
    blk_h1.rich_text = "Title 1 Bis"
    blk_h1.color = NColors.BLUE_BACKGROUND
    blk_h1.update()
    blk_h1.append_children(children)

    blk_h2 = NFactory.find(api.headers, obj_h2)
    blk_h2.is_toggleable = True
    blk_h2.update()
    blk_h2.append_children(children)
    print(blk_h2.get_children())
    print("--------------------------------------------------------------------------------------------------")
    blk_h3 = NFactory.find(api.headers, obj_h3)
    print(blk_h3.to_payload())