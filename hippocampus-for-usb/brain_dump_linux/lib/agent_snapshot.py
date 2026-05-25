#!/usr/bin/env python3
"""
agent_snapshot.py — 跨平台 Agent 发现 + 记忆目录快照备份
==========================================================

从 Windows（WSL内）出发：
  Phase 0: 扫描 Windows 本机 AI 工具路径
  Phase 1: 发现所有 WSL distro
  Phase 2: 在每个 distro 中识别 Agent 类型
  Phase 3: 定位记忆目录，复制到时间戳快照

输出目录: /mnt/x/HERABIN/output/hippo_snapshots/<YYYYMMDD_HHMMSS>/

⚠️ 只读取、新建、复制。绝不删除任何文件。
"""

import os
import sys
import json
import shutil
import hashlib
import subprocess
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

# ============================================================================
# 全局配置
# ============================================================================

# 快照输出根目录
OUTPUT_ROOT = Path("/mnt/x/HERABIN/output/hippo_snapshots")

# Agent 签名定义（路径 + 记忆文件模式）
AGENT_SIGNATURES = {
    # ---- Coding / CLI Agents ----
    "hermes": {
        "display": "Hermes Agent (赫墨)",
        "paths": ["~/.hermes/"],
        "memory_patterns": [
            "~/.hermes/memory/",
            "~/.hermes/config.yaml",
            "~/.hermes/skills/",
        ],
        "memory_extensions": [".md", ".yaml", ".yml", ".json"],
    },
    "openclaw": {
        "display": "OpenClaw",
        "paths": ["~/.openclaw/", "~/.openclaw/workspace/"],
        "memory_patterns": [
            "~/.openclaw/workspace/MEMORY.md",
            "~/.openclaw/workspace/SOUL.md",
            "~/.openclaw/workspace/USER.md",
            "~/.openclaw/workspace/AGENTS.md",
        ],
        "memory_extensions": [".md", ".yaml", ".yml", ".json"],
    },
    "claude_code": {
        "display": "Claude Code",
        "paths": ["~/.claude/"],
        "memory_patterns": [
            "~/.claude/settings.json",
            "~/.claude/projects/",
            "~/.claude/.claude/",
        ],
        "memory_extensions": [".md", ".json", ".txt"],
    },
    "cursor_server": {
        "display": "Cursor Server",
        "paths": ["~/.cursor-server/", "~/.cursor/"],
        "memory_patterns": [
            "~/.cursor-server/",
            "~/.cursor/",
        ],
        "memory_extensions": [".md", ".json"],
    },
    "aider": {
        "display": "Aider",
        "paths": ["~/.aider/", "~/.config/aider/"],
        "memory_patterns": [
            "~/.aider/",
        ],
        "memory_extensions": [".md", ".json", ".toml"],
    },
    "continue_dev": {
        "display": "Continue Dev",
        "paths": ["~/.continue/"],
        "memory_patterns": [
            "~/.continue/config.json",
            "~/.continue/history.md",
        ],
        "memory_extensions": [".md", ".json"],
    },
    # ---- GUI AI Assistants ----
    "claude_desktop": {
        "display": "Claude Desktop",
        "platforms": ["windows", "mac"],
        "paths_win": ["AppData/Roaming/Claude/"],
        "paths_mac": ["Library/Application Support/Claude/"],
        "memory_patterns": [
            "claude_desktop_conversations.json",
            "settings.json",
        ],
        "memory_extensions": [".json"],
    },
    "chatgpt": {
        "display": "ChatGPT",
        "platforms": ["windows", "mac"],
        "paths_win": ["AppData/Roaming/ChatGPT/", ".chatgpt/"],
        "paths_mac": ["Library/Application Support/ChatGPT/"],
        "memory_patterns": [
            "conversations.json",
            "user.json",
        ],
        "memory_extensions": [".json", ".md"],
    },
    "cursor": {
        "display": "Cursor (GUI)",
        "platforms": ["windows", "mac"],
        "paths_win": [
            "AppData/Roaming/Cursor/",
            "AppData/Local/Programs/cursor/",
            ".cursor/",
        ],
        "paths_mac": [
            "Library/Application Support/Cursor/",
            "Library/Application Support/cursor/",
        ],
        "memory_patterns": [],
        "memory_extensions": [".json", ".md"],
    },
    "copilot": {
        "display": "VS Code Copilot",
        "platforms": ["windows", "mac"],
        "paths_win": [".vscode/"],
        "paths_mac": [".vscode/"],
        "memory_patterns": [
            ".vscode/extensions/",
            ".vscode/Copilot/",
        ],
        "memory_extensions": [".json"],
    },
    "doubao": {
        "display": "豆包",
        "paths": ["~/.doubao/", "Library/Application Support/doubao/"],
        "memory_patterns": ["memory/"],
        "memory_extensions": [".json", ".md"],
    },
    "kimi": {
        "display": "Kimi",
        "paths": ["~/.kimi/", "Library/Application Support/kimi/"],
        "memory_patterns": ["memory/"],
        "memory_extensions": [".json", ".txt"],
    },
    "qwen": {
        "display": "通义千问",
        "paths": ["~/.qwen/"],
        "memory_patterns": ["memory/"],
        "memory_extensions": [".json", ".md"],
    },
    "yuanbao": {
        "display": "腾讯元宝",
        "paths": ["~/.yuanbao/"],
        "memory_patterns": ["memory/"],
        "memory_extensions": [".json", ".md"],
    },
    "deepseek": {
        "display": "DeepSeek",
        "paths": ["~/.deepseek/"],
        "memory_patterns": ["memory/"],
        "memory_extensions": [".json", ".md"],
    },
    "gemini": {
        "display": "Google Gemini",
        "paths": ["~/.gemini/"],
        "memory_patterns": [],
        "memory_extensions": [".json", ".md"],
    },
    "xfyun": {
        "display": "讯飞星火",
        "paths": ["~/.xfyun/"],
        "memory_patterns": ["memory/"],
        "memory_extensions": [".json", ".md"],
    },
}

