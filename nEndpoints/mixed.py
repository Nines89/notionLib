from client.errors import ValidationError, ObjectNotFound


def find_parent_type(headers: dict,
                     _id: str):
    # TODO: ADD WORKSPACE?
    from pages import get_page
    from databases import get_db
    from blocks import get_block
    from comments import get_comment
    from datasources import get_ds
    try:
        return get_page(headers, _id)['object']
    except ValidationError:
        try:
            return get_db(headers, _id)['object']
        except ObjectNotFound:
            try:
                return get_block(headers, _id)['object']
            except ObjectNotFound:
                raise ValueError("MA CHE CAZZO DI TIPO SEI?")
    except ObjectNotFound:
        try:
            return get_comment(headers, _id)['object']
        except ObjectNotFound as e:
            try:
                return get_ds(headers, _id)['object']
            except ObjectNotFound as e:
                raise ObjectNotFound(e)


def is_there_more():
    # TODO: implement
    pass


if __name__ == "__main__":
    from client.auth import NotionApiClient

    api = NotionApiClient(key="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")

    page_id = "2a7b7a8f729480b3b420f8736c4116d7"
    db_id = "2a7b7a8f7294801ab914e1f063fab45a"
    blk_id = "2a7b7a8f729481c2997effc3c4da56ce"
    page_from_ws_id = "28bb7a8f729480bca147c206032d9273"

    parent_type = find_parent_type(api.headers, blk_id)
    print(parent_type)
