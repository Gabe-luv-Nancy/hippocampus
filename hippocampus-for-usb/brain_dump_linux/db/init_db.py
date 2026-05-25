#!/usr/bin/env python3
"""
Hippocampus BrainDump 数据库初始化脚本
版本：v4.0.0
商家发货前必须运行此脚本初始化数据库
"""

import sqlite3
import os
import sys
from pathlib import Path

MARKER_CONTENT = "HIPPOCAMPUS_BRAINDUMP_v4.0.0"

SCHEMA_SQL = """
-- files: 抓取的文件记录
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_ai TEXT NOT NULL,
    original_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    relative_path TEXT NOT NULL,
    size_bytes INTEGER,
    modified_at TEXT,
    captured_at TEXT NOT NULL,
    hash TEXT,
    content_preview TEXT
);

-- captures: 每次抓取会话
CREATE TABLE IF NOT EXISTS captures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    capture_date TEXT NOT NULL,
    total_files INTEGER DEFAULT 0,
    total_size_bytes INTEGER DEFAULT 0,
    host_computer TEXT,
    notes TEXT
);

-- tags: 文件标签
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER REFERENCES files(id),
    tag TEXT NOT NULL
);

-- indexes: 加速查询
CREATE INDEX IF NOT EXISTS idx_files_source ON files(source_ai);
CREATE INDEX IF NOT EXISTS idx_files_captured ON files(captured_at);
CREATE INDEX IF NOT EXISTS idx_captures_date ON captures(capture_date);

-- file_hashes: 文件哈希值记录
CREATE TABLE IF NOT EXISTS file_hashes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    hash_value TEXT NOT NULL,
    hash_algorithm TEXT DEFAULT 'sha256',
    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

SEED_SQL = """
-- 插入一条欢迎记录
INSERT INTO captures (capture_date, total_files, total_size_bytes, host_computer, notes)
VALUES (
    '1970-01-01',
    0,
    0,
    'Hippocampus BrainDump v4.0.0',
    'U 盘初始化完成。请在电脑上运行 Hippocampus Host 进行首次扫描。'
);

-- 插入示例标签
INSERT INTO tags (file_id, tag) VALUES (NULL, 'brain-dump-initialized');
"""


def get_db_path(script_dir: Path = None) -> Path:
    """获取数据库路径"""
    if script_dir is None:
        script_dir = Path(__file__).parent
    
    db_dir = script_dir
    # 向上两级：db/ -> brain_dump/ -> hippoocampus-for-usb/
    if db_dir.name == "db":
        db_dir = db_dir.parent
    elif db_dir.name == "brain_dump":
        pass
    
    db_path = db_dir / "db" / "brain_dump.sqlite"
    return db_path


def init_database(db_path: Path = None) -> bool:
    """初始化数据库"""
    if db_path is None:
        db_path = get_db_path(Path(__file__).parent)
    
    # 确保 db 目录存在
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 如果数据库已存在，先备份
    if db_path.exists():
        backup_path = db_path.with_suffix(".sqlite.backup")
        print(f"[信息] 数据库已存在，备份到 {backup_path}")
        import shutil
        shutil.copy2(db_path, backup_path)
    
    # 创建数据库
    print(f"[信息] 创建数据库: {db_path}")
    conn = sqlite3.connect(str(db_path))
    
    # 执行建表
    cursor = conn.cursor()
    for statement in SCHEMA_SQL.strip().split(";"):
        statement = statement.strip()
        if statement:
            cursor.execute(statement)
    
    # 插入种子数据
    for statement in SEED_SQL.strip().split(";"):
        statement = statement.strip()
        if statement:
            cursor.execute(statement)
    
    conn.commit()
    conn.close()
    
    print("[完成] 数据库初始化成功")
    return True


def validate_database(db_path: Path = None) -> bool:
    """验证数据库完整性"""
    if db_path is None:
        db_path = get_db_path(Path(__file__).parent)
    
    if not db_path.exists():
        print("[错误] 数据库文件不存在")
        return False
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    errors = []
    
    # 检查表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    for required in ["files", "captures", "tags", "file_hashes"]:
        if required not in tables:
            errors.append(f"缺少表: {required}")
    
    # 检查索引
    if "files" in tables:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='files';")
        indexes = [row[0] for row in cursor.fetchall()]
        if "idx_files_source" not in indexes:
            errors.append("缺少索引: idx_files_source")
    
    conn.close()
    
    if errors:
        print("[错误] 数据库验证失败:")
        for e in errors:
            print(f"  - {e}")
        return False
    
    print("[通过] 数据库验证成功")
    return True


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Hippocampus BrainDump 数据库初始化")
    parser.add_argument("--path", "-p", type=str, default=None,
                        help="数据库路径（默认: db/brain_dump.sqlite）")
    parser.add_argument("--validate", "-v", action="store_true",
                        help="只验证，不初始化")
    parser.add_argument("--force", "-f", action="store_true",
                        help="强制重新初始化（覆盖现有数据库）")
    
    args = parser.parse_args()
    
    # 确定数据库路径
    if args.path:
        db_path = Path(args.path)
    else:
        db_path = get_db_path()
    
    print(f"{'='*60}")
    print("Hippocampus BrainDump 数据库初始化")
    print(f"{'='*60}")
    print(f"数据库路径: {db_path}")
    print()
    
    # 验证模式
    if args.validate:
        success = validate_database(db_path)
        sys.exit(0 if success else 1)
    
    # 初始化模式
    if db_path.exists() and not args.force:
        print("[警告] 数据库已存在")
        print("使用 --force 强制重新初始化（会覆盖现有数据）")
        sys.exit(1)
    
    success = init_database(db_path)
    if success:
        print()
        validate_database(db_path)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