# 扫描时忽略的路径模式（排除 node_modules、__pycache__ 等）
EXCLUDE_PATTERNS = [
    "**/node_modules/**",
    "**/__pycache__/**",
    "**/.git/**",
    "**/venv/**",
    "**/.venv/**",
    "**/dist/**",
    "**/build/**",
    "**/cache/**",
    "**/.cache/**",
    "**/.npm/**",
    "**/.cargo/registry/**",
]

# 最大单文件大小（超过跳过，单位：字节）
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

# ============================================================================
# 工具函数
# ============================================================================

def cprint(msg: str, color: str = ""):
    """简单彩色打印"""
    COLORS = {
        "header": "\033[1;36m",
        "ok": "\033[1;32m",
        "warn": "\033[1;33m",
        "fail": "\033[1;31m",
        "info": "\033[1;34m",
        "dim": "\033[2m",
        "bold": "\033[1m",
        "reset": "\033[0m",
    }
    c = COLORS.get(color, "")
    print(f"{c}{msg}{COLORS['reset']}")


def expand_path(p: str, home: str = os.path.expanduser("~")) -> Path:
    """展开 ~ 和环境变量，返回绝对 Path"""
    p = os.path.expandvars(p)
    p = p.replace("~", home)
    return Path(p).resolve()


def get_sha256(path: Path) -> Optional[str]:
    """计算文件 SHA256（失败返回 None）"""
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def matches_exclude(path: Path) -> bool:
    """检查路径是否匹配排除模式"""
    path_str = str(path)
    for pattern in EXCLUDE_PATTERNS:
        pattern = pattern.replace("**/", "")
        if pattern in path_str:
            return True
    return False


def should_backup_file(path: Path) -> bool:
    """判断文件是否应该备份"""
    if not path.is_file():
        return False
    try:
        size = path.stat().st_size
        if size > MAX_FILE_SIZE or size == 0:
            return False
    except Exception:
        return False
    if matches_exclude(path):
        return False
    return True


def get_current_wsl_distro() -> Optional[str]:
    """获取当前 WSL distro 名称（通过 /etc/wsl.conf 或 /proc/version）"""
    # 方法1: 读取 /proc/sys/kernel/osrelease
    try:
        with open("/proc/version", "r") as f:
            content = f.read().lower()
            if "microsoft" in content or "wsl" in content:
                pass  # 确实在 WSL 里
    except Exception:
        return None

    # 方法2: 读取 /etc/os-release
    try:
        with open("/etc/os-release", "r") as f:
            for line in f:
                if line.startswith("NAME="):
                    distro_name = line.split("=", 1)[1].strip().strip('"')
                    return distro_name
    except Exception:
        pass

    # 方法3: hostname（WSL 默认是机器名）
    try:
        hostname = os.uname().nodename
        if hostname:
            return hostname
    except Exception:
        pass

    return None


