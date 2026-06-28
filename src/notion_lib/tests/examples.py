"""
examples.py
===========
Esempi eseguibili di tutte le funzionalità della libreria.

Ogni sezione è una funzione autonoma che si può eseguire
singolarmente commentando/decommentando la chiamata in fondo al file.

Esecuzione
----------
    cd <root del progetto>
    python examples.py

Struttura
---------
  1.  Auth & client
  2.  Blocks — paragraph
  3.  Blocks — headings
  4.  Blocks — list blocks (to_do, toggle, bulleted, numbered)
  5.  Blocks — media (image, video, file, embed)
  6.  Blocks — table
  7.  Blocks — special (callout, code, equation, bookmark, divider, quote, toc, columns)
  8.  Blocks — synced_block, breadcrumb, child_page, child_database
  9.  Blocks — link_to_page, link_preview
  10. Blocks — meeting_notes
  11. Pages — SimplePage (read, update, children)
  12. Pages — DatabasePage (read, typed props, update)
  13. Pages — PageFactory routing
  14. Databases — NDatabase (read, update, datasources)
  15. DataSources — NDataSource (filter, sort, schema, entries)
  16. Users — UserFactory (person, bot)
  17. Filters — F (tutti i tipi, compound)
  18. Sorts — S
  19. Search
  20. Comments
"""

import sys

from notion_lib.nModels import ParagraphBlock
from notion_lib.nTypes import IconFactory

sys.path.insert(0, "")

from notion_lib.client.auth import NotionApiClient

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG — sostituisci con la tua chiave se necessario
# ─────────────────────────────────────────────────────────────────────────────

API_KEY = "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"

# Pagina principale usata come parent/container negli esempi
PAGE_URL      = "https://www.notion.so/color-A2DCEE-textbf-API-Integration-2a7b7a8f729480b3b420f8736c4116d7"
PAGE_ID       = "2a7b7a8f729480b3b420f8736c4116d7"

# Database e DataSource
DB_URL        = "https://www.notion.so/2a7b7a8f729481919ac9c1853a813571?v=2a7b7a8f7294819bb426000cf2da4ff8&source=copy_link"
DB_CONTAINER  = "https://www.notion.so/ad506059a56f4626b7a4c4ee5a1f4430?v=e589b1d587604016ba6e9b840da871b3&source=copy_link"
DS_URL        = "https://www.notion.so/2c0b7a8f72948024a529f2a82e767024?v=2c0b7a8f72948174811f000c8c4bab20&source=copy_link"

# DatabasePage (entry in un DataSource)
DB_PAGE_URL   = "https://www.notion.so/New-Title-2-The-revenge-2a7b7a8f729481ffadcfe600364f3fd4?source=copy_link"

# Pagina semplice (parent = page)
SIMPLE_PAGE   = "https://www.notion.so/Amleto-aggiornato-via-API-2a7b7a8f7294814596c1dd2c262ffed7"

# Blocchi specifici sulla pagina di integrazione
_BASE = PAGE_URL + "?source=copy_link#"

BLK_PARAGRAPH  = _BASE + "2a7b7a8f729481078b12e5862da8ce76"
BLK_H1         = _BASE + "2a7b7a8f7294814297b9cc59924601e3"
BLK_H2         = _BASE + "2a7b7a8f729481f2a917e1c673fb8cf4"
BLK_H3         = _BASE + "2a7b7a8f72948193860fc75f7b83d099"
BLK_TODO       = _BASE + "2a7b7a8f729481c18d4cd0ed0e447f68"
BLK_TOGGLE     = _BASE + "2a7b7a8f729481529995ce46b59b34c5"
BLK_BULLET     = _BASE + "334b7a8f7294801f9418fb4c06a0c87d"
BLK_NUMBER     = _BASE + "2a7b7a8f7294814da22cea8f62aed209"
BLK_IMAGE      = _BASE + "2a7b7a8f729481e6b128c8ffeaa62669"
BLK_FILE       = _BASE + "2fbb7a8f7294807ca2c0fde21cc2b968"
BLK_EMBED      = _BASE + "2fbb7a8f72948021a338ef1ea3216203"
BLK_TABLE      = _BASE + "31cb7a8f729480a79acdd38d9ccae328"
BLK_TOGGLE_FATHER = _BASE + "304b7a8f729480ff8cccedd17c271fd9"
BLK_CALLOUT    = _BASE + "2a7b7a8f729481b4957be14adb7d707f"
BLK_SYNCED_F   = _BASE + "2fcb7a8f72948076861afbb4aefa6490"
BLK_BREADCRUMB = _BASE + "2a7b7a8f729481ce9154c80df1008698"
BLK_CHILD_PAGE = "https://www.notion.so/Is-it-a-child-page-2a7b7a8f7294814596c1dd2c262ffed7?source=copy_link"
BLK_CHILD_DB   = "https://www.notion.so/2a7b7a8f729481919ac9c1853a813571?v=2a7b7a8f7294819bb426000cf2da4ff8&source=copy_link"
BLK_CODE       = _BASE + "2a7b7a8f729481d48f7af478566b8bb2"
BLK_EQUATION   = _BASE + "2a7b7a8f7294815bad7ee297d18a8c34"
BLK_BOOKMARK   = _BASE + "2a7b7a8f729481a88bb8f028e919c93f"
BLK_COLUMN     = _BASE + "304b7a8f729480cc8ae9f786a0b05d79"
BLK_DIVIDER    = _BASE + "305b7a8f729480dc80bfd914821b79c9"
BLK_QUOTE      = _BASE + "322b7a8f7294802fba7af54ca8f03d78"
BLK_TOC        = _BASE + "325b7a8f729480e1b401f81fb5c311da"
BLK_MEETING    = _BASE + "325b7a8f72948037bc72dfd0a8726941"

