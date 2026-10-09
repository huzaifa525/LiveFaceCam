@echo off
cd /d "%~dp0"
if not exist "venv\Scripts\python.exe" (
    echo LiveFaceCam is not installed yet - running Setup.bat first...
    call Setup.bat || exit /b 1
)
set "EP=cpu"
where nvidia-smi >nul 2>nul && set "EP=cuda"
"%~dp0venv\Scripts\python.exe" run.py --execution-provider %EP% %*
if errorlevel 1 pause
