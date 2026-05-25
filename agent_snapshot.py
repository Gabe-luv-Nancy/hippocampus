#!/usr/bin/env python3
"""
agent_snapshot.py — 跨平台 Agent 发现 + 记忆目录快照备份
============================================================

功能：
  Phase 1: 扫描当前 Linux/WSL distro 中的 Agent 并备份记忆文件
  Phase 2: 手动指定 Agent 路径进行备份（用于其他 distro）

输出目录: /mnt/x/HERABIN/output/hippo_snapshots/<timestamp>/

⚠️ 只读取、新建、复制。绝不删除任何文件。
"""

import os
import sys
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

# ============================================================================
# 全局配置
# ============================================================================

OUTPUT_ROOT = Path("/mnt/x/HERABIN/output/hippo_snapshots")

# Agent 签名库
AGENT_SIGNATURES = {
    "hermes": {
        "display": "Hermes Agent",
        "platforms": ["linux", "wsl"],
        "paths": ["~/.hermes/"],
        "memory_roots": ["memories", "skills", "workspace", "sessions"],
        "memory_files": ["SOUL.md", "config.yaml", "MEMORY.md"],
        "memory_exts": [".md", ".yaml", ".yml", ".json", ".db"],
    },
    "openclaw": {
        "display": "OpenClaw",
        "platforms": ["linux", "wsl"],
        "paths": ["~/.openclaw/"],
        "memory_roots": ["workspace"],
        "memory_files": ["SOUL.md", "MEMORY.md", "USER.md", "AGENTS.md"],
        "memory_exts": [".md", ".yaml", ".yml"],
    },
    "claude_code": {
        "display": "Claude Code",
        "platforms": ["linux", "wsl", "mac", "windows"],
        "paths": ["~/.claude/"],
        "memory_files": ["settings.json"],
        "memory_exts": [".md", ".json", ".txt"],
    },
    "claude_desktop": {
        "display": "Claude Desktop",
        "platforms": ["windows", "mac"],
        "paths": ["~/Library/Application Support/Claude/"],
        "memory_files": ["claude_desktop_conversations.json"],
        "memory_exts": [".json"],
    },
    "chatgpt": {
        "display": "ChatGPT",
        "platforms": ["windows", "mac"],
        "paths": ["~/Library/Application Support/ChatGPT/"],
        "memory_files": ["conversations.json"],
        "memory_exts": [".json", ".md"],
    },
    "cursor": {
        "display": "Cursor",
        "platforms": ["windows", "mac"],
        "paths": ["~/Library/Application Support/Cursor/"],
        "memory_exts": [".json", ".md"],
    },
    "aider": {
        "display": "Aider",
        "platforms": ["linux", "wsl", "mac"],
        "paths": ["~/.aider/"],
        "memory_exts": [".md", ".json", ".toml"],
    },
    "continue_dev": {
        "display": "Continue Dev",
        "platforms": ["linux", "wsl", "mac", "windows"],
        "paths": ["~/.continue/"],
        "memory_files": ["config.json", "history.md"],
        "memory_exts": [".md", ".json"],
    },
    "kimi": {
        "display": "Kimi",
        "platforms": ["windows", "mac"],
        "paths": ["~/Library/Application Support/kimi/"],
        "memory_exts": [".json", ".md", ".txt"],
    },
    "qwen": {
        "display": "通义千问",
        "platforms": ["windows", "mac"],
        "paths": ["~/Library/Application Support/qwen/"],
        "memory_exts": [".json", ".md"],
    },
    "doubao": {
        "display": "豆包",
        "platforms": ["windows", "mac"],
        "paths": ["~/Library/Application Support/doubao/"],
        "memory_exts": [".json", ".md"],
    },
    "yuanbao": {
        "display": "腾讯元宝",
        "platforms": ["windows", "mac"],
        "paths": ["~/Library/Application Support/yuanbao/"],
        "memory_exts": [".json", ".md"],
    },
    "deepseek": {
        "display": "DeepSeek",
        "platforms": ["windows", "mac"],
        "paths": ["~/Library/Application Support/deepseek/"],
        "memory_exts": [".json", ".md"],
    },
    "gemini": {
        "display": "Google Gemini",
        "platforms": ["windows", "mac"],
        "paths": ["~/Library/Application Support/Gemini/"],
        "memory_exts": [".json", ".md"],
    },
}