# Users
USER_PERSON_ID = "8711f079-8ae4-4748-89a7-d2daf31ff8fe"
USER_BOT_ID    = "9816fe23-bc82-4025-aa43-76789960e89a"


def sep(title: str):
    print(f"\n{'═' * 60}")
    print(f"  {title}")
    print('═' * 60)


def single_sep():
    print(f"\n{'═' * 60}")



# ─────────────────────────────────────────────────────────────────────────────
# 1. AUTH & CLIENT
# ─────────────────────────────────────────────────────────────────────────────

def example_auth():
    sep("1. Auth & Client")
    api = NotionApiClient(key=API_KEY)
    print("Headers costruiti:", list(api.headers.keys()))
    print("Version:", api.version)

    # Immutabilità
    try:
        api.key = "cambiato"
    except AttributeError as e:
        print("Immutabilità key OK:", e)
    single_sep()
    # Bot token (whoami)
    print("Retrieve bot user for given API")
    from notion_lib.nEndpoints.users import get_bot_token
    me = get_bot_token(api.headers)
    print("Bot name:", me.response.get("name"))
    print("Bot type:", me.response.get("type"))


# ─────────────────────────────────────────────────────────────────────────────
# 2. BLOCKS — PARAGRAPH
# ─────────────────────────────────────────────────────────────────────────────

def example_paragraph():
    sep("2. Blocks — Paragraph")
    from notion_lib.nModels.blocks.base_block import NFactory
    from notion_lib.nModels.blocks.paragraph import ParagraphBlock
    from notion_lib.utils.constants import NColors

    api = NotionApiClient(key=API_KEY)
    father = NFactory.find(api.headers, BLK_TOGGLE_FATHER)

    # Leggi il blocco esistente
    blk = NFactory.find(api.headers, BLK_PARAGRAPH)
    print("Testo attuale:", blk.rich_text.text)
    print("Colore attuale:", blk.color)
    print("Payload corrente:", blk.to_payload())

    # Modifica testo e colore, poi aggiorna su Notion
    blk.rich_text = "Paragrafo aggiornato via API"
    blk.color = NColors.BLUE_BACKGROUND
    blk.update()
    print("Aggiornato ✓")

    # Aggiungi due figli
    child1 = ParagraphBlock.create("Figlio 1")
    child2 = ParagraphBlock.create("Figlio 2", color="red") # TODO: perché il colore non sta funzionando
    blk.append_children([child1, child2])
    print("Figli aggiunti ✓")

    # Leggi i figli
    children = blk.get_children()
    print("Figli trovati:", len(children))
    for c in children:
        print("  →", c.rich_text.text)


# ─────────────────────────────────────────────────────────────────────────────
# 3. BLOCKS — HEADINGS
# ─────────────────────────────────────────────────────────────────────────────

def example_headings():
    sep("3. Blocks — Headings")
    from notion_lib.nModels.blocks.base_block import NFactory
    from notion_lib.nModels.blocks.heading import Heading3
    from notion_lib.utils.constants import NColors

    api = NotionApiClient(key=API_KEY)
    father = NFactory.find(api.headers, BLK_TOGGLE_FATHER)

    # H1 — cambia testo e colore
    h1 = NFactory.find(api.headers, BLK_H1)
    print("H1 attuale:", h1.rich_text.text)
    h1.rich_text = "Heading 1 — aggiornato"
    h1.color = NColors.BLUE_BACKGROUND
    h1.update()
    print("H1 aggiornato ✓")

    # H2 — rendi toggleable e aggiungi un figlio
    h2 = NFactory.find(api.headers, BLK_H2)
    print("H2 is_toggleable:", h2.is_toggleable)
    h2.is_toggleable = True
    h2.update()
    child = Heading3.create("Sotto-titolo figlio di H2")
    h2.append_children([child])
    print("H2 toggleable + figlio aggiunti ✓")

    # H2 — leggi figli
    children = h2.get_children()
    print("Figli di H2:", [c.rich_text.text for c in children])

    # H3 — solo lettura payload
    h3 = NFactory.find(api.headers, BLK_H3)
    print("H3 payload:", h3.to_payload())


# ─────────────────────────────────────────────────────────────────────────────
# 4. BLOCKS — LIST BLOCKS
# ─────────────────────────────────────────────────────────────────────────────

