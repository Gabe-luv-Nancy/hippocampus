# Styles
# ====

DARK_STYLE = """
QMainWindow {
    background-color: #0f1419;
    color: #e7e9ea;
}
QWidget {
    background-color: #0f1419;
    color: #e7e9ea;
    font-family: "Segoe UI", "SF Pro Display", -apple-system, sans-serif;
    font-size: 13px;
}
QPushButton {
    background-color: #1d9bf0;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
    min-width: 80px;
}
QPushButton:hover {
    background-color: #1a8cd8;
}
QPushButton:pressed {
    background-color: #1778c4;
}
QPushButton:disabled {
    background-color: #253345;
    color: #536471;
}
QPushButton.secondary {
    background-color: #1e2a3a;
    color: #8b98a5;
    border: 1px solid #2f3f54;
}
QPushButton.secondary:hover {
    background-color: #253345;
    color: #e7e9ea;
}
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #1e2a3a;
    color: #e7e9ea;
    border: 1px solid #2f3f54;
    border-radius: 8px;
    padding: 8px 12px;
    selection-background-color: #1d9bf0;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #1d9bf0;
}
QTabWidget::pane {
    border: 1px solid #2f3f54;
    border-radius: 8px;
    background-color: #1e2a3a;
    padding: 12px;
}
QTabBar::tab {
    background-color: transparent;
    color: #8b98a5;
    padding: 10px 20px;
    border: none;
    border-bottom: 2px solid transparent;
    font-weight: 600;
}
QTabBar::tab:selected {
    color: #e7e9ea;
    border-bottom: 2px solid #1d9bf0;
}
QTabBar::tab:hover:!selected {
    color: #e7e9ea;
    background-color: #1e2a3a;
}
QListWidget, QTableWidget {
    background-color: #1e2a3a;
    color: #e7e9ea;
    border: 1px solid #2f3f54;
    border-radius: 8px;
    outline: none;
}
QListWidget::item, QTableWidget::item {
    padding: 8px 12px;
    border-bottom: 1px solid #2f3f54;
}
QListWidget::item:selected, QTableWidget::item:selected {
    background-color: #2d3d52;
    color: #e7e9ea;
}
QListWidget::item:hover:!selected, QTableWidget::item:hover:!selected {
    background-color: #253345;
}
QCheckBox {
    color: #e7e9ea;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid #2f3f54;
    background-color: transparent;
}
QCheckBox::indicator:checked {
    background-color: #1d9bf0;
    border-color: #1d9bf0;
}
QComboBox {
    background-color: #1e2a3a;
    color: #e7e9ea;
    border: 1px solid #2f3f54;
    border-radius: 8px;
    padding: 8px 12px;
}
QComboBox:hover {
    border-color: #1d9bf0;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox QAbstractItemView {
    background-color: #1e2a3a;
    color: #e7e9ea;
    border: 1px solid #2f3f54;
    selection-background-color: #2d3d52;
}
QScrollBar:vertical {
    width: 8px;
    background-color: transparent;
}
QScrollBar::handle:vertical {
    background-color: #2f3f54;
    border-radius: 4px;
    min-height: 40px;
}
QScrollBar::handle:vertical:hover {
    background-color: #536471;
}
QScrollBar:horizontal {
    height: 8px;
    background-color: transparent;
}
QScrollBar::handle:horizontal {
    background-color: #2f3f54;
    border-radius: 4px;
    min-width: 40px;
}
QScrollBar::handle:horizontal:hover {
    background-color: #536471;
}
QLabel {
    background-color: transparent;
    color: #e7e9ea;
}
QLabel.title {
    font-size: 24px;
    font-weight: 700;
}
QLabel.subtitle {
    color: #8b98a5;
    font-size: 12px;
}
QLabel.card {
    background-color: #1e2a3a;
    border: 1px solid #2f3f54;
    border-radius: 12px;
    padding: 16px;
}
QLabel.card:hover {
    border-color: #3d5166;
}
QGroupBox {
    background-color: #1e2a3a;
    border: 1px solid #2f3f54;
    border-radius: 12px;
    padding: 16px;
    margin-top: 8px;
    font-weight: 600;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 8px;
    color: #8b98a5;
}
QProgressBar {
    background-color: #1e2a3a;
    border: none;
    border-radius: 6px;
    height: 8px;
    text-align: center;
}
QProgressBar::chunk {
    background-color: #1d9bf0;
    border-radius: 6px;
}
QStatusBar {
    background-color: #0f1419;
    color: #536471;
    border-top: 1px solid #2f3f54;
}
QToolTip {
    background-color: #1e2a3a;
    color: #e7e9ea;
    border: 1px solid #2f3f54;
    border-radius: 6px;
    padding: 6px;
}
"""

PURPLE_ACCENT = "#7856ff"
GREEN_ACCENT = "#00ba7c"
ORANGE_ACCENT = "#ff7a00"
