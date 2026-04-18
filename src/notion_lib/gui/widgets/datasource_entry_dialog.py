"""
gui/widgets/datasource_entry_dialog.py
Dialog per creare una nuova entry in un DataSource.
Genera form dinamico basato sullo schema.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QWidget, QGroupBox, QCheckBox,
    QComboBox, QDoubleSpinBox, QDateEdit, QTextEdit, QListWidget,
    QMessageBox, QListWidgetItem,
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from datetime import datetime


class PropertyInputWidget(QWidget):
    """Base class per widget di input di una proprietà."""

    def __init__(self, prop_name: str, prop_type: str, prop_config: dict):
        super().__init__()
        self.prop_name = prop_name
        self.prop_type = prop_type
        self.prop_config = prop_config

    def get_value(self):
        """Restituisce il valore nel formato corretto per l'API Notion."""
        raise NotImplementedError

    def is_valid(self) -> tuple[bool, str]:
        """Restituisce (valido, messaggio_errore)."""
        return True, ""


class TitleInput(PropertyInputWidget):
    def __init__(self, prop_name: str, prop_type: str, prop_config: dict):
        super().__init__(prop_name, prop_type, prop_config)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Inserisci il titolo...")
        self.input.setFixedHeight(36)
        lay.addWidget(self.input)

    def get_value(self):
        text = self.input.text().strip()
        return {"title": [{"text": {"content": text}}]} if text else None

    def is_valid(self):
        if not self.input.text().strip():
            return False, "Il titolo non può essere vuoto"
        return True, ""


class RichTextInput(PropertyInputWidget):
    def __init__(self, prop_name: str, prop_type: str, prop_config: dict):
        super().__init__(prop_name, prop_type, prop_config)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)

        self.input = QTextEdit()
        self.input.setPlaceholderText("Inserisci testo...")
        self.input.setMaximumHeight(80)
        lay.addWidget(self.input)

    def get_value(self):
        text = self.input.toPlainText().strip()
        return {"rich_text": [{"text": {"content": text}}]} if text else None


class NumberInput(PropertyInputWidget):
    def __init__(self, prop_name: str, prop_type: str, prop_config: dict):
        super().__init__(prop_name, prop_type, prop_config)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)

        self.input = QDoubleSpinBox()
        self.input.setRange(-999999999, 999999999)
        self.input.setDecimals(2)
        self.input.setValue(0)
        self.input.setFixedHeight(36)
        lay.addWidget(self.input)

    def get_value(self):
        return {"number": self.input.value()}


class CheckboxInput(PropertyInputWidget):
    def __init__(self, prop_name: str, prop_type: str, prop_config: dict):
        super().__init__(prop_name, prop_type, prop_config)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        self.checkbox = QCheckBox("Spuntato")
        lay.addWidget(self.checkbox)

    def get_value(self):
        return {"checkbox": self.checkbox.isChecked()}


class SelectInput(PropertyInputWidget):
    def __init__(self, prop_name: str, prop_type: str, prop_config: dict):
        super().__init__(prop_name, prop_type, prop_config)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)

        self.combo = QComboBox()
        self.combo.setFixedHeight(36)
        self.combo.addItem("— Nessuna selezione —", None)

        # Estrai opzioni dallo schema
        options = prop_config.get("select", {}).get("options", [])
        for opt in options:
            name = opt.get("name", "")
            if name:
                self.combo.addItem(name, name)

        lay.addWidget(self.combo)

    def get_value(self):
        val = self.combo.currentData()
        return {"select": {"name": val} if val else None}


class MultiSelectInput(PropertyInputWidget):
    def __init__(self, prop_name: str, prop_type: str, prop_config: dict):
        super().__init__(prop_name, prop_type, prop_config)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)

        self.list = QListWidget()
        self.list.setMaximumHeight(100)
        self.list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)

        # Estrai opzioni dallo schema
        options = prop_config.get("multi_select", {}).get("options", [])
        for opt in options:
            name = opt.get("name", "")
            if name:
                item = QListWidgetItem(name)
                item.setData(Qt.ItemDataRole.UserRole, name)
                self.list.addItem(item)

        hint = QLabel("Ctrl+Click per selezione multipla")
        hint.setStyleSheet("color: #787774; font-size: 10px; font-style: italic;")

        lay.addWidget(self.list)
        lay.addWidget(hint)

    def get_value(self):
        selected = [
            item.data(Qt.ItemDataRole.UserRole)
            for item in self.list.selectedItems()
        ]
        return {"multi_select": [{"name": s} for s in selected]}


class StatusInput(PropertyInputWidget):
    def __init__(self, prop_name: str, prop_type: str, prop_config: dict):
        super().__init__(prop_name, prop_type, prop_config)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)

        self.combo = QComboBox()
        self.combo.setFixedHeight(36)

        # Estrai opzioni dallo schema
        options = prop_config.get("status", {}).get("options", [])
        for opt in options:
            name = opt.get("name", "")
            if name:
                self.combo.addItem(name, name)

        # Seleziona il primo di default se presente
        if self.combo.count() > 0:
            self.combo.setCurrentIndex(0)

        lay.addWidget(self.combo)

    def get_value(self):
        val = self.combo.currentData()
        return {"status": {"name": val} if val else None}


