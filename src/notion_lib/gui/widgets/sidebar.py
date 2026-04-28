"""
gui/widgets/sidebar.py
Pannello laterale sinistro: form di login o stato connesso.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QComboBox, QHBoxLayout,
)
from PyQt6.QtCore import pyqtSignal, Qt

from notion_lib.client.keystore import (
    save_key, get_key, delete_key,
    list_profiles, save_profile_name, remove_profile_name
)


class SidebarWidget(QWidget):
    connect_requested    = pyqtSignal(str)
    disconnect_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setFixedWidth(290)
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignmentFlag.AlignTop)
        lay.setSpacing(0)
        lay.setContentsMargins(18, 24, 18, 16)

        logo = QLabel("NOVA CONTROL")
        logo.setObjectName("Title")
        lay.addWidget(logo)
        chip = QLabel("● ONLINE WORKSPACE DESIGN")
        chip.setStyleSheet(
            "font-size: 10px; font-weight: 700; letter-spacing: 0.8px; "
            "padding: 5px 8px; border-radius: 8px; color: #22D3EE; "
            "background: #102B38; border: 1px solid #1E495F;"
        )
        lay.addWidget(chip)
        lay.addSpacing(8)
        lay.addWidget(self._sep())
        lay.addSpacing(20)

        self._login_area  = self._build_login_area()
        self._status_area = self._build_status_area()
        self._status_area.hide()

        lay.addWidget(self._login_area)
        lay.addWidget(self._status_area)
        lay.addStretch()

        hint = QLabel(
            "💡 Suggerimento rapido\n"
            "Apri ogni database in Notion →\n"
            "⋯ → Connetti a → integrazione"
        )
        hint.setWordWrap(True)
        hint.setObjectName("Muted")
        lay.addWidget(hint)

    def _build_login_area(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setSpacing(8)

        profile_lbl = QLabel("Profilo salvato")
        profile_lbl.setStyleSheet("font-weight: 700; font-size: 11px; color: #A3B3CE;")

        self._profile_combo = QComboBox()
        self._profile_combo.setFixedHeight(36)
        self._profile_combo.addItem("— Nuovo profilo —", None)
        for name in list_profiles():
            self._profile_combo.addItem(name, name)
        self._profile_combo.currentIndexChanged.connect(self._on_profile_selected)

        name_lbl = QLabel("Nome profilo")
        name_lbl.setStyleSheet("font-weight: 700; font-size: 11px; color: #A3B3CE;")
        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("Es: Workspace personale")
        self._name_input.setFixedHeight(36)

        key_lbl = QLabel("Token API")
        key_lbl.setStyleSheet("font-weight: 700; font-size: 11px; color: #A3B3CE;")
        self._key_input = QLineEdit()
        self._key_input.setPlaceholderText("ntn_...")
        self._key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._key_input.setFixedHeight(36)

        btn_row = QWidget()
        br = QHBoxLayout(btn_row)
        br.setContentsMargins(0, 0, 0, 0)
        br.setSpacing(8)

        self._connect_btn = QPushButton("⚡ Connetti")
        self._connect_btn.setObjectName("PrimaryBtn")
        self._connect_btn.setFixedHeight(36)
        self._connect_btn.clicked.connect(self._on_connect_clicked)

        self._save_btn = QPushButton("💾")
        self._save_btn.setToolTip("Salva profilo nel vault di sistema")
        self._save_btn.setFixedSize(36, 36)
        self._save_btn.clicked.connect(self._on_save_profile)

        self._del_btn = QPushButton("🗑")
        self._del_btn.setToolTip("Elimina profilo")
        self._del_btn.setFixedSize(36, 36)
        self._del_btn.setEnabled(False)
        self._del_btn.clicked.connect(self._on_delete_profile)

        br.addWidget(self._connect_btn, stretch=1)
        br.addWidget(self._save_btn)
        br.addWidget(self._del_btn)

        self._error_lbl = QLabel()
        self._error_lbl.setWordWrap(True)
        self._error_lbl.setObjectName("Error")
        self._error_lbl.hide()

        for w_ in [profile_lbl, self._profile_combo,
                   name_lbl, self._name_input,
                   key_lbl, self._key_input,
                   btn_row, self._error_lbl]:
            lay.addWidget(w_)

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

        disc_btn = QPushButton("⏻ Disconnetti")
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
        line.setStyleSheet("color: #24314B;")
        return line

    def _on_profile_selected(self, _):
        name = self._profile_combo.currentData()
        is_new = name is None
        self._key_input.setVisible(is_new)
        self._del_btn.setEnabled(not is_new)
        if not is_new:
            self._name_input.setText(name)
            self._key_input.clear()

    def _on_save_profile(self):
        name = self._name_input.text().strip()
        key = self._key_input.text().strip()
        if not name or not key:
            self.show_error("Inserisci nome profilo e token.")
            return
        save_key(name, key)
        save_profile_name(name)
        if self._profile_combo.findData(name) == -1:
            self._profile_combo.addItem(name, name)
        self._profile_combo.setCurrentIndex(
            self._profile_combo.findData(name)
        )

    def _on_delete_profile(self):
        name = self._profile_combo.currentData()
        if not name:
            return
        delete_key(name)
        remove_profile_name(name)
        idx = self._profile_combo.findData(name)
        self._profile_combo.removeItem(idx)
        self._profile_combo.setCurrentIndex(0)

    def _on_connect_clicked(self):
        name = self._profile_combo.currentData()
        if name:
            key = get_key(name)
        else:
            key = self._key_input.text().strip()
        if not key:
            self.show_error("Nessun token disponibile.")
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