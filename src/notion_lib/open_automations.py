"""
CLI entry point: open the custom automations folder in the system file manager.

Run with:  notion-automations
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from .gui.logic.custom_automation_manager import default_custom_automations_root


def _open_folder(path: Path) -> None:
    path = path.resolve()
    path.mkdir(parents=True, exist_ok=True)

    if sys.platform == "win32":
        os.startfile(str(path))
    elif sys.platform == "darwin":
        subprocess.run(["open", str(path)], check=False)
    else:
        subprocess.run(["xdg-open", str(path)], check=False)


def main() -> None:
    folder = default_custom_automations_root()
    print(folder)
    _open_folder(folder)


if __name__ == "__main__":
    main()
