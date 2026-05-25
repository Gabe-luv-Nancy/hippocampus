@echo off
chcp 65001 >nul
:: =============================================
:: Hippocampus Windows - U盘版启动器
:: 输入 U盘盘符，通过 WSL 桥接写入
:: 版本：v4.0.0
:: =============================================

echo.
echo ==========================================
echo   Hippocampus - U盘版 (Windows + WSL)
echo ==========================================
echo.

set "SCRIPT_DIR=%~dp0"
set "LINUX_DIR=%SCRIPT_DIR%..\brain_dump_linux"

:: 检查 WSL
where wsl >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 需要 WSL，请运行: wsl --install
    pause
    exit /b 1
)

echo 请输入 U盘 盘符（例如 F）：
echo.
set /p DRIVE=盘符 (例如 F): 

if "%DRIVE%"=="" (
    echo 未输入盘符，退出
    pause
    exit /b 1
)

:: 规范盘符
if "%DRIVE:~1,1%"==":" (
    set "DISK_PATH=%DRIVE%\"
) else (
    set "DISK_PATH=%DRIVE%:"
)

echo.
echo 正在扫描 U盘 %DISK_PATH% ...
echo.

:: U盘路径在 WSL 中是 /mnt/f/ 之类的
wsl bash -c "cd '$(wslpath -a '%LINUX_DIR%')' && python3 lib/scanner.py scan --path '$(wslpath -a '%DISK_PATH%')' --output '$(wslpath -a '%SCRIPT_DIR%output')' --db '$(wslpath -a '%LINUX_DIR%\db\brain_dump.sqlite')'"

echo.
echo 扫描完成，结果已写入 output/
pause
