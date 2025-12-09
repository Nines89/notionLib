from client.https import NGET, NPATCH, NPOST
from nEndpoints.mixed import find_parent_type
from nTypes.rich_text import simple_rich_text_list
from utils.utils import check_url_or_id

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


if __name__ == "__main__":
    from client.auth import NotionApiClient
    api = NotionApiClient(key="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")
    blk_id = "https://www.notion.so/color-A2DCEE-textbf-API-Integration-2a7b7a8f729480b3b420f8736c4116d7?source=copy_link#2a7b7a8f729481f2a917e1c673fb8cf4"
    #################### CREATE COMMENT EXAMPLE ######################################
    # create_comment(api.headers, blk_id, "Secondo comment")
    #################### GET ALL COMMENTS EXAMPLE ######################################
    # cmts = get_all_comments(api.headers, blk_id)
    # print(cmts['results'])
    # print(len(cmts['results']))
    #################### GET COMMENT EXAMPLE ######################################
    cmt_id = '2c3b7a8f-7294-81ab-9365-001de10989fc'
    cmt = get_comment(api.headers, cmt_id)
    print(cmt)