def example_list_blocks():
    sep("4. Blocks — List blocks")
    from notion_lib.nModels.blocks.base_block import NFactory
    from notion_lib.nModels.blocks.list_blocks import Toggle
    from notion_lib.utils.constants import NColors

    api = NotionApiClient(key=API_KEY)
    father = NFactory.find(api.headers, BLK_TOGGLE_FATHER)

    # To-Do: spunta il task
    todo = NFactory.find(api.headers, BLK_TODO)
    print("To-Do checked:", todo.checked)
    todo.checked = True
    todo.update()
    print("To-Do spuntato ✓")
    # Aggiungi due figli toggle
    todo.append_children([Toggle.create("sub-task 1"), Toggle.create("sub-task 2")])
    print("Sub-task aggiunti ✓")

    # Toggle: modifica testo e aggiungi figli
    toggle = NFactory.find(api.headers, BLK_TOGGLE)
    toggle.rich_text = "Toggle modificato"
    toggle.update()
    toggle.append_children([Toggle.create("figlio toggle")])
    print("Toggle aggiornato ✓")
    print("Figli toggle:", [c.rich_text.text for c in toggle.get_children()])

    # Bulleted — leggi figli (il blocco ne ha già)
    bullet = NFactory.find(api.headers, BLK_BULLET)
    print("Bullet text:", bullet.rich_text.text)
    children = bullet.get_children()
    if children:
        print("Primo figlio:", children[0].rich_text.text)

    # Numbered — cambia colore
    numbered = NFactory.find(api.headers, BLK_NUMBER)
    numbered.color = NColors.BLUE_BACKGROUND
    numbered.update()
    print("Numbered colore aggiornato ✓")


# ─────────────────────────────────────────────────────────────────────────────
# 5. BLOCKS — MEDIA
# ─────────────────────────────────────────────────────────────────────────────

def example_media():
    sep("5. Blocks — Media")
    from notion_lib.nModels.blocks.base_block import NFactory
    from notion_lib.nTypes.files import FileTypeExternal

    api = NotionApiClient(key=API_KEY)
    father = NFactory.find(api.headers, BLK_TOGGLE_FATHER)

    # Image — leggi e aggiorna caption + URL
    img = NFactory.find(api.headers, BLK_IMAGE)
    print("Image URL:", img.file_object.url)
    print("Image caption:", img.caption.text)
    img.caption = "Caption aggiornata via API"
    img.file_object = FileTypeExternal("https://m.media-amazon.com/images/I/61EHasGroeL._UF1000,1000_QL80_.jpg")
    img.update()
    print("Image aggiornata ✓")

    # File — solo lettura (file Notion non aggiornabili)
    file_blk = NFactory.find(api.headers, BLK_FILE)
    print("File name:", file_blk.name)
    print("File URL:", file_blk.file_object.url)
    print("File expiry:", file_blk.file_object.expiry_time)
    ##############
    # File expiry si riferisce alla scadenza temporanea degli URL dei file ospitati su Notion (tipo "file").
    # Ogni volta che recuperi un file Notion-hosted tramite l'API, l'oggetto include un campo expiry_time
    # (in formato ISO 8601) che indica quando l'URL scadrà — tipicamente 1 ora dopo il recupero.
    ##############

    # Embed — leggi URL
    embed = NFactory.find(api.headers, BLK_EMBED)
    print("Embed URL:", embed.url)

    # Aggiungi un'immagine esterna come figlio del toggle padre
    from notion_lib.nModels.blocks.media import Image
    new_img = Image.create("nuova immagine", FileTypeExternal("https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/Siege_of_Peking%2C_Boxer_Rebellion.jpg/250px-Siege_of_Peking%2C_Boxer_Rebellion.jpg"))
    father.append_children([new_img])
    print("Nuova immagine aggiunta come figlio ✓")


# ─────────────────────────────────────────────────────────────────────────────
# 6. BLOCKS — TABLE
# ─────────────────────────────────────────────────────────────────────────────

def example_table():
    sep("6. Blocks — Table")
    from notion_lib.nModels.blocks.base_block import NFactory
    from notion_lib.nModels.blocks.table import TableBlock, TableRowBlock
    from notion_lib.nTypes.rich_text import simple_rich_text_list

    api = NotionApiClient(key=API_KEY)
    father = NFactory.find(api.headers, BLK_TOGGLE_FATHER)

    # Leggi tabella esistente
    table = NFactory.find(api.headers, BLK_TABLE)
    print("has_column_header:", table.has_column_header)
    print("has_row_header:", table.has_row_header)
    print("Cella (1,1):", table.cell(1, 1))
    print("Cella via []:", table[1, 1])

    # Modifica una cella e aggiorna
    table[1, 1] = "valore modificato"
    table.update()
    print("Cella aggiornata ✓")

    # Aggiorna header flags
    table.has_column_header = True
    table.update()
    print("Column header abilitato ✓")

    # Crea una nuova tabella 2x2 e aggiungila come figlio
    rows = [
        TableRowBlock.create([simple_rich_text_list("A"), simple_rich_text_list("B")]),
        TableRowBlock.create([simple_rich_text_list("C"), simple_rich_text_list("D")]),
    ]
    new_table = TableBlock.create(
        table_width=2,
        has_column_header=True,
        has_row_header=False,
        cells=rows,
    )
    father.append_children([new_table])
    print("Nuova tabella 2x2 aggiunta ✓")


# ─────────────────────────────────────────────────────────────────────────────
# 7. BLOCKS — SPECIAL
# ─────────────────────────────────────────────────────────────────────────────

