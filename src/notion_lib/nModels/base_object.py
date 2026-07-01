from abc import ABC, abstractmethod


class ObjInterface(ABC):
    def __init__(self, headers: dict, obj_id):
        self.headers = headers
        self.obj_id = obj_id
        self._data = None
        self._applied = False

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
        if not hasattr(self, "impl"):
            self._refresh()

    def append_children(self, children: list):
        pass

    def get_children(self):
        pass

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
        from notion_lib.nTypes.primitives import NDate
        return {
            'last_edited_time': NDate(self._data['last_edited_time']),
            'create_user': UserFactory.create(self.headers, self._data['last_edited_by']['id'])
        }

    @property
    def last_edit_info(self):
        self._ensure_data()
        from user import UserFactory
        from notion_lib.nTypes.primitives import NDate
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