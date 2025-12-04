# notion_lib/nTypes/primitives.py
from datetime import datetime


class Ntype:
    def __init__(self, data: dict):
        self._data = data

    def to_dict(self):
        return self._data


class NDate:
    def __init__(self, data: str | datetime): # noqa
        if isinstance(data, str):
            self.data = datetime.fromisoformat(data.replace("Z", "+00:00"))
        else:
            self.data = data

    def to_dict(self):
        if self.data is None:
            return None
        return self.data.isoformat(timespec="milliseconds").replace("+00:00", "Z")

    def __repr__(self):
        return f"{self.data}"


class NText(Ntype):
    """
    "text": {
    "content": "Some words ",
    "link": {
            'url': 'some url'
        }
    },
    """
    @property
    def content(self):
        return self._data['text']['content']

    @content.setter
    def content(self, value: str):
        self._data['text']['content'] = value

    @property
    def link(self):
        if self._data['text']['link']:
            return self._data['text']['link']['url']
        return None

    @link.setter
    def link(self, value: str):
        if self._data['text']['link']:
            self._data['text']['link']['url'] = value
        else:
            self._data['text']['link'] = {}
            self._data['text']['link']['url'] = value

    def __repr__(self):
        return f"Content: {self.content}\nLink: {self.link}"

    def to_dict(self):
        if 'text' in self._data.keys():
            return self._data['text']
        return self._data


class NEquation(Ntype):
    """
        "equation": {
        "expression": "E = mc^2"
      },
    """
    @property
    def equation(self):
        return self._data['equation']['expression']

    @equation.setter
    def equation(self, value: str):
        self._data['equation']['expression'] = value

    def __repr__(self):
        return f"Equation: {self.equation}\n"


class NMention:
    """Placeholder: da espandere se servono menzioni di utenti/pagine/database."""
    def __init__(self, mention_obj: dict):
        self.data = mention_obj

    def to_dict(self):
        return {"type": "mention", "mention": self.data}