class DateInput(PropertyInputWidget):
    def __init__(self, prop_name: str, prop_type: str, prop_config: dict):
        super().__init__(prop_name, prop_type, prop_config)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)

        row = QWidget()
        row_lay = QHBoxLayout(row)
        row_lay.setContentsMargins(0, 0, 0, 0)
        row_lay.setSpacing(8)

        self.enabled = QCheckBox("Data:")
        self.enabled.setChecked(True)
        self.enabled.toggled.connect(self._on_toggle)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setFixedHeight(36)

        row_lay.addWidget(self.enabled)
        row_lay.addWidget(self.date_input)
        row_lay.addStretch()

        lay.addWidget(row)

    def _on_toggle(self, checked: bool):
        self.date_input.setEnabled(checked)

    def get_value(self):
        if not self.enabled.isChecked():
            return {"date": None}

        date = self.date_input.date().toPyDate()
        return {"date": {"start": date.isoformat()}}


class URLInput(PropertyInputWidget):
    def __init__(self, prop_name: str, prop_type: str, prop_config: dict):
        super().__init__(prop_name, prop_type, prop_config)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        self.input = QLineEdit()
        self.input.setPlaceholderText("https://esempio.com")
        self.input.setFixedHeight(36)
        lay.addWidget(self.input)

    def get_value(self):
        url = self.input.text().strip()
        return {"url": url if url else None}

    def is_valid(self):
        url = self.input.text().strip()
        if url and not url.startswith(("http://", "https://")):
            return False, "L'URL deve iniziare con http:// o https://"
        return True, ""


class EmailInput(PropertyInputWidget):
    def __init__(self, prop_name: str, prop_type: str, prop_config: dict):
        super().__init__(prop_name, prop_type, prop_config)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        self.input = QLineEdit()
        self.input.setPlaceholderText("email@esempio.com")
        self.input.setFixedHeight(36)
        lay.addWidget(self.input)

    def get_value(self):
        email = self.input.text().strip()
        return {"email": email if email else None}


class PhoneInput(PropertyInputWidget):
    def __init__(self, prop_name: str, prop_type: str, prop_config: dict):
        super().__init__(prop_name, prop_type, prop_config)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        self.input = QLineEdit()
        self.input.setPlaceholderText("+39 123 456 7890")
        self.input.setFixedHeight(36)
        lay.addWidget(self.input)

    def get_value(self):
        phone = self.input.text().strip()
        return {"phone_number": phone if phone else None}


class PeopleInput(PropertyInputWidget):
    def __init__(self, prop_name: str, prop_type: str, prop_config: dict):
        super().__init__(prop_name, prop_type, prop_config)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)

        self.input = QLineEdit()
        self.input.setPlaceholderText("User ID (es: 8711f079-8ae4-4748-89a7-d2daf31ff8fe)")
        self.input.setFixedHeight(36)

        hint = QLabel("💡 Inserisci ID utente Notion. Lascia vuoto se non necessario.")
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #787774; font-size: 10px;")

        lay.addWidget(self.input)
        lay.addWidget(hint)

    def get_value(self):
        user_id = self.input.text().strip()
        return {"people": [{"object": "user", "id": user_id}] if user_id else []}


class RelationInput(PropertyInputWidget):
    def __init__(self, prop_name: str, prop_type: str, prop_config: dict):
        super().__init__(prop_name, prop_type, prop_config)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Page ID (es: 2a7b7a8f729480b3b420f8736c4116d7)")
        self.input.setFixedHeight(36)

        hint = QLabel("💡 Inserisci ID pagina correlata. Lascia vuoto se non necessario.")
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #787774; font-size: 10px;")

        lay.addWidget(self.input)
        lay.addWidget(hint)

    def get_value(self):
        page_id = self.input.text().strip()
        return {"relation": [{"id": page_id}] if page_id else []}


class FilesInput(PropertyInputWidget):
    def __init__(self, prop_name: str, prop_type: str, prop_config: dict):
        super().__init__(prop_name, prop_type, prop_config)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)

        info = QLabel("⚠ La proprietà 'Files' è read-only via API. Sarà ignorata.")
        info.setWordWrap(True)
        info.setStyleSheet("color: #F87171; font-size: 11px;")
        lay.addWidget(info)

    def get_value(self):
        return None  # Files è read-only


# ── Factory ───────────────────────────────────────────────────────

INPUT_WIDGETS = {
    "title": TitleInput,
    "rich_text": RichTextInput,
    "number": NumberInput,
    "checkbox": CheckboxInput,
    "select": SelectInput,
    "multi_select": MultiSelectInput,
    "status": StatusInput,
    "date": DateInput,
    "url": URLInput,
    "email": EmailInput,
    "phone_number": PhoneInput,
    "people": PeopleInput,
    "relation": RelationInput,
    "files": FilesInput,
}


