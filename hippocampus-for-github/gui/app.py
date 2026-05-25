#!/usr/bin/env python3
"""
Hippocampus GUI - Main Window
"""

import sys
from pathlib import Path
from typing import Optional, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTabWidget, QStatusBar, QMenuBar, QMenu,
    QMessageBox, QFileDialog, QProgressDialog
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QAction

from .utils.styles import DARK_STYLE, get_size_str
from .utils.drive_detector import DriveDetector, DriveInfo
from .utils.backup_engine import BackupEngine, FileEntry


class StatsBar(QWidget):
    """Statistics cards row."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(12)
        self.setStyleSheet(DARK_STYLE)

        self.files_label = self._make_stat("📁", "记忆文件", "0")
        self.size_label = self._make_stat("💾", "总大小", "0 B")
        self.captures_label = self._make_stat("🔄", "抓取次数", "0")
        self.sources_label = self._make_stat("🤖", "AI 来源", "0")

        for w in [self.files_label, self.size_label, self.captures_label, self.sources_label]:
            layout.addWidget(w)
        layout.addStretch()

    def _make_stat(self, icon: str, label_text: str, value: str) -> QWidget:
        card = QWidget()
        card.setObjectName("stat_card")
        card.setStyleSheet("""
            QWidget#stat_card {
                background-color: #1e2a3a;
                border: 1px solid #2f3f54;
                border-radius: 12px;
                padding: 16px;
                min-width: 120px;
            }
        """)
        vbox = QVBoxLayout(card)
        hbox = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 28px;")
        value_label = QLabel(value)
        value_label.setObjectName("stat_value")
        value_label.setStyleSheet("font-size: 24px; font-weight: 700; color: #e7e9ea;")
        hbox.addWidget(icon_label)
        hbox.addWidget(value_label)
        hbox.addStretch()
        vbox.addLayout(hbox)
        lbl = QLabel(label_text)
        lbl.setStyleSheet("color: #8b98a5; font-size: 13px;")
        vbox.addWidget(lbl)
        card.value_label = value_label
        return card

    def update_stats(self, files: int, size: int, captures: int, sources: int):
        self.files_label.value_label.setText(str(files))
        self.size_label.value_label.setText(get_size_str(size))
        self.captures_label.value_label.setText(str(captures))
        self.sources_label.value_label.setText(str(sources))


class TargetSelector(QWidget):
    """Backup target selector with drive detection."""
    target_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.detector = DriveDetector()
        self.current_target: Optional[DriveInfo] = None
        self.local_mode = False
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(DARK_STYLE)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)

        lbl = QLabel("备份目标：")
        lbl.setStyleSheet("font-weight: 600; color: #8b98a5;")
        layout.addWidget(lbl)

        self.target_label = QLabel("未设置")
        self.target_label.setStyleSheet("font-weight: 600; color: #e7e9ea;")
        layout.addWidget(self.target_label)

        btn_select = QPushButton("选择目录...")
        btn_select.setObjectName("btn_select")
        btn_select.setStyleSheet("""
            QPushButton#btn_select {
                background-color: #1e2a3a; color: #e7e9ea;
                border: 1px solid #2f3f54; border-radius: 8px;
                padding: 6px 14px; font-weight: 600;
            }
            QPushButton#btn_select:hover {
                background-color: #253345; border-color: #1d9bf0;
            }
        """)
        btn_select.clicked.connect(self.select_target)
        layout.addWidget(btn_select)

        btn_refresh = QPushButton("🔄")
        btn_refresh.setObjectName("btn_refresh")
        btn_refresh.setStyleSheet("""
            QPushButton#btn_refresh {
                background-color: #1e2a3a; color: #8b98a5;
                border: 1px solid #2f3f54; border-radius: 8px;
                padding: 6px 12px; min-width: 36px;
            }
            QPushButton#btn_refresh:hover { background-color: #253345; color: #e7e9ea; }
        """)
        btn_refresh.clicked.connect(self.refresh)
        layout.addWidget(btn_refresh)
        layout.addStretch()

        self.status_label = QLabel("🔴 未连接")
        self.status_label.setStyleSheet("color: #f4212e; font-size: 12px;")
        layout.addWidget(self.status_label)

    def set_local_mode(self, local: bool = True):
        """Disable drive switching in local mode without U盘."""
        self.local_mode = local

    def refresh(self):
        """Re-detect drives."""
        self.detector = DriveDetector()
        default = self.detector.get_default_target()
        if default:
            self.set_target_info(default)
            self.target_changed.emit(str(default.path))

    def select_target(self):
        """Open directory picker."""
        dir_path = QFileDialog.getExistingDirectory(
            self, "选择备份目标目录", str(Path.home())
        )
        if dir_path:
            path = Path(dir_path)
            info = DriveInfo(
                name=path.name or str(path),
                path=path,
                is_braindump=self.detector.is_path_braindump(dir_path),
                is_removable=False
            )
            self.set_target_info(info)
            self.target_changed.emit(dir_path)

    def set_target_info(self, info: DriveInfo):
        self.current_target = info
        label = info.name
        if info.is_braindump:
            label += " (BrainDump)"
        self.target_label.setText(label)

        if info.is_braindump:
            self.status_label.setText("🟢 BrainDump 已连接")
            self.status_label.setStyleSheet("color: #00ba7c; font-size: 12px;")
        elif info.is_removable:
            self.status_label.setText("🟡 外部磁盘")
            self.status_label.setStyleSheet("color: #ff7a00; font-size: 12px;")
        else:
            self.status_label.setText("🟢 本地目录")
            self.status_label.setStyleSheet("color: #00ba7c; font-size: 12px;")

    def get_target(self) -> Optional[DriveInfo]:
        return self.current_target

    def get_target_path(self) -> Optional[Path]:
        return self.current_target.path if self.current_target else None
