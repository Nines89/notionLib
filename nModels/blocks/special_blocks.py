from nModels.blocks.base_block import register_block, BlockImpl
from nTypes import NRichList, IconFactory
from nTypes.rich_text import simple_rich_text_list, create_rich_list
from utils.constants import NColors

@register_block("callout")
class CalloutBlock(BlockImpl):
    type = "callout"
    supports_children = False

    def __init__(self,
                 headers,
                 block_id=None,
                 rich_text: NRichList=None,
                 icon = None,
                 color: str="default"):
        super().__init__(headers, block_id)
        self._rich_text = rich_text or NRichList
        self._icon = icon
        self._color = color

    @classmethod
    def from_data(cls, headers, data, block_id):
        p = data["callout"]
        obj = cls(
            headers=headers,
            block_id=block_id,
            rich_text=create_rich_list(p.get("rich_text", [])),
            color=p.get("color", "default"),
            icon=IconFactory.find(p.get("icon", None))
        )
        obj._data = data
        return obj

    @classmethod
    def create(cls, text: str, icon, color: NColors = NColors.DEFAULT):
        return cls(
            headers=None,
            rich_text=simple_rich_text_list(text),
            color=color.value,
            icon=icon,
        )

    def to_payload(self):
        return {
            "callout": {
                "rich_text": self._rich_text.to_dict(),
                "color": self._color,
                "icon": self._icon.to_payload(),
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
    def icon(self):
        return self._icon

    @icon.setter
    def icon(self, value):
        self._icon = value


@register_block("synced_block")
class SyncedBlock(BlockImpl):
    type = "synced_block"
    supports_children = False

    def __init__(self,
                 headers,
                 block_id=None,
                 children=None,
                 synced_from=None,
                 id_=None):
        super().__init__(headers, block_id)
        self._synced_from = synced_from
        self._children = children or []
        self._id = id_

    @classmethod
    def from_data(cls, headers, data, block_id):
        p = data["synced_block"]
        obj = cls(
            headers=headers,
            block_id=block_id,
            synced_from=p.get("synced_from"),
            children=p.get("children", []),
            id_=p.get("id", None),
        )
        obj._data = data
        return obj

    @classmethod
    def create(cls, synced_from: str, children=None, id_=None):
        pass

    def to_payload(self):
        if self._synced_from is None:
            return {
                "synced_block": {
                    "synced_from": self._synced_from,
                    "children": self._children,
                }
            }
        return {
            "synced_block": {
                "synced_from": self._synced_from,
            }
        }

    def update(self):
        raise NotImplementedError("It's Not Implemented to Update a SyncedBlock")


if __name__ == "__main__":
    from client.auth import NotionApiClient
    from nModels.blocks.base_block import NFactory

    api = NotionApiClient(key="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")
    obj_call = "https://www.notion.so/color-A2DCEE-textbf-API-Integration-2a7b7a8f729480b3b420f8736c4116d7?source=copy_link#2a7b7a8f729481b4957be14adb7d707f"
    obj_sync_fat = "https://www.notion.so/color-A2DCEE-textbf-API-Integration-2a7b7a8f729480b3b420f8736c4116d7?source=copy_link#2fcb7a8f72948076861afbb4aefa6490"
    obj_sync_ch = "https://www.notion.so/bot-title-2a7b7a8f729481cdad34ef057d7149d1?source=copy_link#2fcb7a8f729480eda980fbf5592776e7"
    blk_h1 = NFactory.find(api.headers, obj_call)
    # questi cambieranno in base al tipo di icona
    print(blk_h1.icon.url)
    #############################################
    print(blk_h1.color)
    #############################################
    blk_h2 = NFactory.find(api.headers, obj_sync_ch)
    print(blk_h2.to_payload())

    blk_h2 = NFactory.find(api.headers, obj_sync_ch)
    print(blk_h2.to_payload())

    pass

