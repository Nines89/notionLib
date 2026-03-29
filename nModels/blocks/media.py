from nModels.blocks.base_block import register_block, BlockImpl
from nTypes import NRichList, FileTypeExternal, FileTypeFile, FileTypeUploaded, n_file
from nTypes.rich_text import simple_rich_text_list, create_rich_list


@register_block("image")
class Image(BlockImpl):
    type = "image"

    def __init__(self, headers, block_id=None, caption: NRichList = None, file_object: dict = None):
        super().__init__(headers, block_id)
        self._caption = caption or NRichList()
        self._file_object = n_file(file_object)

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

    def __init__(self, headers, block_id=None, caption: NRichList = None, file_object: dict = None):
        super().__init__(headers, block_id)
        self._caption = caption or NRichList()
        self._file_object = n_file(file_object) if file_object else None

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
            file_object=fo.to_dict(),
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

    def __init__(self, headers, block_id=None, caption: NRichList = None, file_object: dict = None):
        super().__init__(headers, block_id)
        self._caption = caption or NRichList()
        self._file_object = n_file(file_object) if file_object else None

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



if __name__ == "__main__":
    from client.auth import NotionApiClient
    from nModels.blocks.base_block import NFactory

    api = NotionApiClient(key="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")
    img_id = "https://www.notion.so/color-A2DCEE-textbf-API-Integration-2a7b7a8f729480b3b420f8736c4116d7?source=copy_link#2a7b7a8f729481e6b128c8ffeaa62669"
    file_id = "https://www.notion.so/color-A2DCEE-textbf-API-Integration-2a7b7a8f729480b3b420f8736c4116d7?source=copy_link#2fbb7a8f7294807ca2c0fde21cc2b968"
    embed_id = "https://www.notion.so/color-A2DCEE-textbf-API-Integration-2a7b7a8f729480b3b420f8736c4116d7?source=copy_link#2fbb7a8f72948021a338ef1ea3216203"
    # Partendo da una foto
    # recuperiamo tutto e cambiamo la caption
    #########################################  IMG ###################################################################
    # blk = NFactory.find(api.headers, img_id)
    # blk.caption = "Sostituiamo una caption"
    # new_image = FileTypeExternal(url="https://m.media-amazon.com/images/I/61EHasGroeL._UF1000,1000_QL80_.jpg")
    # blk.file_object = new_image
    # print(blk.to_payload())
    # blk.update()
    ###################################################################################################################
    #########################################  FILE ###################################################################
    # blk = NFactory.find(api.headers, file_id)
    # print(blk.block_type)
    # print(blk.name)
    # print(blk.file_object.url)
    # print(blk.file_object.expiry_time)
    ###################################################################################################################
    #########################################  EMBED ###################################################################
    blk = NFactory.find(api.headers, embed_id)
    print(blk.url)