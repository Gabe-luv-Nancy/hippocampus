#!/usr/bin/env python3
"""
Hippocampus Streamlit Frontend
=============================
Unified browser-based frontend for Hippocampus.
Works on any machine with Python (no compilation needed).

Modes:
  --mode local   : Scan host, backup to local dir or U盘
  --mode disk   : Browse U盘 contents (read-only)
"""

import sys
import os
import json
import hashlib
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

import streamlit as st
import streamlit.components.v1 as components

# ============================================================================
# Path setup
# ============================================================================

# When running from hippocampus-for-github/scripts/
SCRIPT_DIR = Path(__file__).parent
HIPPO_DIR = SCRIPT_DIR.parent
GUI_UTIL_DIR = HIPPO_DIR / "gui" / "utils"
if GUI_UTIL_DIR.exists():
    sys.path.insert(0, str(GUI_UTIL_DIR))

# Also make scripts/ importable for scanner/detector
sys.path.insert(0, str(SCRIPT_DIR))

# ============================================================================
# Drive Detection (standalone, no PyQt6 needed)
# ============================================================================

MARKER_CONTENT = "HIPPOCAMPUS_BRAINDUMP_v4.0.0"


def is_braindump(path: Path) -> bool:
    marker = path / "marker.txt"
    if not marker.exists():
        return False
    try:
        return marker.read_text(encoding="utf-8").strip() == MARKER_CONTENT
    except Exception:
        return False


def get_removable_drives() -> List[Dict]:
    """Detect removable drives (Windows/macOS/Linux)."""
    drives = []
    import platform
    system = platform.system().lower()

    if system == "windows":
        import subprocess
        try:
            result = subprocess.run(
                ["wmic", "logicaldisk", "where", "DriveType=2", "get",
                 "Caption,DeviceID,FileSystem,Size,FreeSpace", "/format:csv"],
                capture_output=True, text=True, encoding="utf-8", errors="ignore"
            )
            for line in result.stdout.strip().split("\n")[1:]:
                parts = [p.strip() for p in line.split(",")]
                if len(parts) < 6 or not parts[1]:
                    continue
                caption = parts[1]
                if len(caption) != 2 or caption[1] != ":":
                    continue
                mount = Path(caption + "\\")
                try:
                    size = int(parts[4]) if parts[4] else 0
                    free = int(parts[5]) if parts[5] else 0
                except (ValueError, TypeError):
                    size = free = 0
                drives.append({
                    "name": caption,
                    "path": str(mount),
                    "is_braindump": is_braindump(mount),
                    "size": size,
                    "free": free,
                    "fs": parts[3] if len(parts) > 3 else "",
                })
        except Exception:
            pass

    elif system == "darwin":
        import subprocess
        try:
            result = subprocess.run(
                ["diskutil", "list", "external", "-plist"],
                capture_output=True, text=True, encoding="utf-8", errors="ignore"
            )
            import plistlib
            try:
                data = plistlib.loads(result.stdout.encode())
                for disk in data.get("AllDisksAndPartitions", []):
                    for part in disk.get("Partitions", []):
                        mount = part.get("MountPoint", "")
                        if not mount or not Path(mount).exists():
                            continue
                        p = Path(mount)
                        drives.append({
                            "name": p.name,
                            "path": str(p),
                            "is_braindump": is_braindump(p),
                            "size": 0, "free": 0, "fs": ""
                        })
            except Exception:
                pass
        except Exception:
            pass

    else:  # linux
        try:
            with open("/proc/mounts") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) < 3:
                        continue
                    device, mount_point, fs = parts[0], parts[1], parts[2]
                    if not ("usb" in device.lower() or "sd" in device):
                        continue
                    if mount_point in ["/", "/boot", "/home", "/var", "/usr"]:
                        continue
                    drives.append({
                        "name": Path(mount_point).name or device,
                        "path": mount_point,
                        "is_braindump": is_braindump(Path(mount_point)),
                        "size": 0, "free": 0, "fs": fs
                    })
        except Exception:
            pass

    return drives


# ============================================================================
# Scanner / Detector (reuse from scripts/)
# ============================================================================