def example_special_blocks():
    sep("7. Blocks — Special")
    from notion_lib.nModels.blocks.base_block import NFactory
    from notion_lib.nModels.blocks.special_blocks import (
        CalloutBlock, CodeBlock, EquationBlock, BookmarkBlock,
        DividerBlock, ColumnListBlock,
    )
    from notion_lib.nModels.blocks.paragraph import ParagraphBlock
    from notion_lib.nTypes.icons import NEmoji
    from notion_lib.utils.constants import NColors, NLanguage

    api = NotionApiClient(key=API_KEY)
    father = NFactory.find(api.headers, BLK_TOGGLE_FATHER)

    # Callout — leggi icona e colore, aggiorna testo
    callout = NFactory.find(api.headers, BLK_CALLOUT)
    print("Callout icon:", IconFactory.name(callout.icon))
    print("Callout color:", callout.color)
    callout.rich_text = "Callout aggiornato"
    callout.update()
    print("Callout aggiornato ✓")

    # Code — cambia lingua e caption
    code = NFactory.find(api.headers, BLK_CODE)
    print("Code language:", code.language)
    code.language = NLanguage.PYTHON
    code.caption = "Esempio Python"
    code.update()
    print("Code aggiornato ✓")

    # Equation — modifica espressione
    eq = NFactory.find(api.headers, BLK_EQUATION)
    print("Equation:", eq.expression)
    eq.expression = "(3x)^2 + y"
    eq.update()
    print("Equation aggiornata ✓")

    # Bookmark — cambia caption
    bm = NFactory.find(api.headers, BLK_BOOKMARK)
    print("Bookmark URL:", bm.url)
    bm.caption = "Notion API Docs"
    bm.update()
    print("Bookmark aggiornato ✓")

    # Divider — solo lettura
    div = NFactory.find(api.headers, BLK_DIVIDER)
    print("Divider payload:", div.to_payload())

    # Quote — aggiorna testo, aggiungi figlio, poi rimuovilo
    quote = NFactory.find(api.headers, BLK_QUOTE)
    quote.rich_text = "Citazione modificata"
    quote.color = NColors.BLUE
    quote.update()
    quote.add_child(ParagraphBlock.create("figlio della citazione"))
    print("Quote figli:", [c.rich_text.text for c in quote.children if type(c) == ParagraphBlock])
    if quote.children:
        quote.remove_child_at(0)
    print("Quote aggiornato ✓")

    # Table of Contents — cambia colore
    toc = NFactory.find(api.headers, BLK_TOC)
    print("ToC color:", toc.color)
    toc.color = NColors.BLUE_BACKGROUND
    toc.update()
    print("ToC colore aggiornato ✓")

    # Column list — crea 3 colonne come figli del toggle padre
    ColumnListBlock.create_with_columns(3, father)
    print("ColumnList 3 colonne aggiunta ✓")

    # Aggiungi un callout figlio al toggle padre
    icon = NEmoji({"type": "emoji", "emoji": "🚀"})
    new_callout = CalloutBlock.create("nuovo callout figlio", icon, NColors.GREEN_BACKGROUND)
    father.append_children([new_callout])
    print("Nuovo callout figlio aggiunto ✓")

    # Aggiungi nuovo blocco di codice
    new_code = CodeBlock.create("print('Hello, Notion!')", NLanguage.PYTHON, "Hello World")
    father.append_children([new_code])
    print("Nuovo code block aggiunto ✓")

    # Aggiungi nuova equazione
    new_eq = EquationBlock.create("e = mc^2")
    father.append_children([new_eq])
    print("Nuova equazione aggiunta ✓")

    # Aggiungi nuovo bookmark
    new_bm = BookmarkBlock.create(url="https://developers.notion.com/reference/block", caption="Block API Reference")
    father.append_children([new_bm])
    print("Nuovo bookmark aggiunto ✓")

    # Aggiungi un divider
    father.append_children([DividerBlock.create()])
    print("Divider aggiunto ✓")


# ─────────────────────────────────────────────────────────────────────────────
# 8. BLOCKS — SYNCED, BREADCRUMB, CHILD_PAGE, CHILD_DB
# ─────────────────────────────────────────────────────────────────────────────

def example_structural_blocks():
    sep("8. Blocks — Synced / Breadcrumb / ChildPage / ChildDB")
    from notion_lib.nModels.blocks.base_block import NFactory
    from notion_lib.nModels.blocks.special_blocks import (
        BreadcrumbBlock, )

    api = NotionApiClient(key=API_KEY)
    father = NFactory.find(api.headers, BLK_TOGGLE_FATHER)

    # SyncedBlock — leggi payload (sorgente e copia)
    synced_source = NFactory.find(api.headers, BLK_SYNCED_F)
    print("SyncedBlock (sorgente) payload:", synced_source.to_payload())

    # Breadcrumb — leggi payload
    bc = NFactory.find(api.headers, BLK_BREADCRUMB)
    print("Breadcrumb payload:", bc.to_payload())

    # ChildPage — leggi titolo e aggiornalo
    child_page = NFactory.find(api.headers, BLK_CHILD_PAGE)
    print("ChildPage titolo:", child_page.title)
    child_page.title = "Child Page — aggiornata via API"
    child_page.update()
    print("ChildPage aggiornata ✓")

    # ChildDB — leggi titolo e aggiornalo
    child_db = NFactory.find(api.headers, BLK_CHILD_DB)
    print("ChildDB titolo:", child_db.title)
    child_db.title = "Child DB — aggiornato via API"
    child_db.update()
    print("ChildDB aggiornato ✓")

    # Aggiungi breadcrumb e synced (senza sorgente) come figli
    father.append_children([BreadcrumbBlock.create()])
    print("Breadcrumb aggiunto come figlio ✓")


