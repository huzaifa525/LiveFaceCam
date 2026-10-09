@echo off
setlocal
cd /d "%~dp0"
title LiveFaceCam Setup

echo.
echo  ==========================================
echo    LiveFaceCam - one-click Windows setup
echo  ==========================================
echo.

rem --- 1. Find Python 3.11-3.14 ------------------------------------------
set "PY="
for %%V in (3.13 3.12 3.14 3.11) do (
    if not defined PY (
        py -%%V -c "import sys" >nul 2>nul && set "PY=py -%%V"
    )
)
if not defined PY (
    python -c "import sys; sys.exit(0 if (3,11) <= sys.version_info[:2] <= (3,14) else 1)" >nul 2>nul && set "PY=python"
)
if not defined PY (
    echo [X] Python 3.11 - 3.14 not found.
    echo     Install it from https://www.python.org/downloads/ ^(tick "Add python.exe to PATH"^)
    echo     then run Setup.bat again.
    pause
    exit /b 1
)
echo [OK] Using %PY%

rem --- 2. Check ffmpeg ------------------------------------------------------
where ffmpeg >nul 2>nul
if errorlevel 1 (
    echo [!] ffmpeg not found - needed only for Photo/Video conversion.
    echo     Install with:  winget install Gyan.FFmpeg
)

rem --- 3. Virtual environment + dependencies -------------------------------
if not exist "venv\Scripts\python.exe" (
    echo [..] Creating virtual environment...
    %PY% -m venv venv || goto :fail
)
echo [..] Installing dependencies ^(first time takes 5-15 minutes, ~6 GB^)...
"venv\Scripts\python.exe" -m pip --version >nul 2>nul || "venv\Scripts\python.exe" -m ensurepip --upgrade >nul
"venv\Scripts\python.exe" -m pip install --upgrade pip >nul
"venv\Scripts\python.exe" -m pip install -r requirements.txt || goto :fail

rem --- 4. Models ------------------------------------------------------------
if not exist models mkdir models
call :model inswapper_128_fp16.onnx || goto :fail
call :model gfpgan-1024.onnx || goto :fail
call :model hyperswap_1b_256.onnx https://huggingface.co/facefusion/models-3.3.0/resolve/main || goto :fail

rem --- 5. Desktop shortcut ---------------------------------------------------
powershell -NoProfile -Command "$s=(New-Object -ComObject WScript.Shell).CreateShortcut([Environment]::GetFolderPath('Desktop')+'\LiveFaceCam.lnk'); $s.TargetPath='%~dp0Start-LiveFaceCam.bat'; $s.WorkingDirectory='%~dp0'; $s.IconLocation='%~dp0assets\icon.ico'; $s.Save()" >nul 2>nul && echo [OK] Desktop shortcut created
echo.
echo  [OK] Setup complete. Start the app with Start-LiveFaceCam.bat
echo.
pause
exit /b 0

:model
if exist "models\%~1" (
    echo [OK] models\%~1 already present
    exit /b 0
)
echo [..] Downloading %~1 ...
set "BASE=%~2"
if not defined BASE set "BASE=https://huggingface.co/hacksider/deep-live-cam/resolve/main"
curl.exe -L --fail -o "models\%~1.part" "%BASE%/%~1?download=true" || exit /b 1
move /y "models\%~1.part" "models\%~1" >nul
exit /b 0

:fail
echo.
echo [X] Setup failed - see the messages above.
echo     If insightface fails to build, install "Desktop development with C++" from
echo     https://visualstudio.microsoft.com/visual-cpp-build-tools/ and run Setup.bat again.
pause
exit /b 1
