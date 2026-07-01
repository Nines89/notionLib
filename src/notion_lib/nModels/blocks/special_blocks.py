from notion_lib.nModels.blocks.base_block import register_block, BlockImpl
from notion_lib.nTypes import NRichList, IconFactory, NEmoji
from notion_lib.nTypes.rich_text import simple_rich_text_list, create_rich_list
from notion_lib.utils.constants import NColors, NLanguage


@register_block("callout")
class CalloutBlock(BlockImpl):
    type = "callout"
    supports_children = True

    def __init__(self, headers, block_id=None, rich_text: NRichList = None,
                 icon=None, color: str = "default"):
        super().__init__(headers, block_id)
        self._rich_text = rich_text or NRichList()
        self._icon = icon
        self._color = color

    @classmethod
    def from_data(cls, headers, data, block_id):
        p = data["callout"]
        return cls(
            headers=headers, block_id=block_id,
            rich_text=create_rich_list(p.get("rich_text", [])),
            color=p.get("color", "default"),
            icon=IconFactory.find(p.get("icon")),
        )

    @classmethod
    def create(cls, text: str, icon, color: NColors = NColors.DEFAULT):
        return cls(headers=None, rich_text=simple_rich_text_list(text),
                   color=color.value, icon=icon)

    def to_payload(self):
        return {
            "callout": {
                "rich_text": self._rich_text.to_dict(),
                "color": self._color,
                "icon": self._icon.to_payload() if self._icon else None,
            }
        }

    @property
    def rich_text(self): return self._rich_text
    @rich_text.setter
    def rich_text(self, v): self._rich_text = simple_rich_text_list(v)

    @property
    def color(self): return NColors(self._color)
    @color.setter
    def color(self, v: NColors): self._color = v.value

    @property
    def icon(self): return self._icon
    @icon.setter
    def icon(self, v): self._icon = v


@register_block("code")
class CodeBlock(BlockImpl):
    type = "code"
    supports_children = False

    def __init__(self, headers, block_id=None, rich_text: NRichList = None,
                 caption: NRichList = None, language: str = "plain text"):
        super().__init__(headers, block_id)
        self._rich_text = rich_text or NRichList()
        self._caption = caption or NRichList()
        self._language = language

    @classmethod
    def from_data(cls, headers, data, block_id):
        p = data["code"]
        return cls(
            headers=headers, block_id=block_id,
            rich_text=create_rich_list(p.get("rich_text", [])),
            caption=create_rich_list(p.get("caption", [])),
            language=p.get("language", "plain text"),
        )

    @classmethod
    def create(cls, text: str, language: NLanguage = NLanguage.PLAIN_TEXT, caption: str = None):
        return cls(
            headers=None,
            rich_text=simple_rich_text_list(text),
            language=language.value,
            caption=simple_rich_text_list(caption) if caption else NRichList(),
        )

    def to_payload(self):
        return {"code": {
            "rich_text": self._rich_text.to_dict(),
            "caption": self._caption.to_dict(),
            "language": self._language,
        }}

    @property
    def rich_text(self): return self._rich_text
    @rich_text.setter
    def rich_text(self, v): self._rich_text = simple_rich_text_list(v)

    @property
    def caption(self): return self._caption
    @caption.setter
    def caption(self, v): self._caption = simple_rich_text_list(v)

    @property
    def language(self): return NLanguage(self._language)
    @language.setter
    def language(self, v: NLanguage): self._language = v.value


@register_block("synced_block")
class SyncedBlock(BlockImpl):
    type = "synced_block"
    supports_children = False
    updatable = False

    def __init__(self, headers, block_id=None, children=None, synced_from=None, id_=None):
        super().__init__(headers, block_id)
        self._synced_from = synced_from
        self._children = children or []
        self._id = id_

    @classmethod
    def from_data(cls, headers, data, block_id):
        p = data["synced_block"]
        return cls(
            headers=headers, block_id=block_id,
            synced_from=p.get("synced_from"),
            children=p.get("children", []),
            id_=p.get("id"),
        )

    @classmethod
    def create(cls, synced_from=None, children=None, id_=None):
        return cls(headers=None, synced_from=synced_from, children=children or [], id_=id_)

    def to_payload(self):
        if self._synced_from is None:
            return {"synced_block": {"synced_from": None, "children": self._children}}
        return {"synced_block": {"synced_from": self._synced_from}}


