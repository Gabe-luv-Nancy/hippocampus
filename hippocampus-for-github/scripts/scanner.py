#!/usr/bin/env python3
"""
Hippocampus Scanner v4.0.0
=========================
扫描主机文件系统，发现各 AI 工具的记忆文件。
"""

import os
import sys
import json
import hashlib
import sqlite3
import platform
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import argparse

# 尝试加载配置（如果存在）
SCRIPT_DIR = Path(__file__).parent
CONFIG_DIR = SCRIPT_DIR / "config"

# ============================================================================
# 配置加载
# ============================================================================

def load_ai_tools_config() -> Dict[str, Any]:
    """加载 AI 工具路径配置"""
    config_path = CONFIG_DIR / "ai_tools.yaml"
    if not config_path.exists():
        return {"ai_tools": []}
    
    try:
        import yaml
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {"ai_tools": []}
    except ImportError:
        # 没有 yaml，用 JSON 格式
        json_path = CONFIG_DIR / "ai_tools.yaml"
        if json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"[警告] 加载 ai_tools.yaml 失败: {e}")
    return {"ai_tools": []}


def load_scan_rules() -> Dict[str, Any]:
    """加载扫描规则"""
    rules_path = CONFIG_DIR / "scan_rules.yaml"
    if not rules_path.exists():
        return {"scan": {"exclude_paths": [], "exclude_names": [], "min_file_size": 10, "max_file_size": 5242880}}
    
    try:
        import yaml
        with open(rules_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        json_path = CONFIG_DIR / "scan_rules.yaml"
        if json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"[警告] 加载 scan_rules.yaml 失败: {e}")
    return {"scan": {}}


# ============================================================================
# 文件条目
# ============================================================================

class FileEntry:
    """扫描到的文件条目"""
    
    def __init__(
        self,
        path: Path,
        source_ai: str,
        size: int,
        modified_at: str,
        hash: str = "",
        content_preview: str = ""
    ):
        self.path = path
        self.source_ai = source_ai
        self.size = size
        self.modified_at = modified_at
        self.hash = hash
        self.content_preview = content_preview
    
    def to_dict(self) -> Dict:
        return {
            "path": str(self.path),
            "source_ai": self.source_ai,
            "size": self.size,
            "modified_at": self.modified_at,
            "hash": self.hash,
            "content_preview": self.content_preview
        }
    
    def __repr__(self):
        return f"<FileEntry {self.source_ai}:{self.path.name}>"


# ============================================================================
# WSL 多发行版发现与远程扫描
# ============================================================================

def _find_wsl_exe() -> Optional[str]:
    """查找 wsl.exe（WSL 环境内需要绝对路径）"""
    if platform.system() == "Windows":
        return "wsl"
    for c in [
        "/mnt/c/Windows/System32/wsl.exe",
        "/mnt/c/WINDOWS/system32/wsl.exe",
    ]:
        if os.path.isfile(c):
            return c
    import shutil
    return shutil.which("wsl.exe") or "wsl"


