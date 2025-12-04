from .primitives import Ntype, NText, NMention, NEquation


class RichTextSchemaError(Exception):
    pass


class NRichText(Ntype):
    """
        {
      "type": "equation",
      "equation": {
        "expression": "E = mc^2"
      },
      "annotations": {
        "bold": false,
        "italic": false,
        "strikethrough": false,
        "underline": false,
        "code": false,
        "color": "default"
      },
      "plain_text": "E = mc^2",
      "href": null
    }
    """
    def __init__(self, data: dict): # noqa
        self._data = {}
        self.basic_schema = {
          "type": "",
          "annotations": {
            "bold": False,
            "italic": False,
            "strikethrough": False,
            "underline": False,
            "code": False,
            "color": ""
          },
          "plain_text": "",
          "href": ""
        }
        if isinstance(data, dict):
            for key, item in data.items():
                self._data[key] = item
                if key == 'type':
                    self.basic_schema[item] = {}
                if key == 'text':
                    self._data[key] = NText(item)
                elif key == 'equation':
                    self._data[key] = NEquation(item)
                elif key == 'mention':
                    self._data[key] = NMention(item)
        if self._data.keys() != self.basic_schema.keys():
            raise RichTextSchemaError(
                f"Received Keys {self._data.keys()} are not the expected: {self.basic_schema.keys()}")

    @property
    def type(self):
        return self._data['type']

    @property
    def obj(self):
        return self._data[self.type]

    @property
    def annotations(self):
        return self._data['annotations']

    @property
    def plain_text(self):
        return self._data['plain_text']

    @property
    def href(self):
        return self._data['href']

    def __getitem__(self, item):
        return self._data[item]

    def __repr__(self):
        return f"Plain Text: {self.plain_text}"


class NRichList(list):
    def append(self, item: NRichText):
        if not isinstance(item, NRichText):
            raise ValueError(f"{item} is not a NRichText, but {type(item)}")
        super().append(item)

    def to_dict(self):
        rt = []
        try:
            for r in self:
                rd = r.to_dict()
                for j, item in rd.items():
                    if isinstance(item, Ntype):
                        rd[j] = item.to_dict()
                if rd['annotations'] is None:
                    rd['annotations'] = {
                            "bold": False,
                            "italic": False,
                            "strikethrough": False,
                            "underline": False,
                            "code": False,
                            "color": "default"
                          }
                rt.append(rd)
        except TypeError as e:
            raise TypeError(f"Error: {e}, rich could be empty, try to call self.get_rich_text or use rich_text setter!")
        return rt

    @property
    def text(self):
        return ''.join([element.plain_text for element in self])


def simple_rich_text_list(content: str, t_type: str = 'text'):
    if t_type == 'text':
        item = NText({'text': {"content": content, 'link': None}})
    elif t_type == 'equation':
        item = NEquation({"expression": content})
    else:
        raise ValueError(f"{t_type} is not supported - text or equation")
    rich_json = {
      "type": t_type,
      t_type: item.to_dict(),
      "annotations": {
        "bold": False,
        "italic": False,
        "strikethrough": False,
        "underline": False,
        "code": False,
        "color": "default"
      },
      "plain_text": content,
      "href": None
    }
    ret = NRichList()
    ret.append(NRichText(rich_json))
    return ret
