# notion_lib/nModels/blocks/paragraph.py
from nModels.blocks.base_block import BaseBlock, register_block
from nTypes.rich_text import NRichList

@register_block
class Paragraph(BaseBlock):
    block_type = "paragraph"

    def __init__(self, session, obj_id: str):
        super().__init__(session, obj_id)
        self.rich_text = NRichList()
        self.color = "default"

    def _apply(self, data: dict):
        super()._apply(data)
        p = data.get("paragraph", {})
        rt = p.get("rich_text", [])
        self.rich_text = NRichList([type("T", (), {"to_dict": (lambda self, x=r: x)})() for r in rt]) \
            if rt else NRichList()
        self.color = p.get("color", "default")

    def to_patch_dict(self) -> dict:
        return {
            "type": "paragraph",
            "paragraph": {
                "rich_text": self.rich_text.to_dict(),
                "color": self.color
            }
        }

    @classmethod
    def create(cls, session, parent_id: str, rich_text: NRichList, color: str = "default"):
        payload = [{
            "type": "paragraph",
            "paragraph": {
                "rich_text": rich_text.to_dict(),
                "color": color
            }
        }]
        data = session.patch(f"https://api.notion.com/v1/blocks/{parent_id}/children", json={"children": payload})
        # session.patch already returns parsed json via http client; use results[0]
        first = data.get("results", [None])[0]
        if not first:
            raise RuntimeError("Create paragraph failed")
        return cls.from_json(session, first)
