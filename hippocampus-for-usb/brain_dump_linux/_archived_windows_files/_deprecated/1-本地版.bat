@echo off
chcp 65001 >nul
:: =============================================
:: Hippocampus - 本地版启动器
:: 自动选择最佳方式运行（优先 Streamlit，备用 exe）
:: =============================================

setlocal

set "SCRIPT_DIR=%~dp0"

:: 优先使用 Streamlit Web UI
echo 正在检测运行环境...
echo.

:: 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    python3 --version >nul 2>&1
    if %errorlevel% neq 0 (
        goto :try_exe
    )
    set PYTHON=python3
) else (
    set PYTHON=python
)

:: 检查 streamlit
%PYTHON% -c "import streamlit" 2>nul
if %errorlevel% equ 0 goto :run_streamlit

:: 没有 streamlit，尝试安装
echo [信息] 安装 Streamlit...
%PYTHON% -m pip install streamlit --quiet 2>nul
if %errorlevel% equ 0 goto :run_streamlit

:try_exe
:: 退回到 exe 方式
if exist "%SCRIPT_DIR%Hippocampus.exe" (
    echo 使用 PyQt6 GUI 版本...
    "%SCRIPT_DIR%Hippocampus.exe" --mode local
) else (
    echo [错误] 未安装 Python 且 exe 不存在
    echo 请安装 Python：https://www.python.org/downloads/
    pause
)
goto :eof

:run_streamlit
echo 使用 Streamlit Web UI 版本...
echo.
echo 启动中，浏览器将自动打开...
echo 访问地址：http://localhost:8501
echo.
start "Hippocampus Streamlit" cmd /k "cd /d "%SCRIPT_DIR%" && %PYTHON% -m streamlit run lib\streamlit_app.py --server.port 8501 --server.headless true --server.fileWatcherType none"
goto :eof
