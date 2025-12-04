
class NotionApiClient:
    def __init__(self, key, version: str = "2025-09-03"):
        self.key = key
        self.headers = {
            "Authorization": "Bearer " + self.key,
            "Content-Type": "application/json",
            "Notion-Version": version,
            "accept": "application/json",
        }