def discover_wsl_distros() -> list[dict]:
    """通过 wsl.exe 发现所有注册的 WSL 发行版"""
    distros = []

    # 检测是否在 WSL 内
    is_wsl = False
    try:
        with open("/proc/version", "r") as f:
            if "microsoft" in f.read().lower() or "wsl" in f.read().lower():
                is_wsl = True
    except Exception:
        pass

    if not is_wsl:
        cprint("[Phase 1] 未检测到 WSL 环境，跳过 distro 发现", "warn")
        return []

    # 调用 wsl.exe -l -v（输出是 UTF-16）
    try:
        result = subprocess.run(
            ["wsl.exe", "-l", "-v"],
            capture_output=True,
            timeout=15,
        )
        raw = result.stdout
        # 尝试解码 UTF-16
        try:
            text = raw.decode("utf-16-le").replace("\r", "")
        except Exception:
            text = raw.decode("utf-8", errors="replace").replace("\r", "")

        lines = [l.strip() for l in text.split("\n") if l.strip()]
        for line in lines:
            # 解析格式: NAME              STATE           VERSION
            # 或者带 * 的格式
            line = line.lstrip("* ").strip()
            parts = re.split(r"\s{2,}", line)
            if len(parts) >= 2:
                name = parts[0].strip()
                state = parts[1].strip() if len(parts) > 1 else "Unknown"
                version = parts[2].strip() if len(parts) > 2 else "?"
                if name and name not in ("NAME", "名称") and not name.startswith("-"):
                    distros.append({
                        "name": name,
                        "state": state,
                        "version": version,
                        "is_current": False,
                    })
    except FileNotFoundError:
        cprint("[Phase 1] wsl.exe 未找到，可能不在 Windows WSL 环境中", "warn")
    except subprocess.TimeoutExpired:
        cprint("[Phase 1] wsl.exe 超时", "warn")
    except Exception as e:
        cprint(f"[Phase 1] wsl.exe 调用失败: {e}", "warn")

    # 标记当前 distro
    current = get_current_wsl_distro()
    for d in distros:
        d["is_current"] = d["name"].lower().replace("-", "_").replace(" ", "_") == current.lower().replace("-", "_").replace(" ", "_") \
                          if current else False

    return distros


def run_in_distro(distro_name: str, cmd: str, timeout: int = 20) -> tuple[str, int]:
    """在指定 WSL distro 中执行命令，返回 (stdout, exit_code)"""
    try:
        result = subprocess.run(
            ["wsl.exe", "-d", distro_name, "--", "bash", "-c", cmd],
            capture_output=True,
            timeout=timeout,
        )
        return result.stdout.decode("utf-8", errors="replace"), result.returncode
    except subprocess.TimeoutExpired:
        return "", -1
    except FileNotFoundError:
        return "", -1
    except Exception:
        return "", -1


def list_dir_safe(path: Path, max_items: int = 50) -> list[str]:
    """安全列出目录内容"""
    try:
        items = os.listdir(str(path))
        return items[:max_items]
    except (PermissionError, FileNotFoundError, OSError):
        return []


# ============================================================================
# Phase 0: Windows 本机扫描（通过 /mnt/c/）
# ============================================================================

def scan_windows_agents(windows_user: str) -> dict:
    """扫描 Windows 机器上安装的 AI 工具"""
    results = {}
    windows_base = Path(f"/mnt/c/Users/{windows_user}")

    if not windows_base.exists():
        cprint(f"[Phase 0] Windows 用户目录不存在: {windows_base}", "warn")
        return results

    cprint(f"[Phase 0] 扫描 Windows 本机 (用户: {windows_user})", "header")

    for agent_id, sig in AGENT_SIGNATURES.items():
        if "platforms" not in sig or "windows" not in sig["platforms"]:
            continue

        found_paths = []
        for path_hint in sig.get("paths_win", []):
            full_path = windows_base / path_hint
            if full_path.exists():
                found_paths.append(str(full_path))

        if found_paths:
            results[agent_id] = {
                "display": sig["display"],
                "platform": "windows",
                "found_paths": found_paths,
                "agent_root": found_paths[0],
            }
            cprint(f"  ✅ {sig['display']}: {found_paths[0]}", "ok")

    return results


