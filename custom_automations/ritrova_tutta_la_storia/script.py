"""
Automazione: Ritrova tutta la storia
Generata da Notion Automation GUI.

Modifica il metodo run() con la logica desiderata.
La variabile d'ambiente NOTION_KEY viene iniettata automaticamente
dall'applicazione quando si clicca "Esegui".
"""

import os
import sys
sys.path.insert(0, '.')

from notion_lib.client.auth import NotionApiClient
from notion_lib.nModels.datasources import DataSourceFactory, NDataSource
from notion_lib.nModels.pages import PageFactory, SimplePage, DatabasePage
from notion_lib.nModels.blocks.base_block import NFactory
from notion_lib.nModels.blocks.paragraph import ParagraphBlock
from notion_lib.nModels.blocks.heading import Heading1, Heading2, Heading3
from notion_lib.nModels.blocks.list_blocks import ToDo, Toggle, BulletedListItem
from notion_lib.nModels.blocks.special_blocks import CalloutBlock, CodeBlock
from notion_lib.nModels.databases import DatabaseFactory, NDatabase
from notion_lib.nTypes.ds_filters import F, S
from notion_lib.nTypes.rich_text import simple_rich_text_list, create_rich_list
from notion_lib.nTypes.icons import NEmoji


class RitrovaTuttaLaStoria:
    """Automazione personalizzata: Ritrova tutta la storia"""
    PAGE = "https://app.notion.com/p/Timelines-2df9b4f7b3cd80da88efc8a3c2923ebb"

    def __init__(self, api_key: str):
        self.api = NotionApiClient(key=api_key)

    def run(self):
        """Logica principale dell'automazione. Modifica questo metodo."""
        print(f"Avvio: {self.__class__.__name__}")
        page = PageFactory.find(self.api.headers, self.PAGE)
        print(page.title)
        

        # ── Esempio: carica un DataSource ───────────────────────────────
        # ds_id = 'INSERISCI_ID_DATASOURCE'
        # ds = DataSourceFactory.find(self.api.headers, ds_id)
        # entries = ds.all_entries()
        # print(f'Entry trovate: {len(entries)}')

        # ── Esempio: filtra le entry ─────────────────────────────────────
        # results = ds.filter({'filter': F.checkbox('Done').equals(True)})
        # sorted_results = ds.sort(S().get(('Name', True)))

        # ── Esempio: leggi una pagina ────────────────────────────────────
        # page_id = 'INSERISCI_ID_PAGINA'
        # page = PageFactory.find(self.api.headers, page_id)
        # print(page.title)

        # ── Esempio: aggiungi un blocco a una pagina ─────────────────────
        # page = PageFactory.find(self.api.headers, 'INSERISCI_ID_PAGINA')
        # page.append_children([ParagraphBlock.create('Testo inserito')])

        # ── Esempio: leggi un database ───────────────────────────────────
        # db_id = 'INSERISCI_ID_DATABASE'
        # db = DatabaseFactory.find(self.api.headers, db_id)
        # print(db.title, db.datasources)

        print('Automazione completata.')


if __name__ == "__main__":
    key = os.environ.get("NOTION_KEY") or input("API Key Notion: ").strip()
    if not key:
        print("Errore: nessuna API key fornita.")
        sys.exit(1)
    RitrovaTuttaLaStoria(key).run()
