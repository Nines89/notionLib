from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from nModels.base_object import ObjInterface
from nEndpoints import users as user_endpoint


class UserError(Exception):
    pass


@dataclass
class UserData:
    response: dict


class NUser(ObjInterface):
    obj_type = "user"

    def __init__(self, header: dict, block_id: str | None = None):
        self._raw_data: Optional[dict] = None
        self._header = header
        self._block_id = block_id
        super().__init__(header, block_id)

    def _apply(self, data):
        pass

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
        data = user_endpoint.get_user(self.headers, self.obj_id).response
        self._raw_data = data.response

    @property
    def name(self):
        self._ensure_data()
        return self._raw_data.get("name")

    @property
    def id(self):
        self._ensure_data()
        return self._raw_data.get("id")

    @property
    def avatar(self):
        self._ensure_data()
        return self._raw_data.get("avatar_url")

    @property
    def type(self):
        self._ensure_data()
        return self._raw_data.get("type")

    def __repr__(self):
        return f"<User {self.name} as {self.type}>"


class NPerson(NUser):
    obj_type = "person"

    def _apply(self, data: dict):
        # implementazione vuota ma necessaria
        return

    @property
    def email(self):
        self._ensure_data()
        return self._raw_data["person"]["email"]


class NBot(NUser):
    obj_type = "bot"

    def _apply(self, data: dict):
        # implementazione vuota ma necessaria
        return

    @property
    def owner_type(self):
        self._ensure_data()
        owner = self._raw_data.get("owner")
        return owner.get("type") if isinstance(owner, dict) else None


class NBotUser(NBot):
    pass


class NBotWorkspace(NBot):
    @property
    def workspace_name(self):
        self._ensure_data()
        return self._raw_data["workspace_name"]

    @property
    def workspace_id(self):
        self._ensure_data()
        return self._raw_data["workspace_id"]

    @property
    def workspace_limits(self):
        self._ensure_data()
        return self._raw_data["workspace_limits"]["max_file_upload_size_in_bytes"]


class UserFactory:
    @staticmethod
    def create(header: dict, block_id: str) -> NUser:
        data = user_endpoint.get_user(header, block_id).response
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
            raise UserError(f"Unknown User Type: {t}")
        u._raw_data = data
        return u


if __name__ == "__main__":
    from client.auth import NotionApiClient

    api = NotionApiClient(key="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")
    blockId = "8711f079-8ae4-4748-89a7-d2daf31ff8fe"

    user = UserFactory.create(api.headers, blockId)
    print(user)
