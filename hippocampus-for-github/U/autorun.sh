#!/bin/bash
# ============================================================================
# Hippocampus AI Memory Stick - macOS/Linux Auto-run
# ============================================================================

DRIVE="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="$DRIVE/activity.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "================================================"
log "Hippocampus AI Memory Stick v3.2"
log "Drive: $DRIVE"
log "================================================"

# 检查是否是Hippocampus U盘
if [ ! -f "$DRIVE/HIPPOCAMPUS_Marker.txt" ]; then
    log "[错误] 此U盘不是 Hippocampus 产品"
    exit 1
fi

# 检查Python
if ! command -v python3 &> /dev/null; then
    log "[警告] 未检测到 Python3，部分功能可能不可用"
    log "请访问 https://www.python.org 下载安装"
fi

# 创建必要目录
mkdir -p "$DRIVE/capture" "$DRIVE/output" "$DRIVE/db"

log ""
log "[1/3] 正在抓取 AI 记忆文件..."
if [ -f "$DRIVE/scripts/capture.py" ]; then
    cd "$DRIVE"
    python3 scripts/capture.py -o capture -s 2>&1 | tee -a "$LOG_FILE"
else
    log "[跳过] capture.py 未找到"
fi

log ""
log "[2/3] 正在分析记忆..."
if [ -f "$DRIVE/scripts/analyzer.py" ]; then
    cd "$DRIVE"
    python3 scripts/analyzer.py -b . -i 2>&1 | tee -a "$LOG_FILE"
    python3 scripts/analyzer.py -b . -r markdown 2>&1 | tee -a "$LOG_FILE"
else
    log "[跳过] analyzer.py 未找到"
fi

log ""
log "[3/3] 处理完成！"

# 打开输出目录
if [ -d "$DRIVE/output" ]; then
    log "正在打开输出目录..."
    if [ "$(uname)" = "Darwin" ]; then
        open "$DRIVE/output"
    else
        xdg-open "$DRIVE/output" 2>/dev/null
    fi
fi

log ""
log "================================================"
log "处理完成！请查看 output 目录中的报告"
log "================================================"

# macOS: 保持窗口
if [ "$(uname)" = "Darwin" ]; then
    echo ""
    echo "按 Enter 键退出..."
    read
fi
