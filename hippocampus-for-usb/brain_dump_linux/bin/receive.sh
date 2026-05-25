#!/bin/bash
# ===========================================
# Hippocampus BrainDump 接收脚本
# 版本：v4.0.0
# ===========================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DRIVE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo ""
echo "=========================================="
echo "  Hippocampus BrainDump"
echo "  数据接收检查"
echo "=========================================="
echo ""

# 检查数据库
DB_FILE="$DRIVE_DIR/db/brain_dump.sqlite"
if [ ! -f "$DB_FILE" ]; then
    echo "[错误] 数据库文件不存在"
    echo "请确保这是一个正常的 BrainDump U 盘"
    exit 1
fi
echo "[OK] 数据库文件存在"

# 创建必要目录
mkdir -p "$DRIVE_DIR/capture"
mkdir -p "$DRIVE_DIR/output"
mkdir -p "$DRIVE_DIR/log"
echo "[OK] 目录结构完整"

# 统计文件数量
FILE_COUNT=$(find "$DRIVE_DIR/capture" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
echo ""
echo "抓取统计："
echo "  capture 目录中：$FILE_COUNT 个 .md 文件"

# 查询数据库记录数
if command -v sqlite3 &> /dev/null; then
    DB_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM files;" 2>/dev/null)
    if [ -n "$DB_COUNT" ]; then
        echo "  数据库记录：$DB_COUNT 条"
    fi
fi

echo ""
echo "[完成] 数据接收就绪"
echo ""
echo "如需从电脑端写入数据，请运行："
echo "  python3 scripts/scanner.py scan --usb \"$DRIVE_DIR\""
echo ""

read -p "按 Enter 退出..."
exit 0
