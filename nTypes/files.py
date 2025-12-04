# notion_lib/nTypes/files.py

class BaseFile:
    def __init__(self, type_, data: dict):
        self.type = type_
        self.data = data

    def to_dict(self):
        return {
            "type": self.type,
            self.type: self.data
        }


class FileTypeExternal(BaseFile):
    def __init__(self, url: str):
        super().__init__("external", {"url": url})


class FileTypeFile(BaseFile):
    """Files caricati da Notion, con expiry & signed URL."""
    def __init__(self, url: str, expiry_time=None):
        data = {"url": url}
        if expiry_time:
            data["expiry_time"] = expiry_time
        super().__init__("file", data)


def n_file(data: dict) -> BaseFile:
    """
    Helper: crea la corretta istanza file partendo da un dict Notion.
    data = {"type": "file|external", ...}
    """
    t = data.get("type")
    if t == "file":
        return FileTypeFile(data.get("url"), data.get("expiry_time"))
    elif t == "external":
        return FileTypeExternal(data.get("url"))
    else:
        raise ValueError(f"Unknown file type: {data}")
