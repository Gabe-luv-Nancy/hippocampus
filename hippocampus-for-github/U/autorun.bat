@echo off
chcp 65001 > nul
echo ================================================
echo  Hippocampus AI Memory Stick
echo  Loading...
echo ================================================
echo.

REM 获取U盘盘符
set DRIVE=%~d0

REM 检查是否是Hippocampus U盘
if not exist "%DRIVE%\HIPPOCAMPUS_Marker.txt" (
    echo [错误] 此U盘不是 Hippocampus 产品
    pause
    exit /b
)

REM 等待系统就绪
echo 正在初始化...
timeout /t 3 /nobreak > nul

REM 切换到U盘目录
cd /d "%DRIVE%"

REM 检查Python
python --version > nul 2>&1
if errorlevel 1 (
    echo [警告] 未检测到 Python，部分功能可能不可用
    echo 请访问 https://www.python.org 下载安装
    echo.
)

REM 运行抓取
echo.
echo [1/3] 正在抓取 AI 记忆文件...
if exist "scripts\capture.py" (
    python scripts\capture.py -o capture -s
) else (
    echo [跳过] capture.py 未找到
)

REM 运行分析
echo.
echo [2/3] 正在分析记忆...
if exist "scripts\analyzer.py" (
    python scripts\analyzer.py -b . -i
    python scripts\analyzer.py -b . -r markdown
) else (
    echo [跳过] analyzer.py 未找到
)

REM 完成
echo.
echo [3/3] 处理完成！
echo.

REM 打开输出目录
if exist "output" (
    echo 正在打开输出目录...
    start explorer output
)

echo ================================================
echo  处理完成！请查看 output 目录中的报告
echo  按任意键退出...
echo ================================================
pause > nul
