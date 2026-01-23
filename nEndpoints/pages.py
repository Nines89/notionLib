from client.https import NGET, NPATCH, NPOST
from utils.utils import check_url_or_id

try:
    from mixed import find_parent_type
except ModuleNotFoundError:
    from nEndpoints.mixed import find_parent_type

from utils.constants import ParentTypes

BASE = "https://api.notion.com/v1/pages"
CHILDREN = "https://api.notion.com/v1/blocks"


def get_page(headers, page_id):
    page_id = check_url_or_id(page_id)
    return NGET(header=headers, url=f"{BASE}/{page_id}")


def create_page(headers: dict,
                parent_id: str,
                properties=None,
                title: str = None,
                icon: str = None,
                cover: str = None,
                template_id: str = None
                ):
    # TODO: icon - cover
    template_type = None
    if properties is None:
        properties = {}

    # template section
    if template_id not in ['default', None]:
        template_id = check_url_or_id(template_id)
        template_type = "template_id"
    if template_id:
        template = {'type': template_id} if not template_type else {'type': template_type,
                                                                    template_type: template_id}
    else:
        template = {'type': 'none'}
    # parent section
    parent_id = check_url_or_id(parent_id)
    parents_type = find_parent_type(headers, parent_id)
    if parents_type not in ParentTypes:
        raise AttributeError(f"Parent must be one of "
                             f"{' - '.join([x.value for x in ParentTypes.__members__.values()])}")  # noqa
    if parents_type == "database":
        NPOST(header=headers, url=BASE, data={
            "parent": {
                f"{parents_type}_id": parent_id,
            },
            "icon": icon,
            "cover": cover,
            "properties": properties})
    elif parents_type == "data_source":
        NPOST(header=headers, url=BASE, data={
            "parent": {
                f"{parents_type}_id": parent_id,
            },
            "icon": icon,
            "cover": cover,
            "properties": properties,
            "template": template
        })
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
    page_id = check_url_or_id(page_id)
    all_blocks = []
    cursor = None
    while True:
        params = {"start_cursor": cursor} if cursor else None
        resp = NGET(
            header=headers,
            url=f"{CHILDREN}/{page_id}/children",
            params=params
        ).response
        all_blocks.extend(resp["results"])
        if not resp["has_more"]:
            break
        cursor = resp["next_cursor"]
    return all_blocks


def get_page_property(headers, page_id, property_id):
    page_id = check_url_or_id(page_id)
    return NGET(header=headers, url=f"{BASE}/{page_id}/properties/{property_id}")


def update_page(headers, page_id, payload):
    page_id = check_url_or_id(page_id)
    return NPATCH(header=headers, url=f"{BASE}/{page_id}", data=payload)


def trash_page(headers, page_id):
    page_id = check_url_or_id(page_id)
    return NPATCH(header=headers, url=f"{BASE}/{page_id}", data={'archived': True})


def restore_page(headers, page_id):
    page_id = check_url_or_id(page_id)
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
    pg_id = "https://www.notion.so/Amleto-1939b4f7b3cd8034be82ef3238702119"
    print(get_page(api.headers, page_id=pg_id), '\n\n')
    # print(get_page(api.headers, page_id=pg_db_id))
    ############################# GET BLOCK CHILDREN ########################################
    # objs = get_block_children(api.headers, page_id=pg_id)
    # print(len(objs))
    # for ob in objs:
    #     print(ob['type'])
    ############################# GET PAGE PROPERTIES ########################################
    # ob = get_page_property(api.headers, page_id=pg_id, property_id='title')
    # print(ob)
    # ob_db = get_page_property(api.headers, page_id=pg_db_id, property_id='%3D%60%5BD')
    # print('\n', ob_db)
    ############################# UPDATE PAGE PROPERTIES #####################################
    # from nTypes.primitives import NDate
    # new_data = {
    #   "properties": {
    #     "Date": {
    #         'date': {"start": NDate('1984-04-24T22:49:00.000+00:00').to_dict()}}
    #       }
    #     }
    # update_page(api.headers, page_id=pg_db_id, payload=new_data)
    # time.sleep(2)
    # trash_page(api.headers, page_id=pg_db_id)
    # time.sleep(2)
    # restore_page(api.headers, page_id=pg_db_id)


