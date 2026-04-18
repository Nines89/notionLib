from src.notion_lib.nModels.blocks.base_block import register_block, BlockImpl
from src.notion_lib.nTypes import NRichList
from src.notion_lib.nTypes.rich_text import simple_rich_text_list, create_rich_list
from src.notion_lib.utils.constants import NColors


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



if __name__ == "__main__":
    from src.notion_lib.client.auth import NotionApiClient
    from src.notion_lib.nModels.blocks.base_block import NFactory

    api = NotionApiClient(key="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")
    obj_id = "https://www.notion.so/color-A2DCEE-textbf-API-Integration-2a7b7a8f729480b3b420f8736c4116d7?source=copy_link#2a7b7a8f729481078b12e5862da8ce76"

    # Partendo da un paragrafo bianco, vuoto, normale
    # cambiamo il testo
    # cambiamo il colore di sfondo
    # aggiungiamo un figlio
    # leggiamo tutti i figli

    blk = NFactory.find(api.headers, obj_id)
    print(blk.to_payload())
    blk.rich_text = "Abbiamo un cambiamento netto!2"
    blk.color = NColors.BLUE_BACKGROUND
    print(blk.to_payload())
    child = ParagraphBlock.create("Un paragrafo figlio")
    child2 = ParagraphBlock.create("Un secondo paragrafo figlio")
    children = [child, child2]
    blk.update()
    blk.append_children(children)

    print(blk.get_children())