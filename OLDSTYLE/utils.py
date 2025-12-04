import re


def check_input(url_or_id: str):
    if re.fullmatch(r"[0-9a-f]{32}", url_or_id):
        return url_or_id
    pattern = re.compile(
        r"(?:notion\.so/[A-Za-z0-9_-]+-([0-9a-f]{32}))"   # con slug
        r"|"
        r"(?:notion\.so/([0-9a-f]{32}))"                 # senza slug
    )
    match = pattern.search(url_or_id)
    if not match:
        raise ValueError("Invalid Notion URL or ID")
    _id = match.group(1) or match.group(2)
    if len(_id) != 32:
        raise ValueError("Token Length is Incorrect")
    return _id
