"""
gui/widgets/page_blocks_dialog.py
Dialog per visualizzare e modificare i blocchi di una pagina Notion.

Layout: lista blocchi (sinistra) | form editor (destra)
Caricamento e salvataggio asincroni via QThread interni.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QPushButton, QWidget, QListWidgetItem, QTextEdit, QLineEdit,
    QComboBox, QCheckBox, QSplitter, QScrollArea, QProgressBar,
    QMessageBox, )
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from src.notion_lib.utils.constants import NColors, NLanguage


# ─── Helper: tipo blocco ──────────────────────────────────────────

BLOCK_META: dict[str, tuple[str, str]] = {
    "paragraph":           ("📝", "Paragrafo"),
    "heading_1":           ("H1", "Heading 1"),
    "heading_2":           ("H2", "Heading 2"),
    "heading_3":           ("H3", "Heading 3"),
    "bulleted_list_item":  ("•",  "Elenco puntato"),
    "numbered_list_item":  ("1.", "Elenco numerato"),
    "to_do":               ("☑",  "To-do"),
    "toggle":              ("▶",  "Toggle"),
    "callout":             ("💡", "Callout"),
    "code":                ("</>","Codice"),
    "quote":               ("❝",  "Citazione"),
    "divider":             ("—",  "Divisore"),
    "bookmark":            ("🔗", "Bookmark"),
    "equation":            ("∫",  "Equazione"),
    "table":               ("⊞",  "Tabella"),
    "table_row":           ("—",  "Riga tabella"),
    "image":               ("🖼", "Immagine"),
    "video":               ("🎥", "Video"),
    "audio":               ("🔊", "Audio"),
    "file":                ("📎", "File"),
    "pdf":                 ("📄", "PDF"),
    "embed":               ("🌐", "Embed"),
    "child_page":          ("🗒", "Pagina figlia"),
    "child_database":      ("📦", "Database figlio"),
    "column_list":         ("⎔",  "Layout colonne"),
    "column":              ("⎔",  "Colonna"),
    "table_of_contents":   ("📋", "Indice"),
    "breadcrumb":          ("🔗", "Breadcrumb"),
    "synced_block":        ("🔄", "Sync block"),
    "link_to_page":        ("↗",  "Link a pagina"),
    "link_preview":        ("🔍", "Link preview"),
    "meeting_notes":       ("🎙", "Note riunione"),
    "transcription":       ("🎙", "Trascrizione"),
    "unsupported":         ("⚠",  "Non supportato"),
}

# Blocchi che non supportano update via API
_READ_ONLY_TYPES = frozenset({
    "divider", "breadcrumb", "child_page", "child_database",
    "synced_block", "link_to_page", "link_preview",
    "column_list", "column", "meeting_notes", "transcription",
    "table", "table_row", "audio", "unsupported",
})


def _get_block_type(block) -> str:
    """
    Restituisce il tipo Notion canonico del blocco.
    Fonte primaria: block._data["type"] (stringa API grezza, es. "heading_1").
    Fallback: type/block_type class attribute, escludendo valori generici.
    """
    try:
        return block._data["type"]
    except (AttributeError, KeyError, TypeError):
        pass
    _generic = {"", "paragraph_like", "heading"}
    bt = getattr(block, "block_type", "")
    if bt and bt not in _generic:
        return bt
    t = getattr(block, "type", "")
    return t or "unsupported"


def _block_preview(block) -> str:
    """Testo di anteprima (max 55 char) per la lista blocchi."""
    try:
        rt = getattr(block, "rich_text", None)
        if rt is not None:
            text = rt.text if hasattr(rt, "text") else str(rt)
            text = text.strip()
            return text[:55] + ("…" if len(text) > 55 else "")
    except Exception:
        pass
    for attr in ("expression", "url"):
        try:
            val = getattr(block, attr, None)
            if val:
                return str(val)[:55]
        except Exception:
            pass
    return ""


# ─── Form stili condivisi ─────────────────────────────────────────

_FORM_STYLE = """
    QLabel {
        color: #94A3B8;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.4px;
        text-transform: uppercase;
    }
    QTextEdit, QLineEdit {
        background: #1E293B;
        color: #E2E8F0;
        border: 1px solid #334155;
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 13px;
    }
    QTextEdit:focus, QLineEdit:focus {
        border-color: #22D3EE;
    }
    QComboBox {
        background: #1E293B;
        color: #E2E8F0;
        border: 1px solid #334155;
        border-radius: 6px;
        padding: 5px 10px;
        min-height: 28px;
    }
    QComboBox QAbstractItemView {
        background: #1E293B;
        color: #E2E8F0;
        selection-background-color: #214158;
    }
    QCheckBox {
        color: #CBD5E1;
        font-size: 13px;
    }
    QCheckBox::indicator {
        width: 16px; height: 16px;
        border-radius: 4px;
        border: 2px solid #334155;
        background: #1E293B;
    }
    QCheckBox::indicator:checked {
        background: #22D3EE;
        border-color: #22D3EE;
    }
