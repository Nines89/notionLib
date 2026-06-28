"""
Automazione: Ritrova tutta la storia
Generata da Notion Automation GUI.

Modifica il metodo run() con la logica desiderata.
La variabile d'ambiente NOTION_KEY viene iniettata automaticamente
dall'applicazione quando si clicca "Esegui".
"""

import os
import sys
from collections import defaultdict

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
    ROOT_PAGE = "https://app.notion.com/p/Timelines-2df9b4f7b3cd80da88efc8a3c2923ebb"

    def __init__(self, api_key: str):
        self.api = NotionApiClient(key=api_key)

    def run(self):
        """Logica principale dell'automazione. Modifica questo metodo."""
        print(f"Avvio: {self.__class__.__name__}")
        page = PageFactory.find(self.api.headers, self.ROOT_PAGE)
        children = page.get_children()
        for child in children:
            if child.type != "callout":
                continue
            for ch in child.get_children():
                if ch.type != "child_database":
                    continue
                db = DatabaseFactory.find(self.api.headers, ch.block_id)
                ds = db.datasources[0]
                era = {
                    "title": ds.title.strip(),
                    "sections": []
                }
                print("Processing:", era["title"])
                for pg in ds.sort(S().get(("Anno", True))):
                    page_obj = PageFactory.find(self.api.headers, pg["url"])
                    for blk in page_obj.get_children():
                        if not hasattr(blk, "rich_text"):
                            continue
                        try:
                            print(blk.rich_text.text)
                        except Exception:
                            continue
        print('Automazione completata.')


if __name__ == "__main__":
    key = os.environ.get("NOTION_KEY") or "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"
    if not key:
        print("Errore: nessuna API key fornita.")
        sys.exit(1)
    RitrovaTuttaLaStoria(key).run()
