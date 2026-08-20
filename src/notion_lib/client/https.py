import os
import time
from functools import lru_cache

import certifi
import requests
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import SSLError, Timeout

from notion_lib.client.errors import ERROR_MAP, NotionError
from notion_lib.client.rate_limit import handle_rate_limit

_TRANSIENT = (SSLError, RequestsConnectionError, Timeout)
_MAX_ATTEMPTS = 5


def _verify_arg():
    """
    Resolve SSL verification.

    - NOTION_SSL_VERIFY=0|false|off  → disable verification (last resort)
    - REQUESTS_CA_BUNDLE / SSL_CERT_FILE / CURL_CA_BUNDLE → custom CA file
    - otherwise certifi CA bundle
    """
    flag = os.environ.get("NOTION_SSL_VERIFY", "1").strip().lower()
    if flag in ("0", "false", "no", "off"):
        return False
    for key in ("REQUESTS_CA_BUNDLE", "SSL_CERT_FILE", "CURL_CA_BUNDLE"):
        path = os.environ.get(key)
        if path and os.path.isfile(path):
            return path
    return certifi.where()


def _raw_request(method: str, url: str, headers: dict, json=None, params=None):
    last_exc = None
    for attempt in range(_MAX_ATTEMPTS):
        try:
            return requests.request(
                method,
                url,
                headers=headers,
                json=json,
                params=params,
                timeout=30,
                verify=_verify_arg(),
            )
        except _TRANSIENT as exc:
            last_exc = exc
            if attempt + 1 >= _MAX_ATTEMPTS:
                break
            time.sleep(0.4 * (2 ** attempt))
    raise last_exc


@lru_cache(maxsize=2048)
def _cached_get(url: str, headers_key: tuple, params_key: tuple):
    return _raw_request(
        "GET",
        url,
        headers=dict(headers_key),
        params=dict(params_key) if params_key else None,
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
                r = _raw_request(
                    method,
                    url,
                    headers=self.headers,
                    json=json,
                    params=params,
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
