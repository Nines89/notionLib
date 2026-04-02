from nModels.blocks.base_block import register_block, BlockImpl
from nTypes import NRichList, FileTypeExternal, FileTypeFile, FileTypeUploaded, n_file
from nTypes.files import BaseFile
from nTypes.rich_text import simple_rich_text_list, create_rich_list


def _resolve_file(file_object):
    """
    Normalizza file_object: accetta sia un dict Notion grezzo (path from_data)
    sia un'istanza BaseFile già costruita (path create()).
    """
    if file_object is None:
        return None
    if isinstance(file_object, BaseFile):
        return file_object
    return n_file(file_object)


@register_block("image")
class Image(BlockImpl):
    type = "image"

    def __init__(self, headers, block_id=None, caption: NRichList = None, file_object=None):
        super().__init__(headers, block_id)
        self._caption = caption or NRichList()
        self._file_object = _resolve_file(file_object)

    @classmethod
    def from_data(cls, headers, data, block_id):
        p = data["image"]
        return cls(
            headers=headers, block_id=block_id,
            caption=create_rich_list(p.get("caption", [])),
            file_object=p,
        )

    @classmethod
    def create(cls, caption: str, file_object: FileTypeExternal | FileTypeFile | FileTypeUploaded = None):
        return cls(headers=None, caption=simple_rich_text_list(caption), file_object=file_object)

    def to_payload(self):
        payload = {"image": self._file_object.to_dict()}
        payload["image"]["caption"] = self._caption.to_dict()
        del payload["image"]["type"]
        return payload

    def update(self):
        if self._file_object.type == "external":
            super().update()
        else:
            print("Solo le immagini esterne possono essere aggiornate.")

    @property
    def caption(self):
        return self._caption

    @caption.setter
    def caption(self, value: str):
        self._caption = simple_rich_text_list(value)

    @property
    def file_object(self):
        return self._file_object

    @file_object.setter
    def file_object(self, value):
        self._file_object = value


@register_block("video")
class Video(BlockImpl):
    """
    Blocco video. Supporta URL esterni (es. YouTube, Vimeo).
    Solo file esterni possono essere creati e aggiornati via API.
    """
    type = "video"

    def __init__(self, headers, block_id=None, caption: NRichList = None, file_object=None):
        super().__init__(headers, block_id)
        self._caption = caption or NRichList()
        self._file_object = _resolve_file(file_object)

    @classmethod
    def from_data(cls, headers, data, block_id):
        p = data["video"]
        return cls(
            headers=headers, block_id=block_id,
            caption=create_rich_list(p.get("caption", [])),
            file_object=p,
        )

    @classmethod
    def create(cls, url: str, caption: str = ""):
        """Crea un blocco video con URL esterno (es. YouTube)."""
        from nTypes.files import FileTypeExternal
        fo = FileTypeExternal(url)
        return cls(
            headers=None,
            caption=simple_rich_text_list(caption) if caption else NRichList(),
            file_object=fo,
        )

    def to_payload(self):
        payload = {"video": self._file_object.to_dict()}
        payload["video"]["caption"] = self._caption.to_dict()
        del payload["video"]["type"]
        return payload

    def update(self):
        if self._file_object and self._file_object.type == "external":
            super().update()
        else:
            print("Solo i video esterni possono essere aggiornati.")

    @property
    def caption(self):
        return self._caption

    @caption.setter
    def caption(self, value: str):
        self._caption = simple_rich_text_list(value)

    @property
    def file_object(self):
        return self._file_object

    @file_object.setter
    def file_object(self, value):
        self._file_object = value

    @property
    def url(self):
        if self._file_object and hasattr(self._file_object, "url"):
            return self._file_object.url
        return None


@register_block("audio")
class Audio(BlockImpl):
    """
    Blocco audio. Solo file caricati tramite Notion; read-only via API pubblica.
    Non è possibile creare o aggiornare blocchi audio via API.
    """
    type = "audio"
    updatable = False

    def __init__(self, headers, block_id=None, caption: NRichList = None, file_object=None):
        super().__init__(headers, block_id)
        self._caption = caption or NRichList()
        self._file_object = _resolve_file(file_object)

    @classmethod
    def from_data(cls, headers, data, block_id):
        p = data["audio"]
        return cls(
            headers=headers, block_id=block_id,
            caption=create_rich_list(p.get("caption", [])),
            file_object=p,
        )

    @classmethod
    def create(cls, **kwargs):
        raise NotImplementedError("I blocchi audio non possono essere creati via API pubblica.")

    def to_payload(self):
        raise NotImplementedError("I blocchi audio non possono essere aggiornati via API pubblica.")

    @property
    def caption(self):
        return self._caption

    @property
    def file_object(self):
        return self._file_object

    @property
    def url(self):
        if self._file_object and hasattr(self._file_object, "url"):
            return self._file_object.url
        return None


@register_block("file")
class File(BlockImpl):
    type = "file"
    block_type = "file"

    def __init__(self, headers, block_id=None, caption: NRichList = None,
                 file_object: dict = None, name: str = None):
        super().__init__(headers, block_id)
        self._caption = caption or NRichList()
        self._name = name
        self._file_object = n_file(file_object)

    @classmethod
    def from_data(cls, headers, data, block_id):
        p = data[cls.block_type]
        return cls(
            headers=headers, block_id=block_id,
            caption=create_rich_list(p.get("caption", [])),
            file_object=p,
            name=p.get("name"),
        )

    @classmethod
    def create(cls, caption: str, file_object=None):
        return cls(headers=None, caption=simple_rich_text_list(caption), file_object=file_object)

    def to_payload(self):
        payload = {"file": self._file_object.to_dict()}
        payload["file"]["caption"] = self._caption.to_dict()
        del payload["file"]["type"]
        return payload

    def update(self):
        if self._file_object.type == "external":
            super().update()
        else:
            print("Solo i file esterni possono essere aggiornati.")

    @property
    def caption(self):
        return self._caption

    @caption.setter
    def caption(self, value: str):
        self._caption = simple_rich_text_list(value)

    @property
    def file_object(self):
        return self._file_object

    @file_object.setter
    def file_object(self, value):
        self._file_object = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value


@register_block("pdf")
class Pdf(File):
    type = "pdf"
    block_type = "file"


@register_block("embed")
class Embed(BlockImpl):
    type = "embed"

    def __init__(self, headers, block_id=None, url: str = None):
        super().__init__(headers, block_id)
        self._url = url

    @classmethod
    def from_data(cls, headers, data, block_id):
        p = data["embed"]
        return cls(headers=headers, block_id=block_id, url=p.get("url"))

    @classmethod
    def create(cls, url: str):
        return cls(headers=None, url=url)

    def to_payload(self):
        return {"embed": {"url": self._url}}

    @property
    def url(self):
        return self._url