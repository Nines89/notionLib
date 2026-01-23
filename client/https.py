import requests

from client.errors import ERROR_MAP, NotionError
from client.rate_limit import handle_rate_limit
from functools import lru_cache
import certifi


@lru_cache(maxsize=2048)
def _cached_get(url: str, headers_key: tuple, params_key: tuple):
    return requests.request(
        "GET",
        url,
        headers=dict(headers_key),
        params=dict(params_key) if params_key else None,
        timeout=10,
        verify=certifi.where()
    )


class NotionSession:
    name = 'Session'
    response = None

    def __init__(self, headers):
        self.headers = headers

    def request(self, method, url, json=None, params=None):
        while True:
            if method == "GET":
                r = _cached_get(
                    url,
                    tuple(self.headers.items()),
                    tuple(sorted((params or {}).items()))
                )
            else:
                r = requests.request(
                    method,
                    url,
                    headers=self.headers,
                    json=json,
                    params=params,
                    timeout=10,
                    verify=certifi.where()
                )
            if r.status_code == 429:
                handle_rate_limit(r)
                continue

            return self._process_response(r)

    def _process_response(self, response):
        if response.ok:
            if response.text:
                return response.json()
            return {}
        try:
            data = response.json()
        except Exception:
            raise NotionError(f"{self.name} -> {response.status_code}: {response.text}")

        code = data.get("code")
        msg = data.get("message", "")
        exc = ERROR_MAP.get(code, NotionError)

        raise exc(f"{self.name} -> <[{response.status_code}]> {''.join(x.capitalize() for x in code.split('_'))}: {msg}")

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


class NGET(NotionSession):
    name = "GetSession"

    def __init__(self, url: str, header: dict = None, params: dict = None):
        super().__init__(header)
        self.response = self.request("GET", url=url, params=params)


class NPOST(NotionSession):
    name = "PostSession"

    def __init__(self, url: str, header: dict, data: dict, params: dict = None):
        super().__init__(header)
        self.response = self.request("POST", url=url, json=data, params=params)


class NPATCH(NotionSession):
    name = "PatchSession"

    def __init__(self, url: str, header: dict, data: dict):
        super().__init__(header)
        self.response = self.request("PATCH", url=url, json=data)


class NDEL(NotionSession):
    name = "DelSession"

    def __init__(self, url: str, header: dict):
        super().__init__(header)
        self.response = self.request("DELETE", url=url)


if __name__ == '__main__':
    from auth import NotionApiClient

    api = NotionApiClient(key="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")

    block_id = "2a7b7a8f729480b3b420f8736c4116d7"
    block_id_up = "2bfb7a8f729480be906ff97723827c53"

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
