#!/usr/bin/env python3
"""
Hippocampus GUI - Unified Entry Point
=====================================
Supports two modes:
  --mode local   : Local version (scan host, backup to local dir or U盘)
  --mode disk    : U盘 version (browse U盘 contents, read-only)
"""

import sys
import os
import argparse
import threading
from pathlib import Path
from typing import Optional, List, Dict, Any

# ---------------------------------------------------------------------------
# Windows embeddable Python DLL path fix
# ---------------------------------------------------------------------------
if sys.platform == "win32":
    _sp_candidates = [
        Path(sys.prefix) / "Lib" / "site-packages",
        Path(sys.executable).parent / "Lib" / "site-packages",
    ]
    for _sp in _sp_candidates:
        _qt_bin = _sp / "PyQt6" / "Qt6" / "bin"
        if _qt_bin.is_dir():
            os.add_dll_directory(str(_qt_bin))
            os.environ["PATH"] = str(_qt_bin) + os.pathsep + os.environ.get("PATH", "")
            break

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QLabel, QStatusBar, QMessageBox,
    QFileDialog, QProgressDialog, QListWidget, QListWidgetItem,
    QCheckBox, QGroupBox, QTextEdit, QScrollArea, QSizePolicy,
    QAbstractItemView
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QFont

# Local imports
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from gui.utils.styles import DARK_STYLE
from gui.utils.drive_detector import DriveDetector, DriveInfo
from gui.utils.backup_engine import BackupEngine, FileEntry, ScanResult
from gui.app import StatsBar, TargetSelector


# ============================================================================
# Helpers
# ============================================================================