# ── Dialog principale ─────────────────────────────────────────────

class DataSourceEntryDialog(QDialog):
    """
    Dialog per creare una nuova entry o template in un DataSource.
    Genera form dinamico basato sullo schema.
    """

    def __init__(self, ds_id: str, ds_name: str, schema: dict, is_template: bool = False, parent=None):
        super().__init__(parent)
        self._ds_id = ds_id
        self._ds_name = ds_name
        self._schema = schema
        self._is_template = is_template  # ← NUOVO
        self._inputs: dict[str, PropertyInputWidget] = {}

        # Titolo dinamico
        if is_template:
            self.setWindowTitle(f"Nuovo template in: {ds_name}")
        else:
            self.setWindowTitle(f"Nuova entry in: {ds_name}")

        self.resize(650, 600)
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setSpacing(16)
        lay.setContentsMargins(24, 20, 24, 20)

        # ── Header ────────────────────────────────────────────────
        header = QLabel("Nuovo template" if self._is_template else "Nuova entry")
        header.setStyleSheet("font-size: 18px; font-weight: 700;")
        lay.addWidget(header)

        subtitle = QLabel(f"DataSource: {self._ds_name}")
        subtitle.setStyleSheet("color: #787774; font-size: 12px;")
        lay.addWidget(subtitle)

        # Info template
        if self._is_template:
            info = QLabel(
                "💡 I template sono modelli riutilizzabili. "
                "Potrai creare nuove pagine basate su questo template direttamente in Notion."
            )
            info.setWordWrap(True)
            info.setStyleSheet(
                "background: #EEF2FF; border: 1px solid #C7D2FE; "
                "border-radius: 6px; padding: 10px; color: #4338CA; font-size: 11px;"
            )
            lay.addWidget(info)

        # ── Form scrollabile ──────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        form_container = QWidget()
        form_lay = QVBoxLayout(form_container)
        form_lay.setSpacing(16)
        form_lay.setContentsMargins(0, 0, 0, 0)

        # Genera campo per ogni proprietà
        for prop_name, prop_data in self._schema.items():
            prop_type = prop_data.get("type", "")

            # Skip proprietà read-only
            if prop_type in ("created_time", "last_edited_time", "created_by",
                             "last_edited_by", "formula", "rollup", "unique_id"):
                continue

            # Crea widget input appropriato
            input_cls = INPUT_WIDGETS.get(prop_type)
            if not input_cls:
                continue

            prop_box = QGroupBox(f"{prop_name}")
            prop_box_lay = QVBoxLayout(prop_box)
            prop_box_lay.setSpacing(8)

            # Badge tipo
            type_badge = QLabel(prop_type.upper())
            type_badge.setFixedWidth(120)
            type_badge.setFixedHeight(20)
            type_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            type_badge.setStyleSheet(
                "background: #F0EFEC; border: 1px solid #E3E2DE; "
                "border-radius: 4px; color: #787774; font-size: 9px; "
                "font-weight: 600;"
            )
            prop_box_lay.addWidget(type_badge)

            # Widget input
            input_widget = input_cls(prop_name, prop_type, prop_data)
            self._inputs[prop_name] = input_widget
            prop_box_lay.addWidget(input_widget)

            form_lay.addWidget(prop_box)

        scroll.setWidget(form_container)
        lay.addWidget(scroll)

        # ── Pulsanti ──────────────────────────────────────────────
        btn_row = QWidget()
        br_lay = QHBoxLayout(btn_row)
        br_lay.setContentsMargins(0, 0, 0, 0)
        br_lay.setSpacing(10)

        cancel_btn = QPushButton("Annulla")
        cancel_btn.clicked.connect(self.reject)

        btn_text = "✓ Crea Template" if self._is_template else "✓ Crea Entry"
        self._create_btn = QPushButton(btn_text)
        self._create_btn.setObjectName("PrimaryBtn")
        self._create_btn.setDefault(True)
        self._create_btn.clicked.connect(self._on_create)

        br_lay.addStretch()
        br_lay.addWidget(cancel_btn)
        br_lay.addWidget(self._create_btn)

        lay.addWidget(btn_row)

    def _on_create(self):
        """Valida i campi e accetta il dialog."""
        # Valida tutti gli input
        for prop_name, widget in self._inputs.items():
            valid, error = widget.is_valid()
            if not valid:
                QMessageBox.warning(
                    self, "Validazione fallita",
                    f"Campo '{prop_name}': {error}"
                )
                return

        self.accept()

    def get_properties(self) -> dict:
        """Restituisce il dizionario properties per l'API Notion."""
        props = {}
        for prop_name, widget in self._inputs.items():
            value = widget.get_value()
            if value is not None:
                props[prop_name] = value
        return props

    def is_template_mode(self) -> bool:
        """Restituisce True se il dialog è in modalità template."""
        return self._is_template
