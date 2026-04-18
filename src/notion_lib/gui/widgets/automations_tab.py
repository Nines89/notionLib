"""
gui/widgets/automations_tab.py
Tab Automazioni — home moderna con tile + navigazione a stack.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGridLayout, QStackedWidget, QFrame,
    QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, pyqtProperty
from PyQt6.QtGui import QFont, QColor


# ─── Tile moderna (proporzioni migliorate) ────────────────────

class _ModernTile(QWidget):
    """Card con gradient, shadow e animazioni."""

    def __init__(self, icon: str, title: str, description: str,
                 gradient_start: str, gradient_end: str,
                 on_click, parent=None):
        super().__init__(parent)
        self._on_click = on_click
        self._gradient_start = gradient_start
        self._gradient_end = gradient_end
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(380, 220)  # ← Più grande
        self._build_ui(icon, title, description)
        self._setup_shadow()
        self._setup_animation()
        self._apply_normal_style()

    def _build_ui(self, icon, title, description):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 28, 28, 28)  # ← Più padding
        lay.setSpacing(14)

        # Icona grande e visibile
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(
            "font-size: 56px; background: transparent; border: none;"  # ← Più grande
        )

        # Titolo
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(
            "font-size: 20px; font-weight: 700; "  # ← Leggermente più grande
            "color: #FFFFFF; background: transparent; border: none;"
        )
        title_lbl.setWordWrap(True)

        # Descrizione
        desc_lbl = QLabel(description)
        desc_lbl.setStyleSheet(
            "font-size: 13px; color: rgba(255,255,255,0.9); "
            "background: transparent; border: none; line-height: 1.5;"
        )
        desc_lbl.setWordWrap(True)
        desc_lbl.setMaximumHeight(60)  # ← Limita altezza descrizione

        # Badge "BETA"
        badge = QLabel("BETA")
        badge.setStyleSheet(
            "background: rgba(255,255,255,0.25); color: #FFF; "
            "border: 1.5px solid rgba(255,255,255,0.4); border-radius: 10px; "
            "padding: 4px 12px; font-size: 10px; font-weight: 700; "
            "letter-spacing: 1.2px;"
        )
        badge.setFixedHeight(24)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lay.addWidget(icon_lbl)
        lay.addWidget(title_lbl)
        lay.addWidget(desc_lbl)
        lay.addStretch()
        lay.addWidget(badge, alignment=Qt.AlignmentFlag.AlignLeft)

    def _setup_shadow(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)  # ← Shadow più pronunciata
        shadow.setXOffset(0)
        shadow.setYOffset(6)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)

    def _setup_animation(self):
        self._anim = QPropertyAnimation(self, b"geometry")
        self._anim.setDuration(200)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def _apply_normal_style(self):
        self.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {self._gradient_start}, 
                    stop:1 {self._gradient_end});
                border-radius: 18px;  /* ← Angoli più arrotondati */
                border: 1px solid rgba(255,255,255,0.15);
            }}
        """)

    def _apply_hover_style(self):
        self.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {self._gradient_start}, 
                    stop:1 {self._gradient_end});
                border-radius: 18px;
                border: 2px solid rgba(255,255,255,0.35);
            }}
        """)

    def enterEvent(self, event):
        self._apply_hover_style()
        current = self.geometry()
        self._anim.setStartValue(current)
        self._anim.setEndValue(QRect(
            current.x(), current.y() - 6,  # ← Lift più pronunciato
            current.width(), current.height()
        ))
        self._anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._apply_normal_style()
        current = self.geometry()
        self._anim.setStartValue(current)
        self._anim.setEndValue(QRect(
            current.x(), current.y() + 6,
            current.width(), current.height()
        ))
        self._anim.start()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._on_click()
        super().mousePressEvent(event)


# ─── Home view con hero migliorato ────────────────────────────

class _HomeView(QWidget):
    """Griglia con hero header proporzionato."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._tiles: list = []

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(36, 36, 36, 36)
        lay.setSpacing(32)

        # ── Hero section bilanciato ───────────────────────────────
        hero = QWidget()
        hero.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
            "stop:0 #1E3A8A, stop:1 #3B82F6); "
            "border-radius: 20px;"
        )
        hero.setFixedHeight(240)  # ← Altezza fissa per proporzioni
        hero_lay = QVBoxLayout(hero)
        hero_lay.setContentsMargins(40, 36, 40, 36)
        hero_lay.setSpacing(16)

        hero_icon = QLabel("⚡")
        hero_icon.setStyleSheet("font-size: 64px; background: transparent;")

        hero_title = QLabel("Automazioni intelligenti")
        hero_title.setStyleSheet(
            "font-size: 36px; font-weight: 800; color: #FFFFFF; "
            "background: transparent; letter-spacing: -1px;"
        )

        hero_subtitle = QLabel(
            "Trasforma, sincronizza e ottimizza i tuoi dati Notion "
            "con pipeline configurabili in pochi click."
        )
        hero_subtitle.setWordWrap(True)
        hero_subtitle.setStyleSheet(
            "font-size: 16px; color: rgba(255,255,255,0.95); "
            "background: transparent; line-height: 1.6;"
        )
        hero_subtitle.setMaximumWidth(680)

        hero_lay.addWidget(hero_icon)
        hero_lay.addWidget(hero_title)
        hero_lay.addWidget(hero_subtitle)
        hero_lay.addStretch()

        lay.addWidget(hero)

        # ── Sezione moduli ────────────────────────────────────────
        section_title = QLabel("Moduli disponibili")
        section_title.setStyleSheet(
            "font-size: 13px; font-weight: 700; color: #64748B; "
            "text-transform: uppercase; letter-spacing: 1.2px; "
            "margin-top: 4px;"
        )
        lay.addWidget(section_title)

        self._grid = QGridLayout()
        self._grid.setSpacing(24)  # ← Più spazio tra le tile
        self._grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        lay.addLayout(self._grid)

        lay.addStretch()

    def add_tile(self, icon: str, title: str, description: str,
                 gradient_start: str, gradient_end: str, on_click):
        tile = _ModernTile(icon, title, description, gradient_start, gradient_end, on_click)
        count = len(self._tiles)
        row, col = divmod(count, 2)  # 2 colonne
        self._grid.addWidget(tile, row, col)
        self._tiles.append(tile)


