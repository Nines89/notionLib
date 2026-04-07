"""
gui/widgets/automations_tab.py
Tab Automazioni — home con tile + navigazione a stack.

Struttura interna:
  QStackedWidget
    ├── page 0: HomeView  (griglia di tile)
    └── page N: ogni tool (aggiunto dinamicamente)

Per aggiungere un nuovo tool basta chiamare register_tool().
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGridLayout, QStackedWidget, QFrame,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


# ─── Tile ─────────────────────────────────────────────────────────────────────

class _Tile(QWidget):
    """
    Card cliccabile che rappresenta un'automazione.
    Mostra icona, titolo e descrizione breve.
    """

    def __init__(self, icon: str, title: str, description: str,
                 on_click, parent=None):
        super().__init__(parent)
        self._on_click = on_click
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(220, 150)
        self._build_ui(icon, title, description)
        self._set_normal_style()

    def _build_ui(self, icon, title, description):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 18, 18, 18)
        lay.setSpacing(8)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 28px; background: transparent;")

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(
            "font-size: 13px; font-weight: 700; "
            "color: #1A1A1A; background: transparent;"
        )
        title_lbl.setWordWrap(True)

        desc_lbl = QLabel(description)
        desc_lbl.setStyleSheet(
            "font-size: 11px; color: #787774; background: transparent;"
        )
        desc_lbl.setWordWrap(True)

        lay.addWidget(icon_lbl)
        lay.addWidget(title_lbl)
        lay.addWidget(desc_lbl)
        lay.addStretch()

    def _set_normal_style(self):
        self.setStyleSheet(
            "QWidget { background: white; border: 1px solid #E3E2DE; "
            "border-radius: 12px; }"
        )

    def _set_hover_style(self):
        self.setStyleSheet(
            "QWidget { background: #F7F7F5; border: 1.5px solid #2F80ED; "
            "border-radius: 12px; }"
        )

    def enterEvent(self, event):
        self._set_hover_style()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._set_normal_style()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._on_click()
        super().mousePressEvent(event)


# ─── Home view ────────────────────────────────────────────────────────────────

class _HomeView(QWidget):
    """Griglia di tile — schermata principale della tab."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._tiles: list = []

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(20)

        title = QLabel("Automazioni")
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #1A1A1A;")
        lay.addWidget(title)

        subtitle = QLabel("Scegli uno strumento per iniziare.")
        subtitle.setStyleSheet("font-size: 13px; color: #787774;")
        lay.addWidget(subtitle)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #E3E2DE;")
        lay.addWidget(sep)

        self._grid = QGridLayout()
        self._grid.setSpacing(16)
        self._grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        lay.addLayout(self._grid)
        lay.addStretch()

    def add_tile(self, icon: str, title: str, description: str, on_click):
        tile  = _Tile(icon, title, description, on_click)
        count = len(self._tiles)
        row, col = divmod(count, 3)
        self._grid.addWidget(tile, row, col)
        self._tiles.append(tile)


# ─── Tool view wrapper ────────────────────────────────────────────────────────

class _ToolView(QWidget):
    """
    Wrapper per ogni tool: aggiunge header con ← Indietro e titolo,
    e mette il widget del tool sotto.
    """

    def __init__(self, icon: str, title: str,
                 tool_widget: QWidget, on_back, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # ── Header ────────────────────────────────────────────────
        header = QWidget()
        header.setFixedHeight(48)
        header.setStyleSheet(
            "background: white; border-bottom: 1px solid #E3E2DE;"
        )
        hlay = QHBoxLayout(header)
        hlay.setContentsMargins(16, 0, 16, 0)
        hlay.setSpacing(12)

        back_btn = QPushButton("← Indietro")
        back_btn.setStyleSheet(
            "QPushButton { background: transparent; border: none; "
            "color: #2F80ED; font-size: 13px; font-weight: 600; }"
            "QPushButton:hover { color: #1A6DD4; }"
        )
        back_btn.clicked.connect(on_back)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet("color: #E3E2DE;")
        sep.setFixedHeight(20)

        header_title = QLabel(f"{icon}  {title}")
        header_title.setStyleSheet(
            "font-size: 14px; font-weight: 600; color: #1A1A1A;"
        )

        hlay.addWidget(back_btn)
        hlay.addWidget(sep)
        hlay.addWidget(header_title)
        hlay.addStretch()
        lay.addWidget(header)

        # ── Tool ──────────────────────────────────────────────────
        lay.addWidget(tool_widget)


# ─── AutomationsTab ───────────────────────────────────────────────────────────

class AutomationsTab(QWidget):
    """
    Tab principale con navigazione a stack:
      - indice 0: HomeView (tile)
      - indici 1+: tool registrati
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self._stack = QStackedWidget()
        self._home  = _HomeView()
        self._stack.addWidget(self._home)   # indice 0 = home
        lay.addWidget(self._stack)

    # ── API pubblica ──────────────────────────────────────────────

    def register_tool(self, icon: str, title: str,
                      description: str, tool_widget: QWidget):
        """
        Registra un tool: aggiunge la tile alla home
        e il widget allo stack.
        """
        def open_tool():
            self._stack.setCurrentIndex(idx)

        def go_back():
            self._stack.setCurrentIndex(0)

        wrapped = _ToolView(icon, title, tool_widget, on_back=go_back)
        idx     = self._stack.addWidget(wrapped)
        self._home.add_tile(icon, title, description, on_click=open_tool)
