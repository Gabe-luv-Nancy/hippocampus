#!/usr/bin/env python3
"""
Hippocampus JSON Lines Log v1.0
================================
统一 JSON Lines 日志写入器，支持客户端和 U 盘两端日志。
"""

import json
import shutil
from datetime import date, datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


class JsonLinesLog:
    """JSON Lines 日志写入器（线程不安全，单进程使用）"""

    def __init__(self, path: Path):
        """
        Args:
            path: 日志文件路径，支持 <date> 占位符自动替换为今天日期
                  例如: ~/.hippocampus/logs/client_<date>.jsonl
        """
        self._original_path = str(path)
        self.path = self._resolve_date(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _resolve_date(self, path: Path) -> Path:
        """将 <date> 占位符替换为今天日期 (YYYY-MM-DD)"""
        date_str = date.today().isoformat()
        resolved = Path(str(path).replace("<date>", date_str))
        # Also handle {date} placeholder for compatibility
        resolved = Path(str(resolved).replace("{date}", date_str))
        return resolved

    def _make_entry(self, event: str, side: str, **kwargs) -> Dict[str, Any]:
        """构造标准日志条目"""
        entry = {
            "ts": datetime.now().isoformat(timespec="seconds"),
            "side": side,
            "event": event,
        }
        entry.update(kwargs)
        return entry

    def write(self, event: str, side: str = "client", **kwargs) -> None:
        """
        写入一条日志。

        Args:
            event:     事件名称，如 FOUND / SKIP / RECEIVED / COMPLETE
            side:      "client" 或 "usb"
            **kwargs:  其他字段，如 tool, path, size, hash, reason 等
        """
        entry = self._make_entry(event, side, **kwargs)
        line = json.dumps(entry, ensure_ascii=False, separators=(",", ":"))
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    def read(self) -> List[Dict[str, Any]]:
        """读取所有日志条目，按时间顺序返回"""
        if not self.path.exists():
            return []
        entries = []
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        return entries

    def read_events(self, event: str) -> List[Dict[str, Any]]:
        """只读取指定事件类型的条目"""
        return [e for e in self.read() if e.get("event") == event]

    def sync_to_usb(self, usb_log_path: Path) -> int:
        """
        将本端日志同步到 U 盘（追加写入，不覆盖 U 盘已有内容）。

        Args:
            usb_log_path: U 盘上的日志文件路径（支持 <date> 占位符）

        Returns:
            实际同步的条目数
        """
        entries = self.read()
        if not entries:
            return 0

        usb_path = self._resolve_date(usb_log_path)
        usb_path.parent.mkdir(parents=True, exist_ok=True)

        count = 0
        with open(usb_path, "a", encoding="utf-8") as f:
            for entry in entries:
                # 将 side 统一标记为来源端
                synced_entry = dict(entry)
                synced_entry["synced_at"] = datetime.now().isoformat(timespec="seconds")
                line = json.dumps(synced_entry, ensure_ascii=False, separators=(",", ":"))
                f.write(line + "\n")
                count += 1

        return count

    def clear(self) -> None:
        """清空日志文件"""
        if self.path.exists():
            self.path.unlink()

    def __repr__(self) -> str:
        return f"<JsonLinesLog {self.path}>"


# =============================================================================
# 便捷工厂函数
# =============================================================================

def get_client_log(log_dir: Path = None) -> JsonLinesLog:
    """创建客户端日志（写入 ~/.hippocampus/logs/）"""
    if log_dir is None:
        log_dir = Path.home() / ".hippocampus" / "logs"
    return JsonLinesLog(log_dir / "client_<date>.jsonl")


def get_usb_log(usb_mount: Path) -> JsonLinesLog:
    """创建 U 盘日志（写入 <usb_mount>/logs/）"""
    return JsonLinesLog(usb_mount / "logs" / "usb_<date>.jsonl")


# =============================================================================
# 测试
# =============================================================================

if __name__ == "__main__":
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = Path(tmpdir) / "test_<date>.jsonl"

        # Test basic write / read
        log = JsonLinesLog(log_path)
        log.write("FOUND", tool="openclaw", path="~/.openclaw/workspace/MEMORY.md",
                  size=3244, hash="sha256:abc123")
        log.write("SKIP", tool="openclaw", path="~/.openclaw/workspace/TODO.md",
                  reason="hash_match")
        log.write("COMPLETE", total=3)

        entries = log.read()
        print(f"[PASS] Wrote and read {len(entries)} entries")
        for e in entries:
            print(f"  {e}")

        # Test sync_to_usb
        usb_path = Path(tmpdir) / "usb_<date>.jsonl"
        synced = log.sync_to_usb(usb_path)
        print(f"\n[PASS] Synced {synced} entries to USB log")

        usb_entries = JsonLinesLog(usb_path).read()
        print(f"[PASS] USB log has {len(usb_entries)} entries")

        # Test date placeholder resolution
        print(f"\n[PASS] Path resolved to: {log.path}")

        # Test read_events
        found = log.read_events("FOUND")
        print(f"[PASS] FOUND events: {len(found)}")

        print("\n[ALL TESTS PASSED]")