EXCLUDE_NAMES = {
    "node_modules", "__pycache__", ".git", "venv", ".venv",
    "dist", "build", ".cache", ".npm", ".cargo", ".local",
    "package-lock.json", "yarn.lock", ".DS_Store",
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

# ============================================================================
# 工具函数
# ============================================================================

COLORS = {
    "header": "\033[1;36m", "ok": "\033[1;32m", "warn": "\033[1;33m",
    "fail": "\033[1;31m", "info": "\033[1;34m", "dim": "\033[2m",
    "bold": "\033[1m", "reset": "\033[0m",
}

def cprint(msg: str, color: str = ""):
    c = COLORS.get(color, "")
    print(f"{c}{msg}{COLORS['reset']}")

def fmt_size(size: int) -> str:
    for u in ["B", "KB", "MB", "GB"]:
        if size < 1024: return f"{size:.1f}{u}"
        size /= 1024
    return f"{size:.1f}TB"

def is_excluded(path: Path) -> bool:
    parts = set(path.parts)
    return bool(parts & EXCLUDE_NAMES)

def should_backup(path: Path) -> bool:
    if not path.is_file(): return False
    try:
        sz = path.stat().st_size
        return 0 < sz <= MAX_FILE_SIZE and not is_excluded(path)
    except: return False

def collect_memory_files(root: Path, sig: dict) -> list[Path]:
    """收集 root 目录下的所有记忆文件"""
    files = []
    roots = sig.get("memory_roots", [])
    key_files = sig.get("memory_files", [])
    exts = set(sig.get("memory_exts", [".md", ".json"]))

    # 1. 精确 key_files
    for kf in key_files:
        p = root / kf
        if p.exists() and should_backup(p):
            files.append(p)

    # 2. memory_roots 目录扫描
    for mr in roots:
        p = root / mr
        if p.is_dir():
            for ext in exts:
                for fp in p.rglob(f"*{ext}"):
                    if should_backup(fp) and fp not in files:
                        files.append(fp)

    # 3. 全目录扩展名扫描（限制数量）
    if not files:
        for ext in exts:
            count = 0
            for fp in root.rglob(f"*{ext}"):
                if should_backup(fp) and fp not in files and count < 20:
                    files.append(fp)
                    count += 1

    return files[:30]

def get_current_distro_name() -> str:
    """获取当前 distro 名称"""
    try:
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("PRETTY_NAME="):
                    return line.split("=", 1)[1].strip().strip('"')
    except: pass
    try:
        return os.uname().nodename
    except: pass
    return "unknown"

def check_wsl() -> bool:
    """检查是否在 WSL 环境中"""
    try:
        with open("/proc/version") as f:
            return "microsoft" in f.read().lower() or "wsl" in f.read().lower()
    except: return False

# ============================================================================
# Phase 1: 扫描当前 distro
# ============================================================================

def scan_current_distro() -> list[dict]:
    """扫描当前环境中的所有 Agent"""
    home = Path.home()
    is_wsl = check_wsl()
    platform = "wsl" if is_wsl else "linux"
    detected = []

    cprint(f"  平台: {'WSL' if is_wsl else 'Linux'}  |  Home: {home}", "dim")
    cprint(f"  扫描路径:", "dim")

    for agent_id, sig in AGENT_SIGNATURES.items():
        plats = sig.get("platforms", [])
        if platform not in plats and ("linux" not in plats and "wsl" not in plats):
            continue

        for path_hint in sig["paths"]:
            p = Path(os.path.expanduser(path_hint))
            if p.exists():
                mem_files = collect_memory_files(p, sig)
                detected.append({
                    "id": agent_id,
                    "display": sig["display"],
                    "root": str(p),
                    "platform": platform,
                    "memory_files": [str(f) for f in mem_files],
                })
                cprint(f"    ✅ {sig['display']}: {p}  ({len(mem_files)} 个文件)", "ok")
                break
        else:
            cprint(f"    — {sig['display']}: 未找到", "dim")

    return detected

# ============================================================================
# Phase 2: 手动指定路径备份
# ============================================================================

def backup_path(path_str: str, label: str = "custom") -> list[Path]:
    """手动指定一个 Agent 根目录，收集所有记忆文件"""
    p = Path(os.path.expanduser(path_str))
    if not p.exists():
        cprint(f"  ❌ 路径不存在: {p}", "fail")
        return []

    cprint(f"  扫描目录: {p}", "info")
    files = []
    for ext in [".md", ".yaml", ".yml", ".json", ".txt", ".toml"]:
        for fp in p.rglob(f"*{ext}"):
            if should_backup(fp) and fp not in files:
                files.append(fp)

    cprint(f"  找到 {len(files)} 个文件", "ok")
    return files[:50]

# ============================================================================
# Phase 3: 快照备份
# ============================================================================

def create_snapshot(
    sources: list[dict],
    snapshot_dir: Path,
    label: str = "",
) -> dict:
    """将记忆文件复制到快照目录"""
    manifest = {
        "snapshot_time": datetime.now().isoformat(),
        "label": label,
        "sources": sources,
        "total_files": 0,
        "total_bytes": 0,
        "errors": [],
    }

    snapshot_dir.mkdir(parents=True, exist_ok=True)
    total_files = 0
    total_bytes = 0

    for src in sources:
        if not src.get("memory_files"):
            continue

        safe_name = f"{src['platform']}_{src['id']}"
        subdir = snapshot_dir / safe_name
        subdir.mkdir(parents=True, exist_ok=True)

        for fp_str in src["memory_files"]:
            fp = Path(fp_str)
            if not fp.exists() or not should_backup(fp):
                continue

            dest = subdir / fp.name
            if dest.exists():
                ts = datetime.now().strftime("%Y%m%d%H%M%S")
                dest = subdir / f"{fp.stem}_{ts}{fp.suffix}"

            try:
                shutil.copy2(fp, dest)
                sz = dest.stat().st_size
                total_files += 1
                total_bytes += sz
                cprint(f"    ✅ {fp.name} ({fmt_size(sz)})", "ok")
            except Exception as e:
                manifest["errors"].append(f"{fp}: {e}")
                cprint(f"    ❌ {fp.name}: {e}", "fail")

    manifest["total_files"] = total_files
    manifest["total_bytes"] = total_bytes

    with open(snapshot_dir / "snapshot_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    return manifest

# ============================================================================
# 主流程
# ============================================================================

def main():
    cprint("=" * 56, "bold")
    cprint("  Agent Snapshot  跨平台Agent记忆快照  v2.0", "header")
    cprint("=" * 56, "bold")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot_dir = OUTPUT_ROOT / ts
    cprint(f"\n📁 快照目录: {snapshot_dir}", "info")

    # Phase 1: 自动扫描当前 distro
    cprint(f"\n{'─' * 56}", "dim")
    cprint("Phase 1 — 自动扫描当前环境", "header")
    cprint(f"{'─' * 56}", "dim")

    detected = scan_current_distro()

    if not detected:
        cprint("\n  ⚠️  未检测到任何 Agent，尝试手动指定路径", "warn")
        cprint("  用法: python3 agent_snapshot.py --path ~/.your_agent/ --label your_agent", "dim")
    else:
        cprint(f"\n  共发现 {len(detected)} 个 Agent", "ok")

    # Phase 2: 命令行手动路径（如果传了参数）
    sources = detected
    import argparse
    parser = argparse.ArgumentParser(description="Agent Snapshot")
    parser.add_argument("--path", help="手动指定 Agent 根目录")
    parser.add_argument("--label", default="manual", help="标签名")
    args, _ = parser.parse_known_args()

    if args.path:
        cprint(f"\n{'─' * 56}", "dim")
        cprint(f"Phase 2 — 手动路径: {args.path}", "header")
        cprint(f"{'─' * 56}", "dim")
        files = backup_path(args.path, args.label)
        if files:
            sources.append({
                "id": args.label,
                "display": args.label,
                "root": args.path,
                "platform": "manual",
                "memory_files": [str(f) for f in files],
            })

    # Phase 3: 快照
    cprint(f"\n{'─' * 56}", "dim")
    cprint("Phase 3 — 写入快照", "header")
    cprint(f"{'─' * 56}", "dim")

    if sources:
        manifest = create_snapshot(sources, snapshot_dir)
    else:
        manifest = create_snapshot([], snapshot_dir)

    # 汇总
    cprint(f"\n{'═' * 56}", "bold")
    cprint("  快照完成", "header")
    cprint(f"{'═' * 56}", "bold")
    cprint(f"  时间: {ts}", "info")
    cprint(f"  输出: {snapshot_dir}", "info")
    cprint(f"  Agent: {len(sources)} 个", "ok")
    cprint(f"  备份: {manifest['total_files']} 个 ({fmt_size(manifest['total_bytes'])})", "ok")
    cprint(f"  清单: snapshot_manifest.json", "dim")

    if manifest["total_files"] == 0:
        cprint("\n  ⚠️  未备份任何文件，可能原因：", "warn")
        cprint("  • Agent 尚未生成记忆文件", "warn")
        cprint("  • 需要先在 Agent 中对话一次", "warn")
        cprint("  • 用 --path 手动指定路径", "warn")

    return 0

if __name__ == "__main__":
    sys.exit(main())
