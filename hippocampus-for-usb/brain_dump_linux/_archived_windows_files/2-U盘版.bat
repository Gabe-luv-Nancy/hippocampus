@echo off
chcp 65001 >nul
:: =============================================
:: Hippocampus GUI - U盘版启动器
:: 双击此文件，选择 U盘 盘符
:: =============================================
echo.
echo ==========================================
echo   Hippocampus - U盘版
echo ==========================================
echo.
echo 请输入 U盘 盘符（例如 F）：
echo.
set /p DRIVE=盘符 (例如 F):

if "%DRIVE%"=="" (
    echo 未输入盘符，退出
    pause
    exit /b 1
)

:: Add colon if not present
echo.
echo 正在启动...
if "%DRIVE:~1,1%"==":" (
    set DISK_PATH=%DRIVE%\
) else (
    set DISK_PATH=%DRIVE%:
)

"%~dp0Hippocampus.exe" --mode disk --path "%DISK_PATH%"
pause
