#!/usr/bin/env python3
"""
Hippocampus MemoryScanner v1.0
===============================
全覆盖记忆文件扫描引擎 — 核心基类 + 本地扫描器。
"""

import fnmatch
import os
import shutil
import sqlite3
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

# 复用已有模块
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from json_log import JsonLinesLog, get_client_log, get_usb_log
from file_hasher import compute_hash, needs_backup, record_hash, ensure_schema

# 尝试导入 rules_engine（可选，基类不强制）
try:
    from rules_engine import RulesEngine
    HAS_RULES_ENGINE = True
except ImportError:
    RulesEngine = None
    HAS_RULES_ENGINE = False


# =============================================================================
# 数据结构
# =============================================================================

@dataclass
class MemoryFileRule:
    """单条 AI 工具的记忆文件规则（对应 ai_tools.yaml 中的一条 tool）"""
    name: str
    display_name: str = ""
    enabled: bool = True
    priority: str = "medium"
    paths: List[Dict[str, str]] = field(default_factory=list)
    # 每个 path 项: {"path": "...", "type": "directory|file|glob", "description": "..."}

    @classmethod
    def from_dict(cls, d: Dict) -> "MemoryFileRule":
        return cls(
            name=d.get("name", ""),
            display_name=d.get("display_name", d.get("name", "")),
            enabled=d.get("enabled", True),
            priority=d.get("priority", "medium"),
            paths=d.get("paths", []),
        )


@dataclass
class FileEntry:
    """扫描到的文件条目"""
    path: Path
    tool: str          # AI 工具名
    size: int
    modified_at: str    # ISO 格式时间字符串
    hash: str = ""      # SHA256 形如 sha256:xxxx
    captured: bool = False   # 是否已抓取到 U 盘

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": str(self.path),
            "tool": self.tool,
            "size": self.size,
            "modified_at": self.modified_at,
            "hash": self.hash,
            "captured": self.captured,
        }


@dataclass
class BackupResult:
    """备份结果汇总"""
    total_found: int = 0
    total_needed: int = 0
    total_skipped: int = 0
    total_copied: int = 0
    total_failed: int = 0
    tools_summary: Dict[str, int] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_found": self.total_found,
            "total_needed": self.total_needed,
            "total_skipped": self.total_skipped,
            "total_copied": self.total_copied,
            "total_failed": self.total_failed,
            "tools_summary": self.tools_summary,
            "errors": self.errors,
        }


# =============================================================================
# 扫描规则加载
# =============================================================================

