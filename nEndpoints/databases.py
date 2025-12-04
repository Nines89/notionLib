from client.https import NGET, NPATCH, NDEL
from utils.constants import ParentTypes

BASE = "https://api.notion.com/v1/databases"


def get_db(headers, db_id):
    return NGET(header=headers, url=f"{BASE}/{db_id}")