# ─── Tool view wrapper ────────────────────────────────────────────

class _ToolView(QWidget):
    """Wrapper per tool con header moderno."""

    def __init__(self, icon: str, title: str,
                 tool_widget: QWidget, on_back, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # ── Header moderno ────────────────────────────────────────
        header = QWidget()
        header.setFixedHeight(70)
        header.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:0, y2:1, "
            "stop:0 #0F172A, stop:1 #1E293B); "
            "border-bottom: 2px solid #334155;"
        )
        hlay = QHBoxLayout(header)
        hlay.setContentsMargins(24, 0, 24, 0)
        hlay.setSpacing(16)

        back_btn = QPushButton("← Tutti i flussi")
        back_btn.setStyleSheet(
            "QPushButton { "
            "background: rgba(34, 211, 238, 0.1); "
            "border: 1px solid rgba(34, 211, 238, 0.3); "
            "border-radius: 8px; color: #22D3EE; "
            "font-size: 13px; font-weight: 600; padding: 8px 16px; }"
            "QPushButton:hover { "
            "background: rgba(34, 211, 238, 0.2); "
            "border-color: #22D3EE; }"
        )
        back_btn.clicked.connect(on_back)

        header_icon = QLabel(icon)
        header_icon.setStyleSheet("font-size: 28px; background: transparent;")

        header_title = QLabel(title)
        header_title.setStyleSheet(
            "font-size: 20px; font-weight: 700; color: #E8EEF9; "
            "background: transparent;"
        )

        hlay.addWidget(back_btn)
        hlay.addWidget(header_icon)
        hlay.addWidget(header_title)
        hlay.addStretch()
        lay.addWidget(header)

        # ── Tool ──────────────────────────────────────────────────
        lay.addWidget(tool_widget)


# ─── AutomationsTab ───────────────────────────────────────────────

class AutomationsTab(QWidget):
    """Tab con home moderna + stack per tool."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self._stack = QStackedWidget()
        self._home = _HomeView()
        self._stack.addWidget(self._home)
        lay.addWidget(self._stack)

    def register_tool(self, icon: str, title: str,
                      description: str, gradient_start: str,
                      gradient_end: str, tool_widget: QWidget):
        """Registra un tool con gradiente personalizzato."""
        def open_tool():
            self._stack.setCurrentIndex(idx)

        def go_back():
            self._stack.setCurrentIndex(0)

        wrapped = _ToolView(icon, title, tool_widget, on_back=go_back)
        idx = self._stack.addWidget(wrapped)
        self._home.add_tile(icon, title, description, gradient_start, gradient_end, on_click=open_tool)