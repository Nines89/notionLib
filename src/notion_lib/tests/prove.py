# from notion_lib.client.auth import NotionApiClient
# from notion_lib.nEndpoints.searches import search_by_title
#
# api = NotionApiClient(key="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")
#
# els = search_by_title(api.headers)['results']
#
# for el in els:
#     if el.get("object") == "data_source":
#         print(type(el.get("name")), repr(el.get("name")))


"""
fix_imports.py
Corregge le righe del tipo:
    notion_lib.xxx.yyy import ZZZ
aggiungendo il 'from' mancante:
    from notion_lib.xxx.yyy import ZZZ

Uso:
    python fix_imports.py <percorso_cartella_src>

Esempio:
    python fix_imports.py C:/Users/Utente/Desktop/.../notion_lib/src
"""

import re
import sys
from pathlib import Path

PATTERN = re.compile(r'^(notion_lib\..+\s+import\s+.+)$', re.MULTILINE)


def fix_file(path: Path) -> int:
    """Ritorna il numero di righe corrette."""
    original = path.read_text(encoding="utf-8")
    fixed, count = PATTERN.subn(r'from \1', original)
    if count:
        path.write_text(fixed, encoding="utf-8")
        print(f"  [{count} fix] {path}")
    return count


def main():
    if len(sys.argv) < 2:
        print("Uso: python fix_imports.py <percorso_cartella>")
        sys.exit(1)

    root = Path(sys.argv[1])
    if not root.exists():
        print(f"ERRORE: cartella non trovata: {root}")
        sys.exit(1)

    py_files = list(root.rglob("*.py"))
    print(f"File .py trovati: {len(py_files)}")
    print()

    total = 0
    for f in py_files:
        total += fix_file(f)

    print()
    print(f"Totale correzioni: {total}")


if __name__ == "__main__":
    main()