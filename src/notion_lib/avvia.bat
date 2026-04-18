@echo off
cd /d "%~dp0"
echo Installazione dipendenze...
pip install PyQt6 -q
echo.
echo Avvio Notion Automation...
python notion_gui.py
pause
