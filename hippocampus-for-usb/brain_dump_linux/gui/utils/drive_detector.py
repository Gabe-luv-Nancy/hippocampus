#!/usr/bin/env python3
"""
Drive and path detector for Hippocampus USB Edition.
Detects BrainDump U盘 and local directories.
Adapted from github version — identical logic, self-contained.
"""

import os
import platform
import subprocess
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass


MARKER_CONTENT = "HIPPOCAMPUS_BRAINDUMP_v4.0.0"


@dataclass
class DriveInfo:
    """Represents a storage location."""
    name: str
    path: Path
    is_braindump: bool
    is_removable: bool
    size_bytes: int = 0
    free_bytes: int = 0
    filesystem: str = ""


def get_marker_path(path: Path) -> Path:
    return path / "marker.txt"


def is_braindump(path: Path) -> bool:
    """Check if a path is a BrainDump drive."""
    marker = get_marker_path(path)
    if not marker.exists():
        return False
    try:
        content = marker.read_text(encoding="utf-8").strip()
        return content == MARKER_CONTENT
    except Exception:
        return False


def get_size_str(bytes_count: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_count < 1024:
            return f"{bytes_count:.1f}{unit}"
        bytes_count /= 1024
    return f"{bytes_count:.1f}PB"


class DriveDetector:
    """Detects available backup targets."""

    def __init__(self):
        self.system = platform.system().lower()

    def detect_braindump_drives(self) -> List[DriveInfo]:
        """Detect all connected BrainDump U盘."""
        all_drives = self._detect_removable_drives()
        return [d for d in all_drives if d.is_braindump]

    def detect_all_drives(self) -> List[DriveInfo]:
        """Detect all removable drives."""
        return self._detect_removable_drives()

    def _detect_removable_drives(self) -> List[DriveInfo]:
        """Platform-specific removable drive detection."""
        if self.system == "windows":
            return self._detect_windows()
        elif self.system == "darwin":
            return self._detect_macos()
        elif self.system == "linux":
            return self._detect_linux()
        return []

    def _detect_windows(self) -> List[DriveInfo]:
        drives = []
        try:
            result = subprocess.run(
                ["wmic", "logicaldisk", "where", "DriveType=2", "get",
                 "Caption,DeviceID,FileSystem,Size,FreeSpace", "/format:csv"],
                capture_output=True, text=True, encoding="utf-8", errors="ignore"
            )
            for line in result.stdout.strip().split("\n")[1:]:
                parts = [p.strip() for p in line.split(",")]
                if len(parts) < 6:
                    continue
                caption = parts[1]
                if len(caption) != 2 or caption[1] != ":":
                    continue
                fs = parts[3] if len(parts) > 3 else ""
                try:
                    size = int(parts[4]) if parts[4] else 0
                    free = int(parts[5]) if parts[5] else 0
                except (ValueError, TypeError):
                    size = free = 0
                mount = Path(caption + "\\")
                drives.append(DriveInfo(
                    name=caption,
                    path=mount,
                    is_braindump=is_braindump(mount),
                    is_removable=True,
                    size_bytes=size,
                    free_bytes=free,
                    filesystem=fs
                ))
        except Exception:
            pass
        return drives

    def _detect_macos(self) -> List[DriveInfo]:
        drives = []
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
                        drives.append(DriveInfo(
                            name=p.name,
                            path=p,
                            is_braindump=is_braindump(p),
                            is_removable=True,
                        ))
            except Exception:
                pass
        except Exception:
            pass
        return drives

    def _detect_linux(self) -> List[DriveInfo]:
        drives = []
        try:
            with open("/proc/mounts", "r") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) < 3:
                        continue
                    device, mount_point_str, fs = parts[0], parts[1], parts[2]
                    if not ("usb" in device.lower() or "sd" in device):
                        continue
                    if mount_point_str in ["/", "/boot", "/home", "/var", "/usr"]:
                        continue
                    mount = Path(mount_point_str)
                    drives.append(DriveInfo(
                        name=mount.name or device,
                        path=mount,
                        is_braindump=is_braindump(mount),
                        is_removable=True,
                        filesystem=fs
                    ))
        except Exception:
            pass
        return drives

    def get_default_target(self) -> Optional[DriveInfo]:
        """Get default backup target: prefer BrainDump U盘."""
        braindumps = self.detect_braindump_drives()
        if braindumps:
            return braindumps[0]
        all_drives = self.detect_all_drives()
        if all_drives:
            return all_drives[0]
        return None

    def is_path_braindump(self, path: str) -> bool:
        """Check if a given path is a BrainDump drive."""
        p = Path(path)
        if not p.exists() or not p.is_dir():
            return False
        return is_braindump(p)
