@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    py -3 -m venv .venv
    if errorlevel 1 goto failed
)
".venv\Scripts\python.exe" -c "import flask, holidays, scrum_capacity_calculator" >nul 2>&1
if errorlevel 1 (
    ".venv\Scripts\python.exe" -m pip --version >nul 2>&1
    if errorlevel 1 (
        ".venv\Scripts\python.exe" -m ensurepip --upgrade
        if errorlevel 1 goto failed
    )
    ".venv\Scripts\python.exe" -m pip install -e .
    if errorlevel 1 goto failed
)
".venv\Scripts\python.exe" app.py
exit /b %errorlevel%

:failed
echo.
echo Could not start Scrum Capacity. Install Python 3.10 or newer and try again.
pause
exit /b 1
