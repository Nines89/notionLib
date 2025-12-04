import requests
from notion_errors import *


"""
FIRST STEP:

response = requests.get(self.page, headers=self.headers)
if response:
    return response.json()
else:
    raise ConnectionError(f"Function Failed with: {response}:\n\t\t {response.json()['message']}")
"""


class NotionApiClient:
    def __init__(self, key, version: str = "2025-09-03"):
        self.key = key
        self.headers = {
            "Authorization": "Bearer " + self.key,
            "Content-Type": "application/json",
            "Notion-Version": version,
            "accept": "application/json",
        }


class NotionRequest:
    name = "Request"
    response = None

    def __init__(self, url: str, header: dict = None):
        if not header:
            raise ValueError("Header info must be provided")
        self.header = header
        self.url = url

    def response_handler(self, response: requests.Response):
        if response.ok:
            return response.json()
        try:
            data = response.json()
            code = data.get("code")
            msg = data.get("message", "")
        except Exception:
            raise NotionError(f"{self.name} -> {response.status_code}: {response.text}")

        exc = ERROR_MAP.get(code, NotionError)
        raise exc(f"{self.name} -> <[{code} {response.status_code}]>: {msg}")

    def __getitem__(self, key):
        if self.response:
            if key in self.response:
                return self.response[key]
            raise NotionError(f"The response key {key} does not exist")
        raise NotionError(f"The request response doesn't exists")

    def __repr__(self):
        out = ""
        for key, item in self.response.items():
            out += f"{key}: {item}\n"
        return out


class NGET(NotionRequest):
    def __init__(self, url: str, header: dict = None):
        super().__init__(url, header)
        self.response = self.response_handler(requests.get(self.url, headers=self.header))


class NPOST(NotionRequest):
    def __init__(self, url: str, header: dict, data: dict):
        super().__init__(url, header)
        self.response = self.response_handler(requests.post(self.url, json=data, headers=self.header))


class NPATCH(NotionRequest):
    def __init__(self, url: str, header: dict, data: dict):
        super().__init__(url, header)
        self.response = self.response_handler(requests.patch(self.url, json=data, headers=self.header))


class NDEL(NotionRequest):
    def __init__(self, url: str, header: dict):
        super().__init__(url, header)
        self.response = self.response_handler(requests.delete(self.url, headers=self.header))


if __name__ == '__main__':
    api = NotionApiClient(key="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")

    block_id = "2a7b7a8f729480b3b420f8736c4116d7"
    block_id_up = "2929b4f7b3cd80c180e8c8f0e569c5c1"

    url_get = f"https://api.notion.com/v1/blocks/{block_id}"
    url_up_del = f"https://api.notion.com/v1/blocks/{block_id_up}"

    req = NGET(url_get, api.headers)

    req_update = NPATCH(url_up_del, api.headers, {
                                                  "to_do": {
                                                    "rich_text": [{
                                                      "text": {"content": "try hard"}
                                                      }],
                                                    "checked": True
                                                  }
                                                })

    req_delete = NDEL(url_up_del, api.headers)