# ============================================================================
# Phase 1 & 2: WSL Distro 发现 + Agent 识别
# ============================================================================

def scan_wsl_distros() -> dict:
    """发现所有 WSL distro，并在每个中识别 Agent"""
    results = {}
    distros = discover_wsl_distros()

    if not distros:
        cprint("[Phase 1+2] 未发现任何 WSL distro，扫描当前环境", "warn")
        # 退化为只扫描当前 distro
        current_result = scan_single_distro(get_current_wsl_distro() or "local", "~")
        if current_result:
            results["local"] = current_result
        return results

    cprint(f"[Phase 1] 发现 {len(distros)} 个 WSL distro:", "header")
    for d in distros:
        marker = " ← 当前" if d["is_current"] else ""
        cprint(f"  • {d['name']}  [{d['state']}]  (WSL {d['version']}){marker}", "info")

    for d in distros:
        distro_name = d["name"]
        cprint(f"\n[Phase 2] 扫描 distro: {distro_name}", "header")

        if d["is_current"]:
            # 已经在当前 distro 里，直接用本地路径
            result = scan_single_distro(distro_name, "~")
        else:
            # 在其他 distro 中执行扫描
            result = scan_remote_distro(distro_name)

        if result:
            results[distro_name] = result

    return results


def scan_single_distro(distro_name: str, home_hint: str = "~") -> Optional[dict]:
    """扫描当前 distro 中的 Agent（本地执行）"""
    home = Path.home()

    detected = []
    for agent_id, sig in AGENT_SIGNATURES.items():
        if sig.get("platforms") and "windows" in sig["platforms"]:
            continue  # 跳过 Windows GUI agent

        for path_hint in sig.get("paths", []):
            expanded = expand_path(path_hint, str(home))
            if expanded.exists():
                detected.append({
                    "id": agent_id,
                    "display": sig["display"],
                    "root": str(expanded),
                    "exists": expanded.exists(),
                })
                cprint(f"  ✅ {sig['display']}: {expanded}", "ok")
                break  # 找到一个路径就够

    if not detected:
        cprint(f"  ⚠️  未检测到任何已知 Agent", "warn")

    return {
        "distro": distro_name,
        "agents": detected,
        "is_current_distro": True,
    }


def scan_remote_distro(distro_name: str) -> Optional[dict]:
    """在远程 WSL distro 中执行 Agent 发现"""
    # 先探测 distro 是否运行中
    stdout, code = run_in_distro(distro_name, "echo DISTRO_ALIVE", timeout=10)
    if code != 0:
        # distro 未运行，尝试启动
        cprint(f"  ⏳ distro '{distro_name}' 未运行，尝试启动...", "warn")
        try:
            subprocess.run(["wsl.exe", "-d", distro_name], capture_output=True, timeout=30)
            stdout, code = run_in_distro(distro_name, "echo DISTRO_ALIVE", timeout=15)
        except Exception as e:
            cprint(f"  ❌ 无法启动 distro: {e}", "fail")
            return None

    # 探测 distro 中的 Agent（构造一个跨 distro 的扫描命令）
    # 收集所有已知 Agent 路径
    scan_cmd = _build_remote_scan_command()
    stdout, code = run_in_distro(distro_name, scan_cmd, timeout=60)

    detected = _parse_remote_scan_result(stdout)

    for item in detected:
        cprint(f"  ✅ {item['display']}: {item['root']}", "ok")

    if not detected:
        cprint(f"  ⚠️  未检测到任何已知 Agent", "warn")

    return {
        "distro": distro_name,
        "agents": detected,
        "is_current_distro": False,
    }


def _build_remote_scan_command() -> str:
    """构造在远程 distro 中执行的 Agent 发现脚本（单行）"""
    # 构造 Python 一行脚本
    agents_json = json.dumps(AGENT_SIGNATURES, ensure_ascii=False)
    script = f"""python3 -c \"
import os, json, sys
from pathlib import Path
home = Path.home()
sig = {agents_json}
found = []
for aid, s in sig.items():
    if s.get('platforms') and 'windows' in s['platforms']:
        continue
    for ph in s.get('paths', []):
        p = Path(os.path.expandvars(ph.replace('~', str(home))))
        if p.exists():
            found.append({{'id': aid, 'display': s['display'], 'root': str(p)}})
            break
print(json.dumps(found))
\" 2>/dev/null"""
    return script


