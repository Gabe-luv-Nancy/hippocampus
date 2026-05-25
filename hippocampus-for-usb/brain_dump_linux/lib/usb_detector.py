#!/usr/bin/env python3
"""
Hippocampus USB Detector v4.0.0
============================
检测 BrainDump U 盘。
"""

import os
import platform
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass


@dataclass
class USBDrive:
    """USB 驱动器"""
    name: str
    mount_point: Path
    device: str
    size_bytes: int = 0
    free_bytes: int = 0
    filesystem: str = ""
    is_hippocampus: bool = False
    marker_content: str = ""


MARKER_EXPECTED = "HIPPOCAMPUS_BRAINDUMP_v4.0.0"


# ============================================================================
# USB 检测器
# ============================================================================

class USBDetector:
    """检测 USB 驱动器"""
    
    def __init__(self):
        self.system = platform.system().lower()
    
    def detect_all(self) -> List[USBDrive]:
        """检测所有 USB 驱动器"""
        if self.system == "windows":
            return self._detect_windows()
        elif self.system == "darwin":
            return self._detect_macos()
        elif self.system == "linux":
            return self._detect_linux()
        else:
            return []
    
    def _detect_windows(self) -> List[USBDrive]:
        """Windows: 使用 wmic 检测 USB 驱动器"""
        drives = []
        
        try:
            # 获取 USB 磁盘驱动器
            result = subprocess.run(
                ["wmic", "logicaldisk", "where", "DriveType=2", "get", 
                 "Caption,DeviceID,FileSystem,Size,FreeSpace", "/format:csv"],
                capture_output=True, text=True, encoding="utf-8", errors="ignore"
            )
            
            lines = result.stdout.strip().split("\n")
            for line in lines[1:]:  # 跳过表头
                parts = line.strip().split(",")
                if len(parts) < 5:
                    continue
                
                caption = parts[1] if len(parts) > 1 else ""
                device = parts[2] if len(parts) > 2 else ""
                fs = parts[3] if len(parts) > 3 else ""
                size = parts[4] if len(parts) > 4 else "0"
                free = parts[5] if len(parts) > 5 else "0"
                
                if not caption:
                    continue
                
                mount_point = Path(caption + "\\")
                drive = USBDrive(
                    name=caption,
                    mount_point=mount_point,
                    device=device,
                    size_bytes=int(size) if size.isdigit() else 0,
                    free_bytes=int(free) if free.isdigit() else 0,
                    filesystem=fs
                )
                
                # 检查是否为 Hippocampus U 盘
                self._check_hippocampus(drive)
                drives.append(drive)
                
        except Exception as e:
            print(f"[警告] Windows USB 检测失败: {e}")
        
        return drives
    
    def _detect_macos(self) -> List[USBDrive]:
        """macOS: 使用 diskutil 检测 USB 驱动器"""
        drives = []
        
        try:
            result = subprocess.run(
                ["diskutil", "list", "external"],
                capture_output=True, text=True, encoding="utf-8", errors="ignore"
            )
            
            output = result.stdout
            # 解析 diskutil 输出
            for line in output.split("\n"):
                line = line.strip()
                if line.startswith("/dev/"):
                    parts = line.split()
                    device = parts[0] if parts else ""
                    # 尝试获取更多信息
                    try:
                        info_result = subprocess.run(
                            ["diskutil", "info", device],
                            capture_output=True, text=True, encoding="utf-8", errors="ignore"
                        )
                        info = info_result.stdout
                        
                        mount_point = Path("/Volumes/Unknown")
                        name = "USB Drive"
                        size = 0
                        fs = ""
                        
                        for info_line in info.split("\n"):
                            if "Volume Name:" in info_line:
                                name = info_line.split(":", 1)[1].strip()
                                mount_point = Path(f"/Volumes/{name}")
                            elif "Total Size:" in info_line:
                                size_str = info_line.split(":", 1)[1].strip().split()[0]
                                try:
                                    size = int(float(size_str))
                                except Exception:
                                    pass
                            elif "Filesystem:" in info_line:
                                fs = info_line.split(":", 1)[1].strip()
                        
                        drive = USBDrive(
                            name=name,
                            mount_point=mount_point,
                            device=device,
                            size_bytes=size,
                            filesystem=fs
                        )
                        self._check_hippocampus(drive)
                        drives.append(drive)
                        
                    except Exception:
                        pass
                        
        except Exception as e:
            print(f"[警告] macOS USB 检测失败: {e}")
        
        return drives
    
    def _detect_linux(self) -> List[USBDrive]:
        """Linux: 检测 /proc/mounts 和 lsblk"""
        drives = []
        
        try:
            # 方法1：从 /proc/mounts 获取
            with open("/proc/mounts", "r") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) < 3:
                        continue
                    
                    device = parts[0]
                    mount_point_str = parts[1]
                    fs = parts[2]
                    
                    # 过滤 USB 设备（通常是 /dev/sdX 或 /dev/usb/）
                    is_usb = (
                        device.startswith("/dev/sd") or 
                        "usb" in device.lower() or
                        "usb" in mount_point_str.lower()
                    )
                    
                    # 排除系统分区
                    exclude_mounts = ["/", "/boot", "/home", "/var", "/usr"]
                    if mount_point_str in exclude_mounts:
                        is_usb = False
                    
                    if not is_usb:
                        continue
                    
                    mount_point = Path(mount_point_str)
                    
                    # 获取大小（通过 lsblk）
                    size = 0
                    free = 0
                    try:
                        lsblk_result = subprocess.run(
                            ["lsblk", "-b", "-o", "NAME,SIZE,MOUNTPOINT", "--noheadings"],
                            capture_output=True, text=True, encoding="utf-8"
                        )
                        for lb_line in lsblk_result.stdout.split("\n"):
                            lb_parts = lb_line.strip().split()
                            if len(lb_parts) >= 2 and device in lb_parts[0]:
                                try:
                                    size = int(lb_parts[1]) * 1024
                                except Exception:
                                    pass
                    except Exception:
                        pass
                    
                    drive = USBDrive(
                        name=mount_point.name,
                        mount_point=mount_point,
                        device=device,
                        size_bytes=size,
                        filesystem=fs
                    )
                    self._check_hippocampus(drive)
                    drives.append(drive)
                    
        except Exception as e:
            print(f"[警告] Linux USB 检测失败: {e}")
        
        return drives
    
    def _check_hippocampus(self, drive: USBDrive) -> None:
        """检查是否为 Hippocampus U 盘"""
        marker_path = drive.mount_point / "marker.txt"
        
        if not marker_path.exists():
            drive.is_hippocampus = False
            return
        
        try:
            content = marker_path.read_text(encoding="utf-8").strip()
            drive.marker_content = content
            drive.is_hippocampus = (content == MARKER_EXPECTED)
        except Exception:
            drive.is_hippocampus = False
    
    def detect_hippocampus_drives(self) -> List[USBDrive]:
        """只返回 Hippocampus U 盘"""
        all_drives = self.detect_all()
        return [d for d in all_drives if d.is_hippocampus]
    
    def is_hippocampus_drive(self, path: str) -> bool:
        """检查指定路径是否为 Hippocampus U 盘"""
        marker_path = Path(path) / "marker.txt"
        if not marker_path.exists():
            return False
        try:
            content = marker_path.read_text(encoding="utf-8").strip()
            return content == MARKER_EXPECTED
        except Exception:
            return False
    
    def get_db_path(self, drive: USBDrive) -> Path:
        """获取 U 盘数据库路径"""
        return drive.mount_point / "db" / "brain_dump.sqlite"
    
    def get_capture_dir(self, drive: USBDrive, source_ai: str) -> Path:
        """获取 U 盘 capture 目录"""
        return drive.mount_point / "capture" / source_ai
    
    def validate_drive(self, drive: USBDrive) -> Dict[str, Any]:
        """验证 U 盘完整性"""
        issues = []
        
        # 检查数据库
        db_path = self.get_db_path(drive)
        if not db_path.exists():
            issues.append("数据库文件不存在")
        
        # 检查 capture 目录
        capture_dir = drive.mount_point / "capture"
        if not capture_dir.exists():
            issues.append("capture 目录不存在")
        
        # 检查 marker
        if not drive.is_hippocampus:
            issues.append("marker.txt 内容不正确")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }
    
    def print_drives(self, drives: List[USBDrive] = None):
        """打印驱动器列表"""
        if drives is None:
            drives = self.detect_all()
        
        if not drives:
            print("未检测到 USB 驱动器")
            return
        
        print(f"{'='*60}")
        print(f"USB 驱动器检测")
        print(f"{'='*60}")
        print()
        
        for drive in drives:
            status = "✓ Hippocampus" if drive.is_hippocampus else "✗ 普通"
            size_str = self._format_size(drive.size_bytes) if drive.size_bytes else "?"
            free_str = self._format_size(drive.free_bytes) if drive.free_bytes else "?"
            
            print(f"  {drive.name}: {drive.mount_point}")
            print(f"    状态: {status}")
            print(f"    文件系统: {drive.filesystem or '?'}")
            print(f"    容量: {size_str} | 剩余: {free_str}")
            if drive.is_hippocampus:
                validation = self.validate_drive(drive)
                if validation["valid"]:
                    print(f"    验证: ✓ 通过")
                else:
                    print(f"    验证: ✗ 失败")
                    for issue in validation["issues"]:
                        print(f"           - {issue}")
            print()
    
    def _format_size(self, bytes_count: int) -> str:
        """格式化字节大小"""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if bytes_count < 1024:
                return f"{bytes_count:.1f}{unit}"
            bytes_count /= 1024
        return f"{bytes_count:.1f}PB"


# ============================================================================
# 命令行入口
# ============================================================================

def main():
    detector = USBDetector()
    
    import argparse
    parser = argparse.ArgumentParser(description="Hippocampus USB Detector v4.0.0")
    parser.add_argument("--hippocampus", "-H", action="store_true",
                        help="只显示 Hippocampus U 盘")
    parser.add_argument("--validate", "-v", action="store_true",
                        help="验证 U 盘完整性")
    parser.add_argument("--path", "-p", type=str, default=None,
                        help="检查指定路径是否为 Hippocampus U 盘")
    
    args = parser.parse_args()
    
    if args.path:
        is_hippocampus = detector.is_hippocampus_drive(args.path)
        print(f"路径 {args.path}: {'是' if is_hippocampus else '不是'} Hippocampus U 盘")
        return
    
    if args.hippocampus:
        drives = detector.detect_hippocampus_drives()
        if not drives:
            print("未检测到 Hippocampus U 盘")
        else:
            detector.print_drives(drives)
    else:
        detector.print_drives()


if __name__ == "__main__":
    main()