@register_block("breadcrumb")
class BreadcrumbBlock(BlockImpl):
    type = "breadcrumb"
    supports_children = False
    updatable = False

    @classmethod
    def from_data(cls, headers, data, block_id):
        obj = cls(headers, block_id)
        obj._data = data
        return obj

    @classmethod
    def create(cls):
        return cls(headers=None)

    def to_payload(self):
        return {"breadcrumb": {}}


@register_block("child_page")
class ChildPageBlock(BlockImpl):
    type = "child_page"
    supports_children = True
    updatable = False

    def __init__(self, headers, block_id=None, title: str = ""):
        super().__init__(headers, block_id)
        self._title = title

    @classmethod
    def from_data(cls, headers, data, block_id):
        p = data["child_page"]
        obj = cls(headers=headers, block_id=block_id, title=p.get("title", ""))
        obj._data = data
        return obj

    @classmethod
    def create(cls, title: str):
        return cls(headers=None, title=title)

    def update(self):
        from notion_lib.nEndpoints.pages import update_page
        from notion_lib.nTypes.rich_text import simple_rich_text_list
        return update_page(self.headers, self.block_id, {
            "properties": {"title": simple_rich_text_list(self._title).to_dict()}
        })

    def to_payload(self):
        return {"child_page": {"title": self._title}}

    @property
    def title(self): return self._title
    @title.setter
    def title(self, v): self._title = v


@register_block("child_database")
class ChildDatabaseBlock(BlockImpl):
    type = "child_database"
    supports_children = False
    updatable = False

    def __init__(self, headers, block_id=None, title: str = ""):
        super().__init__(headers, block_id)
        self._title = title

    @classmethod
    def from_data(cls, headers, data, block_id):
        p = data["child_database"]
        obj = cls(headers=headers, block_id=block_id, title=p.get("title", ""))
        obj._data = data
        return obj

    @classmethod
    def create(cls, title: str):
        return cls(headers=None, title=title)

    def to_payload(self):
        return {"child_database": {"title": self._title}}

    def update(self):
        from notion_lib.nEndpoints.databases import update_db
        return update_db(self.headers, self.block_id, title=self._title)

    @property
    def title(self): return self._title
    @title.setter
    def title(self, v): self._title = v


@register_block("equation")
class EquationBlock(BlockImpl):
    type = "equation"
    supports_children = False

    def __init__(self, headers, block_id=None, expression: str = ""):
        super().__init__(headers, block_id)
        self._expression = expression

    @classmethod
    def from_data(cls, headers, data, block_id):
        p = data["equation"]
        return cls(headers=headers, block_id=block_id, expression=p.get("expression", ""))

    @classmethod
    def create(cls, expression: str):
        return cls(headers=None, expression=expression)

    def to_payload(self):
        return {"equation": {"expression": self._expression}}

    @property
    def expression(self): return self._expression
    @expression.setter
    def expression(self, v): self._expression = v


@register_block("bookmark")
class BookmarkBlock(BlockImpl):
    type = "bookmark"
    supports_children = False

    def __init__(self, headers, block_id=None, caption: NRichList = None, url: str = None):
        super().__init__(headers, block_id)
        self._caption = caption or NRichList()
        self._url = url

    @classmethod
    def from_data(cls, headers, data, block_id):
        p = data["bookmark"]
        return cls(
            headers=headers, block_id=block_id,
            caption=create_rich_list(p.get("caption", [])),
            url=p.get("url", ""),
        )

    @classmethod
    def create(cls, caption: str = None, url: str = None):
        return cls(
            headers=None,
            caption=simple_rich_text_list(caption) if caption else NRichList(),
            url=url,
        )

    def to_payload(self):
        return {"bookmark": {"caption": self._caption.to_dict(), "url": self._url}}

    @property
    def url(self): return self._url
    @url.setter
    def url(self, v): self._url = v

    @property
    def caption(self): return self._caption
    @caption.setter
    def caption(self, v): self._caption = simple_rich_text_list(v)


