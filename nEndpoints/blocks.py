import time

from client.https import NGET, NPATCH, NDEL

BASE = "https://api.notion.com/v1/blocks"


def get_block(headers, block_id):
    return NGET(header=headers, url=f"{BASE}/{block_id}")


def get_block_children(headers, block_id):
    return NGET(header=headers, url=f"{BASE}/{block_id}/children")


def update_block(headers, block_id, payload):
    return NPATCH(header=headers, url=f"{BASE}/{block_id}", data=payload)


def delete_block(headers, block_id):
    return NDEL(header=headers, url=f"{BASE}/{block_id}")


def append_children(headers, block_id, children: list[dict]):
    return NPATCH(header=headers, url=f"{BASE}/{block_id}/children", data={"children": children})


if __name__ == "__main__":
    from client.auth import NotionApiClient

    api = NotionApiClient(key="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")

    blk_id = "2a7b7a8f729480b3b420f8736c4116d7"
    
    req = get_block(api.headers, blk_id)
    print(req)
    children_ = [
        {
            "to_do": {
                "rich_text": [{
                    "text": {"content": "try hard"}
                }],
                "checked": False
            }
        }
    ]
    req_app = append_children(api.headers, blk_id, children_)
    blk_id_up = req_app['results'][0]['id']
    time.sleep(2)
    req_up = update_block(api.headers, blk_id_up, {
            "to_do": {
                "rich_text": [{
                    "text": {"content": "try hard - modified"}
                }],
                "checked": True
            }
        })
    time.sleep(2)
    req_del = delete_block(api.headers, blk_id_up)

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