def detect_tools() -> List[Dict]:
    """Detect installed AI tools (local + WSL distros)."""
    results = []
    try:
        from detector import AIToolDetector
        det = AIToolDetector()
        tools = det.detect_all()
        for t in tools:
            if t.get("installed"):
                t["source"] = "local"
                results.append(t)
    except Exception:
        pass

    # WSL cross-distro discovery
    try:
        from scanner import _is_running_in_wsl, _can_execute_wsl_exe, _discover_wsl_distros, _remote_scan_distro
        if _is_running_in_wsl() and _can_execute_wsl_exe():
            current_distro = os.environ.get("WSL_DISTRO_NAME", "")
            distros = _discover_wsl_distros()
            for d in distros:
                name = d["name"]
                if name.lower().startswith("docker-desktop") or name == current_distro:
                    continue
                found = _remote_scan_distro(name)
                if found:
                    for item in found:
                        results.append({
                            "name": item["dir_name"].lstrip("."),
                            "display_name": f"{name}: {item['dir_name']}",
                            "installed": True,
                            "found_paths": [item["path"]],
                            "source": f"wsldistro:{name}",
                        })
    except Exception:
        pass

    return results


def scan_host_tools(tool_names: List[str]) -> List[Dict]:
    """Scan specified AI tools for memory files."""
    results = []
    try:
        from scanner import Scanner
        scanner = Scanner(dry_run=True)
        for name in tool_names:
            scanner.scan_by_tool_name(name)
        for e in scanner.results:
            results.append({
                "path": str(e.path),
                "source": e.source_ai,
                "name": e.path.name,
                "size": e.size,
                "modified": e.modified_at,
                "preview": e.content_preview[:100] if e.content_preview else "",
            })
    except Exception:
        pass
    return results


def scan_manual_path(path_str: str, tool_name: str = "custom") -> List[Dict]:
    """Scan a user-specified directory for .md files."""
    p = Path(path_str).expanduser()
    if not p.exists() or not p.is_dir():
        return []
    results = []
    try:
        for f in p.rglob("*.md"):
            try:
                size = f.stat().st_size
                results.append({
                    "path": str(f),
                    "source": tool_name,
                    "name": f.name,
                    "size": size,
                    "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                    "preview": f.read_text(encoding="utf-8", errors="ignore")[:100].strip(),
                })
            except Exception:
                continue
    except Exception:
        pass
    return results


# ============================================================================
# DB Helpers
# ============================================================================

def get_db_path(target: Path) -> Optional[Path]:
    if not target:
        return None
    db = target / "db" / "brain_dump.sqlite"
    return db if db.exists() else None


def get_stats(target: Path) -> Dict:
    db_path = get_db_path(target)
    if not db_path:
        return {"total_files": 0, "total_size": 0, "total_captures": 0, "sources": []}
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*), COALESCE(SUM(size_bytes),0) FROM files")
    fc, ts = cur.fetchone()
    cur.execute("SELECT COUNT(*) FROM captures")
    cc = cur.fetchone()[0]
    cur.execute("SELECT source_ai, COUNT(*) FROM files GROUP BY source_ai")
    sources = [{"name": r[0], "count": r[1]} for r in cur.fetchall()]
    conn.close()
    return {"total_files": fc or 0, "total_size": ts or 0, "total_captures": cc or 0, "sources": sources}


def get_files(target: Path, source: str = None) -> List[Dict]:
    db_path = get_db_path(target)
    if not db_path:
        return []
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    if source:
        cur.execute("SELECT * FROM files WHERE source_ai=? ORDER BY captured_at DESC LIMIT 200", (source,))
    else:
        cur.execute("SELECT * FROM files ORDER BY captured_at DESC LIMIT 200")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_history(target: Path) -> List[Dict]:
    db_path = get_db_path(target)
    if not db_path:
        return []
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM captures ORDER BY id DESC LIMIT 50")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def backup_files(target: Path, files: List[Dict], tool_name: str) -> Dict:
    """Backup selected files to target."""
    if not target or not is_braindump(target):
        return {"success": False, "imported": 0, "error": "Not a BrainDump drive"}

    db_path = get_db_path(target)
    if not db_path:
        return {"success": False, "imported": 0, "error": "Database not found"}

    capture_dir = target / "capture" / tool_name
    capture_dir.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    host = os.environ.get("COMPUTERNAME", os.environ.get("HOSTNAME", "unknown"))
    now = datetime.now()
    cur.execute(
        "INSERT INTO captures (capture_date,total_files,total_size_bytes,host_computer) VALUES (?,0,0,?)",
        (now.strftime("%Y-%m-%d"), host)
    )
    capture_id = cur.lastrowid

    imported = 0
    for f in files:
        try:
            src = Path(f["path"])
            if not src.exists():
                continue
            dest = capture_dir / src.name
            counter = 1
            while dest.exists():
                dest = capture_dir / f"{src.stem}_{counter}{src.suffix}"
                counter += 1
            shutil.copy2(src, dest)
            size = dest.stat().st_size
            with open(dest, "rb") as fh:
                h = hashlib.sha256(fh.read()).hexdigest()[:16]
            try:
                with open(dest, "r", encoding="utf-8", errors="ignore") as fh:
                    preview = fh.read(200)
            except Exception:
                preview = ""
            cur.execute(
                "INSERT INTO files (source_ai,original_path,file_name,relative_path,size_bytes,modified_at,captured_at,hash,content_preview) "
                "VALUES (?,?,?,?,?,?,?,?,?)",
                (tool_name, str(src), src.name, str(dest), size,
                 datetime.fromtimestamp(src.stat().st_mtime).isoformat(),
                 now.isoformat(), h, preview)
            )
            imported += 1
        except Exception as e:
            pass

    conn.commit()
    conn.close()
    return {"success": imported > 0, "imported": imported}


