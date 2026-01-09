import time

from client.https import NGET, NPATCH, NDEL
from utils.utils import check_url_or_id

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


if __name__ == "__main__":
    from client.auth import NotionApiClient

    api = NotionApiClient(key="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")
    blk_id = "2a7b7a8f729480b3b420f8736c4116d7"

    # Gle esempi get ed update sono da vedere assieme
    ################### GET EXAMPLE #######################################################
    # req = get_block(api.headers, blk_id)
    # print(req)
    # children_ = [
    #     {
    #         "to_do": {
    #             "rich_text": [{
    #                 "text": {"content": "try hard"}
    #             }],
    #             "checked": False
    #         }
    #     }
    # ]
    # req_app = append_children(api.headers, blk_id, children_)
    # blk_id_up = req_app['results'][0]['id']
    # time.sleep(2)
    ################### UPDATE EXAMPLE #######################################################
    # req_up = update_block(api.headers, blk_id_up, {
    #         "to_do": {
    #             "rich_text": [{
    #                 "text": {"content": "try hard - modified"}
    #             }],
    #             "checked": True
    #         }
    #     })
    # time.sleep(2)
    # req_del = delete_block(api.headers, blk_id_up)
    ################### GET CHILDREN EXAMPLE #######################################################
    blk_with_children = 'https://www.notion.so/color-A2DCEE-textbf-API-Integration-2a7b7a8f729480b3b420f8736c4116d7?source=copy_link#2a7b7a8f729481c2997effc3c4da56ce'
    req_ch = get_block_children(api.headers, block_id=blk_with_children)
    for block in req_ch:
        print(block['bulleted_list_item']['rich_text'][0]['plain_text'])


    # req = NGET(url_get, api.headers)
    #
    # req_update = NPATCH(url_up_del, api.headers, {
    #     "to_do": {
    #         "rich_text": [{
    #             "text": {"content": "try hard"}
    #         }],
    #         "checked": True
    #     }
    # })
    #
    # req_delete = NDEL(url_up_del, api.headers)
