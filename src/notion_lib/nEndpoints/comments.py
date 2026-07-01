from notion_lib.client.https import NGET, NPOST
from notion_lib.nEndpoints.mixed import find_parent_type
from notion_lib.nTypes.rich_text import simple_rich_text_list
from notion_lib.utils.utils import check_url_or_id

BASE = "https://api.notion.com/v1/comments"


def get_all_comments(headers, obj_id):
    obj_id = check_url_or_id(obj_id)
    obj_type = find_parent_type(headers, obj_id)
    if obj_type not in ['page', 'block']:
        raise AttributeError(f"Parent must be one of page - block")
    return NGET(header=headers, url=f"{BASE}?{obj_type}_id={obj_id}")


def get_comment(headers, comment_id):
    obj_id = check_url_or_id(comment_id)
    return NGET(header=headers, url=f"{BASE}/{obj_id}")


def create_comment(headers,
                   parent_id: str,
                   comment: str):
    parent_id = check_url_or_id(parent_id)
    parent_type = find_parent_type(headers, parent_id)
    if parent_type not in ['page', 'block']:
        raise AttributeError(f"Parent must be one of page - block")
    payload = {
        "parent":{
            f"{parent_type}_id": parent_id
        },
        "rich_text": simple_rich_text_list(comment).to_dict(),
        "display_name":{
            "type": "integration"
        }
    }
    return NPOST(header=headers, url=f"{BASE}", data=payload)

