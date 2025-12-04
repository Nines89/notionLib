import re

def parse_id(value):
    m = re.search(r"([0-9a-f]{32})", value)
    if not m:
        raise ValueError("Invalid Notion ID")
    return m.group(1)
