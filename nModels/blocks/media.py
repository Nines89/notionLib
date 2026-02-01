from nModels.blocks.base_block import register_block, BlockImpl
from nTypes import NRichList, FileTypeExternal, FileTypeFile, n_file
from nTypes.rich_text import simple_rich_text_list, create_rich_list


@register_block("image")
class Image(BlockImpl):
    type = "image"

    def __init__(self,
                 headers,
                 block_id=None,
                 caption: NRichList = None,
                 file_object: dict = None):
        super().__init__(headers, block_id)
        self._caption = caption or NRichList
        self._file_object = n_file(file_object)

    @classmethod
    def from_data(cls, headers, data, block_id):
        p = data["image"]
        obj = cls(
            headers=headers,
            block_id=block_id,
            caption=create_rich_list(p.get("caption", [])),
            file_object=p
        )
        obj._data = data
        return obj

    @classmethod
    def create(cls, caption: str, file_object: FileTypeExternal | FileTypeFile = None):
        return cls(
            headers=None,
            caption=simple_rich_text_list(caption),
            file_object=file_object,
        )

    def to_payload(self):
        payload = {"image": self._file_object.to_dict()}
        payload['image']["caption"] = self._caption.to_dict()
        del payload['image']["type"]
        return payload

    def update(self):
        if self._file_object.type == 'external':
            super(Image, self).update()
        else:
            print("Only external Images can be updated.")

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
    def file_object(self, value: FileTypeExternal | FileTypeFile):
        self._file_object = value


if __name__ == "__main__":
    from client.auth import NotionApiClient
    from nModels.blocks.base_block import NFactory

    api = NotionApiClient(key="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")
    img_id = "https://www.notion.so/color-A2DCEE-textbf-API-Integration-2a7b7a8f729480b3b420f8736c4116d7?source=copy_link#2a7b7a8f729481e6b128c8ffeaa62669"

    # Partendo da una foto
    # recuperiamo tutto e cambiamo la caption

    blk = NFactory.find(api.headers, img_id)
    blk.caption = "Sostituiamo una caption"
    new_image = FileTypeExternal(url="https://m.media-amazon.com/images/I/61EHasGroeL._UF1000,1000_QL80_.jpg")
    blk.file_object = new_image
    print(blk.to_payload())
    blk.update()
