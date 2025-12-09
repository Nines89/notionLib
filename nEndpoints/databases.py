import time

from client.https import NGET, NPATCH, NPOST
from nEndpoints.mixed import find_parent_type
from nTypes.rich_text import simple_rich_text_list
from utils.constants import ParentTypes, DbFieldType
from utils.utils import check_url_or_id

BASE = "https://api.notion.com/v1/databases"


def get_db(headers, db_id):
    db_id = check_url_or_id(db_id)
    return NGET(header=headers, url=f"{BASE}/{db_id}")


def get_db_datasources(headers, db_id):
    return get_db(headers, db_id)['data_sources']


def create_db(headers: dict,
              title: str,
              parent_id: str,
              prop_schema: dict = None,
              is_inline: bool = True):
    # TODO: icon - cover
    """
        prop_schema: chiave = tipo proprietà, value = nome proprietà
    """
    prop_dict = {}
    parent_id = check_url_or_id(parent_id)
    parents_type = find_parent_type(headers, parent_id)
    if parents_type not in ParentTypes or parents_type == 'database':
        raise AttributeError(f"Parent must be one of "
                             f"{' - '.join([x.value for x in ParentTypes.__members__.values() if x.value != 'database'])}")  # noqa
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
    }}
    if title: elements['title'] = simple_rich_text_list(title).to_dict()  # noqa
    if prop_dict: elements['initial_data_source'] = {'properties': prop_dict} # noqa
    else: elements['initial_data_source'] = {} # noqa
    if is_inline: elements['is_inline'] = is_inline # noqa
    return NPOST(header=headers, url=BASE, data=elements)


def update_db(headers,
              db_id: str,
              title: str = None,
              is_inline: bool = None,
              is_locked: bool = None,
              in_trash: bool = None):
    # TODO: icon - cover
    db_id = check_url_or_id(db_id)
    elements = {}
    if title:
        elements['title'] = simple_rich_text_list(title).to_dict()
    if is_inline is not None:
        elements['is_inline'] = is_inline
    if is_locked is not None:
        elements['is_locked'] = is_locked
    if in_trash is not None:
        elements['in_trash'] = in_trash
    return NPATCH(header=headers, url=f"{BASE}/{db_id}", data=elements)


def move_db(headers, db_id_to_move, new_parent_id):
    parent_id = check_url_or_id(new_parent_id)
    db_id = check_url_or_id(db_id_to_move)
    parents_type = find_parent_type(headers, parent_id)
    if parents_type not in ParentTypes or parents_type == 'database':
        raise AttributeError(f"Parent must be one of "
                             f"{' - '.join([x.value for x in ParentTypes.__members__.values() if x.value != 'database'])}")  # noqa
    payload = {
        'parent': {
            "type": f"{parents_type}_id" if parents_type != 'workspace' else parents_type,
        }
    }
    payload['parent'][f"{parents_type}_id" if parents_type != 'workaspace' else parents_type]\
        = parent_id if parents_type != 'workaspace' else True
    return NPATCH(header=headers, url=f"{BASE}/{db_id}", data=payload)


if __name__ == "__main__":
    from client.auth import NotionApiClient

    api = NotionApiClient(key="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")
    pg_id = "https://www.notion.so/color-A2DCEE-textbf-API-Integration-2a7b7a8f729480b3b420f8736c4116d7"
    data_id = "https://www.notion.so/ad506059a56f4626b7a4c4ee5a1f4430?v=e589b1d587604016ba6e9b840da871b3&source=copy_link"
    #################### CREATE DB EXAMPLE ######################################
    # create_db(api.headers, title='DB di prova 2', parent_id=pg_id, prop_schema={
    #     'select': 'Selezione'})
    #################### Move DB EXAMPLE ######################################
    # move_to_id = "https://www.notion.so/MovedDB-2beb7a8f72948045ae64e4f68dce154c"
    # data_id_to_move = \
    #     "https://www.notion.so/52f90e2979fc4bf09f72b852fe7be569?v=1429cbc075874ff7bb0aa44624ee76ce&source=copy_link"
    # move_db(api.headers, data_id_to_move, move_to_id)
    #################### Update DB EXAMPLE ######################################
    # data_id_to_up = \
    #     "https://www.notion.so/52f90e2979fc4bf09f72b852fe7be569?v=1429cbc075874ff7bb0aa44624ee76ce&source=copy_link"
    # update_db(api.headers, data_id_to_up, title="DB TITLE UPDATED", is_locked=True, is_inline=False)
    # time.sleep(2)
    # update_db(api.headers, data_id_to_up, in_trash=True)
    # time.sleep(2)
    # update_db(api.headers, data_id_to_up, in_trash=False)
    ################### DataSourceList ##############################################à
    container = 'https://www.notion.so/ad506059a56f4626b7a4c4ee5a1f4430?v=2c0b7a8f72948138abfb000c106f95fd&source=copy_link'
    a = get_db_datasources(api.headers, container)
    for el in a:
        print(el['name'],' -> ',el['id'])
    pass