# ─────────────────────────────────────────────────────────────────────────────
# 9. BLOCKS — LINK_TO_PAGE & LINK_PREVIEW  (read-only)
# ─────────────────────────────────────────────────────────────────────────────

def example_readonly_blocks():
    sep("9. Blocks — LinkToPage / LinkPreview (read-only)")
    from notion_lib.nModels.blocks.base_block import NFactory

    api = NotionApiClient(key=API_KEY)

    # Per trovare un link_to_page/link_preview devi avere il loro block_id.
    # Scorri i figli della pagina principale per trovarne uno.
    from notion_lib.nEndpoints.pages import get_block_children
    children = get_block_children(api.headers, PAGE_ID)
    for blk in children:
        t = blk.get("type")
        if t == "link_to_page":
            b = NFactory.find(api.headers, blk["id"])
            print("LinkToPage target_type:", b.target_type)
            print("LinkToPage target_id:", b.target_id)
            break
        elif t == "link_preview":
            b = NFactory.find(api.headers, blk["id"])
            print("LinkPreview URL:", b.url)
            break
    else:
        print("Nessun link_to_page/link_preview trovato tra i figli diretti della pagina.")
        print("(questi blocchi esistono solo se sono stati creati manualmente in Notion)")


# ─────────────────────────────────────────────────────────────────────────────
# 10. BLOCKS — MEETING NOTES  (read-only)
# ─────────────────────────────────────────────────────────────────────────────

def example_meeting_notes():
    sep("10. Blocks — Meeting Notes")
    from notion_lib.nModels.blocks.base_block import NFactory

    api = NotionApiClient(key=API_KEY)
    meeting = NFactory.find(api.headers, BLK_MEETING)

    print("Titolo:      ", meeting.title)
    print("Status:      ", meeting.status)
    print("Pronto:      ", meeting.is_ready)
    print("Cal start:   ", meeting.calendar_start)
    print("Cal end:     ", meeting.calendar_end)
    print("Rec start:   ", meeting.recording_start)
    print("Rec end:     ", meeting.recording_end)
    print("Partecipanti:", meeting.attendees)

    # Se le note sono pronte, leggi i blocchi figlio
    if meeting.is_ready:
        summary = meeting.get_summary()
        if summary:
            print("\nSummary children:")
            for c in summary.get_children():
                print("  →", c.__class__.__name__, end='\n')
                if isinstance(c, ParagraphBlock):
                    print(f" = {c.rich_text.text}")

        notes = meeting.get_notes()
        if notes:
            print("Notes children:", len(notes.get_children()))

        transcript = meeting.get_transcript()
        if transcript:
            print("Transcript children:", len(transcript.get_children()))


# ─────────────────────────────────────────────────────────────────────────────
# 11. PAGES — SimplePage
# ─────────────────────────────────────────────────────────────────────────────

def example_simple_page():
    sep("11. Pages — SimplePage")
    from notion_lib.nModels.pages import PageFactory, SimplePage
    from notion_lib.nModels.blocks.paragraph import ParagraphBlock
    from notion_lib.nTypes.icons import NEmoji

    api = NotionApiClient(key=API_KEY)

    # Leggi una pagina semplice
    page = PageFactory.find(api.headers, SIMPLE_PAGE)
    print("Tipo:", page.__class__.__name__)
    print("Titolo:", page.title)
    print("URL:", page.url)
    print("Icon:", page.icon.emoji if page.icon and hasattr(page.icon, 'emoji') else page.icon)
    print("Cover:", page.cover.type if page.cover else None)

    # Rinomina la pagina
    page.title = "Amleto — aggiornato via API"
    page.update()
    print("Titolo aggiornato ✓")

    # Aggiungi un paragrafo come figlio
    page.append_children([ParagraphBlock.create("Riga aggiunta via API")])
    print("Figlio aggiunto ✓")

    # Leggi tutti i blocchi figli della pagina
    children = page.get_children()
    print(f"Figli nella pagina: {len(children)}")
    for c in children[:3]:
        print(f"  [{c.__class__.__name__}]", getattr(c, '_rich_text', None) and c.rich_text.text or "")

    # Crea una nuova pagina figlia
    new_page = SimplePage.create(
        headers=api.headers,
        parent_id=PAGE_ID,
        title="Pagina creata via API",
        icon=NEmoji({"type": "emoji", "emoji": "📄"}),
    )
    print("Nuova pagina creata:", new_page)

    # Metti nel cestino, poi ripristina
    new_page.trash()
    print("Pagina nel cestino ✓")
    new_page.restore()
    print("Pagina ripristinata ✓")


# ─────────────────────────────────────────────────────────────────────────────
# 12. PAGES — DatabasePage
# ─────────────────────────────────────────────────────────────────────────────

