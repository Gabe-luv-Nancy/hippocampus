import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Literal

BACKUP_ROOT = Path(__file__).parent.parent.parent / "assets" / "hippocampus" / "monograph" / "file_memory"
BACKUP_ROOT.mkdir(parents=True, exist_ok=True)

def get_file_hash(path: Path) -> str:
    """计算文件 MD5，用于判断是否真的修改了"""
    return hashlib.md5(path.read_bytes()).hexdigest()

def backup_file(
    source_path: Path,
    mode: Literal["new", "modified"],
    backup_root: Path = BACKUP_ROOT
) -> Path:
    """
    备份单个文件

    - new: 直接文件名 → file_memory/filename.ext
    - modified: 加时间戳 → file_memory/filename_YYYYMMDD_HHMMSS.ext

    返回备份文件路径
    """
    target_dir = backup_root

    if mode == "modified":
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        stem = source_path.stem
        suffix = source_path.suffix
        new_name = f"{stem}_{timestamp}{suffix}"
        target_path = target_dir / new_name
    else:
        target_path = target_dir / source_path.name

    shutil.copy2(source_path, target_path)
    return target_path

def restore_backup(backup_path: Path, original_path: Path) -> None:
    """从备份恢复文件到原位置"""
    shutil.copy2(backup_path, original_path)
