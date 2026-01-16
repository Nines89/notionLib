from client.https import NGET, NPATCH, NPOST
from nEndpoints.mixed import find_parent_type
from nTypes.rich_text import simple_rich_text_list
from utils.constants import DbFieldType
from utils.utils import check_url_or_id

BASE = "https://api.notion.com/v1/data_sources"


def get_ds(headers, db_id):
    """
    Qui c'è il campo properties, con tutte le proprietà:
    properties: {'Link': {'id': 'Kg%5C%3A', 'name': 'Link', 'description': None, 'type': 'url', 'url': {}}}
    ed il db parent:
    database_parent: {'type': 'page_id', 'page_id': '2a7b7a8f-7294-80b3-b420-f8736c4116d7'}
    """
    db_id = check_url_or_id(db_id)
    return NGET(header=headers, url=f"{BASE}/{db_id}")


def get_ds_templates(headers, db_id):
    """
    templates: [{'id': '2c0b7a8f-7294-8028-9d51-c27dfc30b640', 'name': 'template1', 'is_default': False}]
    """
    db_id = check_url_or_id(db_id)
    return NGET(header=headers, url=f"{BASE}/{db_id}/templates")


def create_ds(headers: dict,
              title: str,
              parent_id: str,
              prop_schema: dict = None):
    # TODO: icon
    """
        prop_schema: chiave = tipo proprietà, value = nome proprietà
    """
    prop_dict = {}
    parent_id = check_url_or_id(parent_id)
    parents_type = find_parent_type(headers, parent_id)

    if parents_type != 'database':
        raise AttributeError(f"Parent must be database")
    if prop_schema:
        for prop in prop_schema.keys():
            if prop not in DbFieldType:
                raise AttributeError(f'The property {prop} cannot be a database column.\n'
                                     f'Here is the list of allowed values: '
                                     f'{[m.value for m in DbFieldType.__members__.values()]}')  # noqa
            else:
                for pr, nm in prop_schema.items():
                    prop_dict[nm] = {pr: {}}
    elements = {"parent": {
        "type": f"{parents_type}_id",
        f"{parents_type}_id": parent_id,
    }
    }
    if title: elements['title'] = simple_rich_text_list(title).to_dict()  # noqa
    if prop_dict:
        elements['properties'] = prop_dict  # noqa
    else:
        elements['properties'] = {}  # noqa
    return NPOST(header=headers, url=BASE, data=elements)


def update_ds(headers,
              ds_id: str,
              title: str = None,
              prop_schema: dict = None,
              in_trash: bool = None):
    """Change ds title, in tresh and add properties"""
    # TODO: icon
    ds_id = check_url_or_id(ds_id)
    elements = {}
    prop_dict = {}
    if title:
        elements['title'] = simple_rich_text_list(title).to_dict()
    if prop_schema:
        keys = list(prop_schema.keys())
        for prop in keys:
            if prop not in DbFieldType:
                raise AttributeError(f'The property {prop} cannot be a database column.\n'
                                     f'Here is the list of allowed values: '
                                     f'{[m.value for m in DbFieldType.__members__.values()]}')  # noqa
            else:
                for pr, nm in prop_schema.items():
                    prop_dict[nm] = {pr: {}}
        elements['properties'] = prop_dict
    if in_trash is not None:
        elements['in_trash'] = in_trash
    return NPATCH(header=headers, url=f"{BASE}/{ds_id}", data=elements)


def remove_ds_property(headers,
                       ds_id: str,
                       prop_id_or_name: str):
    """
    prop_id_or_name could be the name or an id of the property
    """
    ds_id = check_url_or_id(ds_id)
    return NPATCH(header=headers, url=f"{BASE}/{ds_id}", data={'properties': {prop_id_or_name: None}})


def rename_ds_property(headers,
                       ds_id: str,
                       old_prop_id_or_name: str,
                       new_name: str):
    """
    prop_id_or_name could be the name or an id of the property
    """
    ds_id = check_url_or_id(ds_id)
    return NPATCH(header=headers, url=f"{BASE}/{ds_id}", data={
        'properties':
            {
                old_prop_id_or_name:
                    {'name': new_name}
            }
    })


def move_ds(headers,
            ds_id_to_move,
            new_parent_id):
    parent_id = check_url_or_id(new_parent_id)
    ds_id = check_url_or_id(ds_id_to_move)
    parents_type = find_parent_type(headers, parent_id)
    if parents_type != 'database':
        raise AttributeError(f"Parent must be database")
    payload = {
        'parent': {
            "type": f"database_id",
            "database_id": parent_id
        }
    }
    return NPATCH(header=headers, url=f"{BASE}/{ds_id}", data=payload)


def filter_a_ds(headers, ds_id, filt: dict):
    ds_id = check_url_or_id(ds_id)
    all_blocks = []
    cursor = None
    while True:
        if cursor:
            filt["start_cursor"] = cursor
        resp = NPOST(
            header=headers,
            url=f"{BASE}/{ds_id}/query",
            data=filt,
        ).response
        all_blocks.extend(resp["results"])
        if not resp["has_more"]:
            break
        cursor = resp["next_cursor"]
    return all_blocks



