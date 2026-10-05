@echo off
cd /d "%~dp0"

if exist ".venv\Scripts\pythonw.exe" (
    start "" ".venv\Scripts\pythonw.exe" main.py
    exit
)
if exist "..\.venv\Scripts\pythonw.exe" (
    start "" "..\.venv\Scripts\pythonw.exe" main.py
    exit
)
if exist ".venv\Scripts\python.exe" (
    start "" ".venv\Scripts\python.exe" main.py
    exit
)
if exist "..\.venv\Scripts\python.exe" (
    start "" "..\.venv\Scripts\python.exe" main.py
    exit
)

start "" pythonw main.py 2>nul || start "" python main.py
exit
