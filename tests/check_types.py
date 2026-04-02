import sys
sys.path.insert(0, ".")

from client.auth import NotionApiClient
from nEndpoints.blocks import get_block_children

API_KEY = "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"
BLK_MEETING = "325b7a8f72948037bc72dfd0a8726941"

api = NotionApiClient(key=API_KEY)

# Leggi il blocco meeting_notes grezzo
from nEndpoints.blocks import get_block
raw = get_block(api.headers, BLK_MEETING)
meeting_data = raw.response
block_type = meeting_data["type"]
children_ids = meeting_data[block_type].get("children", {})

summary_id = children_ids.get("summary_block_id")
print("summary_block_id:", summary_id)

if summary_id:
    # Leggi i figli del summary — mostra il tipo RAW restituito dall'API
    children = get_block_children(api.headers, summary_id)
    print(f"\nFigli del summary ({len(children)}):")
    for blk in children:
        print(f"  type='{blk['type']}'  id={blk['id'][:8]}...")