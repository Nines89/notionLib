from nModels.base_object import ObjInterface
from nModels.base_object import NObj, NObjDB, NObjDS, NObjPage
from nModels.blocks.base_block import NObjBlock

class ParentError(Exception):
    pass


class ParentFactory:
    @staticmethod
    def create(header: dict, parent_info: dict) -> NObj:
        t = parent_info.get("type")
        if t == "database_id":
            u = NObjDB(header, obj_id=parent_info["database_id"])
        elif t == "data_source_id":
            u = NObjDS(header, obj_id=parent_info["data_source_id"])
        elif t == "page_id":
            u = NObjPage(header, obj_id=parent_info["page_id"])
        elif t == "workspace":
            u = None
        elif t == "block_id":
            u = NObjBlock(header, obj_id=parent_info["block_id"])
        else:
            raise ParentError(f"Unknown Parent Type: {t}")
        return u


