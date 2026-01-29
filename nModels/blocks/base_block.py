from nModels.base_object import NObj
from abc import ABC, abstractmethod
from nEndpoints.blocks import *


_BLOCK_REGISTRY = {}

def register_block(block_type: str):
    def wrapper(cls):
        _BLOCK_REGISTRY[block_type] = cls
        return cls
    return wrapper


class BlockError(Exception):
    pass


class NObjBlock(NObj):
    def _apply(self, data):
        self._data = data
        self.type = data["type"]
        self.impl = BlockFactory.from_data(
            headers=self.headers,
            data=data,
            block_id=self.obj_id
        )
        self._applied = True

    def _refresh(self):
        self._data = get_block(headers=self.headers,
                               block_id=self.obj_id)
        self._apply(data=self._data)

class BlockImpl(ABC):
    type: str
    supports_children: bool = False

    def __init__(self, headers, block_id=None):
        self.headers = headers
        self.block_id = block_id
        self._data = None

    @classmethod
    @abstractmethod
    def from_data(cls, headers, data: dict, block_id: str):
        pass

    @classmethod
    @abstractmethod
    def create(cls, **kwargs):
        """create block from scratch"""
        pass

    @abstractmethod
    def to_payload(self) -> dict:
        """payload for update / append"""
        pass

    def update(self):
        from nEndpoints.blocks import update_block
        return update_block(self.headers, self.block_id, self.to_payload())

    def delete(self):
        from nEndpoints.blocks import delete_block
        return delete_block(self.headers, self.block_id)

    def get_children(self):
        if not self.supports_children:
            raise TypeError(f"{self.type} does not support children")
        from nEndpoints.blocks import get_block_children
        # TODO: appena finisci di scrivere  i blocchi torna la lista degli oggetti
        return get_block_children(self.headers, self.block_id)

    def append_children(self, children: list=None):
        """
        append children append a block to a parent block
        """
        if children is None:
            raise BlockError(f"At least one child must be specified")
        to_sent = [child.to_payload() for child in children]
        if not self.supports_children:
            return TypeError(f"{self.type} does not support children")
        from nEndpoints.blocks import append_children
        return append_children(self.headers, self.block_id, to_sent)


class UnsupportedBlock(BlockImpl):
    type = "unsupported"

    @classmethod
    def from_data(cls, headers, data, block_id):
        obj = cls(headers=headers, block_id=block_id)
        obj._data = data
        return obj

    @classmethod
    def create(cls, **kwargs):
        raise NotImplementedError("Unsupported block cannot be created")

    def to_payload(self):
        raise NotImplementedError("Unsupported block cannot be updated")


class BlockFactory:
    @staticmethod
    def from_data(headers, data, block_id):
        block_type = data["type"]
        cls = _BLOCK_REGISTRY.get(block_type, UnsupportedBlock)
        return cls.from_data(headers, data, block_id)


class NFactory:
    @staticmethod
    def find(headers, block_id):
        block_id = check_url_or_id(block_id)
        blk = NObjBlock(headers, block_id)
        try:
            _ = blk.object_type
            r = blk.impl
        except AttributeError or TypeError as e:
            raise BlockError(f"Factory cannot find a block because of {e}")
        return r