def _discover_wsl_distros() -> List[Dict[str, Any]]:
    """通过 wsl.exe --list --verbose 发现所有 WSL 发行版"""
    wsl_exe = _find_wsl_exe()
    try:
        # WSL 内执行 .exe 需要 shell=True
        result = subprocess.run(
            f'"{wsl_exe}" --list --verbose',
            capture_output=True, text=True, timeout=15, shell=True
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []
    
    if result.returncode != 0:
        return []
    
    raw = result.stdout.replace("\x00", "").replace("\r", "")
    lines = [l.strip() for l in raw.split("\n") if l.strip()]
    
    distros = []
    for line in lines[1:]:
        parts = line.split()
        if len(parts) < 3:
            continue
        is_default = parts[0] == "*"
        name = parts[1] if is_default else parts[0]
        state = parts[2] if is_default else parts[1]
        try:
            version = int(parts[-1])
        except ValueError:
            version = 2
        distros.append({"name": name, "state": state, "version": version, "is_default": is_default})
    
    return distros


def _get_current_distro_name() -> Optional[str]:
    """获取当前运行的 WSL 发行版名称"""
    # WSL_DISTRO_NAME 环境变量由 WSL 标准登录设置
    name = os.environ.get("WSL_DISTRO_NAME")
    if name:
        return name
    # fallback: 从 /etc/wsl.conf 或 hostname 推断
    try:
        import socket
        hostname = socket.gethostname()
        # 有些 distro 的 hostname 就是 distro name
        # 但不靠谱，返回 None 让后续逻辑通过
    except Exception:
        pass
    return None


def _can_execute_wsl_exe() -> bool:
    """检测当前环境能否执行 wsl.exe（需要 WSL interop）"""
    wsl_exe = _find_wsl_exe()
    if not wsl_exe or not os.path.isfile(wsl_exe):
        return False
    # Windows 原生环境一定能执行
    if platform.system() == "Windows":
        return True
    # WSL 内：检查 WSL_INTEROP 环境变量或 binfmt_misc
    if os.environ.get("WSL_INTEROP"):
        return True
    # 检查 binfmt_misc 是否注册了 WSLInterop
    try:
        for entry in os.listdir("/proc/sys/fs/binfmt_misc"):
            if entry.startswith("WSL"):
                return True
    except Exception:
        pass
    return False


def _is_running_in_wsl() -> bool:
    """检测是否在 WSL 环境内运行"""
    try:
        with open("/proc/version", "r") as f:
            version_str = f.read().lower()
            return "microsoft" in version_str or "wsl" in version_str
    except Exception:
        return False


def _is_running_on_windows() -> bool:
    """检测是否在 Windows 原生环境运行"""
    return platform.system() == "Windows"


def _detect_windows_user_profiles() -> List[str]:
    """发现 Windows 上所有用户目录 (C:/Users/, D:/Users/ 等多盘符)"""
    profiles = []
    # 检查所有可能的盘符
    for drive in "CDEFGH":
        users_dir = Path(f"{drive}:/Users")
        if users_dir.exists():
            for user_dir in users_dir.iterdir():
                if user_dir.is_dir() and user_dir.name not in ("Public", "Default", "Default User", "All Users"):
                    profiles.append(str(user_dir))
    return profiles


# Windows 上常见 AI 工具的路径模式（相对于用户目录）
_WINDOWS_AI_TOOL_PATTERNS = {
    "hermes": [
        ".hermes",           # 如果 Windows 原生安装
    ],
    "openclaw": [
        ".openclaw",         # 如果 Windows 原生安装
        "AppData/Roaming/openclaw",
        "AppData/Local/openclaw",
    ],
    "claude": [
        "AppData/Roaming/Claude",
        "AppData/Local/Claude",
    ],
    "chatgpt": [
        "AppData/Roaming/ChatGPT",
        "AppData/Local/ChatGPT",
    ],
    "cursor": [
        ".cursor",
        "AppData/Roaming/Cursor",
    ],
    "windsurf": [
        ".windsurf",
        "AppData/Roaming/Windsurf",
    ],
}


def _scan_windows_native(user_profiles: List[str] = None) -> List[Dict[str, Any]]:
    """扫描 Windows 原生路径上的 AI 工具目录（Phase 0）
    
    在 WSL 内运行时，通过 /mnt/c/Users/ 路径访问 Windows 用户目录。
    在 Windows 原生运行时，直接用 C:/Users/ 路径。
    
    Returns:
        [{"tool": "hermes", "dir_name": ".hermes", "path": "/mnt/c/Users/Gabe/.hermes"}, ...]
    """
    if user_profiles is None:
        if _is_running_in_wsl():
            # WSL 内：通过 /mnt/ 路径访问 Windows 用户目录
            user_profiles = []
            for drive in "cdefgh":
                users_dir = Path(f"/mnt/{drive}/Users")
                if users_dir.exists():
                    for user_dir in users_dir.iterdir():
                        if user_dir.is_dir() and user_dir.name not in ("Public", "Default", "Default User", "All Users"):
                            user_profiles.append(str(user_dir))
        elif _is_running_on_windows():
            user_profiles = _detect_windows_user_profiles()
        else:
            return []  # macOS/Linux 无 Windows 路径
    
    found = []
    for profile in user_profiles:
        profile_path = Path(profile)
        if not profile_path.exists():
            continue
        for tool_name, patterns in _WINDOWS_AI_TOOL_PATTERNS.items():
            for pattern in patterns:
                check_path = profile_path / pattern
                if check_path.exists():
                    found.append({
                        "tool": tool_name,
                        "dir_name": pattern.split("/")[-1] if "/" in pattern else pattern,
                        "path": str(check_path),
                    })
    
    return found


def _remote_scan_distro(
    distro_name: str,
    target_dir_names: List[str] = None,
    max_depth: int = 4,
) -> List[Dict[str, Any]]:
    """远程扫描指定 WSL distro 中的目标隐藏目录
    
    Returns:
        [{"dir_name": ".hermes", "path": "/home/xxx/.hermes"}, ...]
    """
    if target_dir_names is None:
        target_dir_names = [".hermes", ".openclaw"]
    
    wsl_exe = _find_wsl_exe()
    name_clauses = " -o ".join(f"-name {d}" for d in target_dir_names)
    found = []
    
    for search_root in ["/home", "/root"]:
        find_cmd = (
            f"find {search_root} -maxdepth {max_depth} -type d "
            f"\\( {name_clauses} \\) 2>/dev/null"
        )
        try:
            proc = subprocess.run(
                f'"{wsl_exe}" -d {distro_name} -- bash -c \'{find_cmd}\'',
                capture_output=True, text=True, timeout=30, shell=True
            )
        except subprocess.TimeoutExpired:
            continue
        
        for line in proc.stdout.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            dir_name = os.path.basename(line)
            if dir_name in target_dir_names:
                found.append({"dir_name": dir_name, "path": line, "distro": distro_name})
    
    return found


def discover_all_ai_dirs_across_distros(
    target_dir_names: List[str] = None,
) -> Dict[str, List[Dict[str, Any]]]:
    """跨所有 WSL 发行版发现 AI 工具目录
    
    Returns:
        {
            "Hermes_Ubuntu": [{"dir_name": ".hermes", "path": "/home/agentuser/.hermes", "distro": "Hermes_Ubuntu"}],
            ...
        }
    """
    distros = _discover_wsl_distros()
    current = _get_current_distro_name()
    results = {}
    
    for d in distros:
        name = d["name"]
        # 跳过 docker-desktop 内部 distro 和当前 distro（当前由本地扫描处理）
        if name.lower().startswith("docker-desktop"):
            continue
        if name == current:
            continue
        
        found = _remote_scan_distro(name, target_dir_names)
        if found:
            results[name] = found
    
    return results


# ============================================================================
# 扫描器
# ============================================================================

class Scanner:
    """扫描主机文件系统，发现记忆文件"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.ai_tools = load_ai_tools_config()
        self.rules = load_scan_rules()
        self.exclude_paths = self.rules.get("scan", {}).get("exclude_paths", [])
        self.exclude_names = self.rules.get("scan", {}).get("exclude_names", [])
        self.min_size = self.rules.get("scan", {}).get("min_file_size", 10)
        self.max_size = self.rules.get("scan", {}).get("max_file_size", 5242880)
        self.results: List[FileEntry] = []
    
    def expand_path(self, path_str: str) -> List[Path]:
        """展开路径，支持 ~ 和通配符"""
        expanded = os.path.expanduser(path_str)
        path = Path(expanded)
        
        results = []
        if path.is_dir():
            # 递归查找所有 .md 文件
            try:
                for p in path.rglob("*.md"):
                    results.append(p)
            except PermissionError:
                pass
        elif path.is_file():
            results.append(path)
        
        return results
    
    def should_exclude(self, path: Path) -> bool:
        """检查是否应该排除"""
        path_str = str(path)
        name = path.name
        
        # 检查排除路径
        for pattern in self.exclude_paths:
            pattern_expanded = os.path.expanduser(pattern)
            # 简单通配符匹配
            if "*" in pattern_expanded:
                import fnmatch
                if fnmatch.fnmatch(path_str, pattern_expanded):
                    return True
            elif pattern_expanded in path_str:
                return True
        
        # 检查排除文件名
        for pattern in self.exclude_names:
            if "*" in pattern:
                import fnmatch
                if fnmatch.fnmatch(name, pattern):
                    return True
            elif name == pattern:
                return True
        
        return False
    
    def compute_hash(self, path: Path) -> str:
        """计算文件 SHA256"""
        try:
            with open(path, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()[:16]
        except Exception:
            return ""
    
    def read_preview(self, path: Path) -> str:
        """读取文件前 200 字符"""
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read(200).strip()
        except Exception:
            return ""
    
    def scan_path(self, path_str: str, source_ai: str) -> List[FileEntry]:
        """扫描指定路径"""
        entries = []
        paths = self.expand_path(path_str)
        
        for path in paths:
            if self.should_exclude(path):
                continue
            
            try:
                size = path.stat().st_size
                if size < self.min_size or size > self.max_size:
                    continue
            except Exception:
                continue
            
            modified = datetime.fromtimestamp(path.stat().st_mtime).isoformat()
            
            entry = FileEntry(
                path=path,
                source_ai=source_ai,
                size=size,
                modified_at=modified,
                hash=self.compute_hash(path),
                content_preview=self.read_preview(path)
            )
            entries.append(entry)
        
        return entries
    
    def scan_ai_tool(self, tool: Dict) -> List[FileEntry]:
        """扫描指定 AI 工具的所有路径"""
        entries = []
        tool_name = tool.get("name", "unknown")
        
        if not tool.get("enabled", True):
            return entries
        
        for path_config in tool.get("paths", []):
            path_str = path_config.get("path", "")
            if not path_str:
                continue
            
            try:
                entries.extend(self.scan_path(path_str, tool_name))
            except Exception as e:
                print(f"[警告] 扫描 {path_str} 失败: {e}")
        
        return entries
    
    def scan_all(self) -> List[FileEntry]:
        """全量扫描所有启用的 AI 工具
        
        三层扫描架构:
          Phase 0: Windows 原生路径扫描 (/mnt/c/Users/... 或 C:/Users/...)
          Phase 1: 本地 Linux 扫描 (当前 distro 的 ~/.xxx 路径)
          Phase 2: 跨 WSL distro 远程扫描 (wsl.exe -d <name> -- find ...)
        """
        self.results = []
        
        # ---- Phase 0: Windows 原生路径扫描 ----
        # 检查 Windows 用户目录下是否存在 AI 工具（不依赖 WSL，纯路径检查）
        win_results = _scan_windows_native()
        if win_results:
            print(f"  [Phase 0] Windows 原生路径发现 {len(win_results)} 个 AI 工具目录")
            for item in win_results:
                # 对发现的目录执行文件扫描（.md 文件）
                win_path = Path(item["path"])
                if win_path.is_dir():
                    for md_file in win_path.rglob("*.md"):
                        try:
                            size = md_file.stat().st_size
                            if size < self.min_size or size > self.max_size:
                                continue
                            entry = FileEntry(
                                path=md_file,
                                source_ai=f"win:{item['tool']}",
                                size=size,
                                modified_at=datetime.fromtimestamp(md_file.stat().st_mtime).isoformat(),
                                hash=self.compute_hash(md_file) if not self.dry_run else "",
                                content_preview=self.read_preview(md_file)
                            )
                            self.results.append(entry)
                        except (PermissionError, OSError):
                            continue
                if any(r["tool"] == item["tool"] for r in win_results):
                    print(f"    [win:{item['tool']}] {item['path']}")
        
        # ---- Phase 1: 本地扫描（当前 distro 的 ~/.xxx 路径）----
        for tool in self.ai_tools.get("ai_tools", []):
            if not tool.get("enabled", True):
                continue
            entries = self.scan_ai_tool(tool)
            self.results.extend(entries)
            if entries:
                print(f"  [{tool.get('name', '?')}] 找到 {len(entries)} 个文件 (本地)")
        
        # ---- Phase 2: 跨 WSL distro 远程扫描 ----
        if _is_running_in_wsl() and _can_execute_wsl_exe():
            current_distro = _get_current_distro_name()
            print(f"  [Phase 2] 检测到 WSL 环境 (interop 可用)，正在扫描其他发行版...")
            remote_results = discover_all_ai_dirs_across_distros()
            
            for distro_name, dirs in remote_results.items():
                for item in dirs:
                    # 将远程 distro 中发现的目录也作为扫描结果记录
                    # source_ai 标注为 "distro_name:dir_name" 方便溯源
                    source_label = f"{distro_name}:{item['dir_name'].lstrip('.')}"
                    entry = FileEntry(
                        path=Path(item['path']),
                        source_ai=source_label,
                        size=0,  # 远程目录，暂不获取文件大小
                        modified_at=datetime.now().isoformat(),
                        hash="",
                        content_preview=f"[远程 WSL distro: {distro_name}] {item['path']}"
                    )
                    self.results.append(entry)
                if dirs:
                    print(f"    [{distro_name}] 发现 {len(dirs)} 个目录 ({', '.join(d['dir_name'] for d in dirs)})")
        
        print(f"\n  扫描完成: 共发现 {len(self.results)} 个条目")
        return self.results
    
    def scan_by_tool_name(self, tool_name: str) -> List[FileEntry]:
        """只扫描指定 AI 工具"""
        self.results = []
        
        for tool in self.ai_tools.get("ai_tools", []):
            if tool.get("name", "").lower() == tool_name.lower():
                entries = self.scan_ai_tool(tool)
                self.results.extend(entries)
                print(f"  [{tool_name}] 找到 {len(entries)} 个文件")
                break
        else:
            print(f"[错误] 未找到 AI 工具: {tool_name}")
        
        return self.results
    
    def get_changed_files(self, since_hours: int = 24) -> List[FileEntry]:
        """只返回指定小时数内修改的文件（增量扫描）"""
        cutoff = datetime.now().timestamp() - (since_hours * 3600)
        return [e for e in self.results if e.path.stat().st_mtime > cutoff]
    
    def write_to_usb(self, drive_path: str, capture_base: str = None) -> bool:
        """写入 BrainDump U 盘"""
        if self.dry_run:
            print("[dry-run] 写入 U 盘")
            return True
        
        drive = Path(drive_path)
        if not drive.exists():
            print(f"[错误] U 盘路径不存在: {drive_path}")
            return False
        
        # 检查 marker
        marker = drive / "marker.txt"
        if not marker.exists():
            print(f"[错误] 不是 BrainDump U 盘（缺少 marker.txt）")
            return False
        
        try:
            marker_content = marker.read_text(encoding="utf-8").strip()
            if marker_content != "HIPPOCAMPUS_BRAINDUMP_v4.0.0":
                print(f"[错误] U 盘 marker 不匹配")
                return False
        except Exception:
            print(f"[错误] 读取 marker.txt 失败")
            return False
        
        # 写入数据库
        db_path = drive / "db" / "brain_dump.sqlite"
        if not db_path.exists():
            print(f"[错误] U 盘缺少数据库文件")
            return False
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # 记录本次抓取
            capture_date = datetime.now().strftime("%Y-%m-%d")
            host_computer = os.environ.get("COMPUTERNAME", os.environ.get("HOSTNAME", "unknown"))
            
            cursor.execute("""
                INSERT INTO captures (capture_date, total_files, total_size_bytes, host_computer)
                VALUES (?, ?, ?, ?)
            """, (capture_date, len(self.results), sum(e.size for e in self.results), host_computer))
            capture_id = cursor.lastrowid
            
            # 写入文件记录
            for entry in self.results:
                capture_dir = drive / "capture" / entry.source_ai
                capture_dir.mkdir(parents=True, exist_ok=True)
                
                relative_path = capture_dir / entry.path.name
                
                # 复制文件
                try:
                    import shutil
                    shutil.copy2(entry.path, relative_path)
                except Exception:
                    pass
                
                cursor.execute("""
                    INSERT INTO files 
                    (source_ai, original_path, file_name, relative_path, size_bytes, modified_at, captured_at, hash, content_preview)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry.source_ai,
                    str(entry.path),
                    entry.path.name,
                    str(relative_path),
                    entry.size,
                    entry.modified_at,
                    datetime.now().isoformat(),
                    entry.hash,
                    entry.content_preview
                ))
            
            conn.commit()
            conn.close()
            
            print(f"[完成] 写入 {len(self.results)} 个文件到 U 盘")
            return True
            
        except Exception as e:
            print(f"[错误] 写入 U 盘失败: {e}")
            return False
    
    def write_local_output(self, output_dir: str = None) -> bool:
        """写入本地输出目录"""
        if output_dir is None:
            output_dir = SCRIPT_DIR / "scan_output"
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 写入 manifest.json
        manifest = {
            "scan_time": datetime.now().isoformat(),
            "total_files": len(self.results),
            "total_size": sum(e.size for e in self.results),
            "files": [e.to_dict() for e in self.results]
        }
        
        manifest_path = output_dir / f"manifest_{timestamp}.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        
        # 写入 summary.md
        summary_path = output_dir / f"summary_{timestamp}.md"
        summary_lines = [
            f"# 扫描报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            f"总计：{len(self.results)} 个文件",
            f"总大小：{sum(e.size for e in self.results) / 1024:.1f} KB",
            "",
            "## 按来源统计",
            ""
        ]
        
        from collections import Counter
        by_source = Counter(e.source_ai for e in self.results)
        for source, count in by_source.items():
            summary_lines.append(f"- **{source}**: {count} 个文件")
        
        summary_lines.append("")
        summary_lines.append("## 文件列表")
        summary_lines.append("")
        summary_lines.append("| 来源 | 文件名 | 大小 | 修改时间 |")
        summary_lines.append("|------|--------|------|----------|")
        for e in self.results:
            summary_lines.append(f"| {e.source_ai} | {e.path.name} | {e.size} B | {e.modified_at[:19]} |")
        
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write("\n".join(summary_lines))
        
        print(f"[完成] 报告已保存：")
        print(f"  - {manifest_path}")
        print(f"  - {summary_path}")
        return True
    
    def print_results(self):
        """打印扫描结果"""
        if not self.results:
            print("未发现任何记忆文件")
            return
        
        from collections import Counter
        by_source = Counter(e.source_ai for e in self.results)
        
        print(f"\n{'='*60}")
        print(f"扫描完成：共 {len(self.results)} 个文件")
        print(f"{'='*60}")
        
        for source, count in by_source.items():
            print(f"  [{source}] {count} 个文件")
        
        print()
        for e in self.results[:20]:
            print(f"  {e.source_ai:12} {e.path.name:40} {e.size:>8} B")
        
        if len(self.results) > 20:
            print(f"  ... 还有 {len(self.results) - 20} 个文件")


