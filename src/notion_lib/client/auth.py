class NotionApiClient:
    _IMMUTABLE = frozenset({"key", "version"})

    def __init__(self, key: str, version: str = "2025-09-03"):
        # Bypass __setattr__ per i campi immutabili durante l'init
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "version", version)
        object.__setattr__(self, "headers", {
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
            "Notion-Version": version,
            "accept": "application/json",
        })

    def __setattr__(self, name: str, value):
        if name in self._IMMUTABLE:
            raise AttributeError(f"'{name}' è immutabile dopo l'inizializzazione.")
        super().__setattr__(name, value)

    def __repr__(self):
        return f"<NotionApiClient version={self.version}>"