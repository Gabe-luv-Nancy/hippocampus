@echo off
chcp 65001 >nul 2>nul
setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "PORTABLE_PY=%SCRIPT_DIR%python\python.exe"

echo.
echo ==========================================
echo   Hippocampus Environment Check
echo ==========================================
echo.

:: Check 1: Portable Python
echo [1/6] Portable Python...
if exist "%PORTABLE_PY%" (
    echo   [OK] Found: %PORTABLE_PY%
    "%PORTABLE_PY%" --version 2>&1
) else (
    echo   [FAIL] Not found: %PORTABLE_PY%
)
echo.

:: Check 2: _pth file
echo [2/6] python311._pth...
set "PTH_FILE=%SCRIPT_DIR%python\python311._pth"
if exist "%PTH_FILE%" (
    echo   [OK] Found
    echo   --- Content ---
    type "%PTH_FILE%"
    echo   --- End ---
) else (
    echo   [FAIL] Not found
)
echo.

:: Check 3: PyQt6 directory
echo [3/6] PyQt6 package...
set "PYQT6_DIR=%SCRIPT_DIR%python\Lib\site-packages\PyQt6"
if exist "%PYQT6_DIR%" (
    echo   [OK] Directory exists
    dir /b "%PYQT6_DIR%\*.pyd" 2>nul | find /c ".pyd" >nul
    echo   .pyd files:
    dir /b "%PYQT6_DIR%\*.pyd" 2>nul
) else (
    echo   [FAIL] Not found: %PYQT6_DIR%
)
echo.

:: Check 4: Qt6/bin DLLs
echo [4/6] Qt6 runtime DLLs...
set "QT_BIN=%SCRIPT_DIR%python\Lib\site-packages\PyQt6\Qt6\bin"
if exist "%QT_BIN%" (
    echo   [OK] Directory exists
    echo   Key DLLs:
    if exist "%QT_BIN%\Qt6Core.dll" (echo   [OK] Qt6Core.dll) else (echo   [FAIL] Qt6Core.dll MISSING)
    if exist "%QT_BIN%\Qt6Gui.dll" (echo   [OK] Qt6Gui.dll) else (echo   [FAIL] Qt6Gui.dll MISSING)
    if exist "%QT_BIN%\Qt6Widgets.dll" (echo   [OK] Qt6Widgets.dll) else (echo   [FAIL] Qt6Widgets.dll MISSING)
) else (
    echo   [FAIL] Not found: %QT_BIN%
)
echo.

:: Check 5: sip module
echo [5/6] sip binding...
set "SIP_FILE=%SCRIPT_DIR%python\Lib\site-packages\PyQt6\sip.cp311-win_amd64.pyd"
if exist "%SIP_FILE%" (
    echo   [OK] Found: sip.cp311-win_amd64.pyd
) else (
    echo   [FAIL] Not found
)
echo.

:: Check 6: Actual import test
echo [6/6] Live import test...
if not exist "%PORTABLE_PY%" (
    echo   [SKIP] No portable Python to test
) else (
    echo   Testing: import PyQt6...
    "%PORTABLE_PY%" -c "import sys,os;sp=os.path.join(os.path.dirname(sys.executable),'Lib','site-packages');qt_bin=os.path.join(sp,'PyQt6','Qt6','bin');os.add_dll_directory(qt_bin) if os.path.isdir(qt_bin) else None;from PyQt6.QtWidgets import QApplication;print('[OK] PyQt6 import SUCCESS')" 2>&1
    if !errorlevel! neq 0 (
        echo   [FAIL] PyQt6 import FAILED - see error above
    )
)
echo.

echo ==========================================
echo   Check complete. Press any key to exit.
echo ==========================================
pause