"""


# ─── Worker: caricamento blocchi ──────────────────────────────────

class _LoadBlocksWorker(QThread):
    success = pyqtSignal(list)
    failure = pyqtSignal(str)

    def __init__(self, headers: dict, page_id: str):
        super().__init__()
        self._headers = headers
        self._page_id = page_id

    def run(self):
        try:
            from src.notion_lib.nEndpoints.pages import get_block_children
            from src.notion_lib.nModels.blocks.base_block import BlockFactory, _ensure_registry_populated

            _ensure_registry_populated()
            raw_blocks = get_block_children(self._headers, self._page_id)
            blocks = [
                BlockFactory.from_data(self._headers, blk, blk["id"].replace("-", ""))
                for blk in raw_blocks
            ]
            self.success.emit(blocks)
        except Exception as e:
            self.failure.emit(str(e))


# ─── Worker: aggiornamento blocco ─────────────────────────────────

class _UpdateBlockWorker(QThread):
    success = pyqtSignal(str)
    failure = pyqtSignal(str)

    def __init__(self, block):
        super().__init__()
        self._block = block

    def run(self):
        try:
            self._block.update()
            self.success.emit("Blocco aggiornato.")
        except Exception as e:
            self.failure.emit(str(e))


class _AppendBlockWorker(QThread):
    success = pyqtSignal(object)   # block appended
    failure = pyqtSignal(str)

    def __init__(self, headers: dict, page_id: str, block):
        super().__init__()
        self._headers = headers
        self._page_id = page_id
        self._block   = block

    def run(self):
        try:
            from src.notion_lib.nEndpoints.blocks import append_children
            append_children(
                self._headers,
                self._page_id,
                [self._block.to_payload()]
            )
            self.success.emit(self._block)
        except Exception as e:
            self.failure.emit(str(e))


# ─── Form per read-only ───────────────────────────────────────────

class _ReadOnlyForm(QWidget):
    is_editable = False

    def __init__(self, block_type: str, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        msg = QLabel(f"Il blocco «{block_type}» non è modificabile via API pubblica.")
        msg.setWordWrap(True)
        msg.setStyleSheet("color: #64748B; font-style: italic; font-size: 12px;")
        lay.addWidget(msg)
        lay.addStretch()

    def apply_to_block(self, block):
        pass


# ─── Form: blocchi testuali generici ─────────────────────────────

class _TextBlockForm(QWidget):
    is_editable = True

    def __init__(self, block, extras: dict | None = None, parent=None):
        """
        extras: {attr_name: (label, QWidget)}
        Supporta QCheckBox come widget extra.
        """
        super().__init__(parent)
        self._extras = extras or {}
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(14)

        lay.addWidget(QLabel("Testo"))
        self._text = QTextEdit()
        self._text.setMaximumHeight(130)
        try:
            self._text.setPlainText(block.rich_text.text)
        except Exception:
            pass
        lay.addWidget(self._text)

        lay.addWidget(QLabel("Colore"))
        self._color = QComboBox()
        for c in NColors:
            self._color.addItem(c.name, c.value)
        try:
            current = block.color.value if hasattr(block.color, "value") else "default"
            idx = self._color.findData(current)
            if idx >= 0:
                self._color.setCurrentIndex(idx)
        except Exception:
            pass
        lay.addWidget(self._color)

        for attr, (label, widget) in self._extras.items():
            lay.addWidget(QLabel(label))
            lay.addWidget(widget)

        lay.addStretch()

    def apply_to_block(self, block):
        block.rich_text = self._text.toPlainText()
        block._color = self._color.currentData()
        for attr, (_, widget) in self._extras.items():
            if isinstance(widget, QCheckBox):
                setattr(block, attr, widget.isChecked())


# ─── Form: callout ────────────────────────────────────────────────

class _CalloutForm(QWidget):
    is_editable = True

    def __init__(self, block, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(14)

        lay.addWidget(QLabel("Testo"))
        self._text = QTextEdit()
        self._text.setMaximumHeight(110)
        try:
            self._text.setPlainText(block.rich_text.text)
        except Exception:
            pass
        lay.addWidget(self._text)

        row = QWidget()
        row_lay = QHBoxLayout(row)
        row_lay.setContentsMargins(0, 0, 0, 0)
        row_lay.setSpacing(20)

        emoji_col = QWidget()
        ec_lay = QVBoxLayout(emoji_col)
        ec_lay.setContentsMargins(0, 0, 0, 0)
        ec_lay.setSpacing(6)
        ec_lay.addWidget(QLabel("Icona emoji"))
        self._icon = QLineEdit()
        self._icon.setMaximumWidth(70)
        try:
            from src.notion_lib.nTypes.icons import NEmoji
            if isinstance(block.icon, NEmoji):
                self._icon.setText(block.icon.emoji or "")
        except Exception:
            pass
        ec_lay.addWidget(self._icon)
        row_lay.addWidget(emoji_col)

        color_col = QWidget()
        cc_lay = QVBoxLayout(color_col)
        cc_lay.setContentsMargins(0, 0, 0, 0)
        cc_lay.setSpacing(6)
        cc_lay.addWidget(QLabel("Colore"))
        self._color = QComboBox()
        for c in NColors:
            self._color.addItem(c.name, c.value)
        try:
            current = block.color.value if hasattr(block.color, "value") else "default"
            idx = self._color.findData(current)
            if idx >= 0:
                self._color.setCurrentIndex(idx)
        except Exception:
            pass
        cc_lay.addWidget(self._color)
        row_lay.addWidget(color_col)
        row_lay.addStretch()

        lay.addWidget(row)
        lay.addStretch()

    def apply_to_block(self, block):
        block.rich_text = self._text.toPlainText()
        block._color = self._color.currentData()
        emoji_text = self._icon.text().strip()
        if emoji_text:
            from src.notion_lib.nTypes.icons import NEmoji
            block.icon = NEmoji({"type": "emoji", "emoji": emoji_text})


# ─── Form: code ───────────────────────────────────────────────────

class _CodeForm(QWidget):
    is_editable = True

    def __init__(self, block, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(14)

        lay.addWidget(QLabel("Codice"))
        self._code = QTextEdit()
        self._code.setFont(QFont("Consolas", 10))
        self._code.setMaximumHeight(180)
        try:
            self._code.setPlainText(block.rich_text.text)
        except Exception:
            pass
        lay.addWidget(self._code)

        row = QWidget()
        row_lay = QHBoxLayout(row)
        row_lay.setContentsMargins(0, 0, 0, 0)
        row_lay.setSpacing(20)

        lang_col = QWidget()
        lc_lay = QVBoxLayout(lang_col)
        lc_lay.setContentsMargins(0, 0, 0, 0)
        lc_lay.setSpacing(6)
        lc_lay.addWidget(QLabel("Linguaggio"))
        self._lang = QComboBox()
        self._lang.setMinimumWidth(160)
        for lang in NLanguage:
            self._lang.addItem(lang.value, lang.value)
        try:
            idx = self._lang.findData(block.language.value)
            if idx >= 0:
                self._lang.setCurrentIndex(idx)
        except Exception:
            pass
        lc_lay.addWidget(self._lang)
        row_lay.addWidget(lang_col)
        row_lay.addStretch()
        lay.addWidget(row)

        lay.addWidget(QLabel("Caption"))
        self._caption = QLineEdit()
        try:
            self._caption.setText(block.caption.text)
        except Exception:
            pass
        lay.addWidget(self._caption)
        lay.addStretch()

    def apply_to_block(self, block):
        block.rich_text = self._code.toPlainText()
        block._language = self._lang.currentData()
        block.caption = self._caption.text()


# ─── Form: equation ───────────────────────────────────────────────

class _EquationForm(QWidget):
    is_editable = True

    def __init__(self, block, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(14)
        lay.addWidget(QLabel("Espressione LaTeX"))
        self._expr = QLineEdit()
        self._expr.setPlaceholderText("E = mc^2")
        try:
            self._expr.setText(block.expression)
        except Exception:
            pass
        lay.addWidget(self._expr)
        lay.addStretch()

    def apply_to_block(self, block):
        block.expression = self._expr.text().strip()


# ─── Form: bookmark ───────────────────────────────────────────────

class _BookmarkForm(QWidget):
    is_editable = True

    def __init__(self, block, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(14)

        lay.addWidget(QLabel("URL"))
        self._url = QLineEdit()
        try:
            self._url.setText(block.url or "")
        except Exception:
            pass
        lay.addWidget(self._url)

        lay.addWidget(QLabel("Caption"))
        self._caption = QLineEdit()
        try:
            self._caption.setText(block.caption.text)
        except Exception:
            pass
        lay.addWidget(self._caption)
        lay.addStretch()

    def apply_to_block(self, block):
        block.url = self._url.text().strip()
        block.caption = self._caption.text()


# ─── Form: embed ──────────────────────────────────────────────────

class _EmbedForm(QWidget):
    is_editable = True

    def __init__(self, block, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(14)
        lay.addWidget(QLabel("URL"))
        self._url = QLineEdit()
        try:
            self._url.setText(block.url or "")
        except Exception:
            pass
        lay.addWidget(self._url)
        lay.addStretch()

    def apply_to_block(self, block):
        block.url = self._url.text().strip()


# ─── Form: media (image / video / file / pdf) ─────────────────────

class _MediaForm(QWidget):
    def __init__(self, block, has_caption: bool = True, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(14)

        try:
            file_type = block.file_object.type if block.file_object else None
        except Exception:
            file_type = None

        self._is_external = (file_type == "external")
        self.is_editable = self._is_external or has_caption

        if self._is_external:
            lay.addWidget(QLabel("URL (esterno)"))
            self._url = QLineEdit()
            try:
                self._url.setText(block.file_object.url or "")
            except Exception:
                pass
            lay.addWidget(self._url)
        else:
            info = QLabel(
                "⚠  File interno Notion: l'URL non è modificabile via API pubblica."
            )
            info.setWordWrap(True)
            info.setStyleSheet("color: #F87171; font-size: 11px;")
            lay.addWidget(info)
            self._url = None

        if has_caption:
            lay.addWidget(QLabel("Caption"))
            self._caption = QLineEdit()
            try:
                self._caption.setText(block.caption.text)
            except Exception:
                pass
            lay.addWidget(self._caption)
        else:
            self._caption = None

        lay.addStretch()

    def apply_to_block(self, block):
        if self._is_external and self._url:
            from src.notion_lib.nTypes.files import FileTypeExternal
            url = self._url.text().strip()
            if url:
                block.file_object = FileTypeExternal(url)
        if self._caption is not None:
            block.caption = self._caption.text()


# ─── Form: table of contents ─────────────────────────────────────

class _TocForm(QWidget):
    is_editable = True

    def __init__(self, block, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(14)
        lay.addWidget(QLabel("Colore"))
        self._color = QComboBox()
        for c in NColors:
            self._color.addItem(c.name, c.value)
        try:
            current = block.color.value if hasattr(block.color, "value") else "default"
            idx = self._color.findData(current)
            if idx >= 0:
                self._color.setCurrentIndex(idx)
        except Exception:
            pass
        lay.addWidget(self._color)
        lay.addStretch()

    def apply_to_block(self, block):
        block._color = self._color.currentData()


# ─── Factory: form per tipo ───────────────────────────────────────

def _make_form(block, block_type: str) -> QWidget:
    """Restituisce il form editor appropriato per il tipo di blocco."""
    if block_type in _READ_ONLY_TYPES:
        return _ReadOnlyForm(block_type)

    _TEXT_TYPES = {
        "paragraph", "bulleted_list_item", "numbered_list_item",
        "toggle", "quote",
    }
    if block_type in _TEXT_TYPES:
        return _TextBlockForm(block)

    if block_type in ("heading_1", "heading_2", "heading_3"):
        chk = QCheckBox("Espandibile (toggleable)")
        try:
            chk.setChecked(block.is_toggleable)
        except Exception:
            pass
        return _TextBlockForm(block, extras={"is_toggleable": ("Opzioni", chk)})

    if block_type == "to_do":
        chk = QCheckBox("Completato")
        try:
            chk.setChecked(block.checked)
        except Exception:
            pass
        return _TextBlockForm(block, extras={"checked": ("Stato", chk)})

    if block_type == "callout":
        return _CalloutForm(block)

    if block_type == "code":
        return _CodeForm(block)

    if block_type == "equation":
        return _EquationForm(block)

    if block_type == "bookmark":
        return _BookmarkForm(block)

    if block_type == "embed":
        return _EmbedForm(block)

    if block_type in ("image", "video"):
        return _MediaForm(block, has_caption=True)

    if block_type in ("file", "pdf"):
        return _MediaForm(block, has_caption=True)

    if block_type == "table_of_contents":
        return _TocForm(block)

    return _ReadOnlyForm(block_type)


# ─── Dialog principale ────────────────────────────────────────────

class PageBlocksDialog(QDialog):
    """
    Dialog per esplorare e modificare i blocchi di una pagina.

    - Carica i blocchi in background (_LoadBlocksWorker).
    - Salva via _UpdateBlockWorker senza bloccare la UI.
    - Blocchi read-only: pulsante Save disabilitato.
    """

    def __init__(self, page_id: str, page_title: str,
                 headers: dict, parent=None):
        super().__init__(parent)
        self._page_id  = page_id
        self._headers  = headers
        self._blocks:  list = []
        self._current: int  = -1
        self._workers: list = []

        self.setWindowTitle(f"Blocchi — {page_title}")
        self.resize(960, 640)
        self._build_ui(page_title)
        self._load_blocks()

    # ── Build UI ──────────────────────────────────────────────────

    def _build_ui(self, page_title: str):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        header = QWidget()
        header.setFixedHeight(52)
        header.setStyleSheet(
            "background: #0F172A; border-bottom: 1px solid #1E293B;"
        )
        hl = QHBoxLayout(header)
        hl.setContentsMargins(20, 0, 20, 0)
        title_lbl = QLabel(f"🗒  {page_title}")
        title_lbl.setStyleSheet(
            "font-size: 15px; font-weight: 700; color: #E8EEF9;"
        )
        self._status_lbl = QLabel("Caricamento…")
        self._status_lbl.setStyleSheet("color: #64748B; font-size: 12px;")
        hl.addWidget(title_lbl)
        hl.addStretch()
        hl.addWidget(self._status_lbl)
        root.addWidget(header)

        # Progress bar (indeterminate, nascosta dopo il caricamento)
        self._progress = QProgressBar()
        self._progress.setRange(0, 0)
        self._progress.setFixedHeight(3)
        self._progress.setTextVisible(False)
        self._progress.setStyleSheet(
            "QProgressBar { border:none; background:#1E293B; }"
            "QProgressBar::chunk { background:#22D3EE; }"
        )
        root.addWidget(self._progress)

        # Splitter principale
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet("QSplitter::handle { background: #1E293B; }")

        # ── Pannello sinistro: lista blocchi ──────────────────────
        left = QWidget()
        left.setMinimumWidth(220)
        left.setMaximumWidth(320)
        left.setStyleSheet("background: #0D1628;")
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setSpacing(0)

        list_hdr = QLabel("  BLOCCHI")
        list_hdr.setFixedHeight(30)
        list_hdr.setStyleSheet(
            "font-size: 10px; font-weight: 700; color: #475569; "
            "letter-spacing: 0.8px; background: #0D1628; "
            "border-bottom: 1px solid #1E293B; padding-left: 12px;"
        )
        ll.addWidget(list_hdr)

        self._list = QListWidget()
        self._list.setStyleSheet("""
            QListWidget {
                background: #0D1628;
                border: none;
                outline: none;
                padding: 6px 4px;
            }
            QListWidget::item {
                border-radius: 6px;
                padding: 9px 10px;
                color: #94A3B8;
                font-size: 12px;
                min-height: 18px;
            }
            QListWidget::item:selected {
                background: #1E3A5F;
                color: #E8EEF9;
            }
            QListWidget::item:hover:!selected {
                background: #162033;
                color: #CBD5E1;
            }
        """)
        self._list.setEnabled(False)
        self._list.currentRowChanged.connect(self._on_block_selected)
        ll.addWidget(self._list)

        add_btn = QPushButton("＋  Aggiungi blocco")
        add_btn.setEnabled(False)
        add_btn.setFixedHeight(34)
        add_btn.setStyleSheet("""
            QPushButton {
                background: #0D1628;
                border: none;
                border-top: 1px solid #1E293B;
                color: #22D3EE;
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 0.4px;
            }
            QPushButton:hover:enabled {
                background: #162033;
                color: #38BDF8;
            }
            QPushButton:disabled { color: #1E3A5F; }
        """)
        add_btn.clicked.connect(self._on_add_block)
        self._add_btn = add_btn
        ll.addWidget(add_btn)

        splitter.addWidget(left)

        # ── Pannello destro: form editor ──────────────────────────
        right = QWidget()
        right.setStyleSheet("background: #111827;")
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(0)

        form_hdr = QWidget()
        form_hdr.setFixedHeight(40)
        form_hdr.setStyleSheet(
            "background: #111827; border-bottom: 1px solid #1E293B;"
        )
        fhl = QHBoxLayout(form_hdr)
        fhl.setContentsMargins(20, 0, 20, 0)
        self._type_lbl = QLabel("—")
        self._type_lbl.setStyleSheet(
            "color: #475569; font-size: 11px; font-weight: 700;"
        )
        self._id_lbl = QLabel("")
        self._id_lbl.setStyleSheet("color: #2D3748; font-size: 10px;")
        fhl.addWidget(self._type_lbl)
        fhl.addStretch()
        fhl.addWidget(self._id_lbl)
        rl.addWidget(form_hdr)

        # Area form scrollabile
        self._form_scroll = QScrollArea()
        self._form_scroll.setWidgetResizable(True)
        self._form_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self._form_scroll.setStyleSheet("background: #111827;")

        self._form_host = QWidget()
        self._form_host.setStyleSheet("background: #111827;")
        self._form_lay = QVBoxLayout(self._form_host)
        self._form_lay.setContentsMargins(24, 24, 24, 24)
        self._form_lay.setSpacing(16)

        placeholder = QLabel("Fai doppio click su una pagina\nper visualizzarne i blocchi,\npoi seleziona un blocco dalla lista.")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("color: #2D3748; font-size: 13px;")
        self._form_lay.addStretch()
        self._form_lay.addWidget(placeholder)
        self._form_lay.addStretch()

        self._form_scroll.setWidget(self._form_host)
        rl.addWidget(self._form_scroll, stretch=1)

        splitter.addWidget(right)
        splitter.setSizes([260, 700])
        root.addWidget(splitter, stretch=1)

        # Footer
        footer = QWidget()
        footer.setFixedHeight(52)
        footer.setStyleSheet(
            "background: #0F172A; border-top: 1px solid #1E293B;"
        )
        fl = QHBoxLayout(footer)
        fl.setContentsMargins(20, 0, 20, 0)
        fl.setSpacing(12)

        self._save_btn = QPushButton("💾  Salva modifiche")
        self._save_btn.setEnabled(False)
        self._save_btn.setFixedHeight(34)
        self._save_btn.setObjectName("PrimaryBtn")
        self._save_btn.clicked.connect(self._on_save)

        close_btn = QPushButton("Chiudi")
        close_btn.setFixedHeight(34)
        close_btn.clicked.connect(self.accept)

        fl.addStretch()
        fl.addWidget(close_btn)
        fl.addWidget(self._save_btn)
        root.addWidget(footer)

    # ── Caricamento ───────────────────────────────────────────────

    def _load_blocks(self):
        self._progress.show()
        self._list.setEnabled(False)
        self._status_lbl.setText("Caricamento blocchi…")

        w = _LoadBlocksWorker(self._headers, self._page_id)
        w.success.connect(self._on_loaded)
        w.failure.connect(self._on_load_error)
        w.finished.connect(lambda worker=w: self._cleanup(worker))
        self._workers.append(w)
        w.start()

    def _on_loaded(self, blocks: list):
        self._blocks = blocks
        self._progress.hide()
        self._list.setEnabled(True)
        self._add_btn.setEnabled(True)
        count = len(blocks)
        self._status_lbl.setText(
            f"{count} {'blocco' if count == 1 else 'blocchi'}"
        )
        self._list.clear()
        for block in blocks:
            bt = _get_block_type(block)
            icon, label = BLOCK_META.get(bt, ("?", bt))
            preview = _block_preview(block)
            text = f"{icon}  {label}"
            if preview:
                text += f"  —  {preview}"
            item = QListWidgetItem(text)
            self._list.addItem(item)


    def _on_load_error(self, error: str):
        self._progress.hide()
        self._status_lbl.setText("⚠  Errore caricamento")
        QMessageBox.critical(
            self, "Errore caricamento blocchi",
            f"Impossibile caricare i blocchi:\n{error}"
        )

    # ── Selezione blocco ──────────────────────────────────────────

    def _on_block_selected(self, row: int):
        if row < 0 or row >= len(self._blocks):
            return

        self._current = row
        block = self._blocks[row]
        bt = _get_block_type(block)
        icon, label = BLOCK_META.get(bt, ("?", bt))

        self._type_lbl.setText(f"{icon}  {label.upper()}")
        bid = getattr(block, "block_id", None) or "—"
        self._id_lbl.setText(f"ID: {bid}")

        # Sostituisce form precedente
        self._clear_form()

        form = _make_form(block, bt)
        form.setStyleSheet(_FORM_STYLE)
        self._form_lay.addWidget(form)
        self._form_lay.addStretch()

        updatable = getattr(block, "updatable", True)
        editable = getattr(form, "is_editable", False)
        self._save_btn.setEnabled(editable and updatable)

    def _clear_form(self):
        while self._form_lay.count():
            item = self._form_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _on_add_block(self):
        from src.notion_lib.gui.widgets.block_insert_dialog import InsertBlockDialog
        dialog = InsertBlockDialog(self.windowTitle(), parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        block = dialog.get_block()
        if not block:
            return

        self._add_btn.setEnabled(False)
        self._status_lbl.setText("Aggiunta blocco…")

        w = _AppendBlockWorker(self._headers, self._page_id, block)
        w.success.connect(self._on_append_ok)
        w.failure.connect(self._on_append_error)
        w.finished.connect(lambda worker=w: self._cleanup(worker))
        self._workers.append(w)
        w.start()

    def _on_append_ok(self, block):
        self._add_btn.setEnabled(True)
        self._blocks.append(block)

        bt = _get_block_type(block)
        icon, label = BLOCK_META.get(bt, ("?", bt))
        preview = _block_preview(block)
        text = f"{icon}  {label}"
        if preview:
            text += f"  —  {preview}"

        self._list.addItem(text)
        self._list.setCurrentRow(self._list.count() - 1)  # seleziona il nuovo
        self._status_lbl.setText(
            f"{self._list.count()} {'blocco' if self._list.count() == 1 else 'blocchi'}"
        )

    def _on_append_error(self, error: str):
        self._add_btn.setEnabled(True)
        self._status_lbl.setText("⚠  Errore aggiunta")
        QMessageBox.critical(self, "Errore", f"Impossibile aggiungere il blocco:\n{error}")

    # ── Salvataggio ───────────────────────────────────────────────

    def _on_save(self):
        if self._current < 0 or self._current >= len(self._blocks):
            return

        block = self._blocks[self._current]

        # Recupera il form attivo (primo widget con apply_to_block)
        form = None
        for i in range(self._form_lay.count()):
            item = self._form_lay.itemAt(i)
            if item and item.widget() and hasattr(item.widget(), "apply_to_block"):
                form = item.widget()
                break

        if form is None:
            return

        try:
            form.apply_to_block(block)
        except Exception as e:
            QMessageBox.warning(
                self, "Errore",
                f"Impossibile applicare le modifiche al blocco:\n{e}"
            )
            return

        self._save_btn.setEnabled(False)
        self._save_btn.setText("⏳ Salvataggio…")
        self._status_lbl.setText("Salvataggio…")

        w = _UpdateBlockWorker(block)
        w.success.connect(self._on_save_ok)
        w.failure.connect(self._on_save_error)
        w.finished.connect(lambda worker=w: self._cleanup(worker))
        self._workers.append(w)
        w.start()

    def _on_save_ok(self, msg: str):
        self._save_btn.setEnabled(True)
        self._save_btn.setText("💾  Salva modifiche")
        self._status_lbl.setText(f"✓  {msg}")

        # Aggiorna testo nella lista
        if 0 <= self._current < self._list.count():
            block = self._blocks[self._current]
            bt = _get_block_type(block)
            icon, label = BLOCK_META.get(bt, ("?", bt))
            preview = _block_preview(block)
            text = f"{icon}  {label}"
            if preview:
                text += f"  —  {preview}"
            self._list.item(self._current).setText(text)

    def _on_save_error(self, error: str):
        self._save_btn.setEnabled(True)
        self._save_btn.setText("💾  Salva modifiche")
        self._status_lbl.setText("⚠  Errore salvataggio")
        QMessageBox.critical(self, "Errore salvataggio", error)

    # ── Cleanup ───────────────────────────────────────────────────

    def _cleanup(self, worker):
        if worker in self._workers:
            self._workers.remove(worker)

    def closeEvent(self, event):
        for w in self._workers:
            w.quit()
            w.wait(300)
        super().closeEvent(event)