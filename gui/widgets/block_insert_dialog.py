"""
gui/widgets/block_insert_dialog.py
Dialog per inserire blocchi in una pagina Notion.
Struttura: lista tipi → form specifico → conferma.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QPushButton, QStackedWidget, QWidget, QListWidgetItem,
    QLineEdit, QComboBox, QTextEdit, QCheckBox, QSpinBox,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from nTypes.rich_text import simple_rich_text_list
from utils.constants import NColors, NLanguage


# ── Form per tipi di blocco ───────────────────────────────────────

class ParagraphForm(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setSpacing(12)

        lay.addWidget(QLabel("Testo:"))
        self.text_input = QTextEdit()
        self.text_input.setMaximumHeight(120)
        self.text_input.setPlaceholderText("Scrivi il contenuto del paragrafo...")
        lay.addWidget(self.text_input)

        lay.addWidget(QLabel("Colore sfondo:"))
        self.color_combo = QComboBox()
        for c in ["default", "gray_background", "brown_background",
                  "orange_background", "yellow_background", "green_background",
                  "blue_background", "purple_background", "pink_background", "red_background"]:
            self.color_combo.addItem(c.replace("_", " ").title(), c)
        lay.addWidget(self.color_combo)
        lay.addStretch()

    def get_block(self):
        from nModels.blocks.paragraph import ParagraphBlock
        text = self.text_input.toPlainText().strip()
        if not text:
            raise ValueError("Il testo non può essere vuoto")
        return ParagraphBlock.create(
            text=text,
            color=self.color_combo.currentData()
        )


class HeadingForm(QWidget):
    def __init__(self, level: int):
        super().__init__()
        self.level = level
        lay = QVBoxLayout(self)
        lay.setSpacing(12)

        lay.addWidget(QLabel(f"Testo heading {level}:"))
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText(f"Titolo livello {level}...")
        lay.addWidget(self.text_input)

        lay.addWidget(QLabel("Colore:"))
        self.color_combo = QComboBox()
        for c in ["default", "gray", "brown", "orange", "yellow",
                  "green", "blue", "purple", "pink", "red"]:
            self.color_combo.addItem(c.title(), c)
        lay.addWidget(self.color_combo)

        self.toggle_check = QCheckBox("Blocco espandibile (con figli)")
        lay.addWidget(self.toggle_check)
        lay.addStretch()

    def get_block(self):
        from nModels.blocks.heading import Heading1, Heading2, Heading3
        text = self.text_input.text().strip()
        if not text:
            raise ValueError("Il titolo non può essere vuoto")

        cls = {1: Heading1, 2: Heading2, 3: Heading3}[self.level]
        return cls.create(
            text=text,
            color=self.color_combo.currentData(),
            is_toggleable=self.toggle_check.isChecked()
        )


class ToDoForm(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setSpacing(12)

        lay.addWidget(QLabel("Testo todo:"))
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Cosa fare...")
        lay.addWidget(self.text_input)

        self.checked = QCheckBox("Già completato")
        lay.addWidget(self.checked)
        lay.addStretch()

    def get_block(self):
        from nModels.blocks.list_blocks import ToDo
        text = self.text_input.text().strip()
        if not text:
            raise ValueError("Il testo non può essere vuoto")
        return ToDo.create(text=text, checked=self.checked.isChecked())


class BulletForm(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("Testo voce elenco:"))
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Elemento della lista...")
        lay.addWidget(self.text_input)
        lay.addStretch()

    def get_block(self):
        from nModels.blocks.list_blocks import BulletedListItem
        text = self.text_input.text().strip()
        if not text:
            raise ValueError("Il testo non può essere vuoto")
        return BulletedListItem.create(text=text)


class NumberedForm(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("Testo voce numerata:"))
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Elemento numerato...")
        lay.addWidget(self.text_input)
        lay.addStretch()

    def get_block(self):
        from nModels.blocks.list_blocks import NumberedListItem
        text = self.text_input.text().strip()
        if not text:
            raise ValueError("Il testo non può essere vuoto")
        return NumberedListItem.create(text=text)


class CalloutForm(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setSpacing(12)

        lay.addWidget(QLabel("Testo callout:"))
        self.text_input = QTextEdit()
        self.text_input.setMaximumHeight(100)
        self.text_input.setPlaceholderText("Messaggio importante...")
        lay.addWidget(self.text_input)

        lay.addWidget(QLabel("Emoji icona:"))
        self.icon_input = QLineEdit()
        self.icon_input.setText("💡")
        self.icon_input.setMaximumWidth(60)
        lay.addWidget(self.icon_input)

        lay.addWidget(QLabel("Colore:"))
        self.color_combo = QComboBox()
        for c in NColors:
            self.color_combo.addItem(c.name, c)
        lay.addWidget(self.color_combo)
        lay.addStretch()

    def get_block(self):
        from nModels.blocks.special_blocks import CalloutBlock
        from nTypes.icons import NEmoji
        text = self.text_input.toPlainText().strip()
        if not text:
            raise ValueError("Il testo non può essere vuoto")
        icon = NEmoji({"type": "emoji", "emoji": self.icon_input.text() or "💡"})
        return CalloutBlock.create(
            text=text,
            icon=icon,
            color=self.color_combo.currentData()
        )


class CodeForm(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setSpacing(12)

        lay.addWidget(QLabel("Codice:"))
        self.code_input = QTextEdit()
        self.code_input.setMaximumHeight(150)
        self.code_input.setPlaceholderText("# Inserisci il tuo codice...")
        self.code_input.setFont(QFont("Consolas", 10))
        lay.addWidget(self.code_input)

        lay.addWidget(QLabel("Linguaggio:"))
        self.lang_combo = QComboBox()
        for lang in [NLanguage.PYTHON, NLanguage.JAVASCRIPT, NLanguage.JAVA,
                     NLanguage.CPP, NLanguage.CSHARP, NLanguage.GO,
                     NLanguage.RUST, NLanguage.SQL, NLanguage.BASH,
                     NLanguage.HTML, NLanguage.CSS, NLanguage.JSON,
                     NLanguage.PLAIN_TEXT]:
            self.lang_combo.addItem(lang.value, lang)
        lay.addWidget(self.lang_combo)

        lay.addWidget(QLabel("Caption (opzionale):"))
        self.caption_input = QLineEdit()
        self.caption_input.setPlaceholderText("Descrizione...")
        lay.addWidget(self.caption_input)
        lay.addStretch()

    def get_block(self):
        from nModels.blocks.special_blocks import CodeBlock
        code = self.code_input.toPlainText().strip()
        if not code:
            raise ValueError("Il codice non può essere vuoto")
        return CodeBlock.create(
            text=code,
            language=self.lang_combo.currentData(),
            caption=self.caption_input.text().strip() or None
        )


class QuoteForm(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("Testo citazione:"))
        self.text_input = QTextEdit()
        self.text_input.setMaximumHeight(100)
        self.text_input.setPlaceholderText("Inserisci la citazione...")
        lay.addWidget(self.text_input)
        lay.addStretch()

    def get_block(self):
        from nModels.blocks.special_blocks import QuoteBlock
        text = self.text_input.toPlainText().strip()
        if not text:
            raise ValueError("Il testo non può essere vuoto")
        return QuoteBlock.create(text=text)


class DividerForm(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        info = QLabel("Il divisore è una linea orizzontale senza parametri configurabili.")
        info.setWordWrap(True)
        info.setStyleSheet("color: #787774; font-size: 12px;")
        lay.addWidget(info)
        lay.addStretch()

    def get_block(self):
        from nModels.blocks.special_blocks import DividerBlock
        return DividerBlock.create()


class BookmarkForm(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setSpacing(12)

        lay.addWidget(QLabel("URL:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://esempio.com")
        lay.addWidget(self.url_input)

        lay.addWidget(QLabel("Caption (opzionale):"))
        self.caption_input = QLineEdit()
        self.caption_input.setPlaceholderText("Descrizione link...")
        lay.addWidget(self.caption_input)
        lay.addStretch()

    def get_block(self):
        from nModels.blocks.special_blocks import BookmarkBlock
        url = self.url_input.text().strip()
        if not url:
            raise ValueError("L'URL non può essere vuoto")
        return BookmarkBlock.create(
            url=url,
            caption=self.caption_input.text().strip() or None
        )


class EquationForm(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setSpacing(12)

        lay.addWidget(QLabel("Espressione LaTeX:"))
        self.expr_input = QLineEdit()
        self.expr_input.setPlaceholderText("E = mc^2")
        lay.addWidget(self.expr_input)

        hint = QLabel("Esempio: x^2 + y^2 = r^2")
        hint.setStyleSheet("color: #787774; font-size: 11px; font-style: italic;")
        lay.addWidget(hint)
        lay.addStretch()

    def get_block(self):
        from nModels.blocks.special_blocks import EquationBlock
        expr = self.expr_input.text().strip()
        if not expr:
            raise ValueError("L'espressione non può essere vuota")
        return EquationBlock.create(expression=expr)


class TableForm(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setSpacing(12)

        # ── Controlli dimensioni ─────────────────────────────────
        dims = QWidget()
        dims_lay = QHBoxLayout(dims)
        dims_lay.setContentsMargins(0, 0, 0, 0)
        dims_lay.setSpacing(12)

        dims_lay.addWidget(QLabel("Righe:"))
        self.rows_spin = QSpinBox()
        self.rows_spin.setRange(1, 20)
        self.rows_spin.setValue(3)
        self.rows_spin.setFixedWidth(70)
        self.rows_spin.valueChanged.connect(self._rebuild_table)
        dims_lay.addWidget(self.rows_spin)

        dims_lay.addWidget(QLabel("Colonne:"))
        self.cols_spin = QSpinBox()
        self.cols_spin.setRange(1, 20)
        self.cols_spin.setValue(3)
        self.cols_spin.setFixedWidth(70)
        self.cols_spin.valueChanged.connect(self._rebuild_table)
        dims_lay.addWidget(self.cols_spin)
        dims_lay.addStretch()

        lay.addWidget(dims)

        # ── Opzioni intestazioni ─────────────────────────────────
        self.header_col = QCheckBox("Prima riga come intestazione")
        self.header_col.setChecked(True)
        lay.addWidget(self.header_col)

        self.header_row = QCheckBox("Prima colonna come intestazione")
        lay.addWidget(self.header_row)

        # ── Tabella editabile ────────────────────────────────────
        from PyQt6.QtWidgets import QTableWidget, QHeaderView

        self.table = QTableWidget()
        self.table.setMinimumHeight(220)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        lay.addWidget(self.table)

        hint = QLabel("💡 Compila le celle direttamente. Celle vuote = testo vuoto.")
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #787774; font-size: 11px;")
        lay.addWidget(hint)

        # Inizializza
        self._rebuild_table()

    def _rebuild_table(self):
        """Ricostruisce la tabella quando cambiano dimensioni."""
        rows = self.rows_spin.value()
        cols = self.cols_spin.value()

        # Salva contenuti esistenti
        old_data = {}
        for r in range(self.table.rowCount()):
            for c in range(self.table.columnCount()):
                item = self.table.item(r, c)
                if item:
                    old_data[(r, c)] = item.text()

        # Ricrea griglia
        self.table.clear()
        self.table.setRowCount(rows)
        self.table.setColumnCount(cols)
        self.table.setHorizontalHeaderLabels([f"Col {i + 1}" for i in range(cols)])

        # Ripristina valori dove possibile
        from PyQt6.QtWidgets import QTableWidgetItem
        for r in range(rows):
            for c in range(cols):
                text = old_data.get((r, c), "")
                item = QTableWidgetItem(text)
                self.table.setItem(r, c, item)

    def get_block(self):
        from nModels.blocks.table import TableBlock, TableRowBlock
        from nTypes.rich_text import simple_rich_text_list

        rows = self.rows_spin.value()
        cols = self.cols_spin.value()

        cells = []
        for r in range(rows):
            row_cells = []
            for c in range(cols):
                item = self.table.item(r, c)
                text = item.text() if item else ""
                row_cells.append(simple_rich_text_list(text))
            cells.append(TableRowBlock.create(cells=row_cells))

        return TableBlock.create(
            table_width=cols,
            has_column_header=self.header_col.isChecked(),
            has_row_header=self.header_row.isChecked(),
            cells=cells
        )


class ToggleForm(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setSpacing(12)

        lay.addWidget(QLabel("Testo toggle:"))
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Titolo del blocco espandibile...")
        lay.addWidget(self.text_input)

        lay.addWidget(QLabel("Colore:"))
        self.color_combo = QComboBox()
        for c in ["default", "gray_background", "brown_background",
                  "orange_background", "yellow_background", "green_background",
                  "blue_background", "purple_background", "pink_background", "red_background"]:
            self.color_combo.addItem(c.replace("_", " ").title(), c)
        lay.addWidget(self.color_combo)

        info = QLabel("💡 Il toggle sarà vuoto. Potrai aggiungere blocchi figli in Notion.")
        info.setWordWrap(True)
        info.setStyleSheet("color: #787774; font-size: 11px;")
        lay.addWidget(info)
        lay.addStretch()

    def get_block(self):
        from nModels.blocks.list_blocks import Toggle
        text = self.text_input.text().strip()
        if not text:
            raise ValueError("Il testo non può essere vuoto")
        return Toggle.create(text=text, color=self.color_combo.currentData())


class ImageForm(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setSpacing(12)

        lay.addWidget(QLabel("URL immagine:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://esempio.com/immagine.jpg")
        lay.addWidget(self.url_input)

        lay.addWidget(QLabel("Caption (opzionale):"))
        self.caption_input = QLineEdit()
        self.caption_input.setPlaceholderText("Descrizione immagine...")
        lay.addWidget(self.caption_input)

        warning = QLabel("⚠ Solo URL esterni. L'API Notion non supporta upload diretto.")
        warning.setWordWrap(True)
        warning.setStyleSheet("color: #F87171; font-size: 11px;")
        lay.addWidget(warning)
        lay.addStretch()

    def get_block(self):
        from nModels.blocks.media import Image
        from nTypes.files import FileTypeExternal
        url = self.url_input.text().strip()
        if not url:
            raise ValueError("L'URL non può essere vuoto")
        if not url.startswith(("http://", "https://")):
            raise ValueError("L'URL deve iniziare con http:// o https://")

        caption = self.caption_input.text().strip()
        return Image.create(
            caption=caption,
            file_object=FileTypeExternal(url)
        )


class VideoForm(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setSpacing(12)

        lay.addWidget(QLabel("URL video:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://youtube.com/watch?v=...")
        lay.addWidget(self.url_input)

        lay.addWidget(QLabel("Caption (opzionale):"))
        self.caption_input = QLineEdit()
        self.caption_input.setPlaceholderText("Descrizione video...")
        lay.addWidget(self.caption_input)

        hint = QLabel("💡 Supporta: YouTube, Vimeo, Loom, URL diretti (.mp4, .webm)")
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #787774; font-size: 11px;")
        lay.addWidget(hint)
        lay.addStretch()

    def get_block(self):
        from nModels.blocks.media import Video
        url = self.url_input.text().strip()
        if not url:
            raise ValueError("L'URL non può essere vuoto")
        if not url.startswith(("http://", "https://")):
            raise ValueError("L'URL deve iniziare con http:// o https://")

        caption = self.caption_input.text().strip()
        return Video.create(url=url, caption=caption)


class EmbedForm(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setSpacing(12)

        lay.addWidget(QLabel("URL da embeddare:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://figma.com/file/...")
        lay.addWidget(self.url_input)

        examples = QLabel(
            "Esempi supportati:\n"
            "• Figma, Framer\n"
            "• Google Maps, Sheets, Docs\n"
            "• CodePen, JSFiddle\n"
            "• Miro, Whimsical\n"
            "• Twitter, Instagram"
        )
        examples.setWordWrap(True)
        examples.setStyleSheet("color: #787774; font-size: 11px;")
        lay.addWidget(examples)
        lay.addStretch()

    def get_block(self):
        from nModels.blocks.media import Embed
        url = self.url_input.text().strip()
        if not url:
            raise ValueError("L'URL non può essere vuoto")
        if not url.startswith(("http://", "https://")):
            raise ValueError("L'URL deve iniziare con http:// o https://")
        return Embed.create(url=url)


class FileForm(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setSpacing(12)

        lay.addWidget(QLabel("URL file:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://esempio.com/documento.pdf")
        lay.addWidget(self.url_input)

        lay.addWidget(QLabel("Caption (opzionale):"))
        self.caption_input = QLineEdit()
        self.caption_input.setPlaceholderText("Descrizione file...")
        lay.addWidget(self.caption_input)

        warning = QLabel("⚠ Solo file esterni. Formati: PDF, DOCX, XLSX, ZIP, etc.")
        warning.setWordWrap(True)
        warning.setStyleSheet("color: #F87171; font-size: 11px;")
        lay.addWidget(warning)
        lay.addStretch()

    def get_block(self):
        from nModels.blocks.media import File
        from nTypes.files import FileTypeExternal
        url = self.url_input.text().strip()
        if not url:
            raise ValueError("L'URL non può essere vuoto")
        if not url.startswith(("http://", "https://")):
            raise ValueError("L'URL deve iniziare con http:// o https://")

        caption = self.caption_input.text().strip()
        return File.create(
            caption=caption,
            file_object=FileTypeExternal(url)
        )


class TocForm(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setSpacing(12)

        lay.addWidget(QLabel("Colore:"))
        self.color_combo = QComboBox()
        for c in NColors:
            self.color_combo.addItem(c.name, c)
        lay.addWidget(self.color_combo)

        info = QLabel(
            "📋 Il Table of Contents genera automaticamente un indice "
            "basato sui blocchi Heading presenti nella pagina."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #787774; font-size: 11px;")
        lay.addWidget(info)
        lay.addStretch()

    def get_block(self):
        from nModels.blocks.special_blocks import TableOfContentsBlock
        return TableOfContentsBlock.create(color=self.color_combo.currentData())

# ── Dialog principale ─────────────────────────────────────────────

class InsertBlockDialog(QDialog):
    """
    Dialog per scegliere e configurare un blocco da inserire.
    Layout: sinistra = lista tipi, destra = form configurazione.
    """

    BLOCK_TYPES = [
        ("📝 Paragrafo", "paragraph", ParagraphForm),
        ("# Heading 1", "heading1", lambda: HeadingForm(1)),
        ("## Heading 2", "heading2", lambda: HeadingForm(2)),
        ("### Heading 3", "heading3", lambda: HeadingForm(3)),
        ("▶ Toggle", "toggle", ToggleForm),  # ← NUOVO
        ("☑ To-do", "todo", ToDoForm),
        ("• Elenco puntato", "bullet", BulletForm),
        ("1. Elenco numerato", "numbered", NumberedForm),
        ("💡 Callout", "callout", CalloutForm),
        ("</> Codice", "code", CodeForm),
        ("❝ Citazione", "quote", QuoteForm),
        ("➖ Divisore", "divider", DividerForm),
        ("🔗 Bookmark", "bookmark", BookmarkForm),
        ("🖼 Immagine", "image", ImageForm),  # ← NUOVO
        ("🎥 Video", "video", VideoForm),  # ← NUOVO
        ("🌐 Embed", "embed", EmbedForm),  # ← NUOVO
        ("📎 File", "file", FileForm),  # ← NUOVO
        ("📋 Indice (ToC)", "toc", TocForm),  # ← NUOVO
        ("∫ Equazione", "equation", EquationForm),
        ("⊞ Tabella", "table", TableForm),
    ]

    def __init__(self, page_title: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Inserisci blocco in: {page_title}")
        self.resize(700, 480)
        self._block = None
        self._build_ui()

    def _build_ui(self):
        main_lay = QHBoxLayout(self)
        main_lay.setSpacing(0)
        main_lay.setContentsMargins(0, 0, 0, 0)

        # ── Lista tipi blocco (sinistra) ──────────────────────────
        left = QWidget()
        left.setObjectName("Sidebar")
        left.setFixedWidth(220)
        left_lay = QVBoxLayout(left)
        left_lay.setContentsMargins(12, 16, 12, 16)
        left_lay.setSpacing(8)

        title = QLabel("Tipo blocco")
        title.setStyleSheet("font-weight: 700; font-size: 13px; color: #E8EEF9;")
        left_lay.addWidget(title)

        self._list = QListWidget()
        self._list.setSpacing(2)
        for label, key, _ in self.BLOCK_TYPES:
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, key)
            self._list.addItem(item)
        self._list.setCurrentRow(0)
        self._list.currentRowChanged.connect(self._on_type_changed)
        left_lay.addWidget(self._list)

        # ── Form configurazione (destra) ──────────────────────────
        right = QWidget()
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(24, 20, 24, 20)
        right_lay.setSpacing(16)

        self._form_title = QLabel()
        self._form_title.setStyleSheet("font-size: 16px; font-weight: 700;")
        right_lay.addWidget(self._form_title)

        self._stack = QStackedWidget()
        for _, _, form_cls in self.BLOCK_TYPES:
            self._stack.addWidget(form_cls())
        right_lay.addWidget(self._stack)

        # ── Pulsanti ──────────────────────────────────────────────
        btn_row = QWidget()
        btn_lay = QHBoxLayout(btn_row)
        btn_lay.setContentsMargins(0, 0, 0, 0)
        btn_lay.setSpacing(10)

        cancel_btn = QPushButton("Annulla")
        cancel_btn.clicked.connect(self.reject)

        self._ok_btn = QPushButton("✓ Inserisci")
        self._ok_btn.setObjectName("PrimaryBtn")
        self._ok_btn.setDefault(True)
        self._ok_btn.clicked.connect(self._on_insert)

        btn_lay.addStretch()
        btn_lay.addWidget(cancel_btn)
        btn_lay.addWidget(self._ok_btn)
        right_lay.addWidget(btn_row)

        main_lay.addWidget(left)
        main_lay.addWidget(right, stretch=1)

        # Inizializza vista
        self._on_type_changed(0)

    def _on_type_changed(self, index: int):
        if 0 <= index < len(self.BLOCK_TYPES):
            label, _, _ = self.BLOCK_TYPES[index]
            self._form_title.setText(label)
            self._stack.setCurrentIndex(index)

    def _on_insert(self):
        try:
            form = self._stack.currentWidget()
            self._block = form.get_block()
            self.accept()
        except ValueError as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Errore", str(e))
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Errore", f"Errore creazione blocco: {e}")

    def get_block(self):
        """Restituisce il blocco configurato (dopo accept())."""
        return self._block