def example_database_page():
    sep("12. Pages — DatabasePage")
    from notion_lib.nModels.pages import PageFactory, DatabasePage

    api = NotionApiClient(key=API_KEY)

    # Leggi una entry di un database
    page = PageFactory.find(api.headers, DB_PAGE_URL)
    print("Tipo:", page.__class__.__name__)
    print("Titolo:", page.title())

    # Stampa tutte le proprietà tipizzate
    print("\nProprietà:")
    for name, prop in page.properties.items():
        print(f"  {name!r:30} ({prop.prop_type}): {prop.value}")

    # Modifica una proprietà numerica (se esiste) e aggiorna
    for name, prop in page.properties.items():
        if prop.prop_type == "number":
            old_val = prop.value
            page.set_prop(name, (old_val or 0) + 1)
            print(f"\n{name} incrementato: {old_val} → {prop.value}")
            break

    # Modifica un checkbox (se esiste)
    for name, prop in page.properties.items():
        if prop.prop_type == "checkbox":
            page.set_prop(name, not prop.value)
            print(f"{name} invertito: {not prop.value}")
            break

    page.update()
    print("DatabasePage aggiornata ✓")

    # Crea una nuova entry nel database
    from notion_lib.nEndpoints.databases import get_db_datasources
    ds_list = get_db_datasources(api.headers, DB_URL)
    if ds_list:
        ds_id = ds_list[0]["id"]
        new_entry = DatabasePage.create(
            headers=api.headers,
            parent_db_id=ds_id,
            properties={
                "Name": {"title": [{"text": {"content": "Entry creata via API"}}]},
            },
        )
        print("Nuova entry creata:", new_entry)


# ─────────────────────────────────────────────────────────────────────────────
# 13. PAGES — PageFactory routing
# ─────────────────────────────────────────────────────────────────────────────

def example_page_factory_routing():
    sep("13. Pages — PageFactory routing")
    from notion_lib.nModels.pages import PageFactory

    api = NotionApiClient(key=API_KEY)

    # Pagina con parent page → SimplePage
    p1 = PageFactory.find(api.headers, SIMPLE_PAGE)
    print(f"Parent=page   → {p1.__class__.__name__}  (atteso: SimplePage)")

    # Pagina con parent database → DatabasePage
    p2 = PageFactory.find(api.headers, DB_PAGE_URL)
    print(f"Parent=db     → {p2.__class__.__name__}  (atteso: DatabasePage)")

    # Pagina radice (workspace) → SimplePage
    p3 = PageFactory.find(api.headers, PAGE_ID)
    print(f"Parent=page   → {p3.__class__.__name__}  (atteso: SimplePage)")


# ─────────────────────────────────────────────────────────────────────────────
# 14. DATABASES — NDatabase
# ─────────────────────────────────────────────────────────────────────────────

def example_database():
    sep("14. Databases — NDatabase")
    from notion_lib.nModels.databases import DatabaseFactory, NDatabase

    api = NotionApiClient(key=API_KEY)

    # Leggi il database
    db = DatabaseFactory.find(api.headers, DB_URL)
    print("Titolo:", db.title)
    print("Inline:", db.is_inline)
    print("Locked:", db.is_locked)

    # DataSources figli
    ds_list = db.datasources
    print(f"\nDataSources ({len(ds_list)}):")
    for ds in ds_list:
        print("  →", ds)

    # Modifica titolo e aggiorna
    db.title = "Database — aggiornato via API"
    db.update()
    print("\nTitolo aggiornato ✓")

    # Crea un nuovo DataSource figlio
    new_ds = db.create_datasource(
        title="Nuovo DS via NDatabase",
        prop_schema={"url": "Link", "number": "Punteggio"},
    )
    print("Nuovo DS creato:", new_ds)

    # Trash e restore del database
    db.trash()
    print("Database nel cestino ✓")
    db.restore()
    print("Database ripristinato ✓")

    # Crea un nuovo database da zero sotto la pagina principale
    new_db = NDatabase.create(
        headers=api.headers,
        title="DB creato via API",
        parent_id=PAGE_ID,
        prop_schema={"select": "Categoria", "date": "Scadenza"},
        is_inline=True,
    )
    print("Nuovo DB creato:", new_db)


# ─────────────────────────────────────────────────────────────────────────────
# 15. DATASOURCES — NDataSource
# ─────────────────────────────────────────────────────────────────────────────

