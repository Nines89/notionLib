import time
from abc import ABC, abstractmethod

from nEndpoints.datasources import get_ds


class ObjInterface(ABC):
    def __init__(self, headers: dict, obj_id):
        self.headers = headers
        self.obj_id = obj_id
        self._data = None

    @abstractmethod
    def _apply(self, data):
        """Save retrieved data to self._data .
        Move the results in all special attributes"""
        pass

    @abstractmethod
    def _refresh(self):
        """call again the get of the block"""
        pass


class NObj(ObjInterface):
    def _apply(self, data):
        pass

    def _refresh(self):
        pass

    def _ensure_data(self):
        if not self._data:
            self._refresh()

    @property
    def parent(self):
        self._ensure_data()
        t = self._data['parent']['type']
        return t, self._data['parent'][t]

    @property
    def object_type(self):
        self._ensure_data()
        return self._data['object']

    @property
    def id_(self):
        self._ensure_data()
        return self._data['id']

    @property
    def has_children(self):
        if self.object_type not in ['page', 'database', 'data_source']:
            self._ensure_data()
            return self._data['has_children']
        return f'{self.object_type} has not children flag'

    @property
    def is_archived(self):
        if self.object_type != 'database':
            self._ensure_data()
            return self._data['archived']
        return 'Database has not archived flag'

    @property
    def in_trash(self):
        self._ensure_data()
        return self._data['in_trash']

    @property
    def create_info(self):
        self._ensure_data()
        from user import UserFactory
        from nTypes.primitives import NDate
        return {
            'last_edited_time': NDate(self._data['last_edited_time']),
            'create_user': UserFactory.create(self.headers, self._data['last_edited_by']['id'])
        }

    @property
    def last_edit_info(self):
        self._ensure_data()
        from user import UserFactory
        from nTypes.primitives import NDate
        return {
            'last_edited_time': NDate(self._data['last_edited_time']),
            'create_user': UserFactory.create(self.headers, self._data['last_edited_by']['id'])
        }

    def __repr__(self):
        self._ensure_data()
        return f"\n-------- {self.__class__.__name__} properties -------------\n{self._data!r}---------------------\n"

    def __getitem__(self, item):
        self._ensure_data()
        return self._data[item]


class NObjPage(NObj):
    def _apply(self, data):
        pass

    def _refresh(self):
        self._data = get_page(headers=self.headers,
                              page_id=self.obj_id)

class NObjBlock(NObj):
    def _apply(self, data):
        pass

    def _refresh(self):
        self._data = get_block(headers=self.headers,
                               block_id=self.obj_id)


class NObjDB(NObj):
    def _apply(self, data):
        pass

    def _refresh(self):
        self._data = get_db(headers=self.headers,
                            db_id=self.obj_id)

    @property
    def create_info(self):
        self._ensure_data()
        from nTypes.primitives import NDate
        return {
            'create_time': NDate(self._data['created_time']),
        }

    @property
    def last_edit_info(self):
        self._ensure_data()
        from nTypes.primitives import NDate
        return {
            'last_edited_time': NDate(self._data['last_edited_time']),
        }


class NObjDS(NObj):
    def _apply(self, data):
        pass

    def _refresh(self):
        self._data = get_ds(headers=self.headers,
                            db_id=self.obj_id)


if __name__ == '__main__':
    start = time.time()
    from client.auth import NotionApiClient
    from nEndpoints.pages import get_page
    from nEndpoints.blocks import get_block
    from nEndpoints.databases import get_db

    api = NotionApiClient(key="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")
    pg_id = "2a7b7a8f729480b3b420f8736c4116d7"
    blk_id = "2a7b7a8f7294814297b9cc59924601e3"
    db_id = "2a7b7a8f7294801ab914e1f063fab45a"
    ds_id = "2c0b7a8f-7294-8139-9781-000bd44a418c"

    obj_ = NObjPage(headers=api.headers, obj_id=pg_id)

    print('parent: ', obj_.parent)
    print('type: ', obj_.object_type)
    print('id: ', obj_.id_)
    print('has children: ', obj_.has_children)
    print('is_archived: ', obj_.is_archived)
    print('in_trash: ', obj_.in_trash)
    print('last_edited_info: ', obj_.last_edit_info)
    print('create_info: ', obj_.create_info, '\n\n')

    obj_ = NObjBlock(headers=api.headers, obj_id=blk_id)

    print('parent: ', obj_.parent)
    print('type: ', obj_.object_type)
    print('id: ', obj_.id_)
    print('has children: ', obj_.has_children)
    print('is_archived: ', obj_.is_archived)
    print('in_trash: ', obj_.in_trash)
    print('last_edited_info: ', obj_.last_edit_info)
    print('create_info: ', obj_.create_info, '\n\n')

    obj_ = NObjDB(headers=api.headers, obj_id=db_id)

    print('parent: ', obj_.parent)
    print('type: ', obj_.object_type)
    print('id: ', obj_.id_)
    print('has children: ', obj_.has_children)
    print('is_archived: ', obj_.is_archived)
    print('in_trash: ', obj_.in_trash)
    print('last_edited_info: ', obj_.last_edit_info)
    print('create_info: ', obj_.create_info, '\n\n')

    obj_ = NObjDS(headers=api.headers, obj_id=ds_id)

    print('parent: ', obj_.parent)
    print('type: ', obj_.object_type)
    print('id: ', obj_.id_)
    print('has children: ', obj_.has_children)
    print('is_archived: ', obj_.is_archived)
    print('in_trash: ', obj_.in_trash)
    print('last_edited_info: ', obj_.last_edit_info)
    print('create_info: ', obj_.create_info, '\n\n')


    print("Total time: ", time.time() - start)


