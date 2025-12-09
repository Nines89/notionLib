from enum import Enum


class ParentTypes(Enum):
    DB_ID = 'database'
    DS_ID = 'data_source'
    PAGE_ID = 'page'
    WORKSPACE = "workspace"


class BotType(Enum):
    USER = "user"
    WORKSPACE = "workspace"


class DbFieldType(Enum):
    NUMBER = "number"
    FORMULA = "formula"
    SELECT = "select"
    MULTI_SELECT = "multi_select"
    STATUS = "status"
    RELATION = "relation"
    ROLLUP = "rollup"
    UNIQUE_ID = "unique_id"
    TITLE = "title"
    RICH_TEXT = "rich_text"
    URL = "url"
    PEOPLE = "people"
    FILES = "files"
    EMAIL = "email"
    PHONE_NUMBER = "phone_number"
    DATE = "date"
    CHECKBOX = "checkbox"
    CREATED_BY = "created_by"
    CREATED_TIME = "created_time"
    LAST_EDITED_BY = "last_edited_by"
    LAST_EDITED_TIME = "last_edited_time"
    BUTTON = "button"
    LOCATION = "location"
    VERIFICATION = "verification"
    LAST_VISITED_TIME = "last_visited_time"
    PLACE = "place"

