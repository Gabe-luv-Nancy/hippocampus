@echo off
chcp 65001 >nul
:: ===========================================
:: Hippocampus.exe 一键构建脚本
:: 仅适用于 Windows 10/11 (64位)
:: ===========================================

echo.
echo ==========================================
echo   Hippocampus.exe 构建脚本
echo ==========================================
echo.

:: 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python
    echo 请先安装 Python 3.9+
    echo 下载地址: https://www.python.org/downloads/
    echo 安装时务必勾选 "Add Python to PATH"
    pause
    exit /b 1
)

echo [OK] Python 已安装
python --version
echo.

:: 检查 pip
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] pip 未安装
    pause
    exit /b 1
)

:: 安装依赖
echo [1/3] 安装 PyInstaller 和 PyQt6...
echo 这可能需要 3-5 分钟，请耐心等待...
echo.

pip install pyinstaller --quiet
if %errorlevel% neq 0 (
    echo [警告] PyInstaller 安装遇到问题，尝试普通安装...
    pip install pyinstaller
)

pip install PyQt6 --quiet
if %errorlevel% neq 0 (
    echo [警告] PyQt6 安装遇到问题，尝试普通安装...
    pip install PyQt6
)

echo.
echo [2/3] 开始打包编译...
echo 这可能需要 5-10 分钟，请耐心等待...
echo.

:: 切换到 gui_main.py 所在目录（hippocampus-for-github）
set SCRIPT_DIR=%~dp0
set GUI_ROOT=%SCRIPT_DIR%..\..\hippocampus-for-github

:: 清理旧构建
if exist "%GUI_ROOT%\build" rmdir /s /q "%GUI_ROOT%\build"
if exist "%GUI_ROOT%\dist" rmdir /s /q "%GUI_ROOT%\dist"

:: 打包编译
cd /d "%GUI_ROOT%"
python -m PyInstaller --name Hippocampus --onefile --windowed --clean ^
  --add-data "scripts;scripts" ^
  --add-data "gui;gui" ^
  --hidden-import=PyQt6 ^
  --hidden-import=PyQt6.QtWidgets ^
  --hidden-import=PyQt6.QtCore ^
  --hidden-import=PyQt6.QtGui ^
  --collect-all=PyQt6 ^
  gui_main.py

if %errorlevel% neq 0 (
    echo.
    echo [错误] 编译失败，请检查上方错误信息
    pause
    exit /b 1
)

echo.
echo [3/3] 复制 exe 到 brain_dump 目录...

if not exist "%GUI_ROOT%\dist\Hippocampus.exe" (
    echo [错误] 未找到编译产物
    pause
    exit /b 1
)

copy /Y "%GUI_ROOT%\dist\Hippocampus.exe" "%SCRIPT_DIR%Hippocampus.exe" >nul

if %errorlevel% equ 0 (
    echo.
    echo ==========================================
    echo   构建成功！
    echo ==========================================
    echo.
    echo exe 已生成：%SCRIPT_DIR%Hippocampus.exe
    echo.
    echo 双击 1-本地版.bat 或 2-U盘版.bat 即可运行
    echo.
    pause
) else (
    echo.
    echo [错误] 复制 exe 失败
    pause
    exit /b 1
)
