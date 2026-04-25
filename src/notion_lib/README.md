# Notion Automation GUI

Interfaccia grafica desktop per configurare ed eseguire automazioni Notion
**senza scrivere codice**.

---

## Installazione (una sola volta)

1. Assicurati di avere **Python 3.11+** installato
2. Apri il terminale nella cartella del progetto
3. Installa le dipendenze:
   ```
   pip install -r requirements.txt
   ```

---

## Avvio

**Windows** — doppio clic su `avvia.bat`

**Qualsiasi sistema**:
```
python notion_gui.py
```

---

## Prima configurazione Notion

1. Vai su [notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Crea una nuova integrazione → copia il **Token segreto**
3. In Notion: per ogni database che vuoi usare, apri il menu **···** → **Connetti a** → seleziona la tua integrazione

---

---
## 🔐 Gestione credenziali

Le chiavi API vengono salvate nel **vault nativo del sistema operativo** tramite la libreria `keyring`:

| Sistema operativo | Backend |
|---|---|
| Windows | Gestione credenziali (Credential Manager) |
| macOS | Keychain |
| Linux | GNOME Keyring / KWallet |

Le chiavi non vengono mai scritte in chiaro su disco.

---

## Prerequisiti

```bash
pip install keyring
```

---

## Aggiungere una credenziale

**Dalla GUI:** compila i campi **Nome profilo** e **Token API**, poi clicca 💾.

**Da terminale:**

```python
import keyring
keyring.set_password('NotionAutomation', 'nome_profilo', 'ntn_...')
```

| Parametro | Valore | Note |
|---|---|---|
| `'NotionAutomation'` | fisso | identificatore dell'app, non modificare |
| `'nome_profilo'` | libero | es. `'Workspace personale'` |
| `'ntn_...'` | il tuo token | copialo da [notion.so/my-integrations](https://notion.so/my-integrations) |

---

## Rimuovere una credenziale

**Dalla GUI:** seleziona il profilo nel dropdown e clicca 🗑.

**Da terminale:**

```python
import keyring
keyring.delete_password('NotionAutomation', 'nome_profilo')
```

---

## Verificare che la credenziale sia stata salvata

```python
import keyring
print(keyring.get_password('NotionAutomation', 'nome_profilo'))
```

> Deve stampare il token. Se restituisce `None`, il profilo non esiste.




---
