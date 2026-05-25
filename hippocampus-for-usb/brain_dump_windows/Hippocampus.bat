@echo off
chcp 65001 >nul 2>nul
:: ===========================================
:: Hippocampus v4.0.0 - Universal Launcher
:: Mode 0: Portable Python (bundled)
:: Mode 1: System Python
:: Mode 2: WSL fallback
:: ===========================================

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "LINUX_DIR=%SCRIPT_DIR%..\brain_dump_linux"
set "PORTABLE_PY=%SCRIPT_DIR%python\python.exe"

echo.
echo ==========================================
echo   Hippocampus v4.0.0
echo ==========================================
echo.

:: ===== Mode 0: Portable Python =====
echo [Check] Portable Python...
if exist "%PORTABLE_PY%" (
    echo [OK] Found portable Python
    "%PORTABLE_PY%" -c "import PyQt6" >nul 2>&1
    if !errorlevel! equ 0 (
        echo [OK] PyQt6 ready
        echo.
        echo Starting Hippocampus Desktop...
        echo.
        cd /d "%LINUX_DIR%"
        "%PORTABLE_PY%" gui_main.py --mode local
        if !errorlevel! neq 0 (
            echo.
            echo [ERROR] GUI exited with error. See above for details.
        )
        pause
        goto :end
    ) else (
        echo [WARN] PyQt6 not found, running scan only...
        cd /d "%LINUX_DIR%"
        "%PORTABLE_PY%" lib\scanner.py scan
        pause
        goto :end
    )
) else (
    echo [Skip] Portable Python not found
)

:: ===== Mode 1: System Python =====
echo [Check] System Python...
where python >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Found system Python
    python -c "import PyQt6" >nul 2>&1
    if !errorlevel! equ 0 (
        echo [OK] PyQt6 installed
        echo.
        cd /d "%LINUX_DIR%"
        python gui_main.py --mode local
        pause
        goto :end
    ) else (
        echo PyQt6 missing.
        echo   [1] Install PyQt6 and launch
        echo   [2] Use WSL mode
        echo   [3] Exit
        echo.
        set /p NATIVE_CHOICE=Select (1-3): 
        if "!NATIVE_CHOICE!"=="1" (
            echo Installing PyQt6...
            python -m pip install PyQt6 --quiet 2>&1
            if !errorlevel! equ 0 (
                cd /d "%LINUX_DIR%"
                python gui_main.py --mode local
                pause
                goto :end
            ) else (
                echo [ERROR] PyQt6 install failed, trying WSL...
                goto :wsl_mode
            )
        )
        if "!NATIVE_CHOICE!"=="2" goto :wsl_mode
        goto :end
    )
) else (
    echo [Skip] System Python not found
)

:: ===== Mode 2: WSL =====
:wsl_mode
echo.
echo [Check] WSL...
where wsl >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] WSL not found
    goto :no_env
)
echo [OK] WSL available

if not exist "%LINUX_DIR%\lib\scanner.py" (
    echo [ERROR] Linux engine not found
    echo Make sure brain_dump_linux is next to brain_dump_windows
    pause
    goto :end
)
echo [OK] Linux engine ready

set HAS_PYQT6=0
wsl bash -c "python3 -c 'import PyQt6' 2>/dev/null" && set HAS_PYQT6=1

echo.
if "%HAS_PYQT6%"=="1" (
    echo   [1] Launch GUI
    echo   [2] Scan host files
    echo   [3] Scan all WSL distros
    echo   [4] HTTP API server
    echo   [5] Validate database
    echo   [6] Exit
    echo.
    set /p CHOICE=Select (1-6): 
) else (
    echo   [1] Install PyQt6 then launch GUI
    echo   [2] Scan host files (no GUI)
    echo   [3] Scan all WSL distros
    echo   [4] HTTP API server
    echo   [5] Exit
    echo.
    set /p CHOICE=Select (1-5): 
)

if "%HAS_PYQT6%"=="1" (
    if "%CHOICE%"=="1" goto :wsl_gui
    if "%CHOICE%"=="2" goto :wsl_scan
    if "%CHOICE%"=="3" goto :wsl_scan_distros
    if "%CHOICE%"=="4" goto :wsl_webui
    if "%CHOICE%"=="5" goto :wsl_validate
    if "%CHOICE%"=="6" goto :end
) else (
    if "%CHOICE%"=="1" goto :wsl_install_pyqt
    if "%CHOICE%"=="2" goto :wsl_scan
    if "%CHOICE%"=="3" goto :wsl_scan_distros
    if "%CHOICE%"=="4" goto :wsl_webui
    if "%CHOICE%"=="5" goto :end
)
goto :end

:wsl_install_pyqt
echo Installing PyQt6 in WSL...
wsl bash -c "pip3 install PyQt6 --quiet 2>&1"
if %errorlevel% equ 0 (
    echo [OK] Installed, launching GUI...
    goto :wsl_gui
) else (
    echo [ERROR] Install failed
    pause
    goto :end
)

:wsl_gui
echo.
echo Launching GUI via WSL...
echo.
wsl bash -c "cd '$(wslpath '%SCRIPT_DIR%..\brain_dump_linux')' && python3 gui_main.py --mode disk --path '$(wslpath '%SCRIPT_DIR%..\brain_dump_linux')'"
pause
goto :end

:wsl_scan
echo.
echo Scanning host files via WSL...
echo.
wsl bash -c "cd '$(wslpath '%SCRIPT_DIR%..\brain_dump_linux')' && python3 lib/scanner.py scan --path /mnt/c/ --path /mnt/d/ --output '$(wslpath '%SCRIPT_DIR%output')' --db '$(wslpath '%SCRIPT_DIR%..\brain_dump_linux\db\brain_dump.sqlite')'"
echo.
echo Scan complete.
pause
goto :end

:wsl_scan_distros
echo.
echo Scanning all WSL distros...
wsl bash -c "cd '$(wslpath '%SCRIPT_DIR%')' && python3 wsl_bridge.py"
pause
goto :end

:wsl_webui
echo.
echo Starting local server...
echo URL: http://localhost:8080
echo.
wsl bash -c "cd '$(wslpath '%SCRIPT_DIR%..\brain_dump_linux')' && python3 server.py --port 8080"
pause
goto :end

:wsl_validate
echo.
echo Validating database...
wsl bash -c "cd '$(wslpath '%SCRIPT_DIR%..\brain_dump_linux')' && python3 db/init_db.py validate --db '$(wslpath '%SCRIPT_DIR%..\brain_dump_linux\db\brain_dump.sqlite')'"
pause
goto :end

:no_env
echo.
echo ========================================
echo   No Python environment found
echo ========================================
echo.
echo Option A: Install Windows Python
echo   1. Visit https://www.python.org/downloads/
echo   2. Download and install Python 3.10+
echo   3. Check "Add to PATH" during install
echo   4. Re-run Hippocampus.bat
echo.
echo Option B: Enable WSL
echo   1. Open PowerShell
echo   2. Run: wsl --install
echo   3. Restart computer
echo   4. Re-run Hippocampus.bat
echo.
pause
goto :end

:end
endlocal
