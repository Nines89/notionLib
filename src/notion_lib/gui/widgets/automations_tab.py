"""
gui/widgets/automations_tab.py
Tab Automazioni — home moderna con tile + navigazione a stack.

MODIFICHE:
- Hero compatto (altezza 120px, no icona gigante)
- _HomeView wrappata in QScrollArea
- Tile 300x170 (era 380x220), 3 colonne (era 2)
- Grid spacing 16px (era 24px)
- Tile _AddTile stesso formato delle altre
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGridLayout, QStackedWidget, QFrame,
    QGraphicsDropShadowEffect, QScrollArea, QMenu, QMessageBox,
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QAction


# ─── Tile moderna ────────────────────────────────────────────────

class _ModernTile(QWidget):
    """Card con gradient, shadow e animazioni. 300×170, 3 per riga."""

    def __init__(self, icon: str, title: str, description: str,
                 gradient_start: str, gradient_end: str,
                 on_click, parent=None):
        super().__init__(parent)
        self._on_click = on_click
        self._gradient_start = gradient_start
        self._gradient_end = gradient_end
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(300, 170)
        self._build_ui(icon, title, description)
        self._setup_shadow()
        self._setup_animation()
        self._apply_normal_style()

    def _build_ui(self, icon, title, description):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(8)

        header = QHBoxLayout()
        header.setSpacing(10)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(
            "font-size: 28px; background: transparent; border: none;"
        )
        icon_lbl.setFixedWidth(36)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(
            "font-size: 15px; font-weight: 700; "
            "color: #FFFFFF; background: transparent; border: none;"
        )
        title_lbl.setWordWrap(True)

        header.addWidget(icon_lbl)
        header.addWidget(title_lbl, 1)

        desc_lbl = QLabel(description)
        desc_lbl.setStyleSheet(
            "font-size: 11px; color: rgba(255,255,255,0.85); "
            "background: transparent; border: none; line-height: 1.4;"
        )
        desc_lbl.setWordWrap(True)
        desc_lbl.setMaximumHeight(52)

        badge = QLabel("BETA")
        badge.setStyleSheet(
            "background: rgba(255,255,255,0.2); color: #FFF; "
            "border: 1px solid rgba(255,255,255,0.35); border-radius: 8px; "
            "padding: 2px 8px; font-size: 9px; font-weight: 700; "
            "letter-spacing: 1px;"
        )
        badge.setFixedHeight(20)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lay.addLayout(header)
        lay.addWidget(desc_lbl)
        lay.addStretch()
        lay.addWidget(badge, alignment=Qt.AlignmentFlag.AlignLeft)

    def _setup_shadow(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(18)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 70))
        self.setGraphicsEffect(shadow)

    def _setup_animation(self):
        self._anim = QPropertyAnimation(self, b"geometry")
        self._anim.setDuration(180)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def _apply_normal_style(self):
        self.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {self._gradient_start},
                    stop:1 {self._gradient_end});
                border-radius: 14px;
                border: 1px solid rgba(255,255,255,0.12);
            }}
        """)

    def _apply_hover_style(self):
        self.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {self._gradient_start},
                    stop:1 {self._gradient_end});
                border-radius: 14px;
                border: 2px solid rgba(255,255,255,0.30);
            }}
        """)

    def enterEvent(self, event):
        self._apply_hover_style()
        current = self.geometry()
        self._anim.setStartValue(current)
        self._anim.setEndValue(QRect(
            current.x(), current.y() - 4,
            current.width(), current.height()
        ))
        self._anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._apply_normal_style()
        current = self.geometry()
        self._anim.setStartValue(current)
        self._anim.setEndValue(QRect(
            current.x(), current.y() + 4,
            current.width(), current.height()
        ))
        self._anim.start()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._on_click()
        super().mousePressEvent(event)


# ─── Tile custom (con menu contestuale elimina) ───────────────────

class _CustomTile(_ModernTile):
    """
    Tile per automazioni custom.
    Tasto destro → menu contestuale con voce "Elimina".
    Emette delete_requested(slug) dopo conferma utente.
    """
    delete_requested = pyqtSignal(str)

    def __init__(self, slug: str, icon: str, title: str, description: str,
                 gradient_start: str, gradient_end: str, on_click, parent=None):
        super().__init__(icon, title, description, gradient_start, gradient_end, on_click, parent)
        self._slug = slug
        self._title = title
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def _show_context_menu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background: #10192B;
                border: 1px solid #23314B;
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item {
                padding: 7px 18px;
                border-radius: 4px;
                font-size: 13px;
                color: #E7EEFA;
            }
            QMenu::item:selected { background: #351A28; color: #F87171; }
        """)

        header_act = QAction(f"  {self._title}", menu)
        header_act.setEnabled(False)
        menu.addAction(header_act)
        menu.addSeparator()

        del_act = QAction("🗑  Elimina automazione", menu)
        del_act.triggered.connect(self._confirm_delete)
        menu.addAction(del_act)

        menu.exec(self.mapToGlobal(pos))

    def _confirm_delete(self):
        reply = QMessageBox.question(
            self,
            "Elimina automazione",
            f"Eliminare «{self._title}»?\n\nLo script su disco verrà rimosso definitivamente.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.delete_requested.emit(self._slug)


# ─── Tile "Aggiungi" ─────────────────────────────────────────────

class _AddTile(QWidget):
    """Tile speciale per aggiungere una nuova automazione. Stesso formato delle altre."""

    def __init__(self, on_click, parent=None):
        super().__init__(parent)
        self._on_click = on_click
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(300, 170)
        self._build_ui()
        self._setup_shadow()
        self._apply_normal_style()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        plus = QLabel("+")
        plus.setStyleSheet(
            "font-size: 40px; font-weight: 300; color: #475569; "
            "background: transparent; border: none;"
        )
        plus.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl = QLabel("Nuova automazione")
        lbl.setStyleSheet(
            "font-size: 13px; font-weight: 600; color: #64748B; "
            "background: transparent; border: none;"
        )
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sub = QLabel("Crea uno script personalizzato")
        sub.setStyleSheet(
            "font-size: 11px; color: #334155; "
            "background: transparent; border: none;"
        )
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lay.addWidget(plus)
        lay.addSpacing(4)
        lay.addWidget(lbl)
        lay.addWidget(sub)

    def _setup_shadow(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(14)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.setGraphicsEffect(shadow)

    def _apply_normal_style(self):
        self.setStyleSheet("""
            QWidget {
                background: #0F172A;
                border-radius: 14px;
                border: 2px dashed #1E293B;
            }
        """)

    def _apply_hover_style(self):
        self.setStyleSheet("""
            QWidget {
                background: #111827;
                border-radius: 14px;
                border: 2px dashed #334155;
            }
        """)

    def enterEvent(self, event):
        self._apply_hover_style()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._apply_normal_style()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._on_click()
        super().mousePressEvent(event)


# ─── Home view ────────────────────────────────────────────────────

class _HomeView(QWidget):
    """
    Griglia 3 colonne con hero compatto.
    Wrappata esternamente in QScrollArea da AutomationsTab.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tiles: list = []           # tutte le tile (_ModernTile o _CustomTile)
        self._custom_tiles: dict = {}    # slug -> _CustomTile
        self._add_tile_widget = None
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 24, 28, 28)
        lay.setSpacing(20)

        # ── Hero compatto ─────────────────────────────────────────
        hero = QWidget()
        hero.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
            "stop:0 #1E3A8A, stop:1 #3B82F6); "
            "border-radius: 16px;"
        )
        hero.setFixedHeight(110)
        hero_lay = QHBoxLayout(hero)
        hero_lay.setContentsMargins(28, 0, 28, 0)
        hero_lay.setSpacing(16)

        icon_lbl = QLabel("⚡")
        icon_lbl.setStyleSheet("font-size: 32px; background: transparent;")
        icon_lbl.setFixedWidth(44)

        text_col = QVBoxLayout()
        text_col.setSpacing(4)

        hero_title = QLabel("Automazioni intelligenti")
        hero_title.setStyleSheet(
            "font-size: 22px; font-weight: 800; color: #FFFFFF; "
            "background: transparent; letter-spacing: -0.5px;"
        )

        hero_subtitle = QLabel(
            "Trasforma, sincronizza e ottimizza i tuoi dati Notion "
            "con pipeline configurabili in pochi click."
        )
        hero_subtitle.setWordWrap(True)
        hero_subtitle.setStyleSheet(
            "font-size: 12px; color: rgba(255,255,255,0.88); "
            "background: transparent;"
        )

        text_col.addWidget(hero_title)
        text_col.addWidget(hero_subtitle)

        hero_lay.addWidget(icon_lbl)
        hero_lay.addLayout(text_col, 1)
        lay.addWidget(hero)

        # ── Label sezione ─────────────────────────────────────────
        section_title = QLabel("Moduli disponibili")
        section_title.setStyleSheet(
            "font-size: 11px; font-weight: 700; color: #64748B; "
            "text-transform: uppercase; letter-spacing: 1px;"
        )
        lay.addWidget(section_title)

        # ── Griglia 3 colonne ─────────────────────────────────────
        self._grid = QGridLayout()
        self._grid.setSpacing(16)
        self._grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        lay.addLayout(self._grid)

        lay.addStretch()

    # ── API pubblica ──────────────────────────────────────────────

    def set_add_callback(self, callback):
        self._add_tile_widget = _AddTile(callback)
        self._reposition_add_tile()

    def add_tile(self, icon: str, title: str, description: str,
                 gradient_start: str, gradient_end: str, on_click):
        """Aggiunge una tile standard (non eliminabile)."""
        tile = _ModernTile(icon, title, description, gradient_start, gradient_end, on_click)
        self._tiles.append(tile)
        self._reposition_tiles()

    def add_custom_tile(self, slug: str, icon: str, title: str, description: str,
                        gradient_start: str, gradient_end: str,
                        on_click, on_delete) -> "_CustomTile":
        """
        Aggiunge una tile custom (eliminabile).
        on_delete(slug) viene chiamato dopo la conferma utente.
        """
        tile = _CustomTile(slug, icon, title, description, gradient_start, gradient_end, on_click)
        tile.delete_requested.connect(on_delete)
        self._tiles.append(tile)
        self._custom_tiles[slug] = tile
        self._reposition_tiles()
        return tile

    def remove_custom_tile(self, slug: str):
        """Rimuove la tile con il dato slug dalla griglia e dalla memoria."""
        tile = self._custom_tiles.pop(slug, None)
        if tile is None:
            return
        if tile in self._tiles:
            self._tiles.remove(tile)
        tile.setParent(None)
        tile.deleteLater()
        self._reposition_tiles()

    # ── Layout interno ────────────────────────────────────────────

    # 3 colonne invece di 2
    _COLS = 3

    def _reposition_tiles(self):
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        for i, tile in enumerate(self._tiles):
            row, col = divmod(i, self._COLS)
            self._grid.addWidget(tile, row, col)
            tile.show()

        self._reposition_add_tile()

    def _reposition_add_tile(self):
        if self._add_tile_widget is None:
            return
        self._add_tile_widget.setParent(None)
        next_pos = len(self._tiles)
        row, col = divmod(next_pos, self._COLS)
        self._grid.addWidget(self._add_tile_widget, row, col)
        self._add_tile_widget.show()


# ─── Tool view wrapper ────────────────────────────────────────────

class _ToolView(QWidget):
    """Wrapper per tool con header moderno. on_delete opzionale per tool custom."""

    def __init__(self, icon: str, title: str,
                 tool_widget: QWidget, on_back,
                 on_delete=None, parent=None):
        super().__init__(parent)
        self._on_delete = on_delete
        self._title = title
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # ── Header ────────────────────────────────────────────────
        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:0, y2:1, "
            "stop:0 #0F172A, stop:1 #1E293B); "
            "border-bottom: 2px solid #334155;"
        )
        hlay = QHBoxLayout(header)
        hlay.setContentsMargins(20, 0, 20, 0)
        hlay.setSpacing(12)

        back_btn = QPushButton("← Tutti i flussi")
        back_btn.setStyleSheet(
            "QPushButton { "
            "background: rgba(34,211,238,0.1); "
            "border: 1px solid rgba(34,211,238,0.3); "
            "border-radius: 8px; color: #22D3EE; "
            "font-size: 13px; font-weight: 600; padding: 7px 14px; }"
            "QPushButton:hover { "
            "background: rgba(34,211,238,0.2); border-color: #22D3EE; }"
        )
        back_btn.clicked.connect(on_back)

        header_icon = QLabel(icon)
        header_icon.setStyleSheet("font-size: 24px; background: transparent;")

        header_title = QLabel(title)
        header_title.setStyleSheet(
            "font-size: 18px; font-weight: 700; color: #E8EEF9; background: transparent;"
        )

        hlay.addWidget(back_btn)
        hlay.addWidget(header_icon)
        hlay.addWidget(header_title)
        hlay.addStretch()

        # Bottone elimina — solo per tool custom
        if on_delete is not None:
            del_btn = QPushButton("🗑  Elimina")
            del_btn.setStyleSheet(
                "QPushButton { "
                "background: rgba(248,113,113,0.1); "
                "border: 1px solid rgba(248,113,113,0.3); "
                "border-radius: 8px; color: #F87171; "
                "font-size: 12px; font-weight: 600; padding: 7px 14px; }"
                "QPushButton:hover { "
                "background: rgba(248,113,113,0.22); border-color: #F87171; }"
            )
            del_btn.clicked.connect(self._confirm_delete)
            hlay.addWidget(del_btn)

        lay.addWidget(header)
        lay.addWidget(tool_widget)

    def _confirm_delete(self):
        reply = QMessageBox.question(
            self,
            "Elimina automazione",
            f"Eliminare «{self._title}»?\n\nLo script su disco verrà rimosso definitivamente.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if reply == QMessageBox.StandardButton.Yes and self._on_delete:
            self._on_delete()


# ─── AutomationsTab ───────────────────────────────────────────────

class AutomationsTab(QWidget):
    """Tab con home scrollabile + stack per i tool."""

    # Emesso verso MainWindow dopo conferma eliminazione
    custom_deleted = pyqtSignal(str)   # slug

    def __init__(self, parent=None):
        super().__init__(parent)
        # slug -> indice nello stack (per rimozione)
        self._custom_stack_idx: dict[str, int] = {}
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self._stack = QStackedWidget()

        self._home = _HomeView()
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet(
            "QScrollArea { background: transparent; }"
            "QScrollBar:vertical { background: transparent; width: 6px; }"
            "QScrollBar::handle:vertical { background: #1E293B; border-radius: 3px; min-height: 20px; }"
            "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }"
        )
        self._scroll.setWidget(self._home)

        self._stack.addWidget(self._scroll)   # indice 0 = home
        lay.addWidget(self._stack)

    # ── Tool standard ─────────────────────────────────────────────

    def register_tool(self, icon: str, title: str,
                      description: str, gradient_start: str,
                      gradient_end: str, tool_widget: QWidget):
        """Registra un tool built-in (non eliminabile)."""
        def open_tool():
            self._stack.setCurrentIndex(idx)

        def go_back():
            self._stack.setCurrentIndex(0)

        wrapped = _ToolView(icon, title, tool_widget, on_back=go_back)
        idx = self._stack.addWidget(wrapped)
        self._home.add_tile(
            icon, title, description,
            gradient_start, gradient_end,
            on_click=open_tool,
        )

    # ── Tool custom ───────────────────────────────────────────────

    def register_custom_tool(self, slug: str, icon: str, title: str,
                              description: str, gradient_start: str,
                              gradient_end: str, tool_widget):
        """
        Registra un tool custom con supporto eliminazione.
        - Tile: tasto destro → "Elimina" con conferma
        - Header: bottone "🗑 Elimina" con conferma
        Entrambi emettono custom_deleted(slug) verso MainWindow.
        """
        def open_tool():
            self._stack.setCurrentIndex(idx)

        def go_back():
            self._stack.setCurrentIndex(0)

        wrapped = _ToolView(
            icon, title, tool_widget,
            on_back=go_back,
            on_delete=lambda s=slug: self._remove_custom_tool(s),
        )
        idx = self._stack.addWidget(wrapped)
        self._custom_stack_idx[slug] = idx

        self._home.add_custom_tile(
            slug, icon, title, description,
            gradient_start, gradient_end,
            on_click=open_tool,
            on_delete=lambda s=slug: self._remove_custom_tool(s),
        )

    def _remove_custom_tool(self, slug: str):
        """
        Rimuove tile, torna alla home, rimuove widget dallo stack,
        poi notifica MainWindow via custom_deleted.

        QStackedWidget.removeWidget() compatta gli indici successivi:
        ricalcoliamo _custom_stack_idx per tutti gli slug rimasti
        per evitare che puntino a widget sbagliati.
        """
        # 1. Torna alla home prima di rimuovere lo widget corrente
        self._stack.setCurrentIndex(0)

        # 2. Rimuovi widget dallo stack
        idx = self._custom_stack_idx.pop(slug, None)
        if idx is not None:
            widget = self._stack.widget(idx)
            if widget:
                self._stack.removeWidget(widget)
                widget.deleteLater()
                # Decrementa gli indici di tutti gli slug rimasti che
                # puntavano a una posizione successiva a quella rimossa
                for s, i in self._custom_stack_idx.items():
                    if i > idx:
                        self._custom_stack_idx[s] = i - 1

        # 3. Rimuovi tile dalla home
        self._home.remove_custom_tile(slug)

        # 4. Notifica MainWindow (che chiama CustomAutomationManager.delete)
        self.custom_deleted.emit(slug)

    # ── Home callback ─────────────────────────────────────────────

    def set_add_custom_callback(self, callback):
        """Collega il tasto + della home al callback esterno (MainWindow)."""
        self._home.set_add_callback(callback)