def _parse_remote_scan_result(stdout: str) -> list:
    """解析远程 distro 的 JSON 输出"""
    try:
        # 找 JSON 部分
        text = stdout.strip()
        start = text.find("[")
        end = text.rfind("]") + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
    except Exception:
        pass
    return []


# ============================================================================
# Phase 3: 记忆目录发现 + 快照备份
# ============================================================================

def find_memory_files(agent_info: dict, home: Path) -> list[Path]:
    """在给定 Agent 根目录下找到所有记忆文件"""
    agent_id = agent_info["id"]
    root = Path(agent_info["root"])
    sig = AGENT_SIGNATURES.get(agent_id, {})

    memory_files = []

    # 方法1: 精确匹配 memory_patterns
    for pattern in sig.get("memory_patterns", []):
        p = expand_path(pattern, str(home))
        if p.exists():
            if p.is_file():
                if should_backup_file(p):
                    memory_files.append(p)
            elif p.is_dir():
                for ext in sig.get("memory_extensions", [".md", ".json", ".yaml", ".yml", ".txt"]):
                    for fp in p.rglob(f"*{ext}"):
                        if should_backup_file(fp):
                            memory_files.append(fp)

    # 方法2: 在根目录下扫描所有匹配扩展名的文件
    for ext in sig.get("memory_extensions", [".md", ".json"]):
        for fp in root.rglob(f"*{ext}"):
            if should_backup_file(fp) and fp not in memory_files:
                # 进一步过滤：排除明显不是记忆的文件
                name = fp.name.lower()
                if any(k in name for k in ["memory", "soul", "user", "config", "agent", "memo", "note", "log", "state"]):
                    memory_files.append(fp)

    return list(set(memory_files))


def backup_to_snapshot(
    windows_results: dict,
    wsl_results: dict,
    snapshot_dir: Path,
) -> dict:
    """将所有发现的记忆文件备份到快照目录，返回备份清单"""
    manifest = {
        "snapshot_time": datetime.now().isoformat(),
        "platform": "windows_wsl",
        "sources": [],
        "total_files": 0,
        "total_bytes": 0,
    }

    # 来源顺序：windows → wsl distros
    all_sources = []

    for agent_id, info in windows_results.items():
        src = {
            "platform": "windows",
            "agent_id": agent_id,
            "display": info["display"],
            "root": info["agent_root"],
            "files": [],
        }
        root = Path(info["agent_root"])
        home = Path("/mnt/c/Users/GABETOPZ")  # Windows home
        sig = AGENT_SIGNATURES.get(agent_id, {})

        for pattern in sig.get("memory_patterns", []):
            p = expand_path(pattern.replace("~", str(home)), str(home))
            if p.exists():
                for fp in (list(p.rglob("*")) if p.is_dir() else [p]):
                    if should_backup_file(fp):
                        src["files"].append(str(fp))

        if src["files"]:
            all_sources.append(src)

    for distro_name, distro_info in wsl_results.items():
        for agent_info in distro_info.get("agents", []):
            home = Path.home()
            files = find_memory_files(agent_info, home)
            src = {
                "platform": "wsl",
                "distro": distro_name,
                "agent_id": agent_info["id"],
                "display": agent_info["display"],
                "root": agent_info["root"],
                "files": [str(f) for f in files],
            }
            if src["files"]:
                all_sources.append(src)

    # 执行备份
    backup_count = 0
    backup_bytes = 0

    for src in all_sources:
        cprint(f"\n[Phase 3] 备份 {src['display']} ({src.get('distro', 'windows')})", "header")

        # 确定目标子目录名
        if src["platform"] == "windows":
            subdir = snapshot_dir / "windows" / src["agent_id"]
        else:
            safe_distro = src.get("distro", "unknown").replace(" ", "_")
            subdir = snapshot_dir / "wsl" / safe_distro / src["agent_id"]

        subdir.mkdir(parents=True, exist_ok=True)

        for filepath in src["files"]:
            src_path = Path(filepath)
            dest_path = subdir / src_path.name

            # 同名文件加时间戳
            if dest_path.exists():
                ts = datetime.now().strftime("%Y%m%d%H%M%S")
                stem = src_path.stem
                ext = src_path.suffix
                dest_path = subdir / f"{stem}_{ts}{ext}"

            try:
                shutil.copy2(src_path, dest_path)
                size = dest_path.stat().st_size
                backup_count += 1
                backup_bytes += size
                cprint(f"  ✅ {src_path.name} ({_format_size(size)})", "ok")
            except Exception as e:
                cprint(f"  ❌ {src_path.name}: {e}", "fail")

    manifest["sources"] = all_sources
    manifest["total_files"] = backup_count
    manifest["total_bytes"] = backup_bytes

    # 写 manifest
    manifest_path = snapshot_dir / "snapshot_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    cprint(f"\n[Phase 3] manifest 已写入: {manifest_path}", "dim")

    return manifest


