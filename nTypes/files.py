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
        self.url = url



class FileTypeUploaded(BaseFile):
    def __init__(self, _id: str):
        super().__init__("file_upload", {"id": _id})
        self.id = _id

class FileTypeFile(BaseFile):
    """Files caricati da Notion, con expiry & signed URL."""
    def __init__(self, url: str, expiry_time=None):
        data = {"url": url}
        if expiry_time:
            data["expiry_time"] = expiry_time
        super().__init__("file", data)
        self.url = url
        self.expiry_time = expiry_time if expiry_time else None

def n_file(data: dict) -> BaseFile:
    """
    Helper: crea la corretta istanza file partendo da un dict Notion.
    Data = {"type": "file|external", ...}
    """
    if data:
        t = data.get("type")
        if t == "file":
            return FileTypeFile(data['file'].get("url"), data['file'].get("expiry_time"))
        elif t == "external":
            return FileTypeExternal(data['external'].get("url"))
        elif t == "file_upload":
            return FileTypeUploaded(data['file_upload'].get("id"))
        else:
            raise ValueError(f"Unknown file type: {data}")
    else:
        raise ValueError(f"Empty Data to create the File")