def example_datasource():
    sep("15. DataSources — NDataSource")
    from notion_lib.nModels.datasources import DataSourceFactory
    from notion_lib.nEndpoints.databases import get_db_datasources
    from notion_lib.nTypes.ds_filters import F, S

    api = NotionApiClient(key=API_KEY)

    # Carica il DS tramite la factory
    ds_list_raw = get_db_datasources(api.headers, DS_URL)
    print(f"DS nel container: {len(ds_list_raw)}")
    for raw in ds_list_raw:
        print(f"  {raw['name']} — {raw['id']}")

    ds = DataSourceFactory.find(api.headers, ds_list_raw[0]["id"])
    print("\nNome DS:", ds.title)
    print("Parent DB:", ds.parent_db_id)

    # Schema proprietà
    print("\nSchema:")
    for col_name, col_data in ds.schema.items():
        print(f"  {col_name!r:30} type={col_data.get('type')}")

    # Templates
    print("\nTemplates:", ds.templates)
    print("Default template:", ds.default_template)

    # Tutte le entry
    all_entries = ds.all_entries()
    print(f"\nTotale entry: {len(all_entries)}")

    # Filtra per checkbox
    results = ds.filter({"filter": F.checkbox("check").equals(True)})
    print(f"Entry con check=True: {len(results)}")

    # Filtra con OR
    or_results = ds.filter({
        "filter": F.or_(
            F.rich_text("Random Text").contains("text"),
            F.rich_text("Random Text").contains("dsadsaad"),
        )
    })
    print(f"Filtro OR: {len(or_results)} risultati")

    # Filtra con AND + OR
    complex_results = ds.filter({
        "filter": F.and_(
            F.checkbox("check").equals(True),
            F.or_(
                F.rich_text("Random Text").contains("text"),
                F.rich_text("Random Text").contains("altro"),
            )
        )
    })
    print(f"Filtro AND+OR: {len(complex_results)} risultati")

    # Ordina per nome
    sorted_entries = ds.sort(S().get(("Name", False)))
    print(f"Sorted (DESC): {len(sorted_entries)} entry")
    if sorted_entries:
        title_prop = sorted_entries[0].get("properties", {}).get("Name", {})
        title_val = title_prop.get("title", [{}])[0].get("plain_text", "") if title_prop.get("title") else ""
        print("Prima entry (dopo sort):", title_val)

    # Combina filtro + sort
    combined = ds.query(
        filt={"filter": F.checkbox("check").equals(False)},
        sorties=S().get(("Name", True)),
    )
    print(f"Query combinata: {len(combined)} entry")

    # Gestione schema: aggiungi, rinomina, rimuovi colonna
    ds.add_property("select", "Categoria_test")
    print("Colonna 'Categoria_test' aggiunta ✓")
    ds.rename_property("Categoria_test", "Categoria")
    print("Colonna rinominata in 'Categoria' ✓")
    ds.remove_property("Categoria")
    print("Colonna 'Categoria' rimossa ✓")

    # Crea una nuova entry
    new_entry = ds.create_entry(
        properties={"Name": {"title": [{"text": {"content": "Nuova entry via API"}}]}},
        template_id=ds.default_template,
    )
    print("Nuova entry creata:", new_entry)

    # Aggiorna titolo del DS
    ds.update(title="DS aggiornato via API")
    print("DS aggiornato ✓")

    # Crea un DS figlio e poi spostalo
    ds.move('ad506059a56f4626b7a4c4ee5a1f4430') # altro DB
    print("DS spostato ✓")

    # Trash e restore
    ds.trash()
    print("DS nel cestino ✓")
    ds.restore()
    print("DS ripristinato ✓")


# ─────────────────────────────────────────────────────────────────────────────
# 16. USERS — UserFactory
# ─────────────────────────────────────────────────────────────────────────────

def example_users():
    sep("16. Users — UserFactory")
    from notion_lib.nModels.user import UserFactory, NPerson, NBot, NBotWorkspace
    from notion_lib.nEndpoints.users import get_all_users

    api = NotionApiClient(key=API_KEY)

    # Lista tutti gli utenti del workspace
    users = get_all_users(api.headers)
    print(f"Utenti nel workspace: {len(users)}")
    for u in users:
        print(f"  {u.get('name'):30} type={u.get('type')}")

    # Carica una persona
    person = UserFactory.create(api.headers, USER_PERSON_ID)
    print(f"\nPersona: {person}")
    print("  Nome:", person.name)
    print("  ID:", person.id)
    print("  Avatar:", person.avatar)
    print("  Tipo:", person.type)
    if isinstance(person, NPerson):
        print("  Email:", person.email)

    # Carica un bot
    bot = UserFactory.create(api.headers, USER_BOT_ID)
    print(f"\nBot: {bot}")
    print("  Nome:", bot.name)
    print("  Owner type:", bot.owner_type if isinstance(bot, NBot) else "N/A")
    if isinstance(bot, NBotWorkspace):
        print("  Workspace:", bot.workspace_name)


# ─────────────────────────────────────────────────────────────────────────────
# 17. FILTERS — F (tutti i tipi)
# ─────────────────────────────────────────────────────────────────────────────

