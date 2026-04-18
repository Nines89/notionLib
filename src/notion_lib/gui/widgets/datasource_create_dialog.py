"""
gui/widgets/datasource_create_dialog.py
Dialog per creare un nuovo DataSource con schema personalizzato.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox,
    QWidget, QGroupBox, QScrollArea, QMessageBox,
)
from PyQt6.QtCore import Qt

notion_lib.utils.constants import DbFieldType


class PropertyRow:
    """Rappresenta una proprietà del datasource."""

    def __init__(self, name: str, prop_type: str):
        self.name = name
        self.prop_type = prop_type


class PropertyRowWidget(QWidget):
    """Widget per una singola proprietà (nome + tipo + rimuovi)."""

    def __init__(self, row: PropertyRow, on_remove, parent=None):
        super().__init__(parent)
        self._row = row
        self._on_remove = on_remove
        self._build_ui()

    def _build_ui(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(8, 6, 8, 6)
        lay.setSpacing(12)

        # Nome proprietà
        self._name_input = QLineEdit(self._row.name)
        self._name_input.setPlaceholderText("Nome proprietà...")
        self._name_input.setMinimumWidth(180)
        self._name_input.setFixedHeight(32)
        self._name_input.textChanged.connect(lambda t: setattr(self._row, "name", t.strip()))

        # Tipo proprietà
        self._type_combo = QComboBox()
        self._type_combo.setMinimumWidth(150)
        self._type_combo.setFixedHeight(32)

        # Aggiungi tipi scrivibili (escludi read-only)
        writable_types = [
            ("📝 Testo", DbFieldType.RICH_TEXT.value),
            ("🔢 Numero", DbFieldType.NUMBER.value),
            ("☑ Checkbox", DbFieldType.CHECKBOX.value),
            ("🏷 Select", DbFieldType.SELECT.value),
            ("🏷🏷 Multi-select", DbFieldType.MULTI_SELECT.value),
            ("📊 Status", DbFieldType.STATUS.value),
            ("📅 Data", DbFieldType.DATE.value),
            ("🔗 URL", DbFieldType.URL.value),
            ("📧 Email", DbFieldType.EMAIL.value),
            ("📞 Telefono", DbFieldType.PHONE_NUMBER.value),
            ("👥 Persone", DbFieldType.PEOPLE.value),
            ("🔗 Relazione", DbFieldType.RELATION.value),
            ("📎 File", DbFieldType.FILES.value),
        ]

        for label, value in writable_types:
            self._type_combo.addItem(label, value)

        # Imposta valore corrente
        for i in range(self._type_combo.count()):
            if self._type_combo.itemData(i) == self._row.prop_type:
                self._type_combo.setCurrentIndex(i)
                break

        self._type_combo.currentIndexChanged.connect(
            lambda: setattr(self._row, "prop_type", self._type_combo.currentData())
        )

        # Badge tipo
        self._type_badge = QLabel()
        self._type_badge.setFixedWidth(100)
        self._type_badge.setFixedHeight(24)
        self._type_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._type_badge.setStyleSheet(
            "background: #F0EFEC; border: 1px solid #E3E2DE; "
            "border-radius: 4px; color: #787774; font-size: 10px; "
            "font-weight: 600;"
        )
        self._update_badge()
        self._type_combo.currentIndexChanged.connect(self._update_badge)

        # Pulsante rimozione
        remove_btn = QPushButton("✕")
        remove_btn.setObjectName("RemoveBtn")
        remove_btn.setFixedSize(30, 30)
        remove_btn.clicked.connect(self._on_remove)

        lay.addWidget(self._name_input)
        lay.addWidget(self._type_combo)
        lay.addWidget(self._type_badge)
        lay.addWidget(remove_btn)
        lay.addStretch()

    def _update_badge(self):
        self._type_badge.setText(self._type_combo.currentData().upper())

    def get_row(self) -> PropertyRow:
        return self._row


class DataSourceCreateDialog(QDialog):
    """
    Dialog per creare un DataSource con schema personalizzato.
    """

    def __init__(self, db_id: str, db_title: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Nuovo DataSource in: {db_title}")
        self.resize(750, 550)
        self._db_id = db_id
        self._db_title = db_title
        self._prop_rows: list[PropertyRowWidget] = []
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setSpacing(16)
        lay.setContentsMargins(24, 20, 24, 20)

        # ── Intestazione ──────────────────────────────────────────
        header = QLabel("Crea nuovo DataSource")
        header.setStyleSheet("font-size: 18px; font-weight: 700;")
        lay.addWidget(header)

        subtitle = QLabel(f"Database parent: {self._db_title}")
        subtitle.setStyleSheet("color: #787774; font-size: 12px;")
        lay.addWidget(subtitle)

        # ── Nome datasource ───────────────────────────────────────
        name_box = QGroupBox("Nome DataSource")
        nb_lay = QVBoxLayout(name_box)
        nb_lay.setSpacing(8)

        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("Es: Clienti 2024, Tasks Q1, Inventario...")
        self._name_input.setFixedHeight(36)
        nb_lay.addWidget(self._name_input)
        lay.addWidget(name_box)

        # ── Schema proprietà ──────────────────────────────────────
        schema_box = QGroupBox("Schema (proprietà)")
        sb_lay = QVBoxLayout(schema_box)
        sb_lay.setSpacing(12)

        hint = QLabel(
            "💡 Definisci le colonne del datasource. La proprietà 'Name' (title) "
            "viene aggiunta automaticamente."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #787774; font-size: 11px;")
        sb_lay.addWidget(hint)

        # Scroll per proprietà
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(240)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        self._container = QWidget()
        self._props_lay = QVBoxLayout(self._container)
        self._props_lay.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._props_lay.setSpacing(6)
        self._props_lay.setContentsMargins(0, 0, 0, 0)
        scroll.setWidget(self._container)
        sb_lay.addWidget(scroll)

        # Pulsante aggiungi proprietà
        add_btn = QPushButton("➕ Aggiungi proprietà")
        add_btn.setFixedHeight(34)
        add_btn.clicked.connect(self._add_property)
        sb_lay.addWidget(add_btn)

        lay.addWidget(schema_box)

        # ── Pulsanti azione ───────────────────────────────────────
        btn_row = QWidget()
        br_lay = QHBoxLayout(btn_row)
        br_lay.setContentsMargins(0, 0, 0, 0)
        br_lay.setSpacing(10)

        cancel_btn = QPushButton("Annulla")
        cancel_btn.clicked.connect(self.reject)

        self._create_btn = QPushButton("✓ Crea DataSource")
        self._create_btn.setObjectName("PrimaryBtn")
        self._create_btn.setDefault(True)
        self._create_btn.clicked.connect(self._on_create)

        br_lay.addStretch()
        br_lay.addWidget(cancel_btn)
        br_lay.addWidget(self._create_btn)

        lay.addWidget(btn_row)

        # Aggiungi una proprietà di esempio
        self._add_property()

    def _add_property(self):
        """Aggiunge una nuova riga proprietà."""
        row = PropertyRow(name="", prop_type=DbFieldType.RICH_TEXT.value)
        widget = PropertyRowWidget(row, on_remove=lambda w=None: self._remove_property(widget))
        self._prop_rows.append(widget)
        self._props_lay.addWidget(widget)

    def _remove_property(self, widget: PropertyRowWidget):
        """Rimuove una proprietà."""
        if widget in self._prop_rows:
            self._prop_rows.remove(widget)
        widget.setParent(None)
        widget.deleteLater()

    def _on_create(self):
        """Valida e accetta il dialog."""
        name = self._name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Nome mancante", "Inserisci il nome del datasource.")
            return

        # Valida proprietà
        props = []
        for widget in self._prop_rows:
            row = widget.get_row()
            if not row.name:
                QMessageBox.warning(
                    self, "Proprietà incompleta",
                    "Tutte le proprietà devono avere un nome."
                )
                return
            props.append(row)

        # Controlla duplicati
        names = [p.name for p in props]
        if len(names) != len(set(names)):
            QMessageBox.warning(
                self, "Nomi duplicati",
                "Non puoi avere due proprietà con lo stesso nome."
            )
            return

        self.accept()

    def get_config(self) -> dict:
        """Restituisce la configurazione del datasource."""
        props = {}
        for widget in self._prop_rows:
            row = widget.get_row()
            if row.name and row.prop_type:
                props[row.prop_type] = row.name

        return {
            "db_id": self._db_id,
            "name": self._name_input.text().strip(),
            "prop_schema": props,
        }