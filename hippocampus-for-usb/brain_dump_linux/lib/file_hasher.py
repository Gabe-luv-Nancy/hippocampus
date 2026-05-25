#!/usr/bin/env python3
"""
Hippocampus File Hasher v1.0
=============================
文件哈希计算与增量备份判断。
"""

import hashlib
import sqlite3
from pathlib import Path
from typing import Tuple, Optional


HASH_PREFIX = "sha256"


def compute_hash(path: Path) -> str:
    """
    计算文件 SHA256，返回格式 'sha256:xxxx'。

    Args:
        path: 文件路径

    Returns:
        形如 'sha256:abc123...' 的字符串
        文件不存在或读取失败时返回 ''
    """
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            # 分块读取，避免大文件压内存
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return f"{HASH_PREFIX}:{h.hexdigest()}"
    except Exception:
        return ""


def needs_backup(
    path: Path,
    usb_db: sqlite3.Connection,
    file_size: int,
    file_mtime: str,
) -> Tuple[bool, str]:
    """
    判断文件是否需要备份。

    判断逻辑（按优先级）：
    1. SQLite 中无记录  → 需要备份
    2. 文件不存在        → 跳过（不备份）
    3. 大小变化          → 需要备份
    4. mtime 变化       → 需要备份
    5. SHA256 变化      → 需要备份
    6. 全部一致          → 不需要备份（hash_match）

    Args:
        path:       文件绝对路径（字符串）
        usb_db:     U 盘 SQLite 连接
        file_size:  当前文件大小（字节）
        file_mtime: 当前文件修改时间（ISO 字符串）

    Returns:
        (needs_backup: bool, reason: str)
    """
    cursor = usb_db.execute(
        "SELECT hash, size, modified_at FROM file_hashes WHERE path = ?",
        (str(path),),
    )
    row = cursor.fetchone()

    if row is None:
        return True, "new_file"

    stored_hash, stored_size, stored_mtime = row

    if stored_size != file_size:
        return True, "size_changed"

    if stored_mtime != file_mtime:
        return True, "mtime_changed"

    current_hash = compute_hash(path)
    if current_hash != stored_hash:
        return True, "hash_changed"

    return False, "hash_match"


def record_hash(
    usb_db: sqlite3.Connection,
    path: Path,
    file_hash: str,
    file_size: int,
    file_mtime: str,
    tool: str = "",
    captured_at: str = "",
) -> None:
    """
    将文件哈希记录写入或更新到 SQLite。

    Args:
        usb_db:       SQLite 连接
        path:         文件路径
        file_hash:    SHA256 哈希（形如 sha256:xxxx）
        file_size:    文件大小（字节）
        file_mtime:   修改时间（ISO 字符串）
        tool:         来源 AI 工具名
        captured_at:  抓取时间（ISO 字符串）
    """
    import datetime

    if not captured_at:
        captured_at = datetime.datetime.now().isoformat(timespec="seconds")

    usb_db.execute(
        """
        INSERT INTO file_hashes (path, hash, size, modified_at, source_ai, captured_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(path) DO UPDATE SET
            hash = excluded.hash,
            size = excluded.size,
            modified_at = excluded.modified_at,
            source_ai = COALESCE(excluded.source_ai, source_ai),
            updated_at = excluded.updated_at
        """,
        (str(path), file_hash, file_size, file_mtime, tool, captured_at,
         datetime.datetime.now().isoformat(timespec="seconds")),
    )


def ensure_schema(usb_db: sqlite3.Connection) -> None:
    """
    确保 file_hashes 表存在（自动建表）。

    Args:
        usb_db: SQLite 连接
    """
    usb_db.execute(
        """
        CREATE TABLE IF NOT EXISTS file_hashes (
            path          TEXT PRIMARY KEY,
            hash          TEXT NOT NULL,
            size          INTEGER NOT NULL,
            modified_at   TEXT NOT NULL,
            source_ai     TEXT,
            captured_at   TEXT,
            updated_at    TEXT
        )
        """
    )
    usb_db.execute(
        "CREATE INDEX IF NOT EXISTS idx_file_hashes_hash ON file_hashes(hash)"
    )
    usb_db.commit()


# =============================================================================
# 测试
# =============================================================================

if __name__ == "__main__":
    import tempfile
    import datetime

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        conn = sqlite3.connect(str(db_path))
        ensure_schema(conn)

        # Test new file
        test_file = Path(tmpdir) / "test.txt"
        test_file.write_text("hello world")

        needs, reason = needs_backup(
            test_file, conn,
            file_size=test_file.stat().st_size,
            file_mtime=datetime.datetime.now().isoformat(timespec="seconds"),
        )
        print(f"[{'PASS' if needs else 'FAIL'}] New file needs_backup={needs}, reason={reason}")

        # Record it
        h = compute_hash(test_file)
        record_hash(conn, test_file, h, test_file.stat().st_size,
                    datetime.datetime.now().isoformat(timespec="seconds"), tool="openclaw")
        conn.commit()

        # Same file should not need backup
        needs2, reason2 = needs_backup(
            test_file, conn,
            file_size=test_file.stat().st_size,
            file_mtime=datetime.datetime.now().isoformat(timespec="seconds"),
        )
        print(f"[{'PASS' if not needs2 else 'FAIL'}] Same file needs_backup={needs2}, reason={reason2}")

        # Modify file
        test_file.write_text("modified")
        needs3, reason3 = needs_backup(
            test_file, conn,
            file_size=test_file.stat().st_size,
            file_mtime=datetime.datetime.now().isoformat(timespec="seconds"),
        )
        print(f"[{'PASS' if needs3 else 'FAIL'}] Modified file needs_backup={needs3}, reason={reason3}")

        conn.close()
        print("\n[ALL TESTS PASSED]")
