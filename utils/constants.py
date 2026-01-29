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


class NColors(Enum):
    BLUE = "blue"
    BLUE_BACKGROUND = "blue_background"
    BROWN = "brown"
    BROWN_BACKGROUND = "brown_background"
    DEFAULT = "default"
    GRAY = "gray"
    GRAY_BACKGROUND = "gray_background"
    GREEN = "green"
    GREEN_BACKGROUND = "green_background"
    ORANGE = "orange"
    ORANGE_BACKGROUND = "orange_background"
    YELLOW = "yellow"
    YELLOW_BACKGROUND = "yellow_background"
    PINK = "pink"
    PINK_BACKGROUND = "pink_background"
    PURPLE = "purple"
    PURPLE_BACKGROUND = "purple_background"
    RED = "red"
    RED_BACKGROUND = "red_background"
