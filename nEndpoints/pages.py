import time

from client.https import NGET, NPATCH, NPOST
try:
    from mixed import find_page_parent
except ModuleNotFoundError:
    from nEndpoints.mixed import find_page_parent

from utils.constants import ParentTypes

BASE = "https://api.notion.com/v1/pages"
CHILDREN = "https://api.notion.com/v1/blocks"


def get_page(headers, page_id):
    return NGET(header=headers, url=f"{BASE}/{page_id}")


def create_page(headers: dict,
                parent_id: str,
                properties=None,
                title: str = None,
                icon: str = None,
                cover: str = None
                ):
    if properties is None:
        properties = {}
    parents_type = find_page_parent(headers, parent_id)
    if parents_type not in ParentTypes:
        raise AttributeError(f"Parent must be one of {' '.join(x for x in parents_type)}")
    if parents_type == "database":
        NPOST(header=headers, url=BASE, data={
            "parent": {
                f"{parents_type}_id": parent_id,
            },
            "icon": icon,
            "cover": cover,
            "properties": properties})
    else:
        NPOST(header=headers, url=BASE, data={
            "parent": {f"{parents_type}_id": parent_id},
            "icon": icon,
            "cover": cover,
            "properties": {
                "title": [
                    {
                        "type": "text",
                        "text": {"content": title}
                    }
                ]
            }
        })


def get_block_children(headers, page_id) -> list:
    return NGET(header=headers, url=f"{CHILDREN}/{page_id}/children")['results']


def get_page_property(headers, page_id, property_id):
    return NGET(header=headers, url=f"{BASE}/{page_id}/properties/{property_id}")


def update_page(headers, page_id, payload):
    return NPATCH(header=headers, url=f"{BASE}/{page_id}", data=payload)


def trash_page(headers, page_id):
    return NPATCH(header=headers, url=f"{BASE}/{page_id}", data={'archived': True})


def restore_page(headers, page_id):
    return NPATCH(header=headers, url=f"{BASE}/{page_id}", data={'archived': False})


if __name__ == "__main__":
    from client.auth import NotionApiClient
    api = NotionApiClient(key="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")
    pg_id = "2a7b7a8f729480b3b420f8736c4116d7"
    pg_db_id = "2a7b7a8f729481ffadcfe600364f3fd4"
    ################### CREATE EXAMPLE #######################################################
    # from nTypes.rich_text import simple_rich_text_list
    #
    # db_id = "2a7b7a8f7294801ab914e1f063fab45a"
    #
    # req_creat_page = create_page(api.headers, pg_id, title='PageProva')
    # prop = {
    #     "Name": {
    #         "id": "title",
    #         "type": "title",
    #         "title": simple_rich_text_list("bot db title").to_dict(),
    #     },
    #     'Text': {
    #         'rich_text': simple_rich_text_list("This is the Relation C").to_dict(),
    #     }
    # }
    # req_creat_db = create_page(api.headers, db_id, properties=prop)
    ############################# GET EXAMPLE ###############################################
    # print(get_page(api.headers, page_id=pg_id), '\n\n')
    # print(get_page(api.headers, page_id=pg_db_id))
    ############################# GET BLOCK CHILDREN ########################################
    # objs = get_block_children(api.headers, page_id=pg_id)
    # for ob in objs:
    #     print(ob['type'])
    ############################# GET PAGE PROPERTIES ########################################
    # ob = get_page_property(api.headers, page_id=pg_id, property_id='title')
    # print(ob)
    # ob_db = get_page_property(api.headers, page_id=pg_db_id, property_id='%3D%60%5BD')
    # print('\n', ob_db)
    ############################# UPDATE PAGE PROPERTIES #####################################
    from nTypes.primitives import NDate
    new_data = {
      "properties": {
        "Date": {
            'date': {"start": NDate('1984-04-24T22:49:00.000+00:00').to_dict()}}
          }
        }
    update_page(api.headers, page_id=pg_db_id, payload=new_data)
    time.sleep(2)
    trash_page(api.headers, page_id=pg_db_id)
    time.sleep(2)
    restore_page(api.headers, page_id=pg_db_id)

