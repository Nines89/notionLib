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

## Come si usa

| Tab | Cosa fa |
|-----|---------|
| 🔍 Workspace | Mostra tutti i database e datasource accessibili |
| ⚙️ Configura | Configura nome, sorgente, filtri, ordinamento, destinazione, mapping colonne |
| ▶️ Esegui | Mostra il codice generato, permette di salvarlo e di eseguire l'automazione |

### Flusso tipico

1. Inserisci la chiave API → **Connetti**
2. Vai in **⚙️ Configura**
3. Scegli il datasource sorgente (dove leggere i dati)
4. Aggiungi filtri/ordinamenti se vuoi selezionare solo alcune righe
5. Scegli il datasource destinazione (dove scrivere)
6. Mappa le colonne: per ogni colonna della destinazione scegli quale colonna sorgente copiare
7. Clicca **💾 Genera codice**
8. Nel tab **▶️ Esegui**: controlla il codice, poi clicca **▶️ Esegui automazione**

Il file `.py` scaricato è una classe Python autonoma che un programmatore può
modificare per aggiungere logica più complessa.

---

## Struttura del progetto

```
notion_gui.py          ← entry point
avvia.bat              ← avvio rapido Windows
requirements.txt
gui/
├── constants.py       ← filtri, operatori, tipi
├── state.py           ← stato globale (AppState)
├── workers.py         ← thread background per chiamate API
├── app.py             ← MainWindow
├── logic/
│   ├── connector.py   ← connessione e caricamento workspace
│   ├── runner.py      ← esecuzione automazione
│   └── codegen.py     ← generazione codice Python
└── widgets/
    ├── sidebar.py         ← login / stato connesso
    ├── workspace_tab.py   ← tab Workspace
    ├── filter_editor.py   ← editor filtri
    ├── sort_editor.py     ← editor ordinamenti
    ├── mapping_editor.py  ← editor mapping colonne
    ├── config_tab.py      ← tab Configura
    └── run_tab.py         ← tab Esegui
```

---

## Debug

Ogni file ha un compito unico — se qualcosa non funziona:

| Problema | File da guardare |
|----------|-----------------|
| Connessione fallisce | `gui/logic/connector.py` |
| Filtri non corretti | `gui/logic/runner.py` → `build_filter()` |
| Codice generato sbagliato | `gui/logic/codegen.py` |
| UI filtri non risponde | `gui/widgets/filter_editor.py` |
| Esecuzione non scrive | `gui/logic/runner.py` → `run_automation()` |
