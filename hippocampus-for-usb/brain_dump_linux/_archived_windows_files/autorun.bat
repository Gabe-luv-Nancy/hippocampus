@echo off
:: ===========================================
:: Hippocampus BrainDump U 盘自动运行脚本
:: 版本：v4.0.0
:: ===========================================

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "MARKER_FILE=%SCRIPT_DIR%marker.txt"
set "EXPECTED_MARKER=HIPPOCAMPUS_BRAINDUMP_v4.0.0"

:: 检测 marker 文件
if not exist "%MARKER_FILE%" (
    exit /b 0
)

set /p MARKER_CONTENT=<"%MARKER_FILE%"
set "MARKER_CONTENT=!MARKER_CONTENT: =!"

if not "!MARKER_CONTENT!"=="!EXPECTED_MARKER!" (
    exit /b 0
)

:: ========== 验证通过，显示产品标识 ==========
echo.
echo ==========================================
echo   Hippocampus BrainDump v4.0.0
echo   AI Memory Dump Drive
echo ==========================================
echo.

:: ========== 检查数据库 ==========
set "DB_FILE=%SCRIPT_DIR%db\brain_dump.sqlite"
if not exist "%DB_FILE%" (
    echo [错误] 数据库文件不存在
    echo 请运行 bin\init_db.bat 初始化
    pause
    exit /b 1
)

:: 创建必要目录
if not exist "%SCRIPT_DIR%capture\" mkdir "%SCRIPT_DIR%capture\"
if not exist "%SCRIPT_DIR%output\" mkdir "%SCRIPT_DIR%output\"
if not exist "%SCRIPT_DIR%log\" mkdir "%SCRIPT_DIR%log\"

:: ========== 检查 Python ==========
set PYTHON_CMD=
where python >nul 2>&1
if !errorlevel! equ 0 set PYTHON_CMD=python
if defined PYTHON_CMD (
    echo [OK] Python 已安装: !PYTHON_CMD!
) else (
    where python3 >nul 2>&1
    if !errorlevel! equ 0 set PYTHON_CMD=python3
)

:: ========== 启动选项 ==========
echo.
echo 请选择操作：
echo   [1] 启动 Web UI（推荐）
echo   [2] 仅检查数据完整性
echo   [3] 打开输出目录
echo   [4] 退出
echo.

set /p CHOICE=请输入选项 (1-4): 

if "!CHOICE!"=="1" (
    :: 启动 Web UI
    echo.
    echo 正在启动 BrainDump Web UI...
    echo 浏览器将自动打开
    echo 按 Ctrl+C 停止服务
    echo.
    
    cd /d "%SCRIPT_DIR%"
    
    if defined PYTHON_CMD (
        start "BrainDump UI" cmd /c "!PYTHON_CMD! server.py"
    ) else (
        echo [警告] 未检测到 Python
        echo 请安装 Python 3.8+ 以使用 Web UI
        echo.
        echo 或者直接双击打开 ui\index.html 文件
        start explorer "%SCRIPT_DIR%ui\index.html"
    )
    
) else if "!CHOICE!"=="2" (
    :: 数据验证
    call "%SCRIPT_DIR%bin\validate.bat"
    
) else if "!CHOICE!"=="3" (
    :: 打开输出目录
    if exist "%SCRIPT_DIR%output\" (
        start explorer "%SCRIPT_DIR%output"
    ) else (
        mkdir "%SCRIPT_DIR%output"
        start explorer "%SCRIPT_DIR%output"
    )
    
) else (
    exit /b 0
)

exit /b 0
