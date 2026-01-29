# notion_lib/nModels/blocks/list_blocks.py
from nModels.blocks.base_block import register_block, BlockImpl
from nTypes.rich_text import NRichList, create_rich_list, simple_rich_text_list
from utils.constants import NColors


class ParagraphLike(BlockImpl):
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


if __name__ == "__main__":
    from client.auth import NotionApiClient
    from nModels.blocks.base_block import NFactory

    api = NotionApiClient(key="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")
    obj_todo = "https://www.notion.so/color-A2DCEE-textbf-API-Integration-2a7b7a8f729480b3b420f8736c4116d7?source=copy_link#2a7b7a8f729481c18d4cd0ed0e447f68"
    obj_toggle = "https://www.notion.so/color-A2DCEE-textbf-API-Integration-2a7b7a8f729480b3b420f8736c4116d7?source=copy_link#2a7b7a8f729481529995ce46b59b34c5"
    obj_bullet = "https://www.notion.so/color-A2DCEE-textbf-API-Integration-2a7b7a8f729480b3b420f8736c4116d7?source=copy_link#2a7b7a8f729481c2997effc3c4da56ce"
    obj_number = "https://www.notion.so/color-A2DCEE-textbf-API-Integration-2a7b7a8f729480b3b420f8736c4116d7?source=copy_link#2a7b7a8f7294814da22cea8f62aed209"

    # Partendo da ogni oggetto, ne creiamo uno solo.
    # Per il to-do proviamo il checked.
    # Per gli altri:
    # - cambiamo il colore di sfondo
    # - aggiungiamo un figlio
    # - leggiamo tutti i figli

    child = Toggle.create("toggle for child 1")
    child2 = Toggle.create("toggle for child 2")
    children = [child, child2]

    blk_h1 = NFactory.find(api.headers, obj_todo)
    blk_h1.checked = True
    blk_h1.update()
    blk_h1.append_children(children)
    print("ToDo Class: ", blk_h1.__class__)

    blk_h2 = NFactory.find(api.headers, obj_toggle)
    blk_h2.rich_text = "changed toggle"
    blk_h2.append_children(children)
    print("--------------------------------------------------------------------------------------------------")
    print(blk_h2.get_children())
    print("--------------------------------------------------------------------------------------------------")
    print("Toggle Class: ", blk_h2.__class__)
    print("--------------------------------------------------------------------------------------------------")
    blk_h3 = NFactory.find(api.headers, obj_bullet)
    blk_h3.update()
    print(blk_h3.get_children())
    print("--------------------------------------------------------------------------------------------------")
    print("Bullet Class: ", blk_h3.__class__)
    print("--------------------------------------------------------------------------------------------------")
    blk_h4 = NFactory.find(api.headers, obj_number)
    blk_h4.color = NColors.BLUE_BACKGROUND
    blk_h4.update()
    print("Number Class: ", blk_h4.__class__)