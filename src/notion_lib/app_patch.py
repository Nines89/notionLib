"""
PATCH — gui/app.py

Sezioni da aggiungere/modificare in MainWindow.

─────────────────────────────────────────────────────────────────────
ISTRUZIONI DI INTEGRAZIONE
─────────────────────────────────────────────────────────────────────

1. IMPORT da aggiungere in cima al file:
   ─────────────────────────────────────
   from notion_lib.gui.logic.custom_automation_manager import CustomAutomationManager
   from notion_lib.gui.widgets.custom_automation_dialog import CustomAutomationDialog
   from notion_lib.gui.widgets.automation_tools.custom_tool import CustomAutomationTool

2. In MainWindow.__init__, aggiungere PRIMA di _build_ui():
   ─────────────────────────────────────────────────────────
   self._custom_manager = CustomAutomationManager()
   self._custom_tools: dict[str, CustomAutomationTool] = {}

3. In MainWindow._build_ui(), DOPO la registrazione dei tool esistenti
   (dopo self._radio_todo_tool):
   ─────────────────────────────────────────────────────────────────
   # Collega il tasto + della home
   self._auto_tab.set_add_custom_callback(self._on_add_custom_requested)

   # Carica le automazioni custom salvate
   self._load_custom_automations()

4. Aggiungere i metodi qui sotto a MainWindow.

5. In _on_connect_ok, aggiungere dopo le righe esistenti:
   ─────────────────────────────────────────────────────────────────
   # Propaga la api key a tutti i custom tool già registrati
   for tool in self._custom_tools.values():
       tool.set_api_key(api.key)
─────────────────────────────────────────────────────────────────────
"""

NEW_METHODS = '''
    # ══════════════════════════════════════════════════════════════
    # Custom Automations
    # ══════════════════════════════════════════════════════════════

    def _load_custom_automations(self):
        """Carica dal manifest e registra tutte le automazioni custom salvate."""
        for entry in self._custom_manager.load_all():
            self._register_custom_entry(entry)

    def _register_custom_entry(self, entry: dict):
        """
        Crea il CustomAutomationTool, lo registra nel tab e lo salva
        in self._custom_tools per propagare la api_key in seguito.
        """
        tool = CustomAutomationTool(
            slug=entry["slug"],
            name=entry["name"],
            script_path=entry["script_path"],
        )

        # Se l'utente è già connesso, inietta subito la chiave
        state = get_state()
        if state.api:
            tool.set_api_key(state.api.key)

        self._custom_tools[entry["slug"]] = tool

        self._auto_tab.register_custom_tool(
            slug=entry["slug"],
            icon=entry["icon"],
            title=entry["name"],
            description=entry["description"] or "Automazione personalizzata",
            gradient_start=entry["gradient_start"],
            gradient_end=entry["gradient_end"],
            tool_widget=tool,
        )

    def _on_add_custom_requested(self):
        """Apre il dialog di creazione e, se confermato, registra la nuova automazione."""
        dialog = CustomAutomationDialog(parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        cfg = dialog.get_config()
        try:
            entry = self._custom_manager.save(
                name=cfg["name"],
                icon=cfg["icon"],
                description=cfg["description"],
                gradient_start=cfg["gradient_start"],
                gradient_end=cfg["gradient_end"],
                selected_objects=cfg["selected_objects"],
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Errore",
                f"Impossibile salvare l\'automazione:\\n{e}"
            )
            return

        self._register_custom_entry(entry)
        self._status.showMessage(
            f"Automazione \'{cfg['name']}\' creata. "
            f"Script: {entry['script_path']}"
        )
        QMessageBox.information(
            self,
            "Automazione creata",
            f"✓  \'{cfg['name']}\' è stata aggiunta alla home.\\n\\n"
            f"Il template si trova in:\\n{entry['script_path']}\\n\\n"
            f"Aprilo con \'Apri con editor\' dentro la tile per modificarlo.",
        )
'''
