from client.errors import ValidationError


def find_page_parent(headers: dict,
                     _id: str):
    from pages import get_page
    from databases import get_db
    try:
        return get_page(headers, _id)['object']
    except ValidationError:
        return get_db(headers, _id)['object']


if __name__ == "__main__":
    from client.auth import NotionApiClient

    api = NotionApiClient(key="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")

    page_id = "2a7b7a8f729480b3b420f8736c4116d7"
    db_id = "2a7b7a8f7294801ab914e1f063fab45a"

    parent_type = find_page_parent(api.headers, page_id)
    print(parent_type)
