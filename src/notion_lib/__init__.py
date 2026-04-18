"""
notion_lib — Libreria Python per l'API Notion.

Import rapidi:
    from notion_lib import NotionApiClient
    from notion_lib.nModels.pages import PageFactory
    from notion_lib.nModels.databases import DatabaseFactory
    from notion_lib.nModels.datasources import DataSourceFactory
    from notion_lib.nModels.blocks.base_block import NFactory
    from notion_lib.nTypes.ds_filters import F, S
"""
from notion_lib.client.auth import NotionApiClient
from notion_lib.nModels.pages import PageFactory, SimplePage, DatabasePage
from notion_lib.nModels.databases import DatabaseFactory, NDatabase
from notion_lib.nModels.datasources import DataSourceFactory, NDataSource
from notion_lib.nModels.blocks.base_block import NFactory
from notion_lib.nModels.user import UserFactory
from notion_lib.nTypes.ds_filters import F, S

__all__ = [
    "NotionApiClient",
    "PageFactory", "SimplePage", "DatabasePage",
    "DatabaseFactory", "NDatabase",
    "DataSourceFactory", "NDataSource",
    "NFactory",
    "UserFactory",
    "F", "S",
]