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
from client.auth import NotionApiClient
from nModels.pages import PageFactory, SimplePage, DatabasePage
from nModels.databases import DatabaseFactory, NDatabase
from nModels.datasources import DataSourceFactory, NDataSource
from nModels.blocks.base_block import NFactory
from nModels.user import UserFactory
from nTypes.ds_filters import F, S

__all__ = [
    "NotionApiClient",
    "PageFactory", "SimplePage", "DatabasePage",
    "DatabaseFactory", "NDatabase",
    "DataSourceFactory", "NDataSource",
    "NFactory",
    "UserFactory",
    "F", "S",
]