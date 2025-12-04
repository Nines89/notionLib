# notion_lib/nTypes/icons.py

class NIcon:
    def __init__(self, type_, data):
        self.type = type_
        self.data = data

    def to_dict(self):
        return {"type": self.type, self.type: self.data}


class NEmoji(NIcon):
    def __init__(self, emoji: str):
        super().__init__("emoji", {"emoji": emoji})
