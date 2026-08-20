# Notion Automation — Guida completa

Libreria Python per l'API Notion (versione `2025-09-03`) + applicazione desktop **Notion Automation** (PyQt6) per configurare ed eseguire automazioni **senza scrivere codice**.

Questa guida è pensata per essere autosufficiente sia per chi vuole solo usare la GUI, sia per chi vuole usare `notion_lib` come libreria Python nei propri script.

---

## Indice

**Parte A — Per chi usa la GUI**
1. [Installazione](#1-installazione)
2. [Avvio](#2-avvio)
3. [Prima configurazione Notion](#3-prima-configurazione-notion)
4. [Gestione credenziali](#4-gestione-credenziali)
5. [Tour della GUI](#5-tour-della-gui)
6. [Automazioni integrate — guida passo-passo](#6-automazioni-integrate--guida-passo-passo)
7. [Automazioni personalizzate](#7-automazioni-personalizzate)
8. [Risoluzione problemi (FAQ)](#8-risoluzione-problemi-faq)

**Parte B — Per chi usa la libreria Python**
9. [Architettura del progetto](#9-architettura-del-progetto)
10. [Autenticazione e livello HTTP](#10-autenticazione-e-livello-http)
11. [Pages, Databases, DataSources, Users](#11-pages-databases-datasources-users)
12. [Blocchi — tabella completa](#12-blocchi--tabella-completa)
13. [Tipi di supporto (rich text, file, icone, proprietà)](#13-tipi-di-supporto)
14. [Filtri e ordinamenti](#14-filtri-e-ordinamenti)
15. [Gestione errori e rate limit](#15-gestione-errori-e-rate-limit)
16. [Testing](#16-testing)
17. [Estendere il progetto](#17-estendere-il-progetto)
18. [Cheatsheet import rapidi](#18-cheatsheet-import-rapidi)

---

# Parte A — Per chi usa la GUI

## 1. Installazione

**Requisiti**: Python 3.11+ (il progetto dichiara `requires-python >= 3.10` in `pyproject.toml`, ma usa sintassi type-hint moderna — 3.11 è la baseline consigliata).

### Opzione 1 — installazione rapida (solo GUI, da cartella `src/notion_lib`)

```bash
cd src/notion_lib
pip install -r requirements.txt
```

Installa: `PyQt6>=6.6.0`, `requests>=2.31.0`, `certifi>=2024.0.0`.

> ⚠️ **`keyring` non è incluso** in `requirements.txt` ma è necessario per il salvataggio sicuro delle credenziali (§4). Installalo a parte:
> ```bash
> pip install keyring
> ```

### Opzione 2 — installazione come pacchetto (per usare anche la libreria Python)

Dalla root del progetto (dove si trova `pyproject.toml`):

```bash
pip install -e .
```

Il flag `-e` (editable) rende il pacchetto modificabile senza reinstallare ad ogni modifica al codice sorgente — eccetto quando si tocca `[project.scripts]` in `pyproject.toml`, nel qual caso serve rilanciare `pip install -e .`.

Verifica installazione:
```bash
pip show notion-lib
python -c "from notion_lib import NFactory, PageFactory"
```

---

## 2. Avvio

| Metodo | Comando | Note |
|---|---|---|
| Windows, doppio clic | `avvia.bat` | installa `PyQt6` al volo e lancia la GUI |
| Universale, da cartella `src/notion_lib` | `python notion_gui.py` | funziona sempre |
| Universale, con pacchetto installato | `python -m notion_lib.notion_gui` | |
| Entry point CLI (richiede `pip install -e .`) | `notion-gui` | su Windows, se non riconosciuto, aggiungi al PATH `C:\Users\<utente>\AppData\Roaming\Python\Python312\Scripts`, oppure esegui `pip install -e .` da PowerShell come amministratore |

---

## 3. Prima configurazione Notion

1. Vai su [notion.so/my-integrations](https://www.notion.so/my-integrations).
2. Crea una nuova integrazione (tipo "interna") → copia il **Token segreto** (inizia con `ntn_...`).
3. In Notion, per **ogni pagina/database** che vuoi rendere visibile all'automazione: apri il menu **···** in alto a destra → **Connetti a** → seleziona la tua integrazione.
   - Se un elemento non compare nella GUI dopo la connessione, è quasi sempre perché questo passaggio non è stato fatto su quella specifica pagina/database.
4. Incolla il token nel campo **Token API** della sidebar della GUI e clicca **⚡ Connetti**.

---

## 4. Gestione credenziali

Le chiavi API vengono salvate nel **vault nativo del sistema operativo** tramite la libreria `keyring` — **mai scritte in chiaro su disco**.

| Sistema operativo | Backend usato |
|---|---|
| Windows | Gestione credenziali (Credential Manager) |
| macOS | Keychain |
| Linux | GNOME Keyring / KWallet |

> Solo i **nomi dei profili** (non le chiavi) sono duplicati in un piccolo file JSON locale, `~/.notion_automation_profiles.json`, perché `keyring` non offre un modo nativo per elencare le credenziali salvate.

### Aggiungere una credenziale

**Dalla GUI**: compila **Nome profilo** e **Token API** nella sidebar, poi clicca 💾.

**Da terminale/script Python**:
```python
import keyring
keyring.set_password('NotionAutomation', 'nome_profilo', 'ntn_...')
```

| Parametro | Valore | Note |
|---|---|---|
| `'NotionAutomation'` | fisso | identificatore dell'app — non modificare |
| `'nome_profilo'` | libero | es. `'Workspace personale'` |
| `'ntn_...'` | il tuo token | da [notion.so/my-integrations](https://notion.so/my-integrations) |

### Rimuovere una credenziale

**Dalla GUI**: seleziona il profilo nel dropdown e clicca 🗑.

**Da terminale**:
```python
import keyring
keyring.delete_password('NotionAutomation', 'nome_profilo')
```

### Verificare che una credenziale sia stata salvata

```python
import keyring
print(keyring.get_password('NotionAutomation', 'nome_profilo'))
# Deve stampare il token. None → il profilo non esiste.
```

---

## 5. Tour della GUI

La finestra principale (`MainWindow`) è divisa in **sidebar** (sinistra, login/stato connessione) + **area a tab** (destra).

### 5.1 Sidebar

- **Stato disconnesso**: form con dropdown profili salvati, campo nome profilo, campo token, pulsanti Connetti (⚡) / Salva profilo (💾) / Elimina profilo (🗑).
- **Stato connesso**: nome del bot Notion, conteggio database/data-source rilevati, pulsante Disconnetti (⏻).

### 5.2 Tab "🪐 Panorama" (Workspace)

Vista ad **albero gerarchico**: `Pagina → Database → DataSource`, con 3 contatori in alto (Pagine / Database / DataSource).

I database che non hanno una pagina antenata visibile all'integrazione vengono raggruppati sotto "🧱 Database senza pagina parent".

**Tasto destro** su un elemento apre un menu contestuale specifico:

| Elemento | Azioni disponibili |
|---|---|
| 🗒 Pagina | **Inserisci blocco** → apre il dialog di creazione blocco (19 tipi, vedi §12) |
| 📦 Database | **Aggiungi DataSource** → dialog per creare un nuovo data source con schema custom |
| 🗂 DataSource | **Aggiungi pagina** → form dinamico generato dallo schema del data source |

**Doppio click**:
- su una **pagina** → apre l'esploratore blocchi (lista blocchi a sinistra, form di modifica a destra, salvataggio asincrono senza bloccare la UI)
- su un **data source** → apre la tabella di tutte le entry (colonne = schema, righe = entry, barra di ricerca client-side; doppio click su una riga apre i blocchi di quella pagina)

### 5.3 Tab "🤖 Flussi" (Automazioni)

Home con **tile** (una per automazione) + tile speciale "+ Nuova automazione" per crearne di personalizzate (§7). Click su una tile apre la vista dettaglio dello strumento; il pulsante "← Tutti i flussi" torna alla home.

Le automazioni **personalizzate** hanno in più: menu contestuale "🗑 Elimina automazione" sulla tile (tasto destro) e pulsante "🗑 Elimina" nell'header della vista dettaglio — entrambi chiedono conferma prima di cancellare definitivamente lo script su disco.

---

## 6. Automazioni integrate — guida passo-passo

Ogni strumento ha due azioni finali: **💾 Genera codice** (produce uno script `.py` standalone, salvabile con "⬇ Salva .py", eseguibile anche fuori dalla GUI con `NOTION_KEY` come variabile d'ambiente) e/o **▶ Esegui ora** (lancia l'automazione subito, in background, con log in tempo reale).

### 6.1 🧠 Sync DataSource

Copia/trasforma record da un data source sorgente a uno di destinazione.

**Passi**:
1. Assegna un nome all'automazione.
2. Sezione **Sorgente**: scegli il data source, imposta eventuali **filtri** (➕ Aggiungi filtro — colonna, operatore, valore; gli operatori disponibili dipendono dal tipo colonna, es. `Contiene`/`Inizia con` per testo, `=`/`>`/`<` per numeri) e **ordinamenti** (➕ Aggiungi ordinamento — colonna + crescente/decrescente).
3. Sezione **Destinazione**: scegli il data source target, poi nel **Mapping colonne** scegli per ogni colonna di destinazione quale colonna sorgente copiare (o "— Salta —" per ignorarla).
4. Genera codice e/o esegui. La console mostra output Python e log di esecuzione separati.

### 6.2 🗓️ Blocchi ripetuti

Crea in serie N pagine con la stessa struttura (settimane, sprint, checklist periodiche...).

**Passi**:
1. Scegli il **data source di destinazione** e la **proprietà titolo** da valorizzare.
2. Scegli la modalità di generazione titoli:
   - **Intervallo dinamico**: template titolo (es. `Settimana {index:02d}`), indice iniziale, numero di pagine.
   - **Lista titoli personalizzata**: un titolo per riga in una textarea.
3. Componi il **blueprint** dei blocchi con i pulsanti "＋ H1/H2/H3/Paragrafo/To-Do/Bullet/Numbered/Toggle/Divider/Callout/Breadcrumb/Quote/Tabella" — ogni blocco aggiunto è una riga modificabile (testo, checkbox completato per i To-Do, colonne/righe/intestazioni per le tabelle). Nel testo puoi usare i placeholder `{index}` e `{title}`.
4. Genera codice e/o esegui: crea le pagine e vi inserisce i blocchi del blueprint, sostituendo i placeholder per ogni pagina.

### 6.3 ☑️ Radio To-Do

Garantisce che **una sola** entry/checkbox resti spuntata, deselezionando automaticamente tutte le altre — utile per pattern "seleziona l'opzione attiva" in Notion.

**Due modalità** (pulsanti in alto):
- **🧩 DataSource**: scegli il data source e la proprietà checkbox da usare come "radio", poi seleziona (radio button) l'entry che deve restare spuntata.
- **📄 Pagina**: scegli una pagina dall'elenco, poi seleziona quale blocco `to_do` (tra tutti quelli trovati ricorsivamente nella pagina) deve restare spuntato.

Esegui: tutte le altre entry/checkbox vengono impostate a `False`.

### 6.4 🧹 Pulisci entries vecchie

Elimina automaticamente le entry di un data source più vecchie di X giorni.

**Passi**:
1. Scegli il **data source**.
2. Scegli la **proprietà data** da usare per il confronto (solo proprietà di tipo `date` compaiono nel dropdown — usa "↻ Ricarica schema" se il data source è stato appena connesso).
3. Imposta la **soglia in giorni**.
4. Esegui: le entry con data antecedente a `oggi − soglia` vengono spostate nel cestino Notion (non cancellate in modo permanente, sono recuperabili da Notion).

---

## 7. Automazioni personalizzate

Per logiche non coperte dai 4 strumenti integrati:

1. Dalla home "Flussi", clicca la tile **"+ Nuova automazione"**.
2. Compila: icona (emoji), nome, descrizione, colore tile (scegli tra i preset di gradiente).
3. Seleziona dalla checklist gli **oggetti libreria** che userai (es. `DataSourceFactory`, `PageFactory`, `NFactory` per i blocchi, `F`/`S` per filtri e ordinamenti, `UserFactory`, ricerca globale, utility rich-text). La selezione determina quali import e blocchi di codice-esempio commentato vengono generati nel template.
4. Conferma: viene creato uno script in una **cartella dati utente** (indipendente dalla directory da cui lanci `notion-gui`), con una classe Python pronta (metodo `run()` da completare), e viene aggiunta la tile alla home.
   - Windows: `%LOCALAPPDATA%\notion-lib\custom_automations\<slug>\script.py`
   - macOS: `~/Library/Application Support/notion-lib/custom_automations/<slug>/script.py`
   - Linux: `~/.local/share/notion-lib/custom_automations/<slug>/script.py`
   - Override: variabile d'ambiente `NOTION_LIB_DATA_DIR` (usa `<dir>/custom_automations`).
5. Nella vista dettaglio dell'automazione: **"📂 Apri con editor"** apre lo script con l'editor di testo predefinito del sistema per modificarlo; **"↑ Sostituisci script"** permette di rimpiazzarlo con un file `.py` esterno.
6. **"▶ Esegui ora"**: lo script viene eseguito come **subprocess Python isolato**, con la chiave API iniettata automaticamente come variabile d'ambiente `NOTION_KEY` — non serve inserirla manualmente nello script. Output e errori vengono mostrati in tempo reale nel log; **"⏹ Interrompi"** termina il processo.

---

## 8. Risoluzione problemi (FAQ)

**Un database/pagina non compare nella GUI dopo la connessione.**
→ In Notion, apri l'elemento → **···** → **Connetti a** → seleziona l'integrazione. Le integrazioni Notion vedono *solo* ciò a cui sono state esplicitamente connesse.

**"notion-gui" non riconosciuto da terminale (Windows).**
→ Aggiungi al PATH `C:\Users\<utente>\AppData\Roaming\Python\Python312\Scripts`, oppure esegui `pip install -e .` da PowerShell come amministratore (installa in una cartella già nel PATH di sistema).

**Lo schema di un data source resta su "in caricamento…".**
→ Attendi qualche secondo (caricato in background al primo utilizzo) o usa il pulsante "↻ Ricarica schema"/"↻ Ricarica" presente nei tool che lo richiedono.

**Un'automazione custom eliminata per errore.**
→ Non è recuperabile dalla GUI: lo script su disco viene cancellato in modo permanente dopo conferma. Tienine una copia se contiene logica importante.

**"Genera codice" produce uno script che non trovo dove eseguire.**
→ Va salvato esplicitamente con "⬇ Salva .py"; l'API key va poi fornita via variabile d'ambiente `NOTION_KEY` o inserita a prompt quando richiesta.

**Non vedo le automazioni custom dopo `notion-gui` da un'altra cartella.**
→ Le automazioni non stanno più nella cwd del progetto: vivono nella cartella dati utente (vedi §7). Se avevi una vecchia cartella `./custom_automations` nella directory corrente, al primo avvio viene migrata automaticamente nella nuova sede.

---

# Parte B — Per chi usa la libreria Python

## 9. Architettura del progetto

```
notion_lib/
├── pyproject.toml                  ← packaging (setuptools), entry point CLI
└── src/notion_lib/
    ├── __init__.py                 ← export pubblici di libreria
    ├── notion_gui.py               ← entry point GUI
    ├── client/                     ← autenticazione, HTTP, cache, errori, credenziali
    ├── nEndpoints/                 ← chiamate REST grezze (1:1 con API Notion)
    ├── nModels/                    ← wrapper OOP ad alto livello (Page, Database, DataSource, Block, User)
    │   └── blocks/                 ← una classe per ogni tipo di blocco Notion
    ├── nTypes/                     ← value object (rich text, date, file, icone, filtri, proprietà)
    ├── utils/                      ← costanti (Enum) e funzioni di utilità
    ├── gui/                        ← applicazione desktop PyQt6
    │   ├── widgets/automation_tools/  ← UI dei 4 tool integrati
    │   └── logic/                  ← business logic pura (riusata dai worker QThread)
    └── tests/                      ← unit test + script eseguibili manuali
```

**Layer, dal basso verso l'alto**: `client` (HTTP/auth) → `nEndpoints` (REST grezzo) → `nTypes` (value object) → `nModels` (oggetti stateful ad alto livello) → `gui` (consuma `nModels` tramite worker asincroni).

**Convenzione import obbligatoria**: sempre con prefisso `notion_lib.`:
```python
from notion_lib.nModels.blocks.paragraph import ParagraphBlock   # corretto
```

---

## 10. Autenticazione e livello HTTP

### `NotionApiClient`

```python
from notion_lib.client.auth import NotionApiClient
api = NotionApiClient(key="ntn_...", version="2025-09-03")  # version opzionale, default mostrato
```

`key` e `version` sono **immutabili** dopo l'init (`AttributeError` se riassegnati). `api.headers` espone il dict pronto per `requests`.

### Funzioni HTTP (`client/https.py`)

| Funzione | Metodo | Note |
|---|---|---|
| `NGET(url, header, params=None)` | GET | risposta cachata in memoria (LRU, per processo) |
| `NPOST(url, header, data, params=None)` | POST | invalida la cache GET prima della chiamata |
| `NPATCH(url, header, data)` | PATCH | invalida la cache GET prima della chiamata |
| `NDEL(url, header)` | DELETE | invalida la cache GET prima della chiamata |
| `invalidate_cache()` | — | svuota manualmente la cache |

Tutte restituiscono un oggetto con `.response` (dict JSON) e supporto `obj["chiave"]` per accesso diretto.

**Rate limit**: su HTTP 429, la libreria attende (`Retry-After` o 1s di default) e ritenta automaticamente — trasparente al chiamante.

### Errori

Gerarchia `NotionError` (in `client/errors.py`) con sottoclassi mappate sui codici Notion: `InvalidJsonError`, `InvalidRequestUrl`, `InvalidRequest`, `InvalidGrant`, `ValidationError`, `MissingVersion`, `Unauthorized`, `RestrictedResource`, `ObjectNotFound`, `ConflictError`, `RateLimited`, `InternalServerError`, `BadGateway`, `ServiceUnavailable`, `DatabaseConnectionUnavailable`, `GatewayTimeout`.

---

## 11. Pages, Databases, DataSources, Users

### Pages

Notion distingue pagine "libere" da pagine-riga di un data source. `PageFactory` sceglie automaticamente la classe corretta in base al parent:

```python
from notion_lib.nModels.pages import PageFactory
page = PageFactory.find(api.headers, "URL o ID Notion")
```

- **`SimplePage`** (parent = pagina/workspace/blocco): `.title` (get/set), `SimplePage.create(headers, parent_id, title, icon=None, cover=None)`.
- **`DatabasePage`** (parent = database/data source): `.properties` (dict tipizzato), `.prop("Nome")`, `.set_prop("Nome", valore)` (fluent), `.title()` (cerca la property titolo), `DatabasePage.create(headers, parent_db_id, properties, icon=None, cover=None)`.

Comuni a entrambe: `.icon`/`.cover` (get/set, persistiti al successivo `.update()`), `.url`, `.get_children()` → lista blocchi, `.append_children([...])`, `.update()`, `.trash()`/`.restore()`.

### Databases

Contenitore di uno o più data source:

```python
from notion_lib.nModels.databases import DatabaseFactory
db = DatabaseFactory.find(api.headers, db_id_o_url)

db.title, db.is_inline, db.is_locked   # get/set dove applicabile
db.datasources                          # list[NDataSource]
db.create_datasource(title, prop_schema={"select": "Categoria"})
db.move(new_parent_id); db.trash(); db.restore()
NDatabase.create(headers, title, parent_id, prop_schema=None, is_inline=True)
```

### DataSources

Contiene lo **schema** e le **entry** (righe):

```python
from notion_lib.nModels.datasources import DataSourceFactory
ds = DataSourceFactory.find(api.headers, ds_id)

ds.title; ds.schema; ds.parent_db_id
ds.templates; ds.default_template

ds.all_entries()                                 # tutte le righe (paginazione gestita)
ds.filter({"filter": F...})                       # vedi §14
ds.sort(S().get(("Nome", True)))
ds.query(filt=..., sorties=...)                   # combina filtro + sort

ds.add_property("select", "Categoria")
ds.rename_property("Categoria", "Category")
ds.remove_property("Category")

ds.create_entry(properties: dict, template_id=None, icon=None, cover=None)  # → DatabasePage
ds.update(title=None, prop_schema=None)
ds.move(new_parent_db_id); ds.trash(); ds.restore()
NDataSource.create(headers, title, parent_db_id, prop_schema=None)
```

### Users

```python
from notion_lib.nModels.user import UserFactory
user = UserFactory.create(api.headers, user_id)
```

Gerarchia: `NPerson` (+`.email`), `NBotUser`, `NBotWorkspace` (+`.workspace_name`, `.workspace_id`, `.workspace_limits`) — instanziata automaticamente in base al tipo restituito dall'API.

---

## 12. Blocchi — tabella completa

Punto di ingresso unico per leggere qualunque blocco:

```python
from notion_lib.nModels.blocks.base_block import NFactory
blk = NFactory.find(api.headers, block_id_o_url)
```

Tipi supportati (i tipi non elencati ricadono su `UnsupportedBlock`, sempre leggibile, mai creabile/aggiornabile):

| Tipo Notion | Creabile | Aggiornabile | Figli | Note |
|---|---|---|---|---|
| `paragraph` | ✅ | ✅ | ✅ | `.rich_text`, `.color` |
| `heading_1/2/3` | ✅ | ✅ | solo se `is_toggleable=True` | flag dinamico |
| `to_do` | ✅ | ✅ | ✅ | `.checked` |
| `toggle` | ✅ | ✅ | ✅ | |
| `bulleted_list_item` / `numbered_list_item` | ✅ | ✅ | ✅ | |
| `image` | ✅ | solo file esterno | ✅ | `.file_object`, `.caption` |
| `video` | ✅ (solo URL esterno) | solo se esterno | | `.url` |
| `audio` | ❌ | ❌ | | solo lettura |
| `file` / `pdf` | ✅ | solo se esterno | | `pdf` alias di `file` |
| `embed` | ✅ | ✅ | | `.url` |
| `table` | ✅ | ✅ (solo header flags) | ✅ | `.cell(r,c)`, indicizzazione `blk[r,c]` |
| `table_row` | ✅ | | ❌ | `.cell(col)` |
| `callout` | ✅ | ✅ | ✅ | `.icon`, `.color` |
| `code` | ✅ | ✅ | ❌ | `.language` (Enum `NLanguage`) |
| `synced_block` | ✅ | ❌ | ❌ | |
| `breadcrumb` | ✅ | ❌ | ❌ | |
| `child_page` / `child_database` | ✅ | ✅ | ✅ / ❌ | `.title` |
| `equation` | ✅ | ✅ | ❌ | `.expression` |
| `bookmark` | ✅ | ✅ | ❌ | `.url`, `.caption` |
| `link_to_page` | ❌ | ❌ | ❌ | solo lettura, `.target_type`/`.target_id` |
| `column_list` / `column` | ✅ | | ✅ | `ColumnListBlock.create_with_columns(n, parent)` (max 10) |
| `divider` | ✅ | ❌ | ❌ | |
| `quote` | ✅ | ✅ | ✅ | `.children`, `.add_child()`, `.remove_child_at()`, `.update_child()` |
| `table_of_contents` | ✅ | ✅ | ❌ | `.color` |
| `link_preview` | ❌ | ❌ | ❌ | solo lettura |
| `meeting_notes` / `transcription` | ❌ | ❌ | ✅ | solo lettura; `.status`, `.is_ready`, `.attendees`, `.get_summary()/.get_notes()/.get_transcript()` |

Metodi comuni a ogni blocco: `.update()`, `.delete()`, `.get_children()` (se `supports_children`), `.append_children([...])`.

---

## 13. Tipi di supporto

| Tipo | Ruolo |
|---|---|
| `NDate` | parsing/serializzazione ISO 8601 (`2025-01-15T10:00:00.000Z`) |
| `NRichText` / `NRichList` | modellano il rich text Notion; `simple_rich_text_list("stringa")` per crearne uno da testo Python semplice |
| `n_file(data)` | factory: `FileTypeExternal` / `FileTypeFile` (con `.expiry_time`) / `FileTypeUploaded` |
| `IconFactory` / `NEmoji` / `NIcon` / `NCustomEmoji` | routing icona pagina/blocco |
| `PropertyFactory` | routing proprietà pagina database verso la sottoclasse tipizzata corretta |

**Proprietà scrivibili**: `title`, `rich_text`, `number`, `checkbox`, `select`, `multi_select`, `status`, `date`, `url`, `email`, `phone_number`, `relation`, `people`.
**Proprietà read-only**: `files`, `formula`, `rollup`, `unique_id`, `created_time`, `last_edited_time`, `created_by`, `last_edited_by`, `verification`, `button`, `location`, `place`, `last_visited_time`.

`DatabasePage.to_payload()` scarta automaticamente le proprietà read-only, quindi `.update()` è sicuro anche su pagine con colonne calcolate.

---

## 14. Filtri e ordinamenti

```python
from notion_lib.nTypes.ds_filters import F, S

ds.filter({"filter": F.checkbox("Done").equals(True)})

ds.filter({"filter": F.and_(
    F.checkbox("Done").equals(True),
    F.or_(
        F.multi_select("Tags").contains("Urgente"),
        F.multi_select("Tags").contains("Bloccante"),
    )
)})

ds.sort(S().get(("Nome", True), ("created_time", False)))  # (colonna, ascending)
```

`F` espone un factory per tipo proprietà: `.checkbox()`, `.number()`, `.date()`, `.rich_text()`, `.multi_select()`, `.select()`, `.status()`, `.people()`, `.relation()`, `.rollup()`, `.files()`, `.notion_id()`, `.timestamp("created_time"|"last_edited_time")`, `.verification()`, con operatori specifici per tipo (`.equals`, `.contains`, `.is_empty`, `.after`, `.greater_than`, ...).

---

## 15. Gestione errori e rate limit

Ogni chiamata HTTP fallita solleva un'eccezione `NotionError` (o sottoclasse) con messaggio `"{Sessione} -> [{status}] {Codice}: {messaggio}"`. Status 429 → retry automatico con backoff da header `Retry-After`. `check_url_or_id()` valida/estrae ID Notion da URL o stringa, sollevando `ValueError` su input non riconoscibile.

---

## 16. Testing

```bash
python -m pytest tests/test_all.py -v
```

Copertura: `utils`, `client.auth`, `client.https` (HTTP mockato), tutti i `nTypes`, tutti i tipi di blocco in `nModels.blocks`, `nModels.pages` (routing `PageFactory`), `nModels.databases`, `nModels.datasources`, `nModels.user` (routing `UserFactory`).

`tests/examples.py` contiene 20 funzioni `example_*()` eseguibili singolarmente contro un'**API Notion reale** — richiede una chiave valida e ID di pagine/blocchi/database esistenti nel proprio workspace (i placeholder nel file vanno sostituiti con i propri ID prima dell'uso).

---

## 17. Estendere il progetto

### Aggiungere un nuovo tipo di blocco
1. Creare la classe in `nModels/blocks/`, ereditando `BlockImpl`; implementare `from_data`, `create`, `to_payload`.
2. Decorare con `@register_block("tipo_notion")`.
3. Aggiungere l'import del modulo in `_ensure_registry_populated()` (`base_block.py`) — altrimenti la classe non verrà mai caricata (registrazione lazy).

### Aggiungere un comando CLI

1. Creare un file con funzione `main()`:
   ```python
   # src/notion_lib/automazioni/sync.py
   def main():
       ...
   if __name__ == "__main__":
       main()
   ```
2. Dichiararlo in `pyproject.toml`:
   ```toml
   [project.scripts]
   notion-sync = "notion_lib.automazioni.sync:main"
   ```
3. Reinstallare: `pip install -e .` (obbligatorio dopo ogni modifica a `[project.scripts]`).

Convenzione: nome comando con trattino (`notion-sync`), nome modulo con underscore (`sync.py`).

---

## 18. Cheatsheet import rapidi

```python
from notion_lib import (
    NotionApiClient,
    PageFactory, SimplePage, DatabasePage,
    DatabaseFactory, NDatabase,
    DataSourceFactory, NDataSource,
    NFactory,          # blocchi
    UserFactory,
    F, S,               # filtri/sort
)

api = NotionApiClient(key="ntn_...")

page = PageFactory.find(api.headers, "URL o ID Notion")

ds = DataSourceFactory.find(api.headers, ds_id)
entries = ds.query(
    filt={"filter": F.checkbox("Done").equals(True)},
    sorties=S().get(("Nome", True)),
)

blk = NFactory.find(api.headers, block_id)
blk.rich_text = "nuovo testo"
blk.update()
```
