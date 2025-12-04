from lib.notion_client import NotionApiClient
from lib.notion_object import NObj
import re

from lib.notion_types import simple_rich_text_list
from lib.constants import FieldType
from lib.utils import check_input


class NDataBase(NObj):
    """
    Header contiene sia la versione delle API che il secret token.
    Block_id contiene la stringa con l' id, serve per il patch, il delete e il get

    per recuperare il blocco: block.get_content()
    per aggiornare il blocco: block.update_content(update_data)
    """
    obj_type = "database"
    pattern = re.compile(r"notion\.so/[^/?]*-([0-9a-f]{32})")

    def __init__(self, header: dict, db_id: str = None):
        super().__init__(header=header)
        if db_id:
            self.db_id = check_input(db_id)
            # self.get_url = f"https://api.notion.com/v1/pages/{self.db_id}"
            self.update_url = f"https://api.notion.com/v1/databases/{self.db_id}"
            # self.get_property_url = f"https://api.notion.com/v1/pages/{self.db_id}/properties/"  # + f"{property_id}"
            # self.trash_url = f"https://api.notion.com/v1/pages/{self.db_id}"  # patch
            # self.get_children_url = f"https://api.notion.com/v1/blocks/{self.db_id}/children"
            # self.append_children_url = f"https://api.notion.com/v1/blocks/{self.db_id}/children"
            # self.body = None
            self._icon = None
            self._cover = None
            self.properties = {}
        else:
            self.create_url = f"https://api.notion.com/v1/databases"
            print('This object exists to create a database')

    def create_database(self,
                        title: str,
                        parent_id: str,
                        parent: str,
                        prop_schema: dict = None,
                        ):
        """
        prop_indentifier: chiave = tipo proprietà, value = nome proprietà
        """
        prop_dict = {}
        parent_id = check_input(parent_id)
        parents_type = ["workspace", "page_id"]
        if hasattr(self, "db_id"):
            raise AttributeError("A DB ID is set, create cannot be called.")
        if parent not in parents_type:
            raise AttributeError(f"Parent must be one of {' '.join(x for x in parents_type)}")
        valid_values = [m.value for m in FieldType.__members__.values()]
        if prop_schema:
            for prop in prop_schema.keys():
                if prop not in valid_values:
                    raise AttributeError(f'The property {prop} cannot be a database column.\n'
                                         f'Here is the list of allowed values: {valid_values}')
                else:
                    for pr, nm in prop_schema.items():
                        prop_dict[nm] = {pr: {}}
        self._create(self.create_url, {
            "parent": {
                "type": f"{parent}",
                f"{parent}": parent_id,
            },
            "initial_data_source": {
                'properties': prop_dict if prop_dict else {},
            },
            'title': simple_rich_text_list(title).to_dict()
        })

    def update_database(self,
                        title: str = None,
                        new_parent: tuple = None,
                        is_inline: bool = None,
                        is_locked: bool = None):
        """
        new_parent = (parent_type, parent_id)
        """
        elements = {}
        if title:
            elements['title'] = simple_rich_text_list(title).to_dict()
        if new_parent:
            new_parent_id = check_input(new_parent[1])
            parents_type = ["workspace", "page_id"]
            if new_parent[0] not in parents_type:
                raise AttributeError(f"Parent must be one of {' '.join(x for x in parents_type)}")
            elements['parent'] = {
                "type": f"{new_parent[0]}",
                f"{new_parent[0]}": new_parent_id,
            }
        if is_inline:
            elements['is_inline'] = is_inline
        if is_locked:
            elements['is_locked'] = is_locked
        self._update(api_url=self.update_url, data=elements)


if __name__ == "__main__":
    parent_id_ = "https://www.notion.so/color-A2DCEE-textbf-API-Integration-2a7b7a8f729480b3b420f8736c4116d7"  # "https://www.notion.so/color-A2DCEE-textbf-API-Integration-28f9b4f7b3cd80588296e08e56e45b75"
    db_id = "b44a4a618f294f8c91e21e2bea6e97e5"
    api_ = NotionApiClient(key="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")
    ################## CREATE DB ##################################################
    # db = NDataBase(api_.headers)
    # props = {
    #     'select': 'Selezioni'
    # }
    # db.create_database(title="AutoCreated2",
    #                    parent_id=id_,
    #                    parent='page_id',
    #                    prop_schema=props)
    ###############################################################################
    ################## UPDATE DB ##################################################
    db = NDataBase(api_.headers, db_id)
    to_move_page = "https://www.notion.so/MovedDB-2beb7a8f72948045ae64e4f68dce154c"
    # move to an other page
    # db.update_database(title='AutoCreated3',
    #                    new_parent=('page_id', to_move_page))
    db.update_database(title='AutoCreated3',
                       is_inline=True,
                       is_locked=True
                       )

