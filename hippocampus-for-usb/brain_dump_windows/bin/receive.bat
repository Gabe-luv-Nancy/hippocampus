@echo off
:: ===========================================
:: Hippocampus BrainDump 接收脚本
:: 版本：v4.0.0
:: 由 Host 调用，或用户手动运行
:: ===========================================

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "DRIVE_DIR=%SCRIPT_DIR%..\"

echo.
echo ==========================================
echo   Hippocampus BrainDump
echo   数据接收检查
echo ==========================================
echo.

:: 检查数据库
set "DB_FILE=%DRIVE_DIR%db\brain_dump.sqlite"
if not exist "%DB_FILE%" (
    echo [错误] 数据库文件不存在
    echo 请确保这是一个正常的 BrainDump U 盘
    exit /b 1
)
echo [OK] 数据库文件存在

:: 检查 capture 目录
set "CAPTURE_DIR=%DRIVE_DIR%capture\"
if not exist "%CAPTURE_DIR%" (
    mkdir "%CAPTURE_DIR%"
    echo [OK] 已创建 capture 目录
) else (
    echo [OK] capture 目录存在
)

:: 检查 output 目录
set "OUTPUT_DIR=%DRIVE_DIR%output\"
if not exist "%OUTPUT_DIR%" (
    mkdir "%OUTPUT_DIR%"
    echo [OK] 已创建 output 目录
) else (
    echo [OK] output 目录存在
)

:: 统计文件数量
set FILE_COUNT=0
for /r "%CAPTURE_DIR%" %%F in (*.md) do set /a FILE_COUNT+=1

echo.
echo 抓取统计：
echo   capture 目录中：!FILE_COUNT! 个 .md 文件

:: 查询数据库记录数
set DB_FILE_SQLITE="%DB_FILE%"
for /f %%A in ('sqlite3 "%DB_FILE_SQLITE%" "SELECT COUNT(*) FROM files;" 2^>nul') do set DB_COUNT=%%A
if defined DB_COUNT (
    echo   数据库记录：!DB_COUNT! 条
) else (
    echo   数据库记录：无法查询（需安装 sqlite3）
)

echo.
echo [完成] 数据接收就绪
echo.
echo 如需从电脑端写入数据，请运行：
echo   python3 scripts/scanner.py scan --usb "%DRIVE_DIR:~0,-1%"
echo.

pause
exit /b 0
