@echo off
:: ===========================================
:: Hippocampus BrainDump 数据完整性验证
:: 版本：v4.0.0
:: ===========================================

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "DRIVE_DIR=%SCRIPT_DIR%..\"

echo.
echo ==========================================
echo   Hippocampus BrainDump
echo   数据完整性验证
echo ==========================================
echo.

set VALIDATION_PASSED=1

:: ========== 1. 验证 marker ==========
set "MARKER_FILE=%DRIVE_DIR%marker.txt"
if not exist "%MARKER_FILE%" (
    echo [FAIL] marker.txt 不存在
    set VALIDATION_PASSED=0
) else (
    set /p MARKER_CONTENT=<"%MARKER_FILE%"
    if "!MARKER_CONTENT!"=="HIPPOCAMPUS_BRAINDUMP_v4.0.0" (
        echo [PASS] marker.txt 内容正确
    ) else (
        echo [FAIL] marker.txt 内容不正确
        set VALIDATION_PASSED=0
    )
)

:: ========== 2. 验证数据库 ==========
set "DB_FILE=%DRIVE_DIR%db\brain_dump.sqlite"
if not exist "%DB_FILE%" (
    echo [FAIL] 数据库文件不存在
    set VALIDATION_PASSED=0
) else (
    echo [PASS] 数据库文件存在
    
    :: 检查表结构
    sqlite3 "%DB_FILE%" ".tables" 2>nul | findstr /i "files captures tags" >nul
    if !errorlevel! equ 0 (
        echo [PASS] 数据库表结构完整
    ) else (
        echo [FAIL] 数据库表结构不完整
        set VALIDATION_PASSED=0
    )
)

:: ========== 3. 验证目录结构 ==========
set DIRS_OK=1
if not exist "%DRIVE_DIR%capture\" (
    echo [FAIL] capture 目录不存在
    set DIRS_OK=0
)
if not exist "%DRIVE_DIR%output\" (
    echo [FAIL] output 目录不存在
    set DIRS_OK=0
)
if not exist "%DRIVE_DIR%log\" (
    echo [FAIL] log 目录不存在
    set DIRS_OK=0
)
if !DIRS_OK! equ 1 (
    echo [PASS] 目录结构完整
)

:: ========== 4. 验证脚本可执行性 ==========
set SCRIPTS_OK=1
if not exist "%SCRIPT_DIR%receive.bat" (
    echo [FAIL] receive.bat 不存在
    set SCRIPTS_OK=0
)
if !SCRIPTS_OK! equ 1 (
    echo [PASS] 脚本文件完整
)

:: ========== 结果 ==========
echo.
echo ==========================================
if !VALIDATION_PASSED! equ 1 (
    echo   验证结果：✓ 全部通过
    echo ==========================================
    echo.
    echo U 盘数据完整，可以正常使用
) else (
    echo   验证结果：✗ 存在问题
    echo ==========================================
    echo.
    echo 请联系商家更换 U 盘
)
echo.

pause
exit /b !VALIDATION_PASSED!
