import re


def check_url_or_id(url_or_id: str):
    if re.fullmatch(r"[0-9a-f-]{32,36}", url_or_id, re.IGNORECASE):
        _id = url_or_id.replace("-", "")
        if len(_id) != 32:
            raise ValueError("Token Length is Incorrect")
        return _id

    if re.fullmatch(r"[0-9a-f]{32}", url_or_id, re.IGNORECASE):
        return url_or_id

    pattern = re.compile(
        r"#([0-9a-f]{32})"                          # ID dopo #
        r"|notion\.so/[A-Za-z0-9_-]+-([0-9a-f]{32})"  # con slug
        r"|notion\.so/([0-9a-f]{32})",               # senza slug
        re.IGNORECASE
    )

    matches = pattern.findall(url_or_id)
    if not matches:
        raise ValueError("Invalid Notion URL or ID")

    _id = None
    for groups in matches:
        _id = next((g for g in groups if g), _id)

    if len(_id) != 32:
        raise ValueError("Token Length is Incorrect")
    return _id



if __name__ == "__main__":
    blk_id = "https://www.notion.so/color-A2DCEE-textbf-API-Integration-2a7b7a8f729480b3b420f8736c4116d7?source=copy_link#2a7b7a8f7294814297b9cc59924601e3"
    print(check_url_or_id(blk_id))
    pg_id = "https://www.notion.so/color-A2DCEE-textbf-API-Integration-2a7b7a8f729480b3b420f8736c4116d7"
    print(check_url_or_id(pg_id))
    data_id = "https://www.notion.so/ad506059a56f4626b7a4c4ee5a1f4430?v=e589b1d587604016ba6e9b840da871b3&source=copy_link"
    print(check_url_or_id(data_id))


