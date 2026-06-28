from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget,QVBoxLayout,QLabel,QLineEdit,QComboBox,QScrollArea,QPushButton,QTextEdit,QHBoxLayout,QFileDialog
from .styles import STYLESHEET,_SectionCard,cp_ds_sections

class PruneOldEntriesTool(QWidget):
    schema_needed = pyqtSignal(str)
    generate_requested = pyqtSignal(dict)
    run_requested = pyqtSignal(dict)

    def __init__(self,parent=None):
        super().__init__(parent)
        self._schemas = {}
        self.setStyleSheet(STYLESHEET)
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self); outer.setContentsMargins(0,0,0,0)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        content = QWidget(); lay = QVBoxLayout(content); lay.setContentsMargins(40,40,40,40); lay.setSpacing(28)

        name_card = _SectionCard("🧹","Nome Automazione")
        self._name_input = QLineEdit("Pulisci entries vecchie")
        self._name_input.setMinimumHeight(44)
        name_card.add_content(self._name_input); lay.addWidget(name_card)

        cfg = _SectionCard("⚙️","Configurazione cleanup")
        self._ds_combo = QComboBox(); self._ds_combo.setMinimumHeight(44); self._ds_combo.currentIndexChanged.connect(self._on_ds_changed)
        self._date_prop_combo = QComboBox(); self._date_prop_combo.setMinimumHeight(44); self._date_prop_combo.currentIndexChanged.connect(self._refresh_btns)
        self._days_input = QLineEdit("30"); self._days_input.setMinimumHeight(44); self._days_input.textChanged.connect(self._refresh_btns)
        self._schema_lbl = QLabel("Schema: —"); self._schema_lbl.setStyleSheet(cp_ds_sections)
        self._preview_lbl = QLabel("Elimina entries più vecchie di: — giorni"); self._preview_lbl.setStyleSheet("color: #94A3B8; font-size: 12px;")

        reload_row = QWidget(); rr = QHBoxLayout(reload_row); rr.setContentsMargins(0,0,0,0)
        self._reload_btn = QPushButton("↻ Ricarica schema"); self._reload_btn.setObjectName("SecondaryBtn"); self._reload_btn.clicked.connect(self._reload_schema)
        rr.addStretch(); rr.addWidget(self._reload_btn)

        cfg.add_content(QLabel("DataSource:")); cfg.add_content(self._ds_combo)
        cfg.add_content(self._schema_lbl)
        cfg.add_content(QLabel("Proprietà data da usare per il confronto:")); cfg.add_content(self._date_prop_combo)
        cfg.add_content(QLabel("Soglia (giorni):")); cfg.add_content(self._days_input)
        cfg.add_content(self._preview_lbl)
        cfg.add_content(reload_row)
        lay.addWidget(cfg)

        action = _SectionCard("🚀","Esecuzione")
        row = QWidget(); rl = QHBoxLayout(row); rl.setContentsMargins(0,0,0,0)
        self._gen_btn = QPushButton("💾 Genera codice"); self._gen_btn.setObjectName("SecondaryBtn"); self._gen_btn.setMinimumHeight(50); self._gen_btn.setEnabled(False)
        self._run_btn = QPushButton("🗑️ Elimina entries"); self._run_btn.setObjectName("PrimaryBtn"); self._run_btn.setMinimumHeight(50); self._run_btn.setEnabled(False)
        self._gen_btn.clicked.connect(lambda: self.generate_requested.emit(self.get_config()))
        self._run_btn.clicked.connect(lambda: self.run_requested.emit(self.get_config()))
        rl.addWidget(self._gen_btn); rl.addWidget(self._run_btn); action.add_content(row); lay.addWidget(action)

        code = _SectionCard("</>","Codice generato")
        self._code_edit = QTextEdit(); self._code_edit.setMinimumHeight(220)
        self._save_btn = QPushButton("⬇ Salva .py"); self._save_btn.setObjectName("SecondaryBtn"); self._save_btn.setEnabled(False); self._save_btn.clicked.connect(self._on_save)
        code.add_content(self._code_edit); code.add_content(self._save_btn); lay.addWidget(code)

        log = _SectionCard("📋","Log")
        self._log_edit = QTextEdit(); self._log_edit.setReadOnly(True); self._log_edit.setMinimumHeight(180)
        log.add_content(self._log_edit); lay.addWidget(log)
        lay.addStretch(); scroll.setWidget(content); outer.addWidget(scroll)

    def populate_datasources(self,datasources:list):
        self._ds_combo.blockSignals(True); self._ds_combo.clear()
        for ds in datasources:
            self._ds_combo.addItem(f"{ds['name']}  [{ds['db_title']}]", ds['id'])
        self._ds_combo.blockSignals(False); self._on_ds_changed()

    def update_schema(self, ds_id:str, schema:dict):
        self._schemas[ds_id.replace('-','')] = schema
        if (self._ds_combo.currentData() or '').replace('-','') == ds_id.replace('-',''):
            self._refresh_schema_ui(); self._refresh_btns()

    def show_log(self, lines:list): self._log_edit.setPlainText("\n".join(lines))
    def set_code(self, code:str): self._code_edit.setPlainText(code); self._save_btn.setEnabled(bool(code))
    def set_running(self, running:bool): self._run_btn.setEnabled(not running); self._run_btn.setText("⏳ Eliminazione..." if running else "🗑️ Elimina entries")
    def selected_target_label(self)->str: return self._ds_combo.currentText().strip() or "—"
    def get_config(self)->dict:
        return {"name": self._name_input.text().strip() or "Pulisci entries vecchie", "ds_id": self._ds_combo.currentData(), "date_prop": self._date_prop_combo.currentData(), "days": self._days_input.text().strip()}

    def _reload_schema(self):
        ds = self._ds_combo.currentData();
        if ds: self.schema_needed.emit(ds)
    def _on_ds_changed(self): self._refresh_schema_ui(); self._reload_schema(); self._refresh_btns()
    def _refresh_schema_ui(self):
        self._date_prop_combo.blockSignals(True); self._date_prop_combo.clear()
        ds = (self._ds_combo.currentData() or '').replace('-','')
        schema = self._schemas.get(ds)
        if not schema:
            self._schema_lbl.setText("Schema: in caricamento…")
        else:
            c=0
            for name,meta in schema.items():
                if meta.get('type') == 'date': self._date_prop_combo.addItem(f"📅 {name}", name); c+=1
            self._schema_lbl.setText(f"Schema: {len(schema)} proprietà · {c} date")
        self._date_prop_combo.blockSignals(False)

    def _refresh_btns(self):
        ok_days = self._days_input.text().strip().isdigit() and int(self._days_input.text().strip()) > 0
        if ok_days: self._preview_lbl.setText(f"Elimina entries più vecchie di: {int(self._days_input.text().strip())} giorni")
        else: self._preview_lbl.setText("Elimina entries più vecchie di: — giorni")
        ready = bool(self._ds_combo.currentData()) and bool(self._date_prop_combo.currentData()) and ok_days
        self._gen_btn.setEnabled(ready); self._run_btn.setEnabled(ready)

    def _on_save(self):
        path,_ = QFileDialog.getSaveFileName(self,"Salva script",f"{self._name_input.text().strip().replace(' ','_').lower()}.py","Python (*.py)")
        if path:
            with open(path,'w',encoding='utf-8') as f: f.write(self._code_edit.toPlainText())
