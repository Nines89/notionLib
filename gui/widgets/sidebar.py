"""
gui/widgets/sidebar.py
Pannello laterale sinistro: form di login o stato connesso.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame,
)
from PyQt6.QtCore import pyqtSignal, Qt


class SidebarWidget(QWidget):
    connect_requested    = pyqtSignal(str)
    disconnect_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setFixedWidth(240)
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignmentFlag.AlignTop)
        lay.setSpacing(0)
        lay.setContentsMargins(16, 24, 16, 16)

        logo = QLabel("🔮 Notion\nAutomation")
        logo.setObjectName("Title")
        lay.addWidget(logo)
        lay.addSpacing(4)
        lay.addWidget(self._sep())
        lay.addSpacing(20)

        self._login_area  = self._build_login_area()
        self._status_area = self._build_status_area()
        self._status_area.hide()

        lay.addWidget(self._login_area)
        lay.addWidget(self._status_area)
        lay.addStretch()

        hint = QLabel(
            "💡 In Notion apri ogni database\n"
            "   ··· → Connetti a →\n"
            "   seleziona la tua integrazione"
        )
        hint.setWordWrap(True)
        hint.setObjectName("Muted")
        lay.addWidget(hint)

    def _build_login_area(self) -> QWidget:
        w   = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)

        lbl = QLabel("API Key")
        lbl.setStyleSheet("font-weight: 600; font-size: 12px; color: #4D556B;")

        self._key_input = QLineEdit()
        self._key_input.setPlaceholderText("ntn_...")
        self._key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._key_input.setFixedHeight(36)
        self._key_input.returnPressed.connect(self._on_connect_clicked)

        self._connect_btn = QPushButton("Connetti")
        self._connect_btn.setObjectName("PrimaryBtn")
        self._connect_btn.setFixedHeight(36)
        self._connect_btn.clicked.connect(self._on_connect_clicked)

        self._error_lbl = QLabel()
        self._error_lbl.setWordWrap(True)
        self._error_lbl.setObjectName("Error")
        self._error_lbl.hide()

        api_hint = QLabel("Trovi la chiave su\nnotion.so/my-integrations")
        api_hint.setObjectName("Muted")

        lay.addWidget(lbl)
        lay.addWidget(self._key_input)
        lay.addWidget(self._connect_btn)
        lay.addWidget(self._error_lbl)
        lay.addSpacing(4)
        lay.addWidget(api_hint)
        return w

    def _build_status_area(self) -> QWidget:
        w   = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        self._bot_lbl = QLabel()
        self._bot_lbl.setStyleSheet("font-weight: 700; font-size: 13px; color: #27AE60;")

        self._summary_lbl = QLabel()
        self._summary_lbl.setStyleSheet("font-size: 12px; color: #787774;")

        disc_btn = QPushButton("Disconnetti")
        disc_btn.setFixedHeight(32)
        disc_btn.clicked.connect(self.disconnect_requested.emit)

        lay.addWidget(self._bot_lbl)
        lay.addWidget(self._summary_lbl)
        lay.addSpacing(8)
        lay.addWidget(disc_btn)
        return w

    @staticmethod
    def _sep() -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #E3E2DE;")
        return line

    def _on_connect_clicked(self):
        key = self._key_input.text().strip()
        if not key:
            self.show_error("Inserisci la chiave API.")
            return
        self._error_lbl.hide()
        self._connect_btn.setEnabled(False)
        self._connect_btn.setText("Connessione…")
        self.connect_requested.emit(key)

    def show_error(self, msg: str):
        self._connect_btn.setEnabled(True)
        self._connect_btn.setText("Connetti")
        self._error_lbl.setText(f"⚠ {msg}")
        self._error_lbl.show()

    def show_connected(self, bot_name: str, n_db: int, n_ds: int):
        self._bot_lbl.setText(f"✅  {bot_name}")
        self._summary_lbl.setText(f"{n_db} database · {n_ds} datasource")
        self._login_area.hide()
        self._status_area.show()

    def show_disconnected(self):
        self._status_area.hide()
        self._key_input.clear()
        self._connect_btn.setEnabled(True)
        self._connect_btn.setText("Connetti")
        self._error_lbl.hide()
        self._login_area.show()