# ============================================================================
# 命令行入口
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Hippocampus Scanner v4.0.0 - 扫描主机 AI 记忆文件")
    parser.add_argument("command", nargs="?", default="scan", choices=["scan", "detect"],
                        help="命令: scan（全量扫描）或 detect（仅检测工具）")
    parser.add_argument("--tool", "-t", type=str, default=None,
                        help="只扫描指定 AI 工具（如 openclaw, doubao）")
    parser.add_argument("--output", "-o", type=str, default=None,
                        help="输出目录（默认: scan_output/）")
    parser.add_argument("--usb", "-u", type=str, default=None,
                        help="U 盘路径（如 F:/），写入 BrainDump U 盘")
    parser.add_argument("--dry-run", action="store_true",
                        help="不实际写入，只显示结果")
    
    args = parser.parse_args()
    
    if args.command == "detect":
        # 导入 detector
        sys.path.insert(0, str(SCRIPT_DIR))
        from detector import AIToolDetector
        detector = AIToolDetector()
        tools = detector.detect_all()
        print(f"{'='*60}")
        print(f"检测到 {len(tools)} 个 AI 工具：")
        print(f"{'='*60}")
        for tool in tools:
            status = "✓" if tool.get("installed") else "✗"
            print(f"  {status} {tool.get('display_name', tool.get('name'))}")
            if tool.get("installed"):
                for p in tool.get("found_paths", [])[:3]:
                    print(f"      {p}")
        return
    
    # 扫描
    scanner = Scanner(dry_run=args.dry_run)
    
    if args.tool:
        print(f"正在扫描 [{args.tool}]...")
        scanner.scan_by_tool_name(args.tool)
    else:
        print("正在扫描所有 AI 工具...")
        scanner.scan_all()
    
    if not scanner.results:
        print("未发现任何记忆文件")
        return
    
    scanner.print_results()
    
    # 写入 U 盘
    if args.usb:
        print(f"\n正在写入 U 盘: {args.usb}")
        scanner.write_to_usb(args.usb)
    
    # 写入本地
    elif not args.dry_run:
        scanner.write_local_output(args.output)


if __name__ == "__main__":
    main()