def load_rules(rules_path: Path) -> List[MemoryFileRule]:
    """
    从 YAML/JSON 配置文件加载扫描规则。

    Args:
        rules_path: ai_tools.yaml 路径

    Returns:
        List[MemoryFileRule]
    """
    if not rules_path.exists():
        return []

    try:
        import yaml
        with open(rules_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception:
        # Fallback: 纯 JSON
        import json
        with open(rules_path, "r", encoding="utf-8") as f:
            data = json.load(f)

    tools = data.get("ai_tools", [])
    return [MemoryFileRule.from_dict(t) for t in tools if t.get("enabled", True)]


# =============================================================================
# 核心扫描引擎（基类）
# =============================================================================

class MemoryScanner(ABC):
    """
    全覆盖记忆文件扫描引擎 — 抽象基类。

    子类必须实现 scan_paths() 方法完成实际路径遍历。
    基类负责：增量判断、文件复制、双端日志。
    """

    def __init__(
        self,
        rules_path: Path,
        usb_db_path: Path,
        client_log_dir: Path = None,
        usb_mount: Path = None,
    ):
        """
        Args:
            rules_path:     ai_tools.yaml 路径
            usb_db_path:    U 盘 SQLite 数据库路径
            client_log_dir: 客户端日志目录（默认 ~/.hippocampus/logs/）
            usb_mount:      U 盘挂载点（用于写 USB 日志）
        """
        self.rules = load_rules(rules_path)
        self.usb_db_path = usb_db_path
        self._init_usb_db()
        self._init_logs(client_log_dir, usb_mount)

        # rules_engine 初始化（可选）
        if HAS_RULES_ENGINE and RulesEngine:
            self.rules_engine = RulesEngine()
        else:
            self.rules_engine = None

    # -------------------------------------------------------------------------
    # 初始化
    # -------------------------------------------------------------------------

    def _init_usb_db(self) -> None:
        """初始化 U 盘数据库连接和 schema"""
        self.usb_db = sqlite3.connect(str(self.usb_db_path))
        ensure_schema(self.usb_db)

    def _init_logs(self, client_log_dir: Path, usb_mount: Path) -> None:
        """初始化客户端和 U 盘两端日志"""
        if client_log_dir:
            self.client_log = JsonLinesLog(client_log_dir / "client_<date>.jsonl")
        else:
            self.client_log = get_client_log()

        if usb_mount:
            self.usb_log = get_usb_log(usb_mount)
        else:
            # 默认存根，避免未设置时崩溃
            self.usb_log = JsonLinesLog(Path("/tmp/.hippocampus_usb_log_<date>.jsonl"))

    # -------------------------------------------------------------------------
    # 抽象方法（子类实现）
    # -------------------------------------------------------------------------

    @abstractmethod
    def scan_paths(self, tool: MemoryFileRule) -> List[FileEntry]:
        """
        扫描指定工具的所有路径，返回文件列表。

        子类负责：
        - 递归遍历 tool.paths
        - 对每条路径按 type（directory/file/glob）处理
        - 返回 List[FileEntry]
        """
        ...

    # -------------------------------------------------------------------------
    # 核心业务逻辑
    # -------------------------------------------------------------------------

    def _collect_files_from_rule(self, tool: MemoryFileRule) -> List[FileEntry]:
        """调用子类 scan_paths，收集结果"""
        return self.scan_paths(tool)

    def _filter_rules_engine(self, entry: FileEntry) -> bool:
        """用 rules_engine 二次过滤（如果可用）"""
        if self.rules_engine is None:
            return True
        from rules_engine import MatchResult
        result: MatchResult = self.rules_engine.match(entry.path)
        return result.matched

    def run_backup(self, usb_mount: Path) -> BackupResult:
        """
        完整备份流程：扫描 → 增量判断 → 复制 → 日志。

        Args:
            usb_mount: U 盘挂载点（用于写入捕获文件）

        Returns:
            BackupResult 汇总
        """
        result = BackupResult()
        usb_mount = Path(usb_mount)

        # 确保 U 盘数据库和日志可用
        self.usb_log = get_usb_log(usb_mount)

        for tool_rule in self.rules:
            if not tool_rule.enabled:
                continue

            try:
                entries = self._collect_files_from_rule(tool_rule)
            except Exception as e:
                result.errors.append(f"[{tool_rule.name}] scan error: {e}")
                continue

            result.total_found += len(entries)
            result.tools_summary[tool_rule.name] = len(entries)

            for entry in entries:
                # rules_engine 过滤（可选）
                if not self._filter_rules_engine(entry):
                    self.log_dual("SKIP", {
                        "tool": tool_rule.name,
                        "path": str(entry.path),
                        "reason": "rules_engine_reject",
                    })
                    continue

                # 哈希计算
                entry.hash = compute_hash(entry.path)
                if not entry.hash:
                    self.log_dual("SKIP", {
                        "tool": tool_rule.name,
                        "path": str(entry.path),
                        "reason": "hash_failed",
                    })
                    result.total_skipped += 1
                    continue

                # 增量判断
                needs, reason = needs_backup(
                    entry.path,
                    self.usb_db,
                    entry.size,
                    entry.modified_at,
                )

                if not needs:
                    self.log_dual("SKIP", {
                        "tool": tool_rule.name,
                        "path": str(entry.path),
                        "hash": entry.hash,
                        "reason": reason,
                    })
                    result.total_skipped += 1
                    continue

                # 需要备份：复制到 U 盘
                try:
                    captured_path = self._copy_to_usb(entry, usb_mount, tool_rule.name)
                    entry.captured = True
                    result.total_copied += 1

                    # 记录哈希到 SQLite
                    record_hash(
                        self.usb_db,
                        entry.path,
                        entry.hash,
                        entry.size,
                        entry.modified_at,
                        tool=tool_rule.name,
                    )
                    self.usb_db.commit()

                    self.log_dual("COPIED", {
                        "tool": tool_rule.name,
                        "path": str(entry.path),
                        "size": entry.size,
                        "hash": entry.hash,
                        "captured_path": str(captured_path),
                    })

                except Exception as e:
                    result.total_failed += 1
                    result.errors.append(f"[{tool_rule.name}] copy error: {entry.path} -> {e}")
                    self.log_dual("ERROR", {
                        "tool": tool_rule.name,
                        "path": str(entry.path),
                        "error": str(e),
                    })

        # 写入 COMPLETE 事件
        self.log_dual("COMPLETE", result.to_dict())
        self.client_log.write("COMPLETE", side="client", **result.to_dict())
        self.usb_log.write("COMPLETE", side="usb", **result.to_dict())

        # 同步客户端日志到 U 盘
        self._sync_client_log_to_usb(usb_mount)

        return result

    def _copy_to_usb(self, entry: FileEntry, usb_mount: Path, tool_name: str) -> Path:
        """
        将文件复制到 U 盘 capture/{tool_name}/ 目录。

        Returns:
            目标路径
        """
        dest_dir = usb_mount / "capture" / tool_name
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / entry.path.name

        # 防止文件名冲突：加序号
        if dest_path.exists():
            stem = entry.path.stem
            suffix = entry.path.suffix
            counter = 1
            while dest_path.exists():
                dest_path = dest_dir / f"{stem}_{counter}{suffix}"
                counter += 1

        shutil.copy2(entry.path, dest_path)
        return dest_path

    def _sync_client_log_to_usb(self, usb_mount: Path) -> None:
        """备份完成后将客户端日志同步到 U 盘"""
        try:
            usb_log_path = usb_mount / "logs" / "client_<date>.jsonl"
            count = self.client_log.sync_to_usb(usb_log_path)
        except Exception as e:
            pass  # 日志同步失败不影响主流程

    # -------------------------------------------------------------------------
    # 双端日志
    # -------------------------------------------------------------------------

    def log_dual(self, event: str, data: dict, side: str = "both") -> None:
        """
        同时写入客户端日志和 U 盘日志。

        Args:
            event: 事件名
            data:  日志数据
            side:  "client" | "usb" | "both"
        """
        if side in ("client", "both"):
            self.client_log.write(event, side="client", **data)
        if side in ("usb", "both"):
            self.usb_log.write(event, side="usb", **data)

    def log_event(self, event: str, **kwargs) -> None:
        """便捷方法：同时写两端"""
        self.log_dual(event, kwargs, side="both")

    # -------------------------------------------------------------------------
    # 工具方法
    # -------------------------------------------------------------------------

    def close(self) -> None:
        """关闭数据库连接"""
        if hasattr(self, "usb_db"):
            self.usb_db.close()


# =============================================================================
# 本地扫描器
# =============================================================================

class LocalScanner(MemoryScanner):
    """
    本地磁盘扫描器。

    通过递归遍历 tool.paths 下所有文件，用 fnmatch + rules_engine 过滤。
    零外部依赖（除 rules_engine 可选外）。
    """

    def scan_paths(self, tool: MemoryFileRule) -> List[FileEntry]:
        """
        扫描指定工具的所有路径，返回 FileEntry 列表。
        """
        results: List[FileEntry] = []

        for path_cfg in tool.paths:
            path_str = path_cfg.get("path", "")
            path_type = path_cfg.get("type", "directory")
            if not path_str:
                continue

            expanded = Path(os.path.expanduser(path_str))
            found = self._scan_one_path(expanded, path_type, tool.name)
            results.extend(found)

        return results

    def _scan_one_path(self, path: Path, path_type: str, tool_name: str) -> List[FileEntry]:
        """扫描单个路径配置"""
        entries: List[FileEntry] = []

        if path_type == "file":
            if path.exists() and path.is_file():
                entry = self._make_entry(path, tool_name)
                if entry:
                    entries.append(entry)

        elif path_type == "directory":
            entries.extend(self._scan_directory(path, tool_name))

        elif path_type == "glob":
            # glob 模式：只匹配文件名，不递归
            entries.extend(self._scan_glob(path, tool_name))

        else:
            # 默认当 directory 处理
            if path.is_dir():
                entries.extend(self._scan_directory(path, tool_name))

        return entries

    def _scan_directory(self, directory: Path, tool_name: str) -> List[FileEntry]:
        """递归扫描目录（.md 优先，兼顾其他文本文件）"""
        entries: List[FileEntry] = []

        # 优先扫描 .md 文件
        for ext in ("*.md", "*.yaml", "*.yml", "*.json", "*.txt"):
            try:
                for p in directory.rglob(ext):
                    entry = self._make_entry(p, tool_name)
                    if entry:
                        entries.append(entry)
            except PermissionError:
                continue

        # 如果目录内没有匹配文件，尝试扫描所有文件（无扩展名限制）
        if not entries:
            try:
                for p in directory.rglob("*"):
                    if p.is_file() and not any(p.suffixes):
                        entry = self._make_entry(p, tool_name)
                        if entry:
                            entries.append(entry)
            except PermissionError:
                pass

        return entries

    def _scan_glob(self, pattern_path: Path, tool_name: str) -> List[FileEntry]:
        """处理 glob 模式路径（如 ~/.openclaw/workspace/memory/*.md）"""
        # 把 ~/.openclaw/workspace/memory/*.md 拆成目录 + glob pattern
        parent = pattern_path.parent
        glob_pattern = pattern_path.name

        entries: List[FileEntry] = []
        try:
            for p in parent.glob(glob_pattern):
                if p.is_file():
                    entry = self._make_entry(p, tool_name)
                    if entry:
                        entries.append(entry)
        except PermissionError:
            pass

        return entries

    def _make_entry(self, path: Path, tool_name: str) -> Optional[FileEntry]:
        """根据文件路径构造 FileEntry（不计算 hash）"""
        try:
            stat = path.stat()
        except Exception:
            return None

        size = stat.st_size
        mtime = datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds")

        return FileEntry(
            path=path,
            tool=tool_name,
            size=size,
            modified_at=mtime,
        )


# =============================================================================
# 扫描结果汇总
# =============================================================================

def summarize_entries(entries: List[FileEntry]) -> Dict[str, Any]:
    """返回扫描结果的统计摘要"""
    from collections import Counter
    by_tool = Counter(e.tool for e in entries)
    total_size = sum(e.size for e in entries)
    return {
        "total": len(entries),
        "by_tool": dict(by_tool),
        "total_size_bytes": total_size,
        "total_size_kb": round(total_size / 1024, 1),
    }


# =============================================================================
# 测试
# =============================================================================

if __name__ == "__main__":
    import tempfile

    print("=== MemoryScanner 验证测试 ===\n")

    # 使用真实存在的配置（如果可用）或临时文件
    config_dir = SCRIPT_DIR / "config"
    rules_path = config_dir / "ai_tools.yaml"

    if not rules_path.exists():
        print("[SKIP] ai_tools.yaml not found, using mock config")
        # 创建临时规则
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("""
ai_tools:
  - name: "openclaw"
    display_name: "OpenClaw"
    enabled: true
    priority: high
    paths:
      - path: "~/.openclaw/workspace/"
        type: "directory"
""")
            rules_path = Path(f.name)

    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建临时 USB DB
        usb_db_path = Path(tmpdir) / "test.db"
        client_log_dir = Path(tmpdir) / "logs"

        scanner = LocalScanner(
            rules_path=rules_path,
            usb_db_path=usb_db_path,
            client_log_dir=client_log_dir,
        )

        # 加载规则
        print(f"[PASS] Loaded {len(scanner.rules)} rules")

        # 扫描 OpenClaw（如果存在）
        for tool in scanner.rules:
            if tool.name == "openclaw":
                entries = scanner.scan_paths(tool)
                print(f"[PASS] Scanned openclaw: found {len(entries)} entries")
                for e in entries[:5]:
                    print(f"       - {e.path} ({e.size} B)")
                if len(entries) > 5:
                    print(f"       ... and {len(entries)-5} more")

        # 测试日志写入
        scanner.log_dual("TEST_EVENT", {"msg": "hello from LocalScanner"}, side="both")
        client_entries = scanner.client_log.read()
        print(f"\n[PASS] Client log entries: {len(client_entries)}")

        # 测试 USB 日志
        usb_mount = Path(tmpdir) / "usb"
        usb_mount.mkdir()
        scanner.usb_log = get_usb_log(usb_mount)
        scanner.log_dual("USB_TEST", {"tool": "test", "path": "/tmp/test.md"}, side="usb")
        print(f"[PASS] USB log path: {scanner.usb_log.path}")

        # 测试同步
        synced = scanner.client_log.sync_to_usb(usb_mount / "logs" / "client_<date>.jsonl")
        print(f"[PASS] Synced {synced} entries to USB")

        scanner.close()
        print("\n[ALL TESTS PASSED]")
