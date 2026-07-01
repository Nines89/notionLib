from notion_lib.client.https import NGET, NPATCH, NPOST
from notion_lib.nEndpoints.mixed import find_parent_type
from notion_lib.nTypes.rich_text import simple_rich_text_list
from notion_lib.utils.constants import ParentTypes, DbFieldType
from notion_lib.utils.utils import check_url_or_id

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
    payload['parent'][f"{parents_type}_id" if parents_type != 'workspace' else parents_type]\
        = parent_id if parents_type != 'workspace' else True
    return NPATCH(header=headers, url=f"{BASE}/{db_id}", data=payload)
