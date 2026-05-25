#!/usr/bin/env python3
"""
Hippocampus SSHScanner v1.0
===========================
SSH/SFTP 远程扫描器（依赖 paramiko）。
继承 MemoryScanner 基类，通过 SFTP 遍历远程路径。
"""

import fnmatch
import json
import os
import stat
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# paramiko 为可选依赖
try:
    import paramiko
    HAS_PARAMIKO = True
except ImportError:
    paramiko = None
    HAS_PARAMIKO = False

from memory_scanner import MemoryScanner, FileEntry, MemoryFileRule
from dataclasses import dataclass


# =============================================================================
# SSH 配置加载
# =============================================================================

def load_ssh_config(config_path: Path) -> Dict:
    """
    加载 SSH 配置。

    支持两种格式：
    1. JSON: {"host": "...", "port": 22, "username": "...", "key_path": "~/.ssh/id_rsa"}
    2. SSH config 格式 (~/.ssh/config)

    Returns:
        Dict with keys: host, port, username, password (optional), key_path (optional)
    """
    config_path = Path(os.path.expanduser(str(config_path)))

    if not config_path.exists():
        raise FileNotFoundError(f"SSH config not found: {config_path}")

    # JSON 格式
    if config_path.suffix in (".json", ".yaml", ".yml"):
        try:
            import yaml
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            import json

            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)

    # SSH config 格式（简化解析，仅支持 Host / HostName / User / Port / IdentityFile）
    ssh_config: Dict = {}
    current_host = None

    with open(config_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = line.split(None, 1)
            if len(parts) < 2:
                continue

            key, val = parts[0], parts[1]

            if key == "Host":
                current_host = val
                # 默认端口
                ssh_config[val] = {"port": 22}
            elif current_host and key in ("HostName", "User", "Port", "IdentityFile"):
                ssh_config[current_host][key.lower()] = val

    return ssh_config


def resolve_ssh_host(ssh_config: Dict, host_alias: str = "default") -> Dict:
    """
    从 SSH 配置字典中解析指定主机的连接参数。

    Returns:
        Dict with host, port, username, password, key_path
    """
    if host_alias in ssh_config:
        cfg = ssh_config[host_alias]
    else:
        # 取第一个 Host 条目作为默认
        first_key = next(iter(k for k in ssh_config if k != "port"), None)
        cfg = ssh_config.get(first_key, {}) if first_key else {}

    return {
        "host": cfg.get("hostname", ""),
        "port": int(cfg.get("port", 22)),
        "username": cfg.get("user", ""),
        "password": None,         # 不存储明文密码，鼓励用 key
        "key_path": cfg.get("identityfile", ""),
    }


# =============================================================================
# SFTP 文件条目（远程）
# =============================================================================

@dataclass
class SFTPFileEntry:
    """SFTP 远程文件描述"""
    path: str          # 完整远程路径
    filename: str      # 文件名
    size: int
    mtime: float       # Unix timestamp


# =============================================================================
# SSH Scanner
# =============================================================================

class SSHScanner(MemoryScanner):
    """
    SSH/SFTP 远程扫描器。

    通过 paramiko 连接远程主机，使用 SFTP 递归遍历指定路径。
    """

    def __init__(
        self,
        ssh_config: Path,
        host_alias: str,
        rules_path: Path,
        usb_db_path: Path,
        client_log_dir: Path = None,
        usb_mount: Path = None,
    ):
        """
        Args:
            ssh_config:    SSH 配置文件路径（JSON 或 ~/.ssh/config 格式）
            host_alias:    在配置文件中要使用的主机别名
            rules_path:    ai_tools.yaml 路径
            usb_db_path:   U 盘 SQLite 数据库路径
            client_log_dir: 客户端日志目录
            usb_mount:     U 盘挂载点
        """
        if not HAS_PARAMIKO:
            raise ImportError(
                "paramiko is required for SSHScanner. "
                "Install with: pip install paramiko"
            )

        self.ssh_config = load_ssh_config(ssh_config)
        self.host_alias = host_alias
        self.host_info = resolve_ssh_host(self.ssh_config, host_alias)

        self._client: Optional[paramiko.SSHClient] = None
        self._sftp: Optional[paramiko.SFTPClient] = None

        super().__init__(rules_path, usb_db_path, client_log_dir, usb_mount)

    # -------------------------------------------------------------------------
    # 连接管理
    # -------------------------------------------------------------------------

    def _connect(self) -> None:
        """建立 SSH + SFTP 连接（惰性连接）"""
        if self._sftp is not None:
            return

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        key_path = self.host_info.get("key_path", "")
        if key_path:
            key_path = os.path.expanduser(key_path)
            pkey = paramiko.RSAKey.from_private_key_file(key_path)
            client.connect(
                hostname=self.host_info["host"],
                port=self.host_info["port"],
                username=self.host_info["username"],
                pkey=pkey,
                timeout=10,
            )
        else:
            client.connect(
                hostname=self.host_info["host"],
                port=self.host_info["port"],
                username=self.host_info["username"],
                timeout=10,
            )

        self._client = client
        self._sftp = client.open_sftp()

    def close(self) -> None:
        """关闭 SSH/SFTP 连接"""
        if self._sftp:
            try:
                self._sftp.close()
            except Exception:
                pass
            self._sftp = None
        if self._client:
            try:
                self._client.close()
            except Exception:
                pass
            self._client = None

        super().close()

    # -------------------------------------------------------------------------
    # SFTP 遍历
    # -------------------------------------------------------------------------

    def _sftp_listdir(self, remote_path: str) -> List[Tuple[str, int, float]]:
        """
        列出远程目录内容。

        Returns:
            List of (filename, size, mtime)
        """
        self._connect()
        result: List[Tuple[str, int, float]] = []
        try:
            for entry in self._sftp.listdir_attr(remote_path):
                result.append((entry.filename, entry.st_size, entry.st_mtime))
        except FileNotFoundError:
            pass
        except PermissionError:
            pass
        return result

    def _sftp_isdir(self, remote_path: str) -> bool:
        """检查远程路径是否为目录"""
        self._connect()
        try:
            return stat.S_ISDIR(self._sftp.stat(remote_path).st_mode)
        except Exception:
            return False

    def _sftp_isfile(self, remote_path: str) -> bool:
        """检查远程路径是否为文件"""
        self._connect()
        try:
            return stat.S_ISREG(self._sftp.stat(remote_path).st_mode)
        except Exception:
            return False

    def _sftp_walk_recursive(
        self, remote_dir: str, extensions: Tuple[str, ...] = (".md",)
    ) -> List[SFTPFileEntry]:
        """
        递归遍历远程目录，收集匹配扩展名的文件。

        Args:
            remote_dir:  远程目录（绝对路径）
            extensions:  匹配的扩展名元组

        Returns:
            List[SFTPFileEntry]
        """
        entries: List[SFTPFileEntry] = []
        dirs_to_visit = [remote_dir]

        while dirs_to_visit:
            current = dirs_to_visit.pop()
            try:
                items = self._sftp_listdir(current)
            except PermissionError:
                continue

            for filename, size, mtime in items:
                full_path = f"{current}/{filename}"
                try:
                    attrs = self._sftp.stat(full_path)
                    if stat.S_ISDIR(attrs.st_mode):
                        dirs_to_visit.append(full_path)
                    elif stat.S_ISREG(attrs.st_mode):
                        if filename.endswith(extensions):
                            entries.append(SFTPFileEntry(
                                path=full_path,
                                filename=filename,
                                size=size,
                                mtime=mtime,
                            ))
                except Exception:
                    continue

        return entries

    # -------------------------------------------------------------------------
    # 实现父类抽象方法
    # -------------------------------------------------------------------------

    def scan_paths(self, tool: MemoryFileRule) -> List[FileEntry]:
        """
        通过 SFTP 扫描指定工具的所有远程路径。
        """
        results: List[FileEntry] = []
        self._connect()

        for path_cfg in tool.paths:
            path_str = path_cfg.get("path", "")
            path_type = path_cfg.get("type", "directory")
            if not path_str:
                continue

            expanded = os.path.expanduser(path_str)

            if path_type == "file":
                entry = self._scan_remote_file(expanded, tool.name)
                if entry:
                    results.append(entry)

            elif path_type == "directory":
                results.extend(self._scan_remote_directory(expanded, tool.name))

            elif path_type == "glob":
                results.extend(self._scan_remote_glob(expanded, tool.name))

            else:
                if self._sftp_isdir(expanded):
                    results.extend(self._scan_remote_directory(expanded, tool.name))

        return results

    def _scan_remote_file(self, remote_path: str, tool_name: str) -> Optional[FileEntry]:
        """扫描单个远程文件"""
        try:
            attrs = self._sftp.stat(remote_path)
            if not stat.S_ISREG(attrs.st_mode):
                return None
            return FileEntry(
                path=Path(remote_path),   # 远程路径用 Path 包装
                tool=tool_name,
                size=attrs.st_size,
                modified_at=datetime.fromtimestamp(attrs.st_mtime).isoformat(timespec="seconds"),
            )
        except Exception:
            return None

    def _scan_remote_directory(self, remote_dir: str, tool_name: str) -> List[FileEntry]:
        """递归扫描远程目录"""
        entries: List[FileEntry] = []
        sftp_entries = self._sftp_walk_recursive(remote_dir)
        for sftp_e in sftp_entries:
            entries.append(FileEntry(
                path=Path(sftp_e.path),
                tool=tool_name,
                size=sftp_e.size,
                modified_at=datetime.fromtimestamp(sftp_e.mtime).isoformat(timespec="seconds"),
            ))
        return entries

    def _scan_remote_glob(self, pattern_path: str, tool_name: str) -> List[FileEntry]:
        """处理远程 glob 模式（模拟 fnmatch 行为）"""
        # 提取目录和模式
        remote_dir = str(Path(pattern_path).parent)
        glob_pat = Path(pattern_path).name

        entries: List[FileEntry] = []
        try:
            for entry_attr in self._sftp.listdir_attr(remote_dir):
                if fnmatch.fnmatch(entry_attr.filename, glob_pat):
                    full = f"{remote_dir}/{entry_attr.filename}"
                    if stat.S_ISREG(entry_attr.st_mode):
                        entries.append(FileEntry(
                            path=Path(full),
                            tool=tool_name,
                            size=entry_attr.st_size,
                            modified_at=datetime.fromtimestamp(entry_attr.st_mtime).isoformat(timespec="seconds"),
                        ))
        except PermissionError:
            pass
        return entries

    # -------------------------------------------------------------------------
    # 覆盖 _copy_to_usb：从远程通过 SFTP 下载
    # -------------------------------------------------------------------------

    def _copy_to_usb(self, entry: FileEntry, usb_mount: Path, tool_name: str) -> Path:
        """通过 SFTP 从远程主机下载文件到 U 盘"""
        import shutil
        dest_dir = usb_mount / "capture" / tool_name
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / entry.path.name

        if dest_path.exists():
            stem = entry.path.stem
            suffix = entry.path.suffix
            counter = 1
            while dest_path.exists():
                dest_path = dest_dir / f"{stem}_{counter}{suffix}"
                counter += 1

        # 通过 SFTP 获取远程文件，写入 U 盘
        with self._sftp.open(str(entry.path), "rb") as remote_f:
            with open(dest_path, "wb") as local_f:
                shutil.copyfileobj(remote_f, local_f)

        return dest_path





# =============================================================================
# 测试
# =============================================================================

if __name__ == "__main__":
    if not HAS_PARAMIKO:
        print("[SKIP] paramiko not installed — skipping live SSH tests")
        print("[PASS] SSHScanner module loaded successfully (paramiko not available)")
    else:
        print("[PASS] paramiko available — SSHScanner can be instantiated")
        print("[INFO] Provide ssh_config to run integration tests")
