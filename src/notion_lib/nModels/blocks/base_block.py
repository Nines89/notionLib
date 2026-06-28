from abc import ABC, abstractmethod

from notion_lib.nModels.base_object import NObj
from notion_lib.nEndpoints.blocks import (
    get_block,
    get_block_children,
    update_block,
    delete_block,
    append_children,
    check_url_or_id,
)

_BLOCK_REGISTRY: dict[str, type] = {}


def register_block(block_type: str):
    def wrapper(cls):
        _BLOCK_REGISTRY[block_type] = cls
        return cls
    return wrapper


def _ensure_registry_populated():
    global _REGISTRY_POPULATED
    if _REGISTRY_POPULATED:
        return
    import notion_lib.nModels.blocks.list_blocks    # noqa: F401
    import notion_lib.nModels.blocks.meeting_notes  # noqa: F401
    import notion_lib.nModels.blocks.special_blocks # noqa: F401
    import notion_lib.nModels.blocks.heading        # noqa: F401
    import notion_lib.nModels.blocks.media          # noqa: F401
    import notion_lib.nModels.blocks.table          # noqa: F401
    _REGISTRY_POPULATED = True


class BlockError(Exception):
    pass


class NObjBlock(NObj):
    def _apply(self, data):
        raw = data.response if hasattr(data, "response") else data
        self._data = raw
        self.type = raw["type"]
        self.impl = BlockFactory.from_data(
            headers=self.headers,
            data=raw,
            block_id=self.obj_id
        )
        self._applied = True

    def _refresh(self):
        self._data = get_block(headers=self.headers, block_id=self.obj_id)
        self._apply(data=self._data)


class BlockImpl(ABC):
    type: str
    block_type: str = ""
    supports_children: bool = False
    updatable: bool = True

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
        pass

    @abstractmethod
    def to_payload(self) -> dict:
        pass

    def update(self):
        if not self.updatable:
            raise NotImplementedError(f"Il blocco '{self.type}' non supporta update.")
        return update_block(self.headers, self.block_id, self.to_payload())

    def delete(self):
        return delete_block(self.headers, self.block_id)

    def get_children(self) -> list:
        if not self.supports_children:
            raise TypeError(f"'{self.type}' non supporta children.")
        return [
            NFactory.find(self.headers, blk['id'])
            for blk in get_block_children(self.headers, self.block_id)
        ]

    def append_children(self, children: list = None) -> None:
        if not children:
            raise BlockError("Almeno un figlio deve essere specificato.")
        if not self.supports_children:
            raise TypeError(f"'{self.type}' non supporta children.")

        # FIX: era `child.__class__ not in ["ChildDatabaseBlock", ...]`
        # confronto classe/stringa sempre True → filtro inoperante.
        # Ora import locale per evitare circolarità + isinstance corretto.
        from notion_lib.nModels.blocks.special_blocks import ChildDatabaseBlock, ChildPageBlock
        to_send = [
            child.to_payload()
            for child in children
            if not isinstance(child, (ChildDatabaseBlock, ChildPageBlock))
        ]
        return append_children(self.headers, self.block_id, to_send)


class UnsupportedBlock(BlockImpl):
    type = "unsupported"
    supports_children = True

    @classmethod
    def from_data(cls, headers, data, block_id):
        obj = cls(headers=headers, block_id=block_id)
        obj._data = data
        return obj

    @classmethod
    def create(cls, **kwargs):
        raise NotImplementedError("UnsupportedBlock non può essere creato.")

    def to_payload(self):
        raise NotImplementedError("UnsupportedBlock non può essere aggiornato.")


class BlockFactory:
    @staticmethod
    def from_data(headers, data, block_id):
        block_type = data["type"]
        cls = _BLOCK_REGISTRY.get(block_type, UnsupportedBlock)
        return cls.from_data(headers, data, block_id)


class NFactory:
    @staticmethod
    def find(headers, block_id):
        _ensure_registry_populated()
        block_id = check_url_or_id(block_id)
        blk = NObjBlock(headers, block_id)
        try:
            _ = blk.object_type
            return blk.impl
        except (AttributeError, TypeError) as e:
            raise BlockError(f"NFactory non riesce a trovare il blocco: {e}")