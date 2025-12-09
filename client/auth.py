
class NotionApiClient:
    def __init__(self, key, version: str = "2025-09-03"):
        self.key = key
        self.headers = {
            "Authorization": "Bearer " + self.key,
            "Content-Type": "application/json",
            "Notion-Version": version,
            "accept": "application/json",
        }

    def __setattr__(self, name, value):
        if hasattr(self, name) and name in ("key", "version"):
            raise AttributeError(f"{name} is immutable")
        super().__setattr__(name, value)
