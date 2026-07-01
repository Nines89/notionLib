from notion_lib.client.https import NGET
from notion_lib.utils.utils import check_url_or_id

try:
    from mixed import find_parent_type
except ModuleNotFoundError:
    from notion_lib.nEndpoints.mixed import find_parent_type

BASE = "https://api.notion.com/v1/users"


def get_all_users(headers):
    return NGET(header=headers, url=f"{BASE}")['results']


def get_user(headers, user_id):
    user_id = check_url_or_id(user_id)
    return NGET(header=headers, url=f"{BASE}/{user_id}")


def get_bot_token(headers):
    return NGET(header=headers, url=f"{BASE}/me")


