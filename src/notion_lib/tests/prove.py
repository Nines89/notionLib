from src.notion_lib.client.auth import NotionApiClient
from src.notion_lib.nEndpoints.searches import search_by_title

api = NotionApiClient(key="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")

els = search_by_title(api.headers)['results']

for el in els:
    if el.get("object") == "data_source":
        print(type(el.get("name")), repr(el.get("name")))

