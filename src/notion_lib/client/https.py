import requests
from functools import lru_cache

import certifi

from notion_lib.client.errors import ERROR_MAP, NotionError
from notion_lib.client.rate_limit import handle_rate_limit


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


def invalidate_cache() -> None:
    """
    Svuota la cache delle GET.

    Da chiamare dopo operazioni mutanti (update, append_children, delete, ecc.)
    per garantire che le successive GET restituiscano dati aggiornati.
    """
    _cached_get.cache_clear()


class NotionSession:
    name = "Session"
    response = None

    def __init__(self, headers: dict):
        self.headers = headers

    def request(self, method: str, url: str, json=None, params=None):
        while True:
            if method == "GET":
                r = _cached_get(
                    url,
                    tuple(sorted(self.headers.items())),
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
            return response.json() if response.text else {}

        try:
            data = response.json()
        except Exception:
            raise NotionError(f"{self.name} -> {response.status_code}: {response.text}")

        code = data.get("code", "")
        msg = data.get("message", "")
        exc = ERROR_MAP.get(code, NotionError)
        label = "".join(x.capitalize() for x in code.split("_"))
        raise exc(f"{self.name} -> [{response.status_code}] {label}: {msg}")

    def __getitem__(self, key):
        if self.response is None:
            raise NotionError("La risposta non è ancora disponibile.")
        if key not in self.response:
            raise NotionError(f"Chiave '{key}' non presente nella risposta.")
        return self.response[key]

    def __repr__(self):
        if not self.response:
            return f"<{self.name} (nessuna risposta)>"
        return "\n".join(f"{k}: {v}" for k, v in self.response.items())


class NGET(NotionSession):
    name = "GetSession"

    def __init__(self, url: str, header: dict = None, params: dict = None):
        super().__init__(header)
        self.response = self.request("GET", url=url, params=params)


class NPOST(NotionSession):
    name = "PostSession"

    def __init__(self, url: str, header: dict, data: dict, params: dict = None):
        super().__init__(header)
        # Le POST mutano dati: invalida la cache preventivamente
        invalidate_cache()
        self.response = self.request("POST", url=url, json=data, params=params)


class NPATCH(NotionSession):
    name = "PatchSession"

    def __init__(self, url: str, header: dict, data: dict):
        super().__init__(header)
        # Le PATCH mutano dati: invalida la cache
        invalidate_cache()
        self.response = self.request("PATCH", url=url, json=data)


class NDEL(NotionSession):
    name = "DelSession"

    def __init__(self, url: str, header: dict):
        super().__init__(header)
        # Le DELETE mutano dati: invalida la cache
        invalidate_cache()
        self.response = self.request("DELETE", url=url)


if __name__ == '__main__':
    from auth import NotionApiClient

    api = NotionApiClient(key="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")

    block_id = "2a7b7a8f72948113b82cef011fbc7fd1"
    block_id_up = "332b7a8f729480388444e0ce5586639a"

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