@register_block("link_to_page")
class LinkToPageBlock(BlockImpl):
    """
    Blocco che punta a un'altra pagina o database.

    Notion API restituisce uno di:
      {"link_to_page": {"type": "page_id",    "page_id":    "..."}}
      {"link_to_page": {"type": "database_id","database_id":"..."}}

    Non creabile né aggiornabile via API pubblica.
    """
    type = "link_to_page"
    supports_children = False
    updatable = False

    def __init__(self, headers, block_id=None, target_type: str = None, target_id: str = None):
        super().__init__(headers, block_id)
        self._target_type = target_type   # "page_id" | "database_id"
        self._target_id = target_id

    @classmethod
    def from_data(cls, headers, data, block_id):
        p = data["link_to_page"]
        t = p.get("type")
        return cls(
            headers=headers,
            block_id=block_id,
            target_type=t,
            target_id=p.get(t) if t else None,
        )

    @classmethod
    def create(cls, **kwargs):
        raise NotImplementedError("LinkToPageBlock non può essere creato via API pubblica.")

    def to_payload(self):
        raise NotImplementedError("LinkToPageBlock non può essere aggiornato via API pubblica.")

    def update(self):
        raise NotImplementedError("LinkToPageBlock è read-only.")

    @property
    def target_type(self) -> str:
        return self._target_type

    @property
    def target_id(self) -> str:
        return self._target_id

    def __repr__(self):
        return f"<LinkToPageBlock {self._target_type}={self._target_id}>"


@register_block("column_list")
class ColumnListBlock(BlockImpl):
    type = "column_list"
    supports_children = True
    ratios = {2: 0.5, 3: 0.33, 4: 0.25, 5: 0.20,
              6: 0.17, 7: 0.14, 8: 0.12, 9: 0.11, 10: 0.1}
    ratio = None

    def __init__(self, headers, block_id=None):
        super().__init__(headers, block_id)
        self.children = []

    @classmethod
    def from_data(cls, headers, data, block_id):
        obj = cls(headers=headers, block_id=block_id)
        obj._data = data
        return obj

    @classmethod
    def create(cls):
        return cls(headers=None)

    @classmethod
    def create_with_columns(cls, count: int, parent):
        if count > 10:
            raise ValueError("Massimo 10 colonne.")
        cls.ratio = cls.ratios[count]
        list_block = cls.create()
        list_block.children = [ColumnBlock.create(ratio=cls.ratio) for _ in range(count)]
        parent.append_children([list_block])

    def to_payload(self):
        return {"column_list": {"children": [col.to_payload() for col in self.children]}}


@register_block("column")
class ColumnBlock(BlockImpl):
    type = "column"
    supports_children = True

    def __init__(self, headers, block_id=None, ratio=None):
        super().__init__(headers, block_id)
        self._ratio = ratio
        self.children = []

    @classmethod
    def from_data(cls, headers, data, block_id):
        obj = cls(headers=headers, block_id=block_id)
        obj._data = data
        return obj

    @classmethod
    def create(cls, ratio=None):
        return cls(headers=None, ratio=ratio)

    def to_payload(self):
        from notion_lib.nModels.blocks.paragraph import ParagraphBlock
        dummy = ParagraphBlock.create("dummy text for column")
        payload = {"column": {
            "children": [dummy.to_payload()] + [ch.to_payload() for ch in self.children]
        }}
        if self._ratio is not None:
            payload["column"]["width_ratio"] = self._ratio
        return payload


