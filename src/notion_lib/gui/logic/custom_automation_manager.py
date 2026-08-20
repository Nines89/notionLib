"""
gui/logic/custom_automation_manager.py

Responsabilità:
  - persistenza delle automazioni custom in una cartella dati utente stabile
  - generazione del template Python a partire dalla selezione degli oggetti
  - CRUD base (save, load_all, delete)

Struttura su disco (indipendente dalla cwd):
  <user_data>/notion-lib/custom_automations/
  ├── manifest.json                   ← lista di tutti i metadata
  └── <slug>/
      └── script.py                   ← codice dell'automazione

Override: variabile d'ambiente NOTION_LIB_DATA_DIR (usa <dir>/custom_automations).
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Optional


# ── Path risoluzione ─────────────────────────────────────────────────────────

def default_custom_automations_root() -> Path:
    """
    Cartella stabile per le automazioni custom (non dipende dalla cwd).

    Windows : %LOCALAPPDATA%/notion-lib/custom_automations
    macOS   : ~/Library/Application Support/notion-lib/custom_automations
    Linux   : $XDG_DATA_HOME/notion-lib/custom_automations
              (default ~/.local/share/...)
    """
    override = os.environ.get("NOTION_LIB_DATA_DIR")
    if override:
        return Path(override).expanduser().resolve() / "custom_automations"

    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))

    return (base / "notion-lib" / "custom_automations").resolve()


ROOT = default_custom_automations_root()
MANIFEST = ROOT / "manifest.json"

# Tutti gli oggetti importabili offerti all'utente nella checklist.
# Chiave  → label UI
# "imports" → righe da aggiungere al template
# "description" → tooltip nel dialog
AVAILABLE_OBJECTS: dict[str, dict] = {
    "DataSourceFactory": {
        "label": "DataSourceFactory",
        "imports": ["from notion_lib.nModels.datasources import DataSourceFactory, NDataSource"],
        "description": "Leggi, filtra, crea entry in un DataSource",
    },
    "PageFactory": {
        "label": "PageFactory (pagine)",
        "imports": ["from notion_lib.nModels.pages import PageFactory, SimplePage, DatabasePage"],
        "description": "Leggi e modifica pagine Notion",
    },
    "NFactory": {
        "label": "NFactory (blocchi)",
        "imports": [
            "from notion_lib.nModels.blocks.base_block import NFactory",
            "from notion_lib.nModels.blocks.paragraph import ParagraphBlock",
            "from notion_lib.nModels.blocks.heading import Heading1, Heading2, Heading3",
            "from notion_lib.nModels.blocks.list_blocks import ToDo, Toggle, BulletedListItem",
            "from notion_lib.nModels.blocks.special_blocks import CalloutBlock, CodeBlock",
        ],
        "description": "Crea e modifica blocchi all'interno di pagine",
    },
    "DatabaseFactory": {
        "label": "DatabaseFactory",
        "imports": ["from notion_lib.nModels.databases import DatabaseFactory, NDatabase"],
        "description": "Leggi e modifica database Notion",
    },
    "F_S": {
        "label": "F, S (filtri e sort)",
        "imports": ["from notion_lib.nTypes.ds_filters import F, S"],
        "description": "Costruttori di filtri e ordinamenti per i DataSource",
    },
    "UserFactory": {
        "label": "UserFactory (utenti)",
        "imports": ["from notion_lib.nModels.user import UserFactory"],
        "description": "Recupera informazioni sugli utenti del workspace",
    },
    "search": {
        "label": "search (ricerca globale)",
        "imports": ["from notion_lib.nEndpoints.searches import search_by_title"],
        "description": "Cerca pagine e datasource per titolo",
    },
    "RichText": {
        "label": "RichText utils",
        "imports": [
            "from notion_lib.nTypes.rich_text import simple_rich_text_list, create_rich_list",
            "from notion_lib.nTypes.icons import NEmoji",
        ],
        "description": "Gestione testo formattato e icone",
    },
}

# Gradienti predefiniti tra cui l'utente sceglie nel dialog
GRADIENT_PRESETS: list[dict] = [
    {"label": "Viola → Indigo",  "start": "#7C3AED", "end": "#6366F1"},
    {"label": "Rosa → Arancio",  "start": "#EC4899", "end": "#F97316"},
    {"label": "Verde → Ciano",   "start": "#10B981", "end": "#06B6D4"},
    {"label": "Blu → Ciano",     "start": "#2563EB", "end": "#22D3EE"},
    {"label": "Rosso → Rosa",    "start": "#EF4444", "end": "#EC4899"},
    {"label": "Giallo → Verde",  "start": "#F59E0B", "end": "#10B981"},
    {"label": "Grigio scuro",    "start": "#334155", "end": "#475569"},
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _slugify(name: str) -> str:
    """Genera un identificatore filesystem-safe dal nome."""
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower().strip()).strip("_")
    return slug or "custom"


def _class_name(name: str) -> str:
    """Converte il nome in PascalCase per il nome della classe."""
    return re.sub(r"[^A-Za-z0-9]", "", name.title().replace(" ", "")) or "CustomAutomation"


# ── Generazione template ──────────────────────────────────────────────────────

def generate_template(name: str, selected_objects: list[str]) -> str:
    """
    Genera il codice Python del template a partire dalla selezione degli oggetti.

    selected_objects: lista di chiavi da AVAILABLE_OBJECTS
    """
    cls = _class_name(name)

    # Raccoglie le righe di import senza duplicati, preservando l'ordine
    seen: set[str] = set()
    import_lines: list[str] = [
        "import os",
        "import sys",
        "sys.path.insert(0, '.')",
        "",
        "from notion_lib.client.auth import NotionApiClient",
    ]
    for key in selected_objects:
        meta = AVAILABLE_OBJECTS.get(key)
        if not meta:
            continue
        for line in meta["imports"]:
            if line not in seen:
                import_lines.append(line)
                seen.add(line)

    imports_block = "\n".join(import_lines)

    # Corpo della classe: sezione run() con commenti contestuali
    run_body_lines = [
        '        """Logica principale dell\'automazione. Modifica questo metodo."""',
        "        print(f\"Avvio: {name}\")",
        "",
    ]

    if "DataSourceFactory" in selected_objects:
        run_body_lines += [
            "        # ── Esempio: carica un DataSource ───────────────────────────────",
            "        # ds_id = 'INSERISCI_ID_DATASOURCE'",
            "        # ds = DataSourceFactory.find(self.api.headers, ds_id)",
            "        # entries = ds.all_entries()",
            "        # print(f'Entry trovate: {len(entries)}')",
            "",
        ]

    if "F_S" in selected_objects:
        run_body_lines += [
            "        # ── Esempio: filtra le entry ─────────────────────────────────────",
            "        # results = ds.filter({'filter': F.checkbox('Done').equals(True)})",
            "        # sorted_results = ds.sort(S().get(('Name', True)))",
            "",
        ]

    if "PageFactory" in selected_objects:
        run_body_lines += [
            "        # ── Esempio: leggi una pagina ────────────────────────────────────",
            "        # page_id = 'INSERISCI_ID_PAGINA'",
            "        # page = PageFactory.find(self.api.headers, page_id)",
            "        # print(page.title)",
            "",
        ]

    if "NFactory" in selected_objects:
        run_body_lines += [
            "        # ── Esempio: aggiungi un blocco a una pagina ─────────────────────",
            "        # page = PageFactory.find(self.api.headers, 'INSERISCI_ID_PAGINA')",
            "        # page.append_children([ParagraphBlock.create('Testo inserito')])",
            "",
        ]

    if "DatabaseFactory" in selected_objects:
        run_body_lines += [
            "        # ── Esempio: leggi un database ───────────────────────────────────",
            "        # db_id = 'INSERISCI_ID_DATABASE'",
            "        # db = DatabaseFactory.find(self.api.headers, db_id)",
            "        # print(db.title, db.datasources)",
            "",
        ]

    if "UserFactory" in selected_objects:
        run_body_lines += [
            "        # ── Esempio: recupera un utente ──────────────────────────────────",
            "        # user = UserFactory.create(self.api.headers, 'USER_ID')",
            "        # print(user.name, user.email)",
            "",
        ]

    if "search" in selected_objects:
        run_body_lines += [
            "        # ── Esempio: cerca pagine per titolo ────────────────────────────",
            "        # results = search_by_title(self.api.headers, 'nome pagina')",
            "        # for r in results.response.get('results', []):",
            "        #     print(r['id'], r['object'])",
            "",
        ]

    run_body_lines.append("        print('Automazione completata.')")
    run_body = "\n".join(run_body_lines)

    return f'''\
"""
Automazione: {name}
Generata da Notion Automation GUI.

Modifica il metodo run() con la logica desiderata.
La variabile d'ambiente NOTION_KEY viene iniettata automaticamente
dall'applicazione quando si clicca "Esegui".
"""

{imports_block}


class {cls}:
    """Automazione personalizzata: {name}"""

    def __init__(self, api_key: str):
        self.api = NotionApiClient(key=api_key)

    def run(self):
{run_body}


if __name__ == "__main__":
    key = os.environ.get("NOTION_KEY") or input("API Key Notion: ").strip()
    if not key:
        print("Errore: nessuna API key fornita.")
        sys.exit(1)
    {cls}(key).run()
'''


