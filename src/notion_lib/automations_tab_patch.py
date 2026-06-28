"""
PATCH — gui/widgets/automations_tab.py

Modifica da applicare alla classe _HomeView:
Aggiunge una tile speciale "+" sempre in ultima posizione nella griglia
per creare nuove automazioni personalizzate.

─────────────────────────────────────────────────────────────────────
ISTRUZIONI DI INTEGRAZIONE
─────────────────────────────────────────────────────────────────────

1. Aggiungere la classe _AddTile PRIMA di _HomeView nel file originale.

2. In _HomeView._build_ui(), aggiungere self._add_tile_widget = None
   subito dopo self._tiles: list = []

3. Sostituire il metodo add_tile con la versione qui sotto.

4. Aggiungere il metodo set_add_callback alla classe _HomeView.

5. In AutomationsTab._build_ui(), dopo aver aggiunto self._home allo
   stack, aggiungere:
       self._home.set_add_callback(self._on_add_custom)

6. Aggiungere il metodo register_custom_tool e _on_add_custom
   alla classe AutomationsTab.
─────────────────────────────────────────────────────────────────────
"""

# ════════════════════════════════════════════════════════════════════
# 1. Nuova classe _AddTile  (aggiungere prima di _HomeView)
# ════════════════════════════════════════════════════════════════════

ADD_TILE_CLASS = '''
class _AddTile(QWidget):
    """Tile speciale per aggiungere una nuova automazione personalizzata."""

    def __init__(self, on_click, parent=None):
        super().__init__(parent)
        self._on_click = on_click
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(380, 220)
        self._build_ui()
        self._setup_shadow()
        self._apply_normal_style()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 28, 28, 28)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        plus = QLabel("+")
        plus.setStyleSheet(
            "font-size: 64px; font-weight: 300; color: #475569; "
            "background: transparent; border: none;"
        )
        plus.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl = QLabel("Nuova automazione")
        lbl.setStyleSheet(
            "font-size: 16px; font-weight: 600; color: #64748B; "
            "background: transparent; border: none;"
        )
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sub = QLabel("Crea il tuo script personalizzato")
        sub.setStyleSheet(
            "font-size: 12px; color: #334155; "
            "background: transparent; border: none;"
        )
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lay.addWidget(plus)
        lay.addWidget(lbl)
        lay.addWidget(sub)

    def _setup_shadow(self):
        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        from PyQt6.QtGui import QColor
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 50))
        self.setGraphicsEffect(shadow)

    def _apply_normal_style(self):
        self.setStyleSheet("""
            QWidget {
                background: #0F172A;
                border-radius: 18px;
                border: 2px dashed #1E293B;
            }
        """)

    def _apply_hover_style(self):
        self.setStyleSheet("""
            QWidget {
                background: #111827;
                border-radius: 18px;
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
'''


# ════════════════════════════════════════════════════════════════════
# 2. Sostituzione di _HomeView.add_tile
#    (versione che riposiziona la _AddTile sempre per ultima)
# ════════════════════════════════════════════════════════════════════

ADD_TILE_METHOD = '''
    def set_add_callback(self, callback):
        """Imposta il callback del tasto + e aggiunge la tile alla griglia."""
        self._add_tile_widget = _AddTile(callback)
        self._reposition_add_tile()

    def add_tile(self, icon: str, title: str, description: str,
                 gradient_start: str, gradient_end: str, on_click):
        tile = _ModernTile(icon, title, description, gradient_start, gradient_end, on_click)
        self._tiles.append(tile)
        self._reposition_tiles()

    def _reposition_tiles(self):
        """Ridisegna tutta la griglia: tile normali + _AddTile in fondo."""
        # Rimuove tutto dalla griglia senza distruggere i widget
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        for i, tile in enumerate(self._tiles):
            row, col = divmod(i, 2)
            self._grid.addWidget(tile, row, col)
            tile.show()

        self._reposition_add_tile()

    def _reposition_add_tile(self):
        if self._add_tile_widget is None:
            return
        self._add_tile_widget.setParent(None)
        next_pos = len(self._tiles)
        row, col = divmod(next_pos, 2)
        self._grid.addWidget(self._add_tile_widget, row, col)
        self._add_tile_widget.show()
'''


# ════════════════════════════════════════════════════════════════════
# 3. Nuovi metodi da aggiungere ad AutomationsTab
# ════════════════════════════════════════════════════════════════════

AUTO_TAB_METHODS = '''
    def register_custom_tool(self, slug: str, icon: str, title: str,
                              description: str, gradient_start: str,
                              gradient_end: str, tool_widget):
        """
        Come register_tool ma per automazioni custom.
        Espone lo slug per identificazione futura (es. delete).
        """
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

    def set_add_custom_callback(self, callback):
        """Collega il tasto + della home al callback esterno (MainWindow)."""
        self._home.set_add_callback(callback)
'''
