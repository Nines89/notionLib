from client.https import NGET, NPATCH, NPOST
from nEndpoints.mixed import find_parent_type
from nTypes.rich_text import simple_rich_text_list
from utils.utils import check_url_or_id

BASE = "https://api.notion.com/v1/search"


def search_by_title(headers,
                    query: str,
                    filters: str = None,
                    sorts: str = None):
    payload = {
        'query': query
    }
    if filters:
        if filters not in ['page', 'data_source']:
            raise ValueError('Possible value values are "page" or "data_source"')
        payload['filter'] = {
            "value": filters,
            "property": "object"
        }
    if sorts:
        if sorts not in ['ascending', 'descending']:
            raise ValueError('Possible value values are "ascending" or "descending", '
                             'the only supported timestamp value is "last_edited_time"')
        payload['sort'] = {
            "direction": sorts,
            "timestamp": "last_edited_time"
        }

    return NPOST(header=headers, url=f"{BASE}", data=payload)


if __name__ == "__main__":
    from client.auth import NotionApiClient
    api = NotionApiClient(key="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")
    query_ = "Auto"
    s = search_by_title(api.headers, query_, filters='page', sorts='ascending')
    for ss in s['results']:
        print(ss['object'])

    s = search_by_title(api.headers, query_, filters='data_source', sorts='ascending')
    for ss in s['results']:
        print(ss['object'])

