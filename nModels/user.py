from __future__ import annotations
from typing import Optional

from nModels.base_object import ObjInterface
from nEndpoints import users as user_endpoint
from utils.utils import resolve_response


class UserError(Exception):
    pass


class NUser(ObjInterface):
    obj_type = "user"

    def __init__(self, header: dict, block_id: str | None = None):
        self._raw_data: Optional[dict] = None
        self._header = header
        self._block_id = block_id
        super().__init__(header, block_id)

    def _apply(self, data):
        # Normalizza subito: _raw_data è sempre un dict grezzo
        self._raw_data = resolve_response(data)

    @property
    def headers(self):
        return self._header

    @headers.setter
    def headers(self, value):
        self._header = value

    @property
    def obj_id(self):
        return self._block_id

    @obj_id.setter
    def obj_id(self, value):
        self._block_id = value

    def _ensure_data(self):
        if self._raw_data is None:
            self._refresh()

    def _refresh(self):
        # FIX: era data.response.response — doppio unwrap errato.
        # user_endpoint.get_user ritorna un NGET; .response è già il dict JSON.
        result = user_endpoint.get_user(self.headers, self.obj_id)
        self._raw_data = resolve_response(result)

    @property
    def name(self) -> Optional[str]:
        self._ensure_data()
        return self._raw_data.get("name")

    @property
    def id(self) -> Optional[str]:
        self._ensure_data()
        return self._raw_data.get("id")

    @property
    def avatar(self) -> Optional[str]:
        self._ensure_data()
        return self._raw_data.get("avatar_url")

    @property
    def type(self) -> Optional[str]:
        self._ensure_data()
        return self._raw_data.get("type")

    def __repr__(self):
        return f"<User '{self.name}' type={self.type}>"


class NPerson(NUser):
    obj_type = "person"

    def _apply(self, data: dict):
        super()._apply(data)

    @property
    def email(self) -> Optional[str]:
        self._ensure_data()
        return self._raw_data.get("person", {}).get("email")


class NBot(NUser):
    obj_type = "bot"

    def _apply(self, data: dict):
        super()._apply(data)

    @property
    def owner_type(self) -> Optional[str]:
        self._ensure_data()
        owner = self._raw_data.get("owner")
        return owner.get("type") if isinstance(owner, dict) else None


class NBotUser(NBot):
    pass


class NBotWorkspace(NBot):
    @property
    def workspace_name(self) -> Optional[str]:
        self._ensure_data()
        return self._raw_data.get("workspace_name")

    @property
    def workspace_id(self) -> Optional[str]:
        self._ensure_data()
        return self._raw_data.get("workspace_id")

    @property
    def workspace_limits(self):
        self._ensure_data()
        limits = self._raw_data.get("workspace_limits", {})
        return limits.get("max_file_upload_size_in_bytes")


class UserFactory:
    @staticmethod
    def create(header: dict, block_id: str) -> NUser:
        result = user_endpoint.get_user(header, block_id)
        data = resolve_response(result)
        t = data.get("type")
        if t == "person":
            u = NPerson(header, block_id)
        elif t == "bot":
            owner = data.get("owner")
            owner_type = owner.get("type") if isinstance(owner, dict) else None
            if owner_type == "user":
                u = NBotUser(header, block_id)
            elif owner_type == "workspace":
                u = NBotWorkspace(header, block_id)
            else:
                u = NBot(header, block_id)
        else:
            raise UserError(f"Tipo utente sconosciuto: '{t}'")
        u._raw_data = data
        return u

if __name__ == "__main__":
    from client.auth import NotionApiClient

    api = NotionApiClient(key="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")
    blockId = "8711f079-8ae4-4748-89a7-d2daf31ff8fe"

    user = UserFactory.create(api.headers, blockId)
    print(user)
