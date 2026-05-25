#!/usr/bin/env python3
"""
Backup engine for Hippocampus BrainDump USB Edition.
Handles scanning, file copying, and DB writes.
Adapted from github version — scanner path points to lib/ instead of scripts/.
"""

import os
import sys
import json
import shutil
import hashlib
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

# USB版: scanner.py 在 lib/ 目录下
SCRIPT_DIR = Path(__file__).parent.parent.parent / "lib"
sys.path.insert(0, str(SCRIPT_DIR))


@dataclass
class FileEntry:
    path: Path
    source_ai: str
    file_name: str
    size: int
    modified: str
    hash: str = ""
    preview: str = ""


@dataclass
class ScanResult:
    success: bool
    files: List[FileEntry]
    total: int
    sources: List[str]
    error: str = ""


@dataclass
class BackupResult:
    success: bool
    imported: int
    total: int
    errors: List[str]


class BackupEngine:
    """
    Unified backup engine for USB Edition.
    Works with both BrainDump U盘 and local directories.
    """

    def __init__(self, target_path: Path = None):
        self.target_path = target_path
        self.is_braindump = False
        if target_path:
            self.set_target(target_path)

    def set_target(self, path: Path):
        self.target_path = path
        self.is_braindump = self._check_braindump(path)

    def _check_braindump(self, path: Path) -> bool:
        marker = path / "marker.txt"
        if not marker.exists():
            return False
        try:
            return marker.read_text(encoding="utf-8").strip() == "HIPPOCAMPUS_BRAINDUMP_v4.0.0"
        except Exception:
            return False

    # === Scanning ===

    def scan_host(self, tools: List[str] = None) -> ScanResult:
        """Scan the local machine for memory files."""
        try:
            from scanner import Scanner
            scanner = Scanner(dry_run=True)
            if tools:
                for tool in tools:
                    scanner.scan_by_tool_name(tool)
            else:
                scanner.scan_all()

            entries = []
            for e in scanner.results:
                entries.append(FileEntry(
                    path=e.path,
                    source_ai=e.source_ai,
                    file_name=e.path.name,
                    size=e.size,
                    modified=e.modified_at,
                    hash=e.hash,
                    preview=e.content_preview[:100] if e.content_preview else ""
                ))

            sources = list(set(f.source_ai for f in entries))
            return ScanResult(
                success=True,
                files=entries,
                total=len(entries),
                sources=sources
            )
        except Exception as ex:
            return ScanResult(success=False, files=[], total=0, sources=[], error=str(ex))

    def detect_tools(self) -> List[Dict[str, Any]]:
        """Detect installed AI tools."""
        try:
            from detector import AIToolDetector
            detector = AIToolDetector()
            tools = detector.detect_all()
            return [t for t in tools if t.get("installed")]
        except Exception:
            return []

    # === Backup ===

    def backup_to_braindump(self, files: List[FileEntry]) -> BackupResult:
        """Backup files to a BrainDump U盘."""
        if not self.is_braindump or not self.target_path:
            return BackupResult(success=False, imported=0, total=len(files), errors=["不是 BrainDump U盘"])

        errors = []
        imported = 0

        # DB setup
        db_path = self.target_path / "db" / "brain_dump.sqlite"
        capture_dir = self.target_path / "capture"
        capture_dir.mkdir(parents=True, exist_ok=True)

        if not db_path.exists():
            errors.append("U盘数据库不存在")
            return BackupResult(success=False, imported=0, total=len(files), errors=errors)

        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        host = os.environ.get("COMPUTERNAME", os.environ.get("HOSTNAME", "unknown"))
        now = datetime.now().isoformat()
        cur.execute("""
            INSERT INTO captures (capture_date, total_files, total_size_bytes, host_computer)
            VALUES (?, 0, 0, ?)
        """, (datetime.now().strftime("%Y-%m-%d"), host))
        capture_id = cur.lastrowid

        for f in files:
            try:
                dest_dir = capture_dir / f.source_ai
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest_path = dest_dir / f.file_name

                counter = 1
                while dest_path.exists():
                    stem = f.path.stem
                    suffix = f.path.suffix
                    dest_path = dest_dir / f"{stem}_{counter}{suffix}"
                    counter += 1

                shutil.copy2(f.path, dest_path)

                # hash
                with open(dest_path, "rb") as fh:
                    file_hash = hashlib.sha256(fh.read()).hexdigest()[:16]

                # preview
                try:
                    with open(dest_path, "r", encoding="utf-8", errors="ignore") as fh:
                        preview = fh.read(200)
                except Exception:
                    preview = ""

                cur.execute("""
                    INSERT INTO files
                    (source_ai, original_path, file_name, relative_path, size_bytes,
                     modified_at, captured_at, hash, content_preview)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f.source_ai, str(f.path), f.file_name, str(dest_path),
                    f.size, f.modified, now, file_hash, preview
                ))
                imported += 1
            except Exception as ex:
                errors.append(f"{f.file_name}: {str(ex)}")

        conn.commit()
        conn.close()
        return BackupResult(success=imported > 0, imported=imported, total=len(files), errors=errors)

    def backup_to_local(self, files: List[FileEntry], dest_subdir: str = "capture") -> BackupResult:
        """Backup files to a local directory."""
        if not self.target_path:
            return BackupResult(success=False, imported=0, total=len(files), errors=["未设置目标路径"])

        errors = []
        imported = 0
        dest_base = self.target_path / dest_subdir

        for f in files:
            try:
                dest_dir = dest_base / f.source_ai
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest_path = dest_dir / f.file_name

                counter = 1
                while dest_path.exists():
                    stem = f.path.stem
                    suffix = f.path.suffix
                    dest_path = dest_dir / f"{stem}_{counter}{suffix}"
                    counter += 1

                shutil.copy2(f.path, dest_path)
                imported += 1
            except Exception as ex:
                errors.append(f"{f.file_name}: {str(ex)}")

        return BackupResult(success=imported > 0, imported=imported, total=len(files), errors=errors)

    # === DB queries ===

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics from target."""
        if self.is_braindump and self.target_path:
            return self._get_braindump_stats()
        else:
            return self._get_local_stats()

    def _get_braindump_stats(self) -> Dict[str, Any]:
        db_path = self.target_path / "db" / "brain_dump.sqlite"
        if not db_path.exists():
            return {"total_files": 0, "total_size": 0, "total_captures": 0, "sources": []}

        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*), COALESCE(SUM(size_bytes), 0) FROM files")
        file_count, total_size = cur.fetchone()
        cur.execute("SELECT COUNT(*) FROM captures")
        capture_count = cur.fetchone()[0]
        cur.execute("SELECT source_ai, COUNT(*) FROM files GROUP BY source_ai")
        sources = [{"name": r[0], "count": r[1]} for r in cur.fetchall()]
        conn.close()
        return {
            "total_files": file_count or 0,
            "total_size": total_size or 0,
            "total_captures": capture_count or 0,
            "sources": sources
        }

    def _get_local_stats(self) -> Dict[str, Any]:
        if not self.target_path:
            return {"total_files": 0, "total_size": 0, "total_captures": 0, "sources": []}
        capture_dir = self.target_path / "capture"
        if not capture_dir.exists():
            return {"total_files": 0, "total_size": 0, "total_captures": 0, "sources": []}

        files = list(capture_dir.rglob("*.md"))
        total_size = sum(f.stat().st_size for f in files)

        by_source: Dict[str, int] = {}
        for f in files:
            src = f.parent.name
            by_source[src] = by_source.get(src, 0) + 1

        sources = [{"name": k, "count": v} for k, v in by_source.items()]
        return {
            "total_files": len(files),
            "total_size": total_size,
            "total_captures": 0,
            "sources": sources
        }

    def get_files(self, source: str = None) -> List[Dict]:
        """Get files list from target."""
        if self.is_braindump and self.target_path:
            return self._get_braindump_files(source)
        else:
            return self._get_local_files(source)

    def _get_braindump_files(self, source: str = None) -> List[Dict]:
        db_path = self.target_path / "db" / "brain_dump.sqlite"
        if not db_path.exists():
            return []
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        if source:
            cur.execute("SELECT * FROM files WHERE source_ai = ? ORDER BY captured_at DESC LIMIT 200",
                        (source,))
        else:
            cur.execute("SELECT * FROM files ORDER BY captured_at DESC LIMIT 200")
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def _get_local_files(self, source: str = None) -> List[Dict]:
        if not self.target_path:
            return []
        capture_dir = self.target_path / "capture"
        if not capture_dir.exists():
            return []
        results = []
        if source:
            dirs = [capture_dir / source] if (capture_dir / source).exists() else []
        else:
            dirs = [d for d in capture_dir.iterdir() if d.is_dir()]
        for d in dirs:
            for f in d.glob("*.md"):
                try:
                    stat = f.stat()
                    results.append({
                        "source_ai": d.name,
                        "file_name": f.name,
                        "file_path": str(f),
                        "size_bytes": stat.st_size,
                        "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "captured_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    })
                except Exception:
                    pass
        return results

    def get_history(self) -> List[Dict]:
        """Get capture history."""
        if self.is_braindump and self.target_path:
            db_path = self.target_path / "db" / "brain_dump.sqlite"
            if not db_path.exists():
                return []
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM captures ORDER BY id DESC LIMIT 50")
            rows = cur.fetchall()
            conn.close()
            return [dict(r) for r in rows]
        return []