def get_size_str(b: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if b < 1024:
            return f"{b:.1f}{unit}"
        b /= 1024
    return f"{b:.1f}PB"


def format_date(s: str) -> str:
    if not s:
        return "--"
    try:
        from datetime import datetime
        d = datetime.fromisoformat(s)
        if d.year < 2000:
            return "从未"
        return d.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return s[:16] if s else "--"


# ============================================================================
# Host Scanner Widget
# ============================================================================

class HostScannerWidget(QWidget):
    """Host detection + scanning + backup."""
    scan_done = pyqtSignal(ScanResult)
    backup_done = pyqtSignal(dict)

    def __init__(self, engine: BackupEngine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.scan_result: Optional[ScanResult] = None
        self.detected_tools: List[Dict] = []
        self.selected_files: List[FileEntry] = []
        self.selected_tools: set = set()
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(DARK_STYLE)
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # --- Detection Section ---
        detect_group = QGroupBox("🔍 检测主机上的 AI 工具")
        detect_layout = QVBoxLayout(detect_group)

        self.detect_status = QLabel("点击「开始检测」扫描主机")
        self.detect_status.setStyleSheet("color: #8b98a5; padding: 4px;")
        detect_layout.addWidget(self.detect_status)

        self.tools_list = QListWidget()
        self.tools_list.setStyleSheet("""
            QListWidget {
                background-color: #1e2a3a; border: 1px solid #2f3f54;
                border-radius: 8px; padding: 4px;
            }
            QListWidget::item {
                padding: 10px 12px; border-bottom: 1px solid #2f3f54;
                color: #e7e9ea;
            }
            QListWidget::item:selected { background-color: #2d3d52; }
            QListWidget::item:hover { background-color: #253345; }
        """)
        self.tools_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.tools_list.itemChanged.connect(self.on_tool_toggled)
        detect_layout.addWidget(self.tools_list)

        btn_detect = QPushButton("🔍 开始检测")
        btn_detect.setStyleSheet("""
            QPushButton {
                background-color: #1d9bf0; color: white; border: none;
                border-radius: 8px; padding: 10px 20px; font-weight: 600;
            }
            QPushButton:hover { background-color: #1a8cd8; }
        """)
        btn_detect.clicked.connect(self.do_detect)
        detect_layout.addWidget(btn_detect)

        layout.addWidget(detect_group)

        # --- Scan Section ---
        scan_group = QGroupBox("📡 扫描记忆文件")
        scan_layout = QVBoxLayout(scan_group)

        self.scan_status = QLabel("选择工具后点击「扫描」")
        self.scan_status.setStyleSheet("color: #8b98a5; padding: 4px;")
        scan_layout.addWidget(self.scan_status)

        self.scan_list = QListWidget()
        self.scan_list.setStyleSheet("""
            QListWidget {
                background-color: #1e2a3a; border: 1px solid #2f3f54;
                border-radius: 8px; padding: 4px; min-height: 200px;
            }
            QListWidget::item {
                padding: 8px 12px; border-bottom: 1px solid #2f3f54;
                color: #e7e9ea;
            }
            QListWidget::item:selected { background-color: #2d3d52; }
        """)
        scan_layout.addWidget(self.scan_list)

        btn_scan = QPushButton("📡 扫描选中的来源")
        btn_scan.setStyleSheet("""
            QPushButton {
                background-color: #7856ff; color: white; border: none;
                border-radius: 8px; padding: 10px 20px; font-weight: 600;
            }
            QPushButton:hover { background-color: #6b4de0; }
        """)
        btn_scan.clicked.connect(self.do_scan)
        scan_layout.addWidget(btn_scan)

        layout.addWidget(scan_group)

        # --- Backup Section ---
        backup_group = QGroupBox("💾 备份选中文件")
        backup_layout = QVBoxLayout(backup_group)

        self.backup_status = QLabel("勾选要备份的文件")
        self.backup_status.setStyleSheet("color: #8b98a5; padding: 4px;")
        backup_layout.addWidget(self.backup_status)

        btn_backup = QPushButton("💾 备份到目标")
        btn_backup.setStyleSheet("""
            QPushButton {
                background-color: #00ba7c; color: white; border: none;
                border-radius: 8px; padding: 12px 20px; font-weight: 700;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #00a06d; }
        """)
        btn_backup.clicked.connect(self.do_backup)
        backup_layout.addWidget(btn_backup)

        layout.addWidget(backup_group)

    def on_tool_toggled(self, item):
        tool_name = item.data(Qt.ItemDataRole.UserRole)
        if item.checkState() == Qt.CheckState.Checked:
            self.selected_tools.add(tool_name)
        else:
            self.selected_tools.discard(tool_name)

    def do_detect(self):
        self.detect_status.setText("检测中...")
        self.tools_list.clear()
        QApplication.processEvents()

        tools = self.engine.detect_tools()
        self.detected_tools = tools

        if not tools:
            self.detect_status.setText("未检测到支持的 AI 工具")
            return

        self.detect_status.setText(f"检测到 {len(tools)} 个 AI 工具：")

        for tool in tools:
            item = QListWidgetItem(f"✅ {tool['display_name']} ({tool['name']})")
            item.setData(Qt.ItemDataRole.UserRole, tool["name"])
            item.setCheckState(Qt.CheckState.Unchecked)
            self.tools_list.addItem(item)

    def do_scan(self):
        if not self.selected_tools:
            QMessageBox.warning(self, "提示", "请先选择至少一个 AI 来源")
            return

        self.scan_status.setText("扫描中...")
        self.scan_list.clear()
        QApplication.processEvents()

        self.scan_result = self.engine.scan_host(list(self.selected_tools))

        if not self.scan_result.success:
            self.scan_status.setText(f"扫描失败: {self.scan_result.error}")
            return

        self.scan_status.setText(f"找到 {self.scan_result.total} 个文件")
        self.selected_files = self.scan_result.files

        for f in self.scan_result.files:
            size_str = get_size_str(f.size)
            item = QListWidgetItem(f"☐ {f.file_name}  [{f.source_ai}]  {size_str}")
            item.setData(Qt.ItemDataRole.UserRole, f)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.scan_list.addItem(item)

        self.scan_list.itemChanged.connect(self.on_file_toggled)

    def on_file_toggled(self, item):
        f = item.data(Qt.ItemDataRole.UserRole)
        if item.checkState() == Qt.CheckState.Checked:
            if f not in self.selected_files:
                self.selected_files.append(f)
        else:
            if f in self.selected_files:
                self.selected_files.remove(f)

    def do_backup(self):
        if not self.selected_files:
            QMessageBox.warning(self, "提示", "请先勾选要备份的文件")
            return

        target = self.engine.target_path
        if not target:
            QMessageBox.warning(self, "提示", "请先在顶部选择备份目标")
            return

        # Confirm
        reply = QMessageBox.question(
            self, "确认备份",
            f"将备份 {len(self.selected_files)} 个文件到：\n{target}\n\n是否继续？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.backup_status.setText(f"正在备份 {len(self.selected_files)} 个文件...")

        # Run in thread
        def run():
            if self.engine.is_braindump:
                result = self.engine.backup_to_braindump(self.selected_files)
            else:
                result = self.engine.backup_to_local(self.selected_files)

            def done():
                if result.success:
                    self.backup_status.setText(
                        f"✅ 备份完成：{result.imported}/{result.total} 个文件"
                    )
                    self.backup_done.emit({
                        "imported": result.imported,
                        "total": result.total
                    })
                else:
                    self.backup_status.setText(f"⚠️ 部分完成：{result.imported}/{result.total}")
                    if result.errors:
                        QMessageBox.warning(
                            self, "备份警告",
                            f"部分文件备份失败：\n" + "\n".join(result.errors[:5])
                        )

            QTimer.singleShot(0, done)

        threading.Thread(target=run, daemon=True).start()


# ============================================================================
# File Browser Widget
# ============================================================================

class FileBrowserWidget(QWidget):
    """Browse backed up files."""
    file_selected = pyqtSignal(str)

    def __init__(self, engine: BackupEngine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.current_source = None
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(DARK_STYLE)
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Source filter
        filter_layout = QHBoxLayout()
        self.filter_btns: List[QPushButton] = []
        self.all_filter_btn = QPushButton("全部")
        self.all_filter_btn.setCheckable(True)
        self.all_filter_btn.setChecked(True)
        self.all_filter_btn.clicked.connect(lambda: self.filter_by(None))
        filter_layout.addWidget(self.all_filter_btn)
        filter_layout.addStretch()
        self.source_filters = QHBoxLayout()
        filter_layout.addLayout(self.source_filters)
        layout.addLayout(filter_layout)

        # File list
        self.file_list = QListWidget()
        self.file_list.setStyleSheet("""
            QListWidget {
                background-color: #1e2a3a; border: 1px solid #2f3f54;
                border-radius: 8px;
            }
            QListWidget::item {
                padding: 12px 16px; border-bottom: 1px solid #2f3f54;
                color: #e7e9ea;
            }
            QListWidget::item:hover { background-color: #253345; }
        """)
        self.file_list.itemDoubleClicked.connect(self.on_file_open)
        layout.addWidget(self.file_list)

        self.status = QLabel("双击文件预览内容")
        self.status.setStyleSheet("color: #536471; font-size: 12px;")
        layout.addWidget(self.status)

    def refresh(self):
        self.file_list.clear()
        stats = self.engine.get_stats()
        sources = stats.get("sources", [])

        # Update filter buttons
        while self.source_filters.count():
            w = self.source_filters.takeAt(0).widget()
            if w:
                w.deleteLater()
        self.filter_btns.clear()

        for src in sources:
            btn = QPushButton(f"{src['name']} ({src['count']})")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, s=src["name"]: self.filter_by(s) if checked else None)
            self.source_filters.addWidget(btn)
            self.filter_btns.append(btn)

        # Load files
        self.load_files(self.current_source)

    def filter_by(self, source: Optional[str]):
        self.current_source = source
        for btn in self.filter_btns:
            btn.setChecked(False)
        if source is None:
            self.all_filter_btn.setChecked(True)
        else:
            self.all_filter_btn.setChecked(False)
        self.load_files(source)

    def load_files(self, source: Optional[str]):
        self.file_list.clear()
        files = self.engine.get_files(source)

        if not files:
            self.file_list.addItem("暂无文件")
            return

        for f in files:
            size = f.get("size_bytes", 0)
            modified = format_date(f.get("modified_at", ""))
            name = f.get("file_name", "unknown")
            src = f.get("source_ai", "unknown")
            self.file_list.addItem(
                f"📄 {name}  [{src}]  {get_size_str(size)}  {modified}"
            )

    def on_file_open(self, item):
        files = self.engine.get_files(self.current_source)
        row = self.file_list.row(item)
        if row < len(files):
            f = files[row]
            path = f.get("relative_path") or f.get("file_path")
            if path and Path(path).exists():
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                        content = fh.read(2000)
                    QMessageBox.information(
                        self, f"预览: {f.get('file_name')}",
                        content[:1500]
                    )
                except Exception as e:
                    QMessageBox.warning(self, "错误", f"无法打开文件:\n{e}")
            else:
                QMessageBox.information(self, "提示", f"文件路径:\n{path}")


# ============================================================================
# History Widget
# ============================================================================

class HistoryWidget(QWidget):
    def __init__(self, engine: BackupEngine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(DARK_STYLE)
        layout = QVBoxLayout(self)

        self.history_list = QListWidget()
        self.history_list.setStyleSheet("""
            QListWidget {
                background-color: #1e2a3a; border: 1px solid #2f3f54;
                border-radius: 8px;
            }
            QListWidget::item {
                padding: 12px 16px; border-bottom: 1px solid #2f3f54;
                color: #e7e9ea;
            }
        """)
        layout.addWidget(self.history_list)

    def refresh(self):
        self.history_list.clear()
        history = self.engine.get_history()

        if not history:
            self.history_list.addItem("暂无抓取历史")
            return

        for h in history:
            date = format_date(h.get("capture_date", ""))
            files = h.get("total_files", 0)
            size = get_size_str(h.get("total_size_bytes", 0))
            host = h.get("host_computer", "")
            notes = h.get("notes", "")
            self.history_list.addItem(
                f"📅 {date}  |  📁 {files} 个  |  💾 {size}  |  🖥️ {host}"
            )


# ============================================================================
# Main Window
# ============================================================================

class HippocampusGUI(QMainWindow):
    def __init__(self, mode: str = "local", disk_path: str = None):
        super().__init__()
        self.mode = mode
        self.disk_path = disk_path
        self.engine: Optional[BackupEngine] = None
        self.init_engine()
        self.init_ui()
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_stats)
        self.refresh_timer.start(5000)  # refresh every 5s
        QTimer.singleShot(500, self.auto_detect_target)

    def init_engine(self):
        if self.mode == "disk" and self.disk_path:
            target = Path(self.disk_path)
            self.engine = BackupEngine(target)
        else:
            self.engine = BackupEngine()

    def init_ui(self):
        self.setStyleSheet(DARK_STYLE)
        self.setWindowTitle(
            "Hippocampus BrainDump v4.0.0" if self.mode == "disk"
            else "Hippocampus v4.0.0 - 本地版"
        )
        self.setMinimumSize(800, 600)

        # --- Central widget ---
        central = QWidget()
        self.setCentralWidget(central)
        vbox = QVBoxLayout(central)
        vbox.setSpacing(16)

        # Title bar
        title_layout = QHBoxLayout()
        title = QLabel("🧠 Hippocampus")
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #e7e9ea;")
        title_layout.addWidget(title)

        mode_badge = QLabel(
            "U盘版" if self.mode == "disk" else "本地版"
        )
        mode_badge.setStyleSheet("""
            background-color: #7856ff; color: white;
            padding: 3px 10px; border-radius: 10px; font-size: 12px; font-weight: 600;
        """)
        title_layout.addWidget(mode_badge)
        title_layout.addStretch()

        btn_refresh = QPushButton("🔄")
        btn_refresh.setStyleSheet("""
            background-color: #1e2a3a; color: #8b98a5; border: 1px solid #2f3f54;
            border-radius: 6px; padding: 6px 12px;
        """)
        btn_refresh.clicked.connect(self.refresh_all)
        title_layout.addWidget(btn_refresh)
        vbox.addLayout(title_layout)

        # Stats bar
        self.stats_bar = StatsBar()
        vbox.addWidget(self.stats_bar)

        # Target selector (only in local mode)
        if self.mode != "disk":
            self.target_selector = TargetSelector()
            self.target_selector.target_changed.connect(self.on_target_changed)
            vbox.addWidget(self.target_selector)
        else:
            self.target_selector = None
            target_info = QLabel(f"📂 当前 U盘：{self.disk_path}")
            target_info.setStyleSheet("color: #8b98a5; font-size: 13px; padding: 4px;")
            vbox.addWidget(target_info)

        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #2f3f54; border-radius: 12px;
                background-color: #1e2a3a; padding: 12px; margin-top: -1px;
            }
        """)

        # Host Scanner tab (only in local mode)
        if self.mode == "disk":
            self.scanner_widget = None
        else:
            self.scanner_widget = HostScannerWidget(self.engine)
            self.scanner_widget.backup_done.connect(self.on_backup_done)
            self.tabs.addTab(self.scanner_widget, "🖥️ 主机检测")

        # File Browser tab
        self.browser_widget = FileBrowserWidget(self.engine)
        self.tabs.addTab(self.browser_widget, "📂 文件浏览器")

        # History tab
        self.history_widget = HistoryWidget(self.engine)
        self.tabs.addTab(self.history_widget, "📜 抓取历史")

        vbox.addWidget(self.tabs)

        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("color: #536471; font-size: 12px;")
        self.status_bar.showMessage("就绪")
        self.setStatusBar(self.status_bar)

        self.refresh_stats()

    def auto_detect_target(self):
        """Auto-detect BrainDump U盘 on startup."""
        if self.mode == "disk":
            return
        if not self.target_selector:
            return

        detector = DriveDetector()
        default = detector.get_default_target()
        if default:
            self.target_selector.set_target_info(default)
            self.engine.set_target(default.path)
            self.status_bar.showMessage(f"已自动选择备份目标：{default.name}")
        else:
            self.status_bar.showMessage("未检测到 BrainDump U盘，请手动选择备份目标")

    def on_target_changed(self, path: str):
        if path and self.engine:
            self.engine.set_target(Path(path))
            self.status_bar.showMessage(f"备份目标已切换为：{path}")

    def on_backup_done(self, result: dict):
        self.refresh_all()
        self.status_bar.showMessage(f"备份完成：{result['imported']}/{result['total']} 个文件")

    def refresh_stats(self):
        if not self.engine:
            return
        stats = self.engine.get_stats()
        self.stats_bar.update_stats(
            stats.get("total_files", 0),
            stats.get("total_size", 0),
            stats.get("total_captures", 0),
            len(stats.get("sources", []))
        )

    def refresh_all(self):
        self.refresh_stats()
        if self.browser_widget:
            self.browser_widget.refresh()
        if self.history_widget:
            self.history_widget.refresh()
        self.status_bar.showMessage("已刷新")


# ============================================================================
# Entry Point
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Hippocampus GUI v4.0.0")
    parser.add_argument("--mode", choices=["local", "disk"], default="local",
                        help="local: 本地版（扫描+备份）; disk: U盘版（浏览已有内容）")
    parser.add_argument("--path", type=str, default=None,
                        help="U盘路径（mode=disk 时必填）")
    args = parser.parse_args()

    if args.mode == "disk" and not args.path:
        print("错误：mode=disk 时必须指定 --path")
        sys.exit(1)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    win = HippocampusGUI(mode=args.mode, disk_path=args.path)
    win.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
