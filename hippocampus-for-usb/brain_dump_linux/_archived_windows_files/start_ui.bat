@echo off
:: ===========================================
:: BrainDump UI 快捷启动
:: 双击此文件直接打开 Web UI
:: ===========================================

setlocal

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    python3 --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [错误] 未检测到 Python
        echo 请安装 Python 3.8+ 
        echo 下载地址: https://www.python.org/downloads/
        pause
        exit /b 1
    )
    set PYTHON=python3
) else (
    set PYTHON=python
)

:: 启动服务器
echo Starting BrainDump UI...
echo.
start "BrainDump v3.1" cmd /k "%PYTHON% server.py"
exit /b 0
