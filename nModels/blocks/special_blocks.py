# notion_lib/nModels/blocks/special_blocks.py
from nModels.blocks.base_block import BaseBlock, register_block
from nTypes.rich_text import NRichList


@register_block
class Callout(BaseBlock):
    block_type = "callout"

    def __init__(self, session, obj_id):
        super().__init__(session, obj_id)
        self.rich_text = NRichList()
        self.icon = None
        self.color = "default"

    def _apply(self, data):
        super()._apply(data)
        c = data.get("callout", {})
        self.rich_text = NRichList(
            [type("T", (), {"to_dict": (lambda self, x=r: x)})() for r in c.get("rich_text", [])])
        self.icon = c.get("icon")
        self.color = c.get("color", "default")

    def to_patch_dict(self):
        return {
            "type": "callout",
            "callout": {
                "rich_text": self.rich_text.to_dict(),
                "icon": self.icon,
                "color": self.color
            }
        }


@register_block
class SyncedBlock(BaseBlock):
    block_type = "synced_block"

    def __init__(self, session, obj_id):
        super().__init__(session, obj_id)
        self.synced_from = None

    def _apply(self, data):
        super()._apply(data)
        self.synced_from = data.get("synced_block", {}).get("synced_from")

    def to_patch_dict(self):
        return {"type": "synced_block", "synced_block": {"synced_from": self.synced_from}}


@register_block
class Breadcrumb(BaseBlock):
    block_type = "breadcrumb"

    def to_patch_dict(self):
        return {"type": "breadcrumb", "breadcrumb": {}}


@register_block
class ChildPage(BaseBlock):
    block_type = "child_page"

    def __init__(self, session, obj_id):
        super().__init__(session, obj_id)
        self.title = None

    def _apply(self, data):
        super()._apply(data)
        self.title = data.get("child_page", {}).get("title")

    def to_patch_dict(self):
        return {"type": "child_page", "child_page": {"title": self.title}}


@register_block
class ChildDatabase(BaseBlock):
    block_type = "child_database"

    def __init__(self, session, obj_id):
        super().__init__(session, obj_id)
        self.title = None

    def _apply(self, data):
        super()._apply(data)
        self.title = data.get("child_database", {}).get("title")

    def to_patch_dict(self):
        return {"type": "child_database", "child_database": {"title": self.title}}


@register_block
class CodeBlock(BaseBlock):
    block_type = "code"

    def __init__(self, session, obj_id):
        super().__init__(session, obj_id)
        self.caption = NRichList()
        self.rich_text = NRichList()
        self.language = "plain text"

    def _apply(self, data):
        super()._apply(data)
        c = data.get("code", {})
        self.caption = NRichList([type("T", (), {"to_dict": (lambda self, x=r: x)})() for r in c.get("caption", [])])
        self.rich_text = NRichList(
            [type("T", (), {"to_dict": (lambda self, x=r: x)})() for r in c.get("rich_text", [])])
        self.language = c.get("language", "plain text")

    def to_patch_dict(self):
        return {"type": "code", "code": {"caption": self.caption.to_dict(), "rich_text": self.rich_text.to_dict(),
                                         "language": self.language}}


@register_block
class Equation(BaseBlock):
    block_type = "equation"

    def __init__(self, session, obj_id):
        super().__init__(session, obj_id)
        self.expression = None

    def _apply(self, data):
        super()._apply(data)
        self.expression = data.get("equation", {}).get("expression")

    def to_patch_dict(self):
        return {"type": "equation", "equation": {"expression": self.expression}}


@register_block
class Bookmark(BaseBlock):
    block_type = "bookmark"

    def __init__(self, session, obj_id):
        super().__init__(session, obj_id)
        self.caption = NRichList()
        self.url = None

    def _apply(self, data):
        super()._apply(data)
        b = data.get("bookmark", {})
        self.caption = NRichList([type("T", (), {"to_dict": (lambda self, x=r: x)})() for r in b.get("caption", [])])
        self.url = b.get("url")

    def to_patch_dict(self):
        return {"type": "bookmark", "bookmark": {"caption": self.caption.to_dict(), "url": self.url}}


@register_block
class Column(BaseBlock):
    block_type = "column"

    def __init__(self, session, obj_id):
        super().__init__(session, obj_id)
        self.width_ratio = None

    def _apply(self, data):
        super()._apply(data)
        self.width_ratio = data.get("column", {}).get("width_ratio")

    def to_patch_dict(self):
        return {"type": "column", "column": {"width_ratio": self.width_ratio}}


@register_block
class ColumnList(BaseBlock):
    block_type = "column_list"

    def to_patch_dict(self):
        return {"type": "column_list", "column_list": {}}


@register_block
class Divider(BaseBlock):
    block_type = "divider"

    def to_patch_dict(self):
        return {"type": "divider", "divider": {}}