# ── Manager ───────────────────────────────────────────────────────────────────

class CustomAutomationManager:
    """
    Gestisce la persistenza delle automazioni custom.

    Manifest schema (ogni entry):
    {
        "slug":           str,   # identificatore filesystem-safe
        "name":           str,   # nome display
        "icon":           str,   # emoji
        "description":    str,
        "gradient_start": str,   # hex color
        "gradient_end":   str,   # hex color
        "script_path":    str,   # path assoluto allo script
    }
    """

    def __init__(self, root: Optional[Path] = None):
        self._root = Path(root).resolve() if root else default_custom_automations_root()
        self._root.mkdir(parents=True, exist_ok=True)
        self._manifest_path = self._root / "manifest.json"
        self._migrate_legacy_if_needed()

    # ── CRUD ──────────────────────────────────────────────────────

    def load_all(self) -> list[dict]:
        """Carica tutte le automazioni dal manifest. Lista vuota se non esiste."""
        if not self._manifest_path.exists():
            return []
        try:
            data = json.loads(self._manifest_path.read_text(encoding="utf-8"))
            resolved: list[dict] = []
            changed = False
            for entry in data:
                script = self._resolve_script_path(entry.get("script_path", ""), entry.get("slug", ""))
                if not script.exists():
                    continue
                abs_path = str(script.resolve())
                if entry.get("script_path") != abs_path:
                    entry = {**entry, "script_path": abs_path}
                    changed = True
                resolved.append(entry)
            if changed:
                self._write_manifest(resolved)
            return resolved
        except (json.JSONDecodeError, KeyError, TypeError):
            return []

    def save(
        self,
        name: str,
        icon: str,
        description: str,
        gradient_start: str,
        gradient_end: str,
        selected_objects: list[str],
    ) -> dict:
        """
        Crea una nuova automazione custom.
        Genera lo script template e aggiorna il manifest.
        Restituisce il dict dell'entry appena creata.
        """
        slug = self._unique_slug(name)
        script_dir = self._root / slug
        script_dir.mkdir(parents=True, exist_ok=True)
        script_path = (script_dir / "script.py").resolve()

        # Genera e salva il template
        code = generate_template(name, selected_objects)
        script_path.write_text(code, encoding="utf-8")

        entry = {
            "slug":           slug,
            "name":           name,
            "icon":           icon,
            "description":    description,
            "gradient_start": gradient_start,
            "gradient_end":   gradient_end,
            "script_path":    str(script_path),
        }

        existing = self.load_all()
        existing.append(entry)
        self._write_manifest(existing)

        return entry

    def delete(self, slug: str) -> bool:
        """Rimuove l'automazione dal manifest e cancella lo script."""
        entries = self.load_all()
        to_delete = next((e for e in entries if e["slug"] == slug), None)
        if not to_delete:
            return False

        # Rimuove i file
        script = Path(to_delete["script_path"])
        if script.exists():
            script.unlink()
        if script.parent.exists() and script.parent != self._root and not any(script.parent.iterdir()):
            script.parent.rmdir()

        # Aggiorna manifest
        self._write_manifest([e for e in entries if e["slug"] != slug])
        return True

    def get(self, slug: str) -> Optional[dict]:
        return next((e for e in self.load_all() if e["slug"] == slug), None)

    def script_path(self, slug: str) -> Optional[Path]:
        entry = self.get(slug)
        return Path(entry["script_path"]) if entry else None

    # ── Helpers privati ───────────────────────────────────────────

    def _resolve_script_path(self, script_path: str, slug: str) -> Path:
        """Risolve path assoluti, relativi alla root dati, o legacy cwd-relative."""
        path = Path(script_path) if script_path else Path()
        if path.is_absolute() and path.exists():
            return path
        candidates = [
            self._root / slug / "script.py" if slug else Path(),
            self._root / path if not path.is_absolute() else path,
            Path.cwd() / path if not path.is_absolute() else path,
        ]
        for candidate in candidates:
            if candidate and candidate.exists():
                return candidate
        return self._root / slug / "script.py" if slug else path

    def _legacy_root(self) -> Path:
        """Vecchia cartella relativa alla cwd (pre-fix distributable)."""
        return Path.cwd() / "custom_automations"

    def _manifest_has_entries(self) -> bool:
        if not self._manifest_path.exists():
            return False
        try:
            data = json.loads(self._manifest_path.read_text(encoding="utf-8"))
            return bool(data)
        except (json.JSONDecodeError, OSError):
            return False

    def _migrate_legacy_if_needed(self) -> None:
        """
        Copia one-shot da ./custom_automations (cwd) alla cartella dati utente
        se la destinazione non ha ancora entry valide.
        """
        if self._manifest_has_entries():
            return

        legacy = self._legacy_root()
        legacy_manifest = legacy / "manifest.json"
        if not legacy_manifest.exists():
            return
        # Evita di "migrare" verso se stessi
        try:
            if legacy.resolve() == self._root:
                return
        except OSError:
            return

        try:
            data = json.loads(legacy_manifest.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return
        if not isinstance(data, list) or not data:
            return

        migrated: list[dict] = []
        for entry in data:
            slug = entry.get("slug")
            if not slug:
                continue
            src_script = Path(entry.get("script_path", ""))
            if not src_script.is_absolute():
                src_script = Path.cwd() / src_script
            if not src_script.exists():
                alt = legacy / slug / "script.py"
                if alt.exists():
                    src_script = alt
                else:
                    continue

            dest_dir = self._root / slug
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_script = (dest_dir / "script.py").resolve()
            if src_script.resolve() != dest_script:
                shutil.copy2(src_script, dest_script)

            migrated.append({
                **entry,
                "script_path": str(dest_script),
            })

        if migrated:
            self._write_manifest(migrated)

    def _write_manifest(self, entries: list[dict]) -> None:
        self._manifest_path.write_text(
            json.dumps(entries, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _unique_slug(self, name: str) -> str:
        """Garantisce che lo slug non esista già su disco."""
        base = _slugify(name)
        slug = base
        i = 2
        while (self._root / slug).exists():
            slug = f"{base}_{i}"
            i += 1
        return slug
