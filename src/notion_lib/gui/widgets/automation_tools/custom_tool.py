"""
gui/widgets/automation_tools/custom_tool.py

Widget runtime per un'automazione personalizzata.

Responsabilità:
  - mostrare il path dello script
  - permettere di aprire lo script con l'editor di sistema
  - eseguire lo script come subprocess (via segnale run_requested)
  - mostrare stdout/stderr in tempo reale nel log
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QFileDialog, QMessageBox,
)
from PyQt6.QtCore import pyqtSignal, Qt, QThread, pyqtSlot
from PyQt6.QtGui import QFont, QColor

from notion_lib.gui.widgets.automation_tools.styles import STYLESHEET, _SectionCard


# ── Worker subprocess ─────────────────────────────────────────────────────────

class _SubprocessWorker(QThread):
    """
    Esegue lo script Python in un subprocess isolato.
    Emette stdout+stderr riga per riga via line_emitted.
    """
    line_emitted = pyqtSignal(str)
    finished_ok  = pyqtSignal()
    finished_err = pyqtSignal(str)

    def __init__(self, script_path: str, api_key: str):
        super().__init__()
        self._script_path = script_path
        self._api_key = api_key
        self._process: subprocess.Popen | None = None

    def run(self):
        env = {**os.environ, "NOTION_KEY": self._api_key}
        try:
            self._process = subprocess.Popen(
                [sys.executable, self._script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,   # stderr → stdout unificato
                text=True,
                env=env,
                bufsize=1,                  # line-buffered
            )
            # Legge riga per riga e le emette in tempo reale
            for line in self._process.stdout:
                self.line_emitted.emit(line.rstrip())

            self._process.wait()
            if self._process.returncode == 0:
                self.finished_ok.emit()
            else:
                self.finished_err.emit(
                    f"Processo terminato con codice {self._process.returncode}"
                )
        except Exception as e:
            self.finished_err.emit(str(e))

    def stop(self):
        if self._process and self._process.poll() is None:
            self._process.terminate()


# ── Widget principale ─────────────────────────────────────────────────────────

class CustomAutomationTool(QWidget):
    """
    Widget runtime per una singola automazione personalizzata.

    Parametri
    ---------
    slug        : str  — identificatore dell'automazione
    name        : str  — nome display
    script_path : str  — path assoluto allo script .py
    """

    # Emesso quando l'utente vuole eseguire: la MainWindow inietta la api_key
    run_requested = pyqtSignal(str, str)   # script_path, slug

    def __init__(self, slug: str, name: str, script_path: str, parent=None):
        super().__init__(parent)
        self._slug = slug
        self._name = name
        self._script_path = script_path
        self._worker: _SubprocessWorker | None = None
        self._api_key: str = ""

        self.setStyleSheet(STYLESHEET)
        self._build_ui()

    # ── Build UI ──────────────────────────────────────────────────────────────

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        from PyQt6.QtWidgets import QScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(scroll.Shape.NoFrame)

        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setContentsMargins(40, 36, 40, 36)
        cl.setSpacing(24)

        # ── Info script ───────────────────────────────────────────
        info_card = _SectionCard("📄", "Script")
        path_row = QWidget()
        pr = QHBoxLayout(path_row)
        pr.setContentsMargins(0, 0, 0, 0)
        pr.setSpacing(10)

        self._path_lbl = QLabel(self._script_path)
        self._path_lbl.setStyleSheet(
            "color: #64748B; font-size: 11px; font-family: Consolas, monospace;"
        )
        self._path_lbl.setWordWrap(True)

        open_btn = QPushButton("📂 Apri con editor")
        open_btn.setFixedHeight(34)
        open_btn.clicked.connect(self._open_in_editor)

        import_btn = QPushButton("↑ Sostituisci script")
        import_btn.setFixedHeight(34)
        import_btn.clicked.connect(self._import_script)

        pr.addWidget(self._path_lbl, stretch=1)
        pr.addWidget(open_btn)
        pr.addWidget(import_btn)
        info_card.add_content(path_row)
        cl.addWidget(info_card)

        # ── Azioni ────────────────────────────────────────────────
        action_card = _SectionCard("▶", "Esecuzione")
        btn_row = QWidget()
        bl = QHBoxLayout(btn_row)
        bl.setContentsMargins(0, 0, 0, 0)
        bl.setSpacing(12)

        self._run_btn = QPushButton("▶  Esegui ora")
        self._run_btn.setObjectName("PrimaryBtn")
        self._run_btn.setMinimumHeight(50)
        self._run_btn.clicked.connect(self._on_run)

        self._stop_btn = QPushButton("⏹  Interrompi")
        self._stop_btn.setMinimumHeight(50)
        self._stop_btn.setEnabled(False)
        self._stop_btn.clicked.connect(self._on_stop)

        bl.addWidget(self._run_btn)
        bl.addWidget(self._stop_btn)
        action_card.add_content(btn_row)
        cl.addWidget(action_card)

        # ── Log output ────────────────────────────────────────────
        log_card = _SectionCard("📋", "Output")
        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setMinimumHeight(280)
        self._log.setFont(QFont("Consolas", 10))
        self._log.setStyleSheet(
            "background: #0D1628; color: #CBD5E1; border: 1px solid #1E293B; "
            "border-radius: 8px; padding: 10px;"
        )

        clear_btn = QPushButton("🗑  Pulisci log")
        clear_btn.setFixedHeight(30)
        clear_btn.clicked.connect(self._log.clear)

        log_card.add_content(self._log)
        log_card.add_content(clear_btn)
        cl.addWidget(log_card)

        cl.addStretch()
        scroll.setWidget(content)
        lay.addWidget(scroll)

    # ── Slot pubblici (chiamati da MainWindow) ────────────────────────────────

    def set_api_key(self, key: str):
        """Chiamato da MainWindow dopo la connessione."""
        self._api_key = key

    # ── Slot privati ──────────────────────────────────────────────────────────

    def _on_run(self):
        if not self._api_key:
            QMessageBox.warning(
                self, "Non connesso",
                "Connetti prima l'account Notion dalla sidebar."
            )
            return

        if not Path(self._script_path).exists():
            QMessageBox.critical(
                self, "Script non trovato",
                f"File non trovato:\n{self._script_path}"
            )
            return

        self._log.clear()
        self._log_append("▶  Avvio script...", color="#22D3EE")

        self._run_btn.setEnabled(False)
        self._run_btn.setText("⏳  Esecuzione...")
        self._stop_btn.setEnabled(True)

        self._worker = _SubprocessWorker(self._script_path, self._api_key)
        self._worker.line_emitted.connect(self._on_line)
        self._worker.finished_ok.connect(self._on_finished_ok)
        self._worker.finished_err.connect(self._on_finished_err)
        self._worker.start()

    def _on_stop(self):
        if self._worker:
            self._worker.stop()
        self._log_append("⏹  Interruzione richiesta.", color="#F87171")

    @pyqtSlot(str)
    def _on_line(self, line: str):
        color = "#F87171" if line.lower().startswith(("error", "traceback", "exception")) else None
        self._log_append(line, color=color)

    @pyqtSlot()
    def _on_finished_ok(self):
        self._log_append("✓  Script completato.", color="#34D399")
        self._reset_buttons()

    @pyqtSlot(str)
    def _on_finished_err(self, error: str):
        self._log_append(f"✗  {error}", color="#F87171")
        self._reset_buttons()

    def _open_in_editor(self):
        """Apre lo script con l'editor di testo predefinito del sistema."""
        path = Path(self._script_path)
        if not path.exists():
            QMessageBox.warning(self, "File non trovato", str(path))
            return
        if sys.platform == "win32":
            os.startfile(str(path))
        elif sys.platform == "darwin":
            subprocess.run(["open", str(path)])
        else:
            subprocess.run(["xdg-open", str(path)])

    def _import_script(self):
        """Sostituisce lo script corrente con un file selezionato dall'utente."""
        src, _ = QFileDialog.getOpenFileName(
            self, "Seleziona script Python", "", "Python files (*.py)"
        )
        if not src:
            return

        reply = QMessageBox.question(
            self,
            "Sostituisci script",
            f"Vuoi sostituire lo script corrente con:\n{src}\n\n"
            "Il template precedente verrà sovrascritto.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        import shutil
        shutil.copy2(src, self._script_path)
        self._log_append(f"✓  Script sostituito con: {src}", color="#34D399")

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _reset_buttons(self):
        self._run_btn.setEnabled(True)
        self._run_btn.setText("▶  Esegui ora")
        self._stop_btn.setEnabled(False)
        self._worker = None

    def _log_append(self, text: str, color: str | None = None):
        if color:
            self._log.append(f'<span style="color:{color};">{text}</span>')
        else:
            self._log.append(text)
        # Scroll automatico in fondo
        self._log.verticalScrollBar().setValue(
            self._log.verticalScrollBar().maximum()
        )
