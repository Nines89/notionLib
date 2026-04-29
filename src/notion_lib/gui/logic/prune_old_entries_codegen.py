import re


def generate_prune_old_entries_code(cfg: dict, target_label: str) -> str:
    cls = re.sub(r"[^A-Za-z0-9]", "", cfg['name'].title().replace(' ', '')) or 'PruneOldEntriesAutomation'
    return f'''\
"""
Automazione: {cfg['name']}
DataSource: {target_label}
Proprietà data: {cfg['date_prop']}
Soglia: {cfg['days']} giorni
"""

import os
import sys
from datetime import datetime, timezone, timedelta
sys.path.insert(0, ".")

from client.auth import NotionApiClient
from nModels.datasources import DataSourceFactory
from nEndpoints.blocks import delete_block


class {cls}:
    TARGET_DS = "{cfg['ds_id']}"
    DATE_PROP = "{cfg['date_prop']}"
    DAYS = {int(cfg['days'])}

    def __init__(self, api_key: str):
        self.api = NotionApiClient(key=api_key)

    def _parse_iso(self, value: str):
        if not value:
            return None
        text = value.strip().replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(text)
        except ValueError:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt

    def run(self):
        ds = DataSourceFactory.find(self.api.headers, self.TARGET_DS)
        entries = ds.all_entries()
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.DAYS)
        deleted = 0

        for entry in entries:
            props = entry.get("properties", {{}})
            date_obj = props.get(self.DATE_PROP, {{}}).get("date")
            start = (date_obj or {{}}).get("start") if isinstance(date_obj, dict) else None
            dt = self._parse_iso(start)
            if dt and dt < cutoff:
                delete_block(self.api.headers, entry.get("id"))
                deleted += 1

        print(f"✓ Entry analizzate: {{len(entries)}}")
        print(f"✓ Entry eliminate: {{deleted}}")


if __name__ == "__main__":
    key = os.environ.get("NOTION_KEY") or input("API Key Notion: ").strip()
    {cls}(key).run()
'''
