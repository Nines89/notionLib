from notion_lib.client.https import NGET, NPATCH, NDEL
from notion_lib.utils.utils import check_url_or_id

BASE = "https://api.notion.com/v1/blocks"


def get_block(headers, block_id):
    block_id = check_url_or_id(block_id)
    return NGET(header=headers, url=f"{BASE}/{block_id}")


def get_block_children(headers, block_id):
    block_id = check_url_or_id(block_id)
    all_blocks = []
    cursor = None
    while True:
        params = {"start_cursor": cursor} if cursor else None
        resp = NGET(
            header=headers,
            url=f"{BASE}/{block_id}/children",
            params=params
        ).response
        all_blocks.extend(resp["results"])
        if not resp["has_more"]:
            break
        cursor = resp["next_cursor"]
    return all_blocks


def update_block(headers, block_id, payload):
    block_id = check_url_or_id(block_id)
    return NPATCH(header=headers, url=f"{BASE}/{block_id}", data=payload)


def delete_block(headers, block_id):
    block_id = check_url_or_id(block_id)
    return NDEL(header=headers, url=f"{BASE}/{block_id}")


def append_children(headers, block_id, children: list[dict]):
    block_id = check_url_or_id(block_id)
    return NPATCH(header=headers, url=f"{BASE}/{block_id}/children", data={"children": children})


