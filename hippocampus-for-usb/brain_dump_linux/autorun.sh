#!/bin/bash
# ===========================================
# Hippocampus BrainDump U 盘自动运行脚本
# 版本：v4.0.0
# 支持：macOS / Linux
# GUI: PyQt6 Desktop Application
# ===========================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MARKER_FILE="$SCRIPT_DIR/marker.txt"
EXPECTED_MARKER="HIPPOCAMPUS_BRAINDUMP_v4.0.0"

# 检测 marker 文件
if [ ! -f "$MARKER_FILE" ]; then
    exit 0
fi

MARKER_CONTENT=$(cat "$MARKER_FILE" | tr -d '[:space:]')
if [ "$MARKER_CONTENT" != "$EXPECTED_MARKER" ]; then
    exit 0
fi

# ========== 验证通过，显示产品标识 ==========
echo ""
echo "=========================================="
echo "  🦛 Hippocampus BrainDump v4.0.0"
echo "  AI Memory Dump Drive — USB Edition"
echo "=========================================="
echo ""

# ========== 检查数据库 ==========
DB_FILE="$SCRIPT_DIR/db/brain_dump.sqlite"
if [ ! -f "$DB_FILE" ]; then
    echo "[错误] 数据库文件不存在"
    echo "请运行 python3 db/init_db.py 初始化"
    echo ""
    read -p "按 Enter 退出..."
    exit 1
fi

echo "[OK] 数据库就绪"

# ========== 创建必要目录 ==========
mkdir -p "$SCRIPT_DIR/capture"
mkdir -p "$SCRIPT_DIR/output"
mkdir -p "$SCRIPT_DIR/log"

# ========== 检查 Python ==========
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
fi

# ========== 检查 PyQt6 ==========
HAS_PYQT6=false
if [ -n "$PYTHON_CMD" ]; then
    $PYTHON_CMD -c "import PyQt6" 2>/dev/null && HAS_PYQT6=true
fi

# ========== 显示菜单 ==========
echo ""
if [ "$HAS_PYQT6" = true ]; then
    echo "请选择操作："
    echo "  [1] 启动桌面 GUI（推荐）"
    echo "  [2] 仅检查数据完整性"
    echo "  [3] 打开输出目录"
    echo "  [4] 启动 HTTP API 服务（备用）"
    echo "  [5] 退出"
    echo ""
    read -p "请输入选项 (1-5): " CHOICE
else
    echo "⚠️  未检测到 PyQt6，桌面 GUI 不可用"
    echo ""
    echo "请选择操作："
    echo "  [1] 启动 HTTP API 服务（浏览器访问）"
    echo "  [2] 仅检查数据完整性"
    echo "  [3] 打开输出目录"
    echo "  [4] 退出"
    echo ""
    read -p "请输入选项 (1-4): " CHOICE
fi

# ========== 执行选项 ==========
if [ "$HAS_PYQT6" = true ]; then
    case "$CHOICE" in
        1)
            echo ""
            echo "正在启动 Hippocampus Desktop GUI..."
            echo ""
            cd "$SCRIPT_DIR"
            $PYTHON_CMD gui_main.py --mode disk --path "$SCRIPT_DIR"
            ;;
        2)
            bash "$SCRIPT_DIR/bin/receive.sh"
            ;;
        3)
            mkdir -p "$SCRIPT_DIR/output"
            case "$(uname)" in
                Darwin) open "$SCRIPT_DIR/output" ;;
                Linux) xdg-open "$SCRIPT_DIR/output" 2>/dev/null || echo "请手动打开 output 目录" ;;
            esac
            ;;
        4)
            echo ""
            echo "正在启动 HTTP API 服务..."
            echo "访问 http://127.0.0.1:8080"
            echo "按 Ctrl+C 停止服务"
            echo ""
            cd "$SCRIPT_DIR"
            $PYTHON_CMD server.py --port 8080
            ;;
        *)
            exit 0
            ;;
    esac
else
    case "$CHOICE" in
        1)
            echo ""
            echo "正在启动 HTTP API 服务..."
            echo "访问 http://127.0.0.1:8080"
            echo "按 Ctrl+C 停止服务"
            echo ""
            if [ -n "$PYTHON_CMD" ]; then
                cd "$SCRIPT_DIR"
                $PYTHON_CMD server.py --port 8080
            else
                echo "[错误] 未检测到 Python"
                read -p "按 Enter 退出..."
            fi
            ;;
        2)
            bash "$SCRIPT_DIR/bin/receive.sh"
            ;;
        3)
            mkdir -p "$SCRIPT_DIR/output"
            case "$(uname)" in
                Darwin) open "$SCRIPT_DIR/output" ;;
                Linux) xdg-open "$SCRIPT_DIR/output" 2>/dev/null || echo "请手动打开 output 目录" ;;
            esac
            ;;
        *)
            exit 0
            ;;
    esac
fi

exit 0
