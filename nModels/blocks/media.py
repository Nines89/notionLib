# notion_lib/nModels/blocks/media.py
from nModels.blocks.base_block import BaseBlock, register_block
from nTypes.files import n_file
from nTypes.rich_text import NRichList


@register_block
class Image(BaseBlock):
    block_type = "image"

    def __init__(self, session, obj_id):
        super().__init__(session, obj_id)
        self.caption = NRichList()
        self.file_object = None
        self.type = None

    def _apply(self, data):
        super()._apply(data)
        img = data.get("image", {})
        self.type = img.get("type")
        # caption
        self.caption = NRichList([type("T", (), {"to_dict": (lambda self, x=r: x)})() for r in img.get("caption", [])])
        if self.type:
            typdict = img.get(self.type, {})
            typdict["type"] = self.type
            self.file_object = n_file(typdict)

    def to_patch_dict(self):
        return {
            "type": "image",
            "image": {
                "caption": self.caption.to_dict(),
                "type": self.type,
                self.type: self.file_object.to_dict() if self.file_object else {}
            }
        }


@register_block
class FileBlock(BaseBlock):
    block_type = "file"

    def __init__(self, session, obj_id):
        super().__init__(session, obj_id)
        self.caption = NRichList()
        self.name = None
        self.file_object = None

    def _apply(self, data):
        super()._apply(data)
        f = data.get("file", {})
        self.name = f.get("name")
        self.caption = NRichList([type("T", (), {"to_dict": (lambda self, x=r: x)})() for r in f.get("caption", [])])
        if "type" in f:
            t = f.get("type")
            tmp = f.get(t, {})
            tmp["type"] = t
            self.file_object = n_file(tmp)

    def to_patch_dict(self):
        return {
            "type": "file",
            "file": {
                "caption": self.caption.to_dict(),
                "name": self.name,
                "type": self.file_object.data.get("type") if self.file_object else None,
                self.file_object.data.get("type"): self.file_object.to_dict() if self.file_object else {}
            }
        }


@register_block
class Pdf(FileBlock):
    block_type = "pdf"


@register_block
class Embed(BaseBlock):
    block_type = "embed"

    def __init__(self, session, obj_id):
        super().__init__(session, obj_id)
        self.url = None

    def _apply(self, data):
        super()._apply(data)
        self.url = data.get("embed", {}).get("url")

    def to_patch_dict(self):
        return {"type": "embed", "embed": {"url": self.url}}