def _format_size(size: int) -> str:
    """格式化文件大小"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}TB"


# ============================================================================
# 主流程
# ============================================================================

def main():
    cprint("=" * 60, "bold")
    cprint("  Agent Snapshot — 跨平台 Agent 记忆快照工具  v1.0", "header")
    cprint("=" * 60, "bold")

    # 创建快照目录
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot_dir = OUTPUT_ROOT / ts
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    cprint(f"\n📁 快照目录: {snapshot_dir}", "info")

    # ---- Phase 0: Windows ----
    cprint(f"\n{'─' * 60}", "dim")
    cprint("PHASE 0 — Windows 本机 AI 工具扫描", "header")
    cprint(f"{'─' * 60}", "dim")

    # 尝试自动获取 Windows 用户名
    windows_user = None
    # 从 /mnt/c/Users/ 下找非系统用户
    try:
        users_dir = Path("/mnt/c/Users")
        if users_dir.exists():
            candidates = [d.name for d in users_dir.iterdir()
                          if d.is_dir() and not d.name.startswith(".")]
            # 优先选当前用户名匹配
            import os as _os
            wsl_user = _os.environ.get("USER", "")
            if wsl_user in candidates:
                windows_user = wsl_user
            elif "GabetopZ" in candidates:
                windows_user = "GabetopZ"
            elif candidates:
                windows_user = candidates[0]
    except Exception:
        pass

    windows_results = {}
    if windows_user:
        windows_results = scan_windows_agents(windows_user)
    else:
        cprint("[Phase 0] 无法确定 Windows 用户名，跳过", "warn")

    # ---- Phase 1+2: WSL Distros ----
    cprint(f"\n{'─' * 60}", "dim")
    cprint("PHASE 1+2 — WSL Distro 发现 + Agent 识别", "header")
    cprint(f"{'─' * 60}", "dim")

    wsl_results = scan_wsl_distros()

    # ---- Phase 3: 备份快照 ----
    cprint(f"\n{'─' * 60}", "dim")
    cprint("PHASE 3 — 记忆目录发现 + 快照备份", "header")
    cprint(f"{'─' * 60}", "dim")

    manifest = backup_to_snapshot(windows_results, wsl_results, snapshot_dir)

    # ---- 汇总 ----
    cprint(f"\n{'═' * 60}", "bold")
    cprint("  快照完成", "header")
    cprint(f"{'═' * 60}", "bold")

    cprint(f"  快照时间: {ts}", "info")
    cprint(f"  输出目录: {snapshot_dir}", "info")
    cprint(f"  WSL Distros 扫描: {len(wsl_results)} 个", "ok")
    cprint(f"  Windows Agents 发现: {len(windows_results)} 个", "ok")
    cprint(f"  备份文件数: {manifest['total_files']}", "ok")
    cprint(f"  备份总大小: {_format_size(manifest['total_bytes'])}", "ok")
    cprint(f"  Manifest: {snapshot_dir}/snapshot_manifest.json", "dim")

    # 如果没有任何结果，给提示
    if manifest["total_files"] == 0:
        cprint("\n  ⚠️  未发现任何记忆文件。", "warn")
        cprint("  可能原因：", "warn")
        cprint("  • Agent 尚未生成记忆文件", "warn")
        cprint("  • 路径不在预期位置（可手动指定）", "warn")
        cprint("  • 需要先在 Agent 中进行一次对话", "warn")

    return 0


if __name__ == "__main__":
    sys.exit(main())
