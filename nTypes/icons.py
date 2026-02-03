from nTypes import n_file


class EmojiError(Exception):
    pass


class IconFactory:
    type = "icon"

    @staticmethod
    def find(data):
        """
        data:  is the same of Emoji outputs
        """
        if data.get("type") == "emoji":
            return NEmojiFactory.find(data)
        else:
            return n_file(data)

class NEmoji:
    type = "emoji"

    def __init__(self, data: dict):
        """
          data:  {
                "type": "emoji",
                "emoji": "🥑"
              }
        """
        self.data = data
        self._emoji = self.data.get("emoji")

    @property
    def emoji(self) -> str:
        return self._emoji

    @emoji.setter
    def emoji(self, value: str):
        self._emoji = value

    def to_payload(self) -> dict:
        return {
            "type": self.type,
            "emoji": self._emoji,
        }


class NCustomEmoji:
    type = "custom_emoji"

    def __init__(self, data: dict):
        """
        data = {
            "type": "custom_emoji",
            "custom_emoji": {
              "id": "45ce454c-d427-4f53-9489-e5d0f3d1db6b",
              "name": "bufo",
              "url": "https://s3-us-west-2.amazonaws.com/public.notion-static.com/865e85fc-7442-44d3-b323-9b03a2111720/3c6796979c50f4aa.png"
            }
          }
        """
        self.data = data
        self._id = self.data["custom_emoji"].get("id")
        self._name = self.data["custom_emoji"].get("name")
        self._url = self.data["custom_emoji"].get("url")

    @property
    def id_(self) -> str:
        return self._id

    @id_.setter
    def id_(self, value: str):
        self.id_ = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def url(self) -> str:
        return self._url

    @url.setter
    def url(self, value: str):
        self._url = value

    def to_payload(self) -> dict:
        return {
            "type": self.type,
            "custom_emoji": {
                "id": self.id_,
                "name": self.name,
                "url": self.url,
            }
        }


class NEmojiFactory:

    @staticmethod
    def find(data):
        """
        data:  is the same of Emoji outputs
        """
        if data.get("type") == "emoji":
            return NEmoji(data)
        elif data.get("type") == "custom_emoji":
            return NCustomEmoji(data)
        else:
            raise EmojiError("Emoji is not known")