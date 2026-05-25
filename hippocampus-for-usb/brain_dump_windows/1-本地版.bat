@echo off
chcp 65001 >nul
:: =============================================
:: Hippocampus Windows - 本地版启动器
:: 通过 WSL 运行，自动扫描 /mnt/c/ /mnt/d/ 等磁盘
:: 版本：v4.0.0
:: =============================================

echo.
echo ==========================================
echo   Hippocampus BrainDump - 本地版
echo   通过 WSL 扫描 Windows 文件
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

echo 正在启动 Hippocampus 本地服务...
echo 地址: http://localhost:8080
echo 按 Ctrl+C 停止服务
echo.

wsl bash -c "cd '$(wslpath -a '%LINUX_DIR%')' && python3 server.py --port 8080"

pause
