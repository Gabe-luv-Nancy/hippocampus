@echo off
chcp 65001 >nul
:: =============================================
:: Hippocampus Streamlit Web UI 启动器
:: 双击此文件，浏览器自动打开 Web 界面
:: =============================================

setlocal

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    python3 --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [错误] 未检测到 Python
        echo 请安装 Python 3.9+：https://www.python.org/downloads/
        pause
        exit /b 1
    )
    set PYTHON=python3
) else (
    set PYTHON=python
)

:: 检查 streamlit
%PYTHON% -c "import streamlit" >nul 2>&1
if %errorlevel% neq 0 (
    echo [信息] 正在安装 Streamlit...
    %PYTHON% -m pip install streamlit -q
)

echo.
echo 正在启动 Hippocampus Streamlit Web UI...
echo 浏览器将自动打开
echo 按 Ctrl+C 停止服务
echo.
echo 访问地址：http://localhost:8501
echo.

:: 启动 streamlit
start "Hippocampus Streamlit" cmd /k "cd /d "%SCRIPT_DIR%" && %PYTHON% -m streamlit run lib\streamlit_app.py --server.port 8501 --server.headless true"

exit /b 0