def sort_a_ds(headers, ds_id, sorties: dict):
    ds_id = check_url_or_id(ds_id)
    all_blocks = []
    cursor = None
    while True:
        if cursor:
            sorties["start_cursor"] = cursor
        resp = NPOST(
            header=headers,
            url=f"{BASE}/{ds_id}/query",
            data=sorties,
        ).response
        all_blocks.extend(resp["results"])
        if not resp["has_more"]:
            break
        cursor = resp["next_cursor"]
    return all_blocks
    # return NPOST(header=headers, url=f"{BASE}/{ds_id}/query", data=sorties)


if __name__ == "__main__":
    from client.auth import NotionApiClient
    from databases import get_db_datasources

    api = NotionApiClient(key="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")
    pg_id = "https://www.notion.so/color-A2DCEE-textbf-API-Integration-2a7b7a8f729480b3b420f8736c4116d7"
    data_id = "https://www.notion.so/ad506059a56f4626b7a4c4ee5a1f4430?v=e589b1d587604016ba6e9b840da871b3&source=copy_link"
    #################### CREATE DS EXAMPLE ######################################
    # create_ds(api.headers, title='DS in DB Prova', parent_id=data_id, prop_schema={
    #     'number': 'Arizona', 'url': 'Link', 'status': 'On', 'title': 'FIRST FIELD'})
    #################### Move DS EXAMPLE ######################################
    # prev_parent = "https://www.notion.so/ad506059a56f4626b7a4c4ee5a1f4430?v=2c0b7a8f7294818db4a3000c749871ed&source=copy_link"
    # move_to_id = 'https://www.notion.so/2c0b7a8f72948024a529f2a82e767024?v=2c0b7a8f72948174811f000c8c4bab20&source=copy_link'
    # data_id_to_move = get_db_datasources(api.headers, prev_parent)[1]['id']
    # move_ds(api.headers, data_id_to_move, move_to_id)
    #################### Update DS EXAMPLE ######################################
    # parent_db_id = 'https://www.notion.so/2c0b7a8f72948024a529f2a82e767024?v=2c0b7a8f72948174811f000c8c4bab20&source=copy_link'
    # data_id_to_update = get_db_datasources(api.headers, parent_db_id)[1]['id']
    # update_ds(
    #     api.headers, data_id_to_update,
    #     title='Auto DS in DB 3',
    #     prop_schema={'url': 'LinkUrlato', 'rich_text': 'Random Text'}
    # )
    # remove_ds_property(api.headers, data_id_to_update, 'LinkUrlato')
    # rename_ds_property(api.headers, data_id_to_update, 'LinkUrlato', 'Link')
    #################### GET DS EXAMPLE ######################################
    # parent_db_id = 'https://www.notion.so/2c0b7a8f72948024a529f2a82e767024?v=2c0b7a8f72948174811f000c8c4bab20&source=copy_link'
    # ds_id_ = get_db_datasources(api.headers, parent_db_id)[1]['id']
    # ret = get_ds(api.headers, ds_id_)
    # print(ret)
    # ret = get_ds_templates(api.headers, ds_id_)
    # print(ret)
    #################### FILTER DS EXAMPLE ######################################
    # from nTypes.ds_filters import F
    # db_id_ = "https://www.notion.so/2c0b7a8f72948024a529f2a82e767024?v=2c0b7a8f72948174811f000c8c4bab20&source=copy_link"
    # ds_id_ = get_db_datasources(api.headers, db_id_)[1]['id']
    # simple_f = {
    #     "filter": F.checkbox("check").equals(True)
    # }
    # res_sf = filter_a_ds(api.headers, ds_id_, simple_f)
    # print(len(res_sf['results']))
    #
    # or_f = {
    #     "filter": F.or_(
    #         F.rich_text("Random Text").contains("text"),
    #         F.rich_text("Random Text").contains("dsadsaad")
    #     )
    # }
    # res_or_f = filter_a_ds(api.headers, ds_id_, or_f)
    # print(len(res_or_f['results']))
    #
    # and_or_f = {
    #     "filter": F.and_(
    #         F.checkbox("check").equals(True),
    #         F.or_(
    #             F.rich_text("Random Text").contains("dsadsaad"),
    #             F.rich_text("Random Text").contains("text")
    #         )
    #     )
    # }
    # res_and_or_f = filter_a_ds(api.headers, ds_id_, and_or_f)
    # print(len(res_and_or_f['results']))
    #################### SORT DS EXAMPLE ######################################
    from nTypes.ds_filters import S

    db_id_ = "https://www.notion.so/2c0b7a8f72948024a529f2a82e767024?v=2c0b7a8f72948174811f000c8c4bab20&source=copy_link"
    ds_id_ = get_db_datasources(api.headers, db_id_)[1]['id']
    rules = S().get(
            ("FIRST FIELD", False),
            # ("Link", True),
        )
    roles = sort_a_ds(api.headers, ds_id_, rules)
    print(roles)
    #################### FILTER DS WITH CURSOR EXAMPLE ######################################
    # db_id_ = "https://www.notion.so/2c0b7a8f72948024a529f2a82e767024?v=2c0b7a8f72948174811f000c8c4bab20&source=copy_link"
    # ds_id_ = get_db_datasources(api.headers, db_id_)[1]['id']
    # resp = filter_a_ds(api.headers, ds_id_, {})
    pass