from enum import Enum


class ParentTypes(Enum):
    DB_ID = 'database'
    PAGE_ID = 'page'


class BotType(Enum):
    USER = "user"
    WORKSPACE = "workspace"