def example_filters():
    sep("17. Filters — F")
    from notion_lib.nTypes.ds_filters import F

    examples = {
        "checkbox equals":           F.checkbox("Done").equals(True),
        "checkbox not equals":       F.checkbox("Done").does_not_equal(False),
        "number equals":             F.number("Score").equals_number(42),
        "number gt":                 F.number("Score").greater_than(10),
        "number lt_or_eq":           F.number("Score").less_than_or_equal_to(100),
        "number is_empty":           F.number("Score").is_empty(),
        "number is_not_empty":       F.number("Score").is_not_empty(),
        "date after":                F.date("Due").after("2025-01-01"),
        "date on_or_before":         F.date("Due").on_or_before("2025-12-31"),
        "date next_week":            F.date("Due").next_week(),
        "date past_month":           F.date("Due").past_month(),
        "date this_week":            F.date("Due").this_week(),
        "text contains":             F.rich_text("Desc").contains("urgent"),
        "text starts_with":          F.rich_text("Name").starts_with("A"),
        "text ends_with":            F.rich_text("Name").ends_with("Z"),
        "text equals":               F.rich_text("Name").equals_text("exact"),
        "text is_empty":             F.rich_text("Name").is_empty(),
        "select equals":             F.select("Priority").equals("High"),
        "select is_empty":           F.select("Priority").is_empty(),
        "multi_select contains":     F.multi_select("Tags").contains("urgent"),
        "status equals":             F.status("Progress").equals("Done"),
        "people is_not_empty":       F.people("Assignee").is_not_empty(),
        "relation contains":         F.relation("Project").contains("Alpha"),
        "files is_empty":            F.files("Attachments").is_empty(),
        "notion_id gt":              F.notion_id("ID").greater_than(42),
        "timestamp created after":   F.timestamp("created_time").after("2025-01-01"),
        "timestamp edited before":   F.timestamp("last_edited_time").on_or_before("2025-12-31"),
        "verification verified":     F.verification("Ver").status("verified"),
        "rollup any":                F.rollup("Tasks").any("Complete"),
        "rollup every":              F.rollup("Tasks").every("Done"),
        "rollup none":               F.rollup("Tasks").none("Blocked"),
        "AND compound":              F.and_(F.checkbox("Done").equals(True), F.select("P").equals("High")),
        "OR compound":               F.or_(F.select("S").equals("Open"), F.select("S").equals("Pending")),
        "AND+OR nested":             F.and_(F.checkbox("Done").equals(True), F.or_(F.multi_select("T").contains("A"), F.multi_select("T").contains("B"))),
    }

    for name, f in examples.items():
        print(f"  {name:<30} → {f}")

    # Verifica isolamento stato _RollupFilter
    r1 = F.rollup("A").any("foo")
    r2 = F.rollup("B").any("bar")
    assert r1["rollup"]["any"]["rich_text"]["contains"] == "foo"
    assert r2["rollup"]["any"]["rich_text"]["contains"] == "bar"
    print("\n  _RollupFilter isolation: OK ✓")


# ─────────────────────────────────────────────────────────────────────────────
# 18. SORTS — S
# ─────────────────────────────────────────────────────────────────────────────

def example_sorts():
    sep("18. Sorts — S")
    from notion_lib.nTypes.ds_filters import S

    # Sort singolo ascending
    s1 = S().get(("Name", True))
    print("Single ASC:", s1)

    # Sort singolo descending
    s2 = S().get(("Name", False))
    print("Single DESC:", s2)

    # Timestamp sort
    s3 = S().get(("created_time", False))
    print("created_time DESC:", s3)

    s4 = S().get(("last_edited_time", True))
    print("last_edited_time ASC:", s4)

    # Multi-sort
    s5 = S().get(
        ("FIRST FIELD", True),
        ("created_time", False),
        ("Score", False),
    )
    print("Multi-sort (3 criteri):", s5)
    print(f"  Numero di criteri: {len(s5['sorts'])}")


# ─────────────────────────────────────────────────────────────────────────────
# 19. SEARCH
# ─────────────────────────────────────────────────────────────────────────────

def example_search():
    sep("19. Search")
    from notion_lib.nEndpoints.searches import search_by_title

    api = NotionApiClient(key=API_KEY)

    # Cerca tutte le pagine con "API" nel titolo
    results = search_by_title(api.headers, "API", filters="page", sorts="descending")
    pages = results.response.get("results", [])
    print(f"Pagine trovate con 'API': {len(pages)}")
    for p in pages:
        props = p.get("properties", {})
        title_prop = next((v for v in props.values() if v.get("id") == "title"), None)
        name = title_prop["title"][0]["plain_text"] if title_prop and title_prop.get("title") else p.get("id", "")
        print(f"  [{p.get('object')}] {name}")
    # Cerca data_source
    ds_results = search_by_title(api.headers, "DS", filters="data_source", sorts="ascending")
    ds_list = ds_results.response.get("results", [])
    print(f"\nDataSource trovati con 'DS': {len(ds_list)}")
    for ds in ds_list[:5]:
        print(f"  {ds.get('id')}")


# ─────────────────────────────────────────────────────────────────────────────
# 20. COMMENTS
# ─────────────────────────────────────────────────────────────────────────────

def example_comments():
    sep("20. Comments")
    from notion_lib.nEndpoints.comments import create_comment, get_all_comments, get_comment

    api = NotionApiClient(key=API_KEY)

    # Crea un commento su un blocco
    comment_result = create_comment(api.headers, BLK_H2, "Commento via API — libreria funziona! ✓")
    comment_id = comment_result.response.get("id")
    print("Commento creato:", comment_id)

    # Leggi tutti i commenti del blocco
    all_comments = get_all_comments(api.headers, BLK_H2)
    comments_list = all_comments.response.get("results", [])
    print(f"Commenti su H2: {len(comments_list)}")
    for c in comments_list:
        text = c.get("rich_text", [{}])[0].get("plain_text", "")
        print(f"  [{c.get('id')[:8]}...] {text}")

    # Leggi un singolo commento per ID
    if comment_id:
        single = get_comment(api.headers, comment_id)
        text = single.response.get("rich_text", [{}])[0].get("plain_text", "")
        print(f"\nCommento singolo: {text}")


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT — commenta/decommenta le sezioni da eseguire
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":

    # example_auth()
    # example_paragraph()
    # example_headings()
    # example_list_blocks()
    # example_media()
    # example_table()
    # example_special_blocks()
    # example_structural_blocks()
    # example_readonly_blocks()
    # example_meeting_notes()
    # example_simple_page()
    example_database_page()
    # example_page_factory_routing()
    # example_database()
    # example_datasource()
    # example_users()
    # example_filters()
    # example_sorts()
    # example_search()
    example_comments()