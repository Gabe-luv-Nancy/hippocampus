@echo off
chcp 65001 >nul
:: ===========================================
:: Hippocampus BrainDump — Windows 启动器
:: 通过 WSL 桥接运行 Linux 原生引擎
:: 版本：v4.0.1
:: 
:: 新增：跨 WSL 发行版扫描
::   选项 [2] 可自动发现所有 WSL distro 中的
::   .hermes / .openclaw 等 AI 工具目录
:: ===========================================

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "MARKER_FILE=%SCRIPT_DIR%marker.txt"
set "EXPECTED_MARKER=HIPPOCAMPUS_BRAINDUMP_v4.0.0"

:: ========== 检测 WSL ==========
where wsl >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 WSL
    echo Hippocampus Windows 版需要 WSL2 支持
    echo 请先安装 WSL: wsl --install
    pause
    exit /b 1
)
echo [OK] WSL 已安装

:: ========== 检测 marker 文件 ==========
if not exist "%MARKER_FILE%" (
    exit /b 0
)

:: ========== 显示产品标识 ==========
echo.
echo ==========================================
echo   Hippocampus BrainDump v4.0.0
echo   Windows + WSL Edition
echo ==========================================
echo.

:: ========== 检查 Linux 引擎 ==========
:: brain_dump_linux 与 brain_dump_windows 同级
set "LINUX_DIR=%SCRIPT_DIR%..\brain_dump_linux"

if not exist "%LINUX_DIR%\lib\scanner.py" (
    echo [错误] 未找到 Linux 引擎
    echo 请确保 brain_dump_linux/ 目录与 brain_dump_windows/ 同级
    pause
    exit /b 1
)
echo [OK] Linux 引擎就绪

:: ========== 创建必要目录 ==========
if not exist "%SCRIPT_DIR%capture\" mkdir "%SCRIPT_DIR%capture\"
if not exist "%SCRIPT_DIR%output\" mkdir "%SCRIPT_DIR%output\"
if not exist "%SCRIPT_DIR%logs\" mkdir "%SCRIPT_DIR%logs\"

:: ========== 检测 PyQt6 ==========
set HAS_PYQT6=0
wsl bash -c "python3 -c 'import PyQt6' 2>/dev/null" && set HAS_PYQT6=1

:: ========== 启动选项 ==========
echo.
if "%HAS_PYQT6%"=="1" (
    echo 请选择操作：
    echo   [1] 启动桌面 GUI（推荐）
    echo   [2] 扫描本机文件（通过 WSL 扫描 Windows 磁盘）
    echo   [3] 扫描所有 WSL 发行版
    echo   [4] 启动 HTTP API 服务（备用）
    echo   [5] 检查数据完整性
    echo   [6] 退出
    echo.
    set /p CHOICE=请输入选项 (1-6): 
) else (
    echo ⚠️  未检测到 PyQt6，桌面 GUI 不可用
    echo.
    echo 请选择操作：
    echo   [1] 扫描本机文件（通过 WSL 扫描 Windows 磁盘）
    echo   [2] 扫描所有 WSL 发行版
    echo   [3] 启动 HTTP API 服务
    echo   [4] 检查数据完整性
    echo   [5] 退出
    echo.
    set /p CHOICE=请输入选项 (1-5): 
)

if "%HAS_PYQT6%"=="1" (
    if "%CHOICE%"=="1" goto :gui
    if "%CHOICE%"=="2" goto :scan
    if "%CHOICE%"=="3" goto :scan_distros
    if "%CHOICE%"=="4" goto :webui
    if "%CHOICE%"=="5" goto :validate
    if "%CHOICE%"=="6" exit /b 0
) else (
    if "%CHOICE%"=="1" goto :scan
    if "%CHOICE%"=="2" goto :scan_distros
    if "%CHOICE%"=="3" goto :webui
    if "%CHOICE%"=="4" goto :validate
    if "%CHOICE%"=="5" exit /b 0
)
goto :eof

:gui
echo.
echo 正在启动 Hippocampus Desktop GUI...
echo.

wsl bash -c "cd '$(wslpath -a '%SCRIPT_DIR%..\\brain_dump_linux')' && python3 gui_main.py --mode disk --path '$(wslpath -a '%SCRIPT_DIR%..\\brain_dump_linux')'"

pause
goto :eof

:scan
echo.
echo 正在通过 WSL 扫描本机文件...
echo 扫描路径: /mnt/c/, /mnt/d/ ...
echo.

:: 将 Windows 路径转为 WSL 路径，然后调用 Linux scanner
wsl bash -c "cd '$(wslpath -a '%SCRIPT_DIR%..\brain_dump_linux')' && python3 lib/scanner.py scan --path /mnt/c/ --path /mnt/d/ --output '$(wslpath -a '%SCRIPT_DIR%output')' --db '$(wslpath -a '%SCRIPT_DIR%..\brain_dump_linux\db\brain_dump.sqlite')'"

echo.
echo 扫描完成
pause
goto :eof

:scan_distros
echo.
echo 正在扫描所有 WSL 发行版...
echo 查找: .hermes, .openclaw 等目录
echo.

wsl bash -c "cd '$(wslpath -a '%SCRIPT_DIR%')' && python3 wsl_bridge.py"

echo.
pause
goto :eof

:webui
echo.
echo 正在启动 Hippocampus 本地服务...
echo 地址: http://localhost:8080
echo 按 Ctrl+C 停止服务
echo.

:: 通过 WSL 启动 server.py（本地 HTTP + HTML/JS 前端）
wsl bash -c "cd '$(wslpath -a '%SCRIPT_DIR%..\\brain_dump_linux')' && python3 server.py --port 8080"

pause
goto :eof

:validate
echo.
echo 检查数据完整性...
wsl bash -c "cd '$(wslpath -a '%SCRIPT_DIR%..\brain_dump_linux')' && python3 db/init_db.py validate --db '$(wslpath -a '%SCRIPT_DIR%..\brain_dump_linux\db\brain_dump.sqlite')'"
echo.
pause
goto :eof
