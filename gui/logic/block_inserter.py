"""
gui/logic/block_inserter.py
Logica pura per costruire e inserire blocchi in una pagina Notion.
"""

from utils.constants import NColors, NLanguage
from nTypes import NEmoji

from nModels.blocks.paragraph import ParagraphBlock
from nModels.blocks.heading import Heading1, Heading2, Heading3
from nModels.blocks.list_blocks import BulletedListItem, NumberedListItem, Toggle, ToDo
from nModels.blocks.special_blocks import CalloutBlock, CodeBlock, DividerBlock
from nModels.blocks.base_block import NFactory


BLOCK_DEFINITIONS = {
    "paragraph": {
        "label": "Paragrafo",
        "icon": "¶",
        "fields": [
            {"name": "text", "type": "text", "label": "Testo"},
            {"name": "color", "type": "color", "label": "Colore"},
        ],
        "build": lambda values: ParagraphBlock.create(
            text=values.get("text", ""),
            color=values.get("color", "default"),
        ),
    },
    "heading_1": {
        "label": "Heading 1",
        "icon": "H1",
        "fields": [
            {"name": "text", "type": "text", "label": "Testo"},
            {"name": "color", "type": "color", "label": "Colore"},
        ],
        "build": lambda values: Heading1.create(
            text=values.get("text", ""),
            color=values.get("color", "default"),
        ),
    },
    "heading_2": {
        "label": "Heading 2",
        "icon": "H2",
        "fields": [
            {"name": "text", "type": "text", "label": "Testo"},
            {"name": "color", "type": "color", "label": "Colore"},
        ],
        "build": lambda values: Heading2.create(
            text=values.get("text", ""),
            color=values.get("color", "default"),
        ),
    },
    "heading_3": {
        "label": "Heading 3",
        "icon": "H3",
        "fields": [
            {"name": "text", "type": "text", "label": "Testo"},
            {"name": "color", "type": "color", "label": "Colore"},
        ],
        "build": lambda values: Heading3.create(
            text=values.get("text", ""),
            color=values.get("color", "default"),
        ),
    },
    "bulleted_list_item": {
        "label": "Bullet",
        "icon": "•",
        "fields": [
            {"name": "text", "type": "text", "label": "Testo"},
            {"name": "color", "type": "color", "label": "Colore"},
        ],
        "build": lambda values: BulletedListItem.create(
            text=values.get("text", ""),
            color=values.get("color", "default"),
        ),
    },
    "numbered_list_item": {
        "label": "Numbered",
        "icon": "1.",
        "fields": [
            {"name": "text", "type": "text", "label": "Testo"},
            {"name": "color", "type": "color", "label": "Colore"},
        ],
        "build": lambda values: NumberedListItem.create(
            text=values.get("text", ""),
            color=values.get("color", "default"),
        ),
    },
    "toggle": {
        "label": "Toggle",
        "icon": "▸",
        "fields": [
            {"name": "text", "type": "text", "label": "Testo"},
            {"name": "color", "type": "color", "label": "Colore"},
        ],
        "build": lambda values: Toggle.create(
            text=values.get("text", ""),
            color=values.get("color", "default"),
        ),
    },
    "to_do": {
        "label": "To-do",
        "icon": "☑",
        "fields": [
            {"name": "text", "type": "text", "label": "Testo"},
            {"name": "color", "type": "color", "label": "Colore"},
            {"name": "checked", "type": "bool", "label": "Completato"},
        ],
        "build": lambda values: ToDo.create(
            text=values.get("text", ""),
            color=values.get("color", "default"),
            checked=bool(values.get("checked", False)),
        ),
    },
    "callout": {
        "label": "Callout",
        "icon": "💡",
        "fields": [
            {"name": "text", "type": "text", "label": "Testo"},
            {"name": "color", "type": "color", "label": "Colore"},
        ],
        "build": lambda values: CalloutBlock.create(
            text=values.get("text", ""),
            icon=NEmoji({"emoji": "💡"}),
            color=NColors(values.get("color", "default")),
        ),
    },
    "code": {
        "label": "Codice",
        "icon": "</>",
        "fields": [
            {"name": "text", "type": "text", "label": "Codice"},
            {"name": "language", "type": "language", "label": "Linguaggio"},
        ],
        "build": lambda values: CodeBlock.create(
            text=values.get("text", ""),
            language=NLanguage(values.get("language", NLanguage.PLAIN_TEXT.value)),
        ),
    },
    "divider": {
        "label": "Divisore",
        "icon": "—",
        "fields": [],
        "build": lambda values: DividerBlock.create(),
    },
}


def insert_block(headers: dict, page_id: str, block_key: str, values: dict):
    """
    Crea un blocco da BLOCK_DEFINITIONS e lo appende alla pagina target.
    """
    definition = BLOCK_DEFINITIONS.get(block_key)
    if not definition:
        raise ValueError(f"Tipo blocco non supportato: {block_key}")

    block = definition["build"](values or {})
    page = NFactory.find(headers, page_id)
    page.append_children([block])
    return block
