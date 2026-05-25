#!/usr/bin/env python3
"""
Hippocampus WSL Bridge — Windows/Linux 路径桥接层
==================================================
Windows 版启动器通过 WSL 调用 Linux 原生引擎时，
需要此模块进行路径转换。

核心职责：
  - Windows 盘符 ↔ WSL /mnt/x/ 路径互转
  - 自动检测 Windows 可用磁盘
  - 发现所有 WSL 发行版并逐个扫描
  - 为 scanner 提供正确的扫描路径列表
"""

import os
import sys
import json
import platform
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any


def windows_to_wsl(win_path: str) -> str:
    """Windows 路径转 WSL 路径
    
    Examples:
        C:\\Users\\xxx -> /mnt/c/Users/xxx
        D:\\ -> /mnt/d/
        F: -> /mnt/f
    """
    # 如果已经是 WSL 路径，直接返回
    if win_path.startswith("/mnt/"):
        return win_path
    
    # 使用 wslpath 转换（最可靠）
    try:
        result = subprocess.run(
            ["wsl", "wslpath", "-a", win_path],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    
    # 手动转换 fallback
    path = win_path.replace("\\", "/")
    if len(path) >= 2 and path[1] == ":":
        drive = path[0].lower()
        rest = path[2:].lstrip("/")
        return f"/mnt/{drive}/{rest}"
    return path


def wsl_to_windows(wsl_path: str) -> str:
    """WSL 路径转 Windows 路径
    
    Examples:
        /mnt/c/Users/xxx -> C:\\Users\\xxx
        /mnt/f/ -> F:\\
    """
    if wsl_path.startswith("/mnt/"):
        parts = wsl_path[5:].split("/", 1)
        drive = parts[0].upper()
        rest = parts[1] if len(parts) > 1 else ""
        win_rest = rest.replace("/", "\\")
        return f"{drive}:\\{win_rest}"
    return wsl_path


def detect_windows_drives() -> List[str]:
    """检测 Windows 上所有可用的磁盘盘符
    
    Returns:
        ["/mnt/c", "/mnt/d", "/mnt/e", ...]
    """
    drives = []
    for letter in "abcdefghijklmnopqrstuvwxyz":
        wsl_path = f"/mnt/{letter}"
        if os.path.ismount(wsl_path) or os.path.isdir(wsl_path):
            drives.append(wsl_path)
    return drives


# ============================================================================
# WSL Distro 发现与扫描
# ============================================================================

def _find_wsl_exe() -> Optional[str]:
    """查找 wsl.exe 可执行文件路径
    
    在 WSL 内部调用时，需要用 Windows 的 wsl.exe 绝对路径。
    在 Windows 原生 Python 中，直接用 "wsl"。
    """
    # 1) 如果是 Windows 原生环境，直接用 "wsl"
    if platform.system() == "Windows":
        return "wsl"
    
    # 2) WSL 内部：用绝对路径
    candidates = [
        "/mnt/c/Windows/System32/wsl.exe",
        "/mnt/c/WINDOWS/system32/wsl.exe",
        "/mnt/c/Windows/SysNative/wsl.exe",
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    
    # 3) 尝试 PATH 里找
    import shutil
    wsl = shutil.which("wsl.exe")
    if wsl:
        return wsl
    
    # 4) 最终 fallback
    return "wsl"


# 模块级缓存
_WSL_EXE = None

def get_wsl_exe() -> str:
    """获取 wsl.exe 路径（带缓存）"""
    global _WSL_EXE
    if _WSL_EXE is None:
        _WSL_EXE = _find_wsl_exe()
    return _WSL_EXE


def discover_distros() -> List[Dict[str, Any]]:
    """发现所有 WSL 发行版
    
    通过 `wsl --list --verbose` 获取所有已注册的 distro，
    解析名称、状态、WSL 版本、是否为默认 distro。
    
    Returns:
        [
            {
                "name": "Ubuntu",
                "state": "Running",
                "version": 2,
                "is_default": True,
            },
            ...
        ]
    """
    wsl_exe = get_wsl_exe()
    
    # 检测能否执行 wsl.exe
    can_exec = False
    if platform.system() == "Windows":
        can_exec = True
    elif os.environ.get("WSL_INTEROP"):
        can_exec = True
    else:
        try:
            for entry in os.listdir("/proc/sys/fs/binfmt_misc"):
                if entry.startswith("WSL"):
                    can_exec = True
                    break
        except Exception:
            pass
    
    if not can_exec:
        return []
    
    try:
        result = subprocess.run(
            [wsl_exe, "--list", "--verbose"],
            capture_output=True, text=True, timeout=15
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return []
    
    if result.returncode != 0:
        return []
    
    # wsl.exe 输出含 UTF-16 BOM + \0 穿插，需清理
    raw = result.stdout.replace("\x00", "").replace("\r", "")
    lines = [l.strip() for l in raw.split("\n") if l.strip()]
    
    distros = []
    for line in lines[1:]:  # 跳过表头 NAME / STATE / VERSION
        parts = line.split()
        if len(parts) < 3:
            continue
        
        # 默认 distro 以 * 标记
        is_default = parts[0] == "*"
        name = parts[0] if not is_default else parts[1]
        state = parts[1] if not is_default else parts[2]
        
        # WSL 版本号在最后
        try:
            version = int(parts[-1])
        except ValueError:
            version = 2
        
        distros.append({
            "name": name,
            "state": state,
            "version": version,
            "is_default": is_default,
        })
    
    return distros


def scan_distro_for_dirs(
    distro_name: str,
    target_dirs: List[str] = None,
    max_depth: int = 4,
) -> List[Dict[str, Any]]:
    """在指定 WSL distro 内搜索目标隐藏目录
    
    通过 `wsl.exe -d <distro> -- bash -c "find ..."` 实现跨 distro 扫描，
    无需进入 distro 内部安装任何依赖。
    
    Args:
        distro_name: WSL 发行版名称（如 "Ubuntu", "Hermes_Ubuntu"）
        target_dirs: 要搜索的隐藏目录名列表，默认 [".hermes", ".openclaw"]
        max_depth: find 搜索最大深度
    
    Returns:
        [
            {
                "distro": "Hermes_Ubuntu",
                "dir_name": ".hermes",
                "path": "/home/agentuser/.hermes",
            },
            ...
        ]
    """
    if target_dirs is None:
        target_dirs = [".hermes", ".openclaw"]
    
    wsl_exe = get_wsl_exe()
    results = []
    
    # 构造 find 的 -name 参数
    name_clauses = " -o ".join(f"-name {d}" for d in target_dirs)
    
    # 搜索 /home 和 /root，用 bash -c 包裹
    for search_root in ["/home", "/root"]:
        find_cmd = (
            f"find {search_root} -maxdepth {max_depth} -type d "
            f"\\( {name_clauses} \\) 2>/dev/null"
        )
        
        cmd = [wsl_exe, "-d", distro_name, "--", "bash", "-c", find_cmd]
        
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True, text=True, timeout=30
            )
        except (subprocess.TimeoutExpired, OSError):
            continue
        
        for line in proc.stdout.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            # 提取目录名
            dir_name = os.path.basename(line)
            if dir_name in target_dirs:
                results.append({
                    "distro": distro_name,
                    "dir_name": dir_name,
                    "path": line,
                })
    
    return results


def scan_all_distros(
    target_dirs: List[str] = None,
    max_depth: int = 4,
) -> Dict[str, List[Dict[str, Any]]]:
    """扫描所有 WSL 发行版，查找目标隐藏目录
    
    Returns:
        {
            "Hermes_Ubuntu": [{"dir_name": ".hermes", "path": "/home/agentuser/.hermes"}],
            "Openclaw_Ubuntu": [{"dir_name": ".openclaw", "path": "/home/xxx/.openclaw"}],
            ...
        }
    """
    distros = discover_distros()
    all_results = {}
    
    for distro in distros:
        name = distro["name"]
        if name.lower().startswith("docker-desktop"):
            continue
        
        found = scan_distro_for_dirs(name, target_dirs, max_depth)
        if found:
            all_results[name] = found
    
    return all_results


def get_scan_paths(explicit_paths: List[str] = None) -> List[str]:
    """获取扫描路径列表
    
    Args:
        explicit_paths: 用户指定的路径（Windows 或 WSL 格式均可）
    
    Returns:
        统一为 WSL 格式的路径列表
    """
    if explicit_paths:
        return [windows_to_wsl(p) for p in explicit_paths]
    
    # 自动检测所有 Windows 磁盘
    return detect_windows_drives()


def find_linux_engine() -> Optional[str]:
    """查找 Linux 原生引擎目录
    
    查找顺序:
    1. 环境变量 HIPPO_LINUX_DIR
    2. 与当前目录同级的 brain_dump_linux/
    3. 父目录下的 brain_dump_linux/
    """
    # 环境变量
    env_dir = os.environ.get("HIPPO_LINUX_DIR")
    if env_dir and os.path.isdir(env_dir):
        return env_dir
    
    # 同级目录
    script_dir = Path(__file__).parent
    sibling = script_dir.parent / "brain_dump_linux"
    if sibling.is_dir():
        return str(sibling)
    
    # 父目录
    parent = script_dir / "brain_dump_linux"
    if parent.is_dir():
        return str(parent)
    
    return None


def run_in_wsl(cmd: List[str], cwd: str = None, distro: str = None) -> subprocess.CompletedProcess:
    """在 WSL 中执行命令
    
    Args:
        cmd: 命令列表，路径会自动转换
        cwd: 工作目录（Windows 格式会自动转换）
        distro: 指定 WSL 发行版名称（默认用系统默认 distro）
    """
    wsl_cmd = ["wsl"]
    
    if distro:
        wsl_cmd.extend(["-d", distro])
    
    if cwd:
        wsl_cwd = windows_to_wsl(cwd) if not cwd.startswith("/mnt/") else cwd
        wsl_cmd.extend(["--cd", wsl_cwd])
    
    wsl_cmd.extend(cmd)
    return subprocess.run(wsl_cmd, capture_output=True, text=True, timeout=300)


def print_discovery_report(results: Dict[str, List[Dict[str, Any]]]):
    """打印跨 distro 扫描报告"""
    distros = discover_distros()
    
    print("=" * 60)
    print("  Hippocampus — WSL 多发行版扫描报告")
    print("=" * 60)
    print(f"  发行版总数: {len(distros)}")
    print()
    
    for d in distros:
        name = d["name"]
        state = d["state"]
        ver = d["version"]
        default = " ★ Default" if d["is_default"] else ""
        state_icon = "🟢" if state == "Running" else "⚫"
        print(f"  {state_icon} {name} (WSL{ver}){default}")
        
        if name in results:
            for item in results[name]:
                print(f"      📂 {item['dir_name']}  →  {item['path']}")
        else:
            print(f"      (无匹配)")
    
    print()
    # 汇总
    total_found = sum(len(v) for v in results.values())
    print(f"  共发现 {total_found} 个目标目录")
    print("=" * 60)


if __name__ == "__main__":
    print("Hippocampus WSL Bridge v4.0.0")
    print()
    print("检测到的 Windows 磁盘:")
    for d in detect_windows_drives():
        print(f"  {d} -> {wsl_to_windows(d)}")
    
    engine = find_linux_engine()
    print(f"\nLinux 引擎目录: {engine or '未找到'}")
    
    # 新功能：扫描所有 distro
    print("\n" + "=" * 60)
    print("  扫描所有 WSL 发行版中的 .hermes / .openclaw ...")
    print("=" * 60)
    
    results = scan_all_distros()
    print_discovery_report(results)
