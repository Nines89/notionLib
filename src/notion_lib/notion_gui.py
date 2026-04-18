"""
notion_gui.py — Entry point
Esegui con:  python notion_gui.py
"""

import sys
sys.path.insert(0, "../..")

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from .gui.style import apply as apply_style
from .gui.app import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    apply_style(app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
