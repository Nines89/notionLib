from notion_lib.client.https import NGET, NPATCH, NPOST
from notion_lib.utils.utils import check_url_or_id

try:
    from mixed import find_parent_type
except ModuleNotFoundError:
    from notion_lib.nEndpoints.mixed import find_parent_type

from notion_lib.utils.constants import ParentTypes

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
                template_id: str = None):
    # TODO: icon - cover (oggetti tipizzati)
    template_type = None
    if properties is None:
        properties = {}

    # template section
    if template_id not in ['default', None]:
        template_id = check_url_or_id(template_id)
        template_type = "template_id"
    if template_id:
        template = {'type': template_id} if not template_type else {
            'type': template_type,
            template_type: template_id
        }
    else:
        template = {'type': 'none'}

    # parent section
    parent_id = check_url_or_id(parent_id)
    parents_type = find_parent_type(headers, parent_id)
    if parents_type not in ParentTypes:
        raise AttributeError(
            f"Parent deve essere uno tra: "
            f"{' - '.join([x.value for x in ParentTypes.__members__.values()])}"
        )

    # FIX: tutti i branch ora restituiscono il risultato di NPOST
    if parents_type == "database":
        return NPOST(header=headers, url=BASE, data={
            "parent": {f"{parents_type}_id": parent_id},
            "icon": icon,
            "cover": cover,
            "properties": properties,
        })
    elif parents_type == "data_source":
        return NPOST(header=headers, url=BASE, data={
            "parent": {f"{parents_type}_id": parent_id},
            "icon": icon,
            "cover": cover,
            "properties": properties,
            "template": template,
        })
    else:
        return NPOST(header=headers, url=BASE, data={
            "parent": {f"{parents_type}_id": parent_id},
            "icon": icon,
            "cover": cover,
            "properties": {
                "title": [{"type": "text", "text": {"content": title or ""}}]
            },
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