# ============================================================================
# Streamlit UI
# ============================================================================

def init_session():
    if "mode" not in st.session_state:
        st.session_state.mode = "local"
    if "target" not in st.session_state:
        st.session_state.target = None
    if "scan_results" not in st.session_state:
        st.session_state.scan_results = []
    if "detected_tools" not in st.session_state:
        st.session_state.detected_tools = []
    if "tab" not in st.session_state:
        st.session_state.tab = "dashboard"


def render_header():
    st.markdown("""
    <style>
    .stApp { background-color: #0f1419; }
    .stButton>button { background-color: #1d9bf0; color: white; border: none; border-radius: 8px; }
    .stButton>button:hover { background-color: #1a8cd8; }
    .stMetric { background-color: #1e2a3a; border-radius: 12px; padding: 16px; border: 1px solid #2f3f54; }
    div[data-testid="stMetricValue"] { color: #e7e9ea; font-size: 24px; font-weight: 700; }
    div[data-testid="stMetricLabel"] { color: #8b98a5; }
    .stSelectbox label, .stMultiSelect label { color: #8b98a5; }
    h1, h2, h3 { color: #e7e9ea; }
    </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 8])
    with col1:
        st.markdown("🧠")
    with col2:
        mode_label = "📂 BrainDump U盘版" if st.session_state.mode == "disk" else "💻 本地版"
        st.markdown(f"## Hippocampus v4.0.0  —  {mode_label}")


def render_stats(target: Path):
    stats = get_stats(target) if target else {"total_files": 0, "total_size": 0, "total_captures": 0, "sources": []}
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📁 记忆文件", stats["total_files"])
    c2.metric("💾 总大小", _format_size(stats["total_size"]))
    c3.metric("🔄 抓取次数", stats["total_captures"])
    c4.metric("🤖 AI 来源", len(stats["sources"]))


def _format_size(b: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if b < 1024:
            return f"{b:.1f}{unit}"
        b /= 1024
    return f"{b:.1f}TB"


def render_target_selector():
    """Target drive selector."""
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        if st.session_state.mode == "disk":
            # Fixed target from query param
            disk_path = st.query_params.get("path", "F:\\")
            st.info(f"📂 目标：{disk_path}")
            st.session_state.target = Path(disk_path)
        else:
            drives = get_removable_drives()
            options = []
            labels = []
            for d in drives:
                label = f"{d['name']}"
                if d["is_braindump"]:
                    label += " ✅ BrainDump"
                else:
                    label += " 🔌 外部磁盘"
                labels.append(label)
                options.append(d["path"])

            if options:
                selected = st.selectbox("备份目标", options, format_func=lambda x: next((l for l, p in zip(labels, options) if p == x), x))
                st.session_state.target = Path(selected)
            else:
                st.warning("未检测到外部磁盘，请插入 U盘")
                st.session_state.target = None

    with col2:
        if st.session_state.target:
            t = st.session_state.target
            bd = is_braindump(t)
            if bd:
                st.success(f"✅ BrainDump 已连接")
            else:
                st.warning(f"⚠️ 普通目录（非 BrainDump U盘）")
        else:
            st.info("未选择目标")

    with col3:
        if st.button("🔄 刷新", use_container_width=True):
            st.rerun()


def render_dashboard(target: Path):
    st.subheader("📊 仪表盘")
    render_stats(target)


def render_file_browser(target: Path):
    st.subheader("📂 文件浏览器")
    if not target:
        st.info("请先选择备份目标")
        return

    files = get_files(target)
    if not files:
        st.info("暂无已备份文件")
        return

    # Group by source
    sources = list({f["source_ai"] for f in files})
    col_filter, _ = st.columns([1, 3])
    with col_filter:
        selected = st.selectbox("筛选来源", ["全部"] + sources)

    filtered = files if selected == "全部" else [f for f in files if f["source_ai"] == selected]

    for f in filtered:
        with st.expander(f"📄 {f['file_name']}  ·  {f['source_ai']}  ·  {_format_size(f.get('size_bytes', 0))}"):
            col_a, col_b = st.columns([3, 1])
            with col_a:
                preview = f.get("content_preview", "")
                if preview:
                    st.text(preview[:500])
            with col_b:
                st.caption(f"抓取时间：{f.get('captured_at', '')[:16]}")
                st.caption(f"原始路径：{f.get('original_path', '')[:50]}")


def render_host_scanner():
    st.subheader("🖥️ 主机检测 + 扫描")

    if st.session_state.mode == "disk":
        st.info("U盘版仅支持浏览已有内容，请在本地版中使用扫描功能")
        return

    # ---- 自动检测 ----
    col_detect, col_manual = st.columns(2)

    with col_detect:
        if st.button("🔍 自动检测 AI 工具", use_container_width=True):
            with st.spinner("检测中（含 WSL 跨发行版）..."):
                st.session_state.detected_tools = detect_tools()
            if st.session_state.detected_tools:
                st.success(f"检测到 {len(st.session_state.detected_tools)} 个 AI 工具/目录")
            else:
                st.warning("未检测到，请在右侧手动填写目录")

    # ---- 手填目录 ----
    with col_manual:
        st.markdown("**找不到？手动指定目录**")
        manual_path = st.text_input(
            "AI 工具目录路径",
            placeholder="例如: ~/.hermes 或 /home/user/.openclaw",
            key="manual_path_input",
        )
        manual_name = st.text_input(
            "工具名称",
            value="custom",
            key="manual_name_input",
        )
        if manual_path and st.button("📂 扫描手动目录", use_container_width=True):
            with st.spinner(f"扫描 {manual_path} ..."):
                manual_results = scan_manual_path(manual_path, manual_name)
            if manual_results:
                st.session_state.scan_results = st.session_state.get("scan_results", [])
                # 去重
                existing_paths = {f["path"] for f in st.session_state.scan_results}
                for r in manual_results:
                    if r["path"] not in existing_paths:
                        st.session_state.scan_results.append(r)
                st.success(f"找到 {len(manual_results)} 个文件")
            else:
                st.warning(f"在 {manual_path} 中未找到 .md 文件，请检查路径")

    # ---- 展示检测结果 ----
    if st.session_state.detected_tools:
        st.divider()
        st.markdown("**📡 检测到的 AI 工具**")

        # 按来源分组显示
        local_tools = [t for t in st.session_state.detected_tools if t.get("source") == "local"]
        wsl_tools = [t for t in st.session_state.detected_tools if t.get("source", "").startswith("wsldistro:")]

        if local_tools:
            st.markdown("**本机**")
            for t in local_tools:
                paths_str = "  ·  ".join(t.get("found_paths", [])[:2])
                st.markdown(f"  ✅ **{t['display_name']}** — `{paths_str}`")

        if wsl_tools:
            # 按 distro 分组
            by_distro: Dict[str, List] = {}
            for t in wsl_tools:
                distro = t["source"].split(":", 1)[1]
                by_distro.setdefault(distro, []).append(t)
            for distro, tools in by_distro.items():
                st.markdown(f"**🐧 WSL: {distro}**")
                for t in tools:
                    paths_str = "  ·  ".join(t.get("found_paths", []))
                    st.markdown(f"  ✅ **{t['display_name']}** — `{paths_str}`")

        # 选择要扫描的工具
        tool_names = [t["name"] for t in st.session_state.detected_tools]
        tool_labels = {t["name"]: t["display_name"] for t in st.session_state.detected_tools}

        selected_tools = st.multiselect(
            "选择要扫描的 AI 来源",
            options=tool_names,
            default=tool_names,
            format_func=lambda x: tool_labels.get(x, x)
        )

        if selected_tools and st.button("📡 扫描记忆文件", use_container_width=True):
            with st.spinner("扫描中..."):
                st.session_state.scan_results = scan_host_tools(selected_tools)
            if st.session_state.scan_results:
                st.success(f"找到 {len(st.session_state.scan_results)} 个文件")
            else:
                st.info("未找到记忆文件")

    if st.session_state.scan_results:
        st.divider()
        st.markdown(f"**找到 {len(st.session_state.scan_results)} 个文件 — 勾选要备份的文件**")

        # Group by source
        by_source: Dict[str, List] = {}
        for f in st.session_state.scan_results:
            src = f["source"]
            by_source.setdefault(src, []).append(f)

        selected_files = []
        selected_files = []
        for src, flist in by_source.items():
            with st.expander(f"**{src}** ({len(flist)} 个文件)"):
                for f in flist:
                    size_str = _format_size(f["size"])
                    checked = st.checkbox(
                        f"📄 {f['name']}  ·  {size_str}",
                        value=True, key=f"file_{f['path']}"
                    )
                    if checked:
                        selected_files.append(f)

        if selected_files and st.session_state.target:
            if st.button(f"💾 备份 {len(selected_files)} 个文件到目标", type="primary", use_container_width=True):
                # Determine source tool
                tool_name = selected_files[0]["source"] if selected_files else "unknown"
                result = backup_files(st.session_state.target, selected_files, tool_name)
                if result["success"]:
                    st.success(f"✅ 已备份 {result['imported']} 个文件")
                    st.session_state.scan_results = []
                    st.rerun()
                else:
                    st.error(f"备份失败: {result.get('error', '未知错误')}")


def render_history(target: Path):
    st.subheader("📜 抓取历史")
    if not target:
        st.info("请先选择备份目标")
        return

    history = get_history(target)
    if not history:
        st.info("暂无抓取历史")
        return

    for h in history:
        date_str = h.get("capture_date", "")
        try:
            d = datetime.fromisoformat(date_str)
            if d.year < 2000:
                date_str = "初始化"
            else:
                date_str = d.strftime("%Y-%m-%d %H:%M")
        except Exception:
            pass

        with st.expander(f"📅 {date_str}  ·  📁 {h.get('total_files',0)} 个  ·  💾 {_format_size(h.get('total_size_bytes',0))}"):
            st.caption(f"主机：{h.get('host_computer','未知')}")
            if h.get("notes"):
                st.caption(f"备注：{h['notes']}")


def render_settings():
    st.subheader("⚙️ 设置")
    st.markdown("**当前模式**")
    mode = st.radio("模式", ["local", "disk"],
                    index=0 if st.session_state.mode == "local" else 1,
                    format_func=lambda x: "本地版（扫描+备份）" if x == "local" else "U盘版（浏览已有内容）",
                    label_visibility="collapsed")
    st.session_state.mode = mode

    if mode == "disk":
        path_input = st.text_input("U盘路径", value=st.query_params.get("path", "F:\\"))
        st.query_params["path"] = path_input
        st.session_state.target = Path(path_input)

    st.markdown("---")
    st.markdown("**关于**")
    st.caption("Hippocampus v4.0.0 — AI Memory Enhancement System")
    st.caption("https://github.com/Gabe-luv-Nancy/hippocampus")


# ============================================================================
# Main
# ============================================================================

def main():
    init_session()

    # Parse CLI args
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="local")
    parser.add_argument("--path", default=None)
    parser.add_argument("--server.port", dest="port", type=int, default=8501)
    args, _ = parser.parse_known_args()

    st.set_page_config(
        page_title="Hippocampus v4.0.0",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Override mode from CLI
    if args.mode:
        st.session_state.mode = args.mode
    if args.path:
        st.session_state.target = Path(args.path)

    render_header()
    st.divider()

    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 🧭 导航")
        page = st.radio("页面", [
            "📊 仪表盘", "📂 文件浏览器",
            "🖥️ 主机检测", "📜 抓取历史", "⚙️ 设置"
        ], label_visibility="collapsed")

        st.divider()
        render_target_selector()

    # Render current page
    if page == "📊 仪表盘":
        render_dashboard(st.session_state.target)
    elif page == "📂 文件浏览器":
        render_file_browser(st.session_state.target)
    elif page == "🖥️ 主机检测":
        render_host_scanner()
    elif page == "📜 抓取历史":
        render_history(st.session_state.target)
    elif page == "⚙️ 设置":
        render_settings()


if __name__ == "__main__":
    main()