@register_block("divider")
class DividerBlock(BlockImpl):
    type = "divider"
    supports_children = False
    updatable = False

    @classmethod
    def from_data(cls, headers, data, block_id):
        obj = cls(headers=headers, block_id=block_id)
        obj._data = data
        return obj

    @classmethod
    def create(cls):
        return cls(headers=None)

    def to_payload(self):
        return {"divider": {}}


@register_block("quote")
class QuoteBlock(BlockImpl):
    type = "quote"
    supports_children = True

    def __init__(self, headers, block_id=None, rich_text: NRichList = None,
                 color: str = "default", children: list = None):
        super().__init__(headers, block_id)
        self._rich_text = rich_text or NRichList()
        self._color = color
        self._children_cache = children or []

    @property
    def children(self):
        if not self._children_cache and self.block_id:
            self._children_cache = self.get_children()
        return self._children_cache

    def _invalidate_cache(self):
        self._children_cache = []

    def add_child(self, block):
        self.append_children([block])
        self._invalidate_cache()

    def add_children(self, blocks: list):
        self.append_children(blocks)
        self._invalidate_cache()

    def remove_child(self, block):
        block.delete()
        self._invalidate_cache()

    def remove_child_at(self, index: int):
        self.children[index].delete()
        self._invalidate_cache()

    def update_child(self, block):
        if not block.updatable:
            print(f"Warning: {block.type} non è aggiornabile, saltato.")
            return
        block.update()
        self._invalidate_cache()

    @classmethod
    def from_data(cls, headers, data, block_id):
        p = data["quote"]
        return cls(
            headers=headers, block_id=block_id,
            rich_text=create_rich_list(p.get("rich_text", [])),
            color=p.get("color", "default"),
        )

    @classmethod
    def create(cls, text: str, color: NColors = NColors.DEFAULT, children: list = None):
        return cls(headers=None, rich_text=simple_rich_text_list(text),
                   color=color.value, children=children or [])

    def to_payload(self):
        payload = {"quote": {"rich_text": self._rich_text.to_dict(), "color": self._color}}
        if self.block_id is None and self._children_cache:
            payload["quote"]["children"] = [c.to_payload() for c in self._children_cache]
        return payload

    @property
    def rich_text(self): return self._rich_text
    @rich_text.setter
    def rich_text(self, v): self._rich_text = simple_rich_text_list(v)

    @property
    def color(self): return NColors(self._color)
    @color.setter
    def color(self, v: NColors): self._color = v.value


@register_block("table_of_contents")
class TableOfContentsBlock(BlockImpl):
    type = "table_of_contents"
    supports_children = False

    def __init__(self, headers, block_id=None, color: str = "default"):
        super().__init__(headers, block_id)
        self._color = color

    @classmethod
    def from_data(cls, headers, data, block_id):
        p = data["table_of_contents"]
        return cls(headers=headers, block_id=block_id, color=p.get("color", "default"))

    @classmethod
    def create(cls, color: NColors = NColors.DEFAULT):
        return cls(headers=None, color=color.value)

    def to_payload(self):
        return {"table_of_contents": {"color": self._color}}

    @property
    def color(self): return NColors(self._color)
    @color.setter
    def color(self, v: NColors): self._color = v.value


@register_block("link_preview")
class LinkPreviewBlock(BlockImpl):
    type = "link_preview"
    supports_children = False
    updatable = False

    def __init__(self, headers, block_id=None, url: str = None):
        super().__init__(headers, block_id)
        self._url = url

    @classmethod
    def from_data(cls, headers, data, block_id):
        p = data["link_preview"]
        return cls(headers=headers, block_id=block_id, url=p.get("url"))

    @classmethod
    def create(cls, **kwargs):
        raise NotImplementedError("LinkPreviewBlock è read-only.")

    def to_payload(self):
        raise NotImplementedError("LinkPreviewBlock è read-only.")

    def update(self):
        raise NotImplementedError("LinkPreviewBlock è read-only.")

    @property
    def url(self): return self._url

    def __repr__(self):
        return f"<LinkPreviewBlock url='{self._url}'>"

