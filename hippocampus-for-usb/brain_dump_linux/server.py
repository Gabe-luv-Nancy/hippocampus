#!/usr/bin/env python3
"""
Hippocampus BrainDump Server
============================
HTTP 服务器 + SQLite 数据库 + 扫描引擎
提供 REST API 给前端 UI 调用
"""

import os
import sys
import json
import sqlite3
import hashlib
import threading
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Dict, List, Optional, Any

# 尝试导入扫描模块
SCRIPT_DIR = Path(__file__).parent
SCANNER_DIR = SCRIPT_DIR / "lib"

# ============================================================================
# 路径配置
# ============================================================================

def get_drive_root() -> Path:
    """获取 U 盘根目录（server.py 所在目录）"""
    return SCRIPT_DIR


def get_db_path() -> Path:
    """获取数据库路径"""
    return get_drive_root() / "db" / "brain_dump.sqlite"


def get_capture_dir() -> Path:
    """获取 capture 目录"""
    return get_drive_root() / "capture"


def get_output_dir() -> Path:
    """获取 output 目录"""
    return get_drive_root() / "output"


# ============================================================================
# 数据库操作
# ============================================================================

def db_get_files(source_ai: str = None, limit: int = 100) -> List[Dict]:
    """获取文件列表"""
    db = get_db_path()
    if not db.exists():
        return []
    
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    if source_ai:
        cur.execute("""
            SELECT * FROM files WHERE source_ai = ? 
            ORDER BY captured_at DESC LIMIT ?
        """, (source_ai, limit))
    else:
        cur.execute("""
            SELECT * FROM files ORDER BY captured_at DESC LIMIT ?
        """, (limit,))
    
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def db_get_captures(limit: int = 20) -> List[Dict]:
    """获取抓取记录"""
    db = get_db_path()
    if not db.exists():
        return []
    
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM captures ORDER BY id DESC LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def db_get_stats() -> Dict:
    """获取统计信息"""
    db = get_db_path()
    if not db.exists():
        return {
            "total_files": 0,
            "total_size": 0,
            "total_captures": 0,
            "sources": [],
            "db_exists": False
        }
    
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*), COALESCE(SUM(size_bytes), 0) FROM files")
    file_count, total_size = cur.fetchone()
    
    cur.execute("SELECT COUNT(*) FROM captures")
    capture_count = cur.fetchone()[0]
    
    cur.execute("SELECT source_ai, COUNT(*) as cnt FROM files GROUP BY source_ai")
    sources = [{"name": row[0], "count": row[1]} for row in cur.fetchall()]
    
    conn.close()
    
    return {
        "total_files": file_count or 0,
        "total_size": total_size or 0,
        "total_captures": capture_count or 0,
        "sources": sources,
        "db_exists": True
    }


def db_insert_file(file_info: Dict) -> int:
    """插入文件记录"""
    db = get_db_path()
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO files 
        (source_ai, original_path, file_name, relative_path, size_bytes, modified_at, captured_at, hash, content_preview)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        file_info["source_ai"],
        file_info["original_path"],
        file_info["file_name"],
        file_info["relative_path"],
        file_info["size_bytes"],
        file_info["modified_at"],
        file_info["captured_at"],
        file_info["hash"],
        file_info["content_preview"]
    ))
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id


def db_insert_capture(host_computer: str = "", notes: str = "") -> int:
    """插入抓取记录"""
    db = get_db_path()
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d")
    cur.execute("""
        INSERT INTO captures (capture_date, total_files, total_size_bytes, host_computer, notes)
        VALUES (?, 0, 0, ?, ?)
    """, (now, host_computer, notes))
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id


def db_update_capture_stats(capture_id: int):
    """更新抓取统计"""
    db = get_db_path()
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    cur.execute("""
        UPDATE captures SET 
            total_files = (SELECT COUNT(*) FROM files WHERE captured_at >= 
                (SELECT captured_at FROM captures WHERE id = ?)),
            total_size_bytes = (SELECT COALESCE(SUM(size_bytes), 0) FROM files WHERE captured_at >= 
                (SELECT captured_at FROM captures WHERE id = ?))
        WHERE id = ?
    """, (capture_id, capture_id, capture_id))
    conn.commit()
    conn.close()


# ============================================================================
# 扫描操作（调用 scanner.py）
# ============================================================================

def scan_host(tools: List[str] = None) -> Dict:
    """扫描主机文件"""
    sys.path.insert(0, str(SCANNER_DIR))
    
    try:
        from scanner import Scanner
        
        scanner = Scanner(dry_run=True)  # dry_run，只扫描不写入
        
        if tools:
            for tool in tools:
                scanner.scan_by_tool_name(tool)
        else:
            scanner.scan_all()
        
        results = []
        for entry in scanner.results:
            results.append({
                "path": str(entry.path),
                "source_ai": entry.source_ai,
                "file_name": entry.path.name,
                "size": entry.size,
                "modified": entry.modified_at,
                "hash": entry.hash,
                "preview": entry.content_preview[:100] if entry.content_preview else ""
            })
        
        return {
            "success": True,
            "files": results,
            "total": len(results),
            "sources": list(set(f["source_ai"] for f in results))
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "files": [],
            "total": 0
        }


def detect_host_tools() -> Dict:
    """检测主机上的 AI 工具"""
    sys.path.insert(0, str(SCANNER_DIR))
    
    try:
        from detector import AIToolDetector
        
        detector = AIToolDetector()
        tools = detector.detect_all()
        
        return {
            "success": True,
            "tools": [
                {
                    "name": t["name"],
                    "display_name": t["display_name"],
                    "installed": t["installed"],
                    "found_paths": t.get("found_paths", [])
                }
                for t in tools if t["installed"]
            ]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "tools": []
        }


def backup_files(file_paths: List[str], source_ai: str) -> Dict:
    """备份选中的文件到 U 盘"""
    capture_dir = get_capture_dir() / source_ai
    capture_dir.mkdir(parents=True, exist_ok=True)
    
    db = get_db_path()
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    
    # 获取主机名
    host_computer = os.environ.get("COMPUTERNAME", os.environ.get("HOSTNAME", "unknown"))
    capture_id = db_insert_capture(host_computer, f"从 {source_ai} 备份 {len(file_paths)} 个文件")
    
    imported = 0
    errors = []
    
    for path_str in file_paths:
        path = Path(path_str)
        if not path.exists():
            errors.append(f"文件不存在: {path_str}")
            continue
        
        try:
            size = path.stat().st_size
            modified = datetime.fromtimestamp(path.stat().st_mtime).isoformat()
            
            # 复制文件
            dest_path = capture_dir / path.name
            counter = 1
            while dest_path.exists():
                dest_path = capture_dir / f"{path.stem}_{counter}{path.suffix}"
                counter += 1
            
            import shutil
            shutil.copy2(path, dest_path)
            
            # 计算 hash
            with open(dest_path, "rb") as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()[:16]
            
            # 读取预览
            try:
                with open(dest_path, "r", encoding="utf-8", errors="ignore") as f:
                    preview = f.read(200)
            except Exception:
                preview = ""
            
            # 写入数据库
            cur.execute("""
                INSERT INTO files 
                (source_ai, original_path, file_name, relative_path, size_bytes, modified_at, captured_at, hash, content_preview)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                source_ai,
                str(path),
                path.name,
                str(dest_path),
                size,
                modified,
                datetime.now().isoformat(),
                file_hash,
                preview
            ))
            
            imported += 1
            
        except Exception as e:
            errors.append(f"处理失败 {path.name}: {str(e)}")
    
    conn.commit()
    conn.close()
    
    return {
        "success": imported > 0,
        "imported": imported,
        "total": len(file_paths),
        "errors": errors,
        "capture_id": capture_id
    }


def get_file_content(relative_path: str) -> Dict:
    """读取文件内容"""
    drive_root = get_drive_root()
    file_path = drive_root / relative_path
    
    if not file_path.exists():
        return {"success": False, "error": "文件不存在"}
    
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        return {
            "success": True,
            "content": content,
            "path": str(file_path),
            "size": file_path.stat().st_size
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================================
# API Handler
# ============================================================================

class BrainDumpHandler(SimpleHTTPRequestHandler):
    """HTTP 请求处理器"""
    
    def __init__(self, *args, **kwargs):
        # 设置静态文件目录
        static_dir = SCRIPT_DIR / "ui" / "static"
        template_dir = SCRIPT_DIR / "ui_templates"
        
        self.static_dir = static_dir
        self.template_dir = template_dir
        
        super().__init__(*args, directory=str(static_dir), **kwargs)
    
    def do_GET(self):
        """处理 GET 请求"""
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == "/" or path == "/index.html":
            self.serve_index()
        elif path.startswith("/api/stats"):
            self.send_json(db_get_stats())
        elif path.startswith("/api/files"):
            params = parse_qs(parsed.query)
            source = params.get("source", [None])[0]
            self.send_json({"success": True, "files": db_get_files(source_ai=source if source else None)})
        elif path.startswith("/api/captures"):
            self.send_json({"success": True, "captures": db_get_captures()})
        elif path.startswith("/api/detect"):
            self.send_json(detect_host_tools())
        elif path.startswith("/api/file/"):
            # /api/file/<relative_path>
            file_rel = path[10:]  # 去掉 "/api/file/"
            self.send_json(get_file_content(file_rel))
        else:
            super().do_GET()
    
    def do_POST(self):
        """处理 POST 请求"""
        parsed = urlparse(self.path)
        path = parsed.path
        
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        
        try:
            data = json.loads(body) if body else {}
        except Exception:
            data = {}
        
        if path == "/api/scan":
            tools = data.get("tools", None)
            result = scan_host(tools)
            self.send_json(result)
        
        elif path == "/api/backup":
            file_paths = data.get("files", [])
            source_ai = data.get("source", "unknown")
            result = backup_files(file_paths, source_ai)
            self.send_json(result)
        
        else:
            self.send_json({"success": False, "error": "Unknown endpoint"}, status=404)
    
    def serve_index(self):
        """服务 index.html"""
        index_path = self.static_dir / "index.html"
        if index_path.exists():
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            with open(index_path, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404, "index.html not found")
    
    def send_json(self, data: Dict, status: int = 200):
        """发送 JSON 响应"""
        self.send_response(status)
        self.send_header("Content-type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"[BrainDump] {args[0]}")


# ============================================================================
# 服务器启动
# ============================================================================

def get_free_port() -> int:
    """获取空闲端口"""
    import socket
    s = socket.socket()
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def start_server(port: int = None):
    """启动服务器"""
    if port is None:
        port = get_free_port()
    
    server = HTTPServer(("127.0.0.1", port), BrainDumpHandler)
    
    print()
    print(f"  ╔{'═'*56}╗")
    print(f"  ║{'':56}║")
    print(f"  ║   🦛  Hippocampus BrainDump  v4.0.0                  ║")
    print(f"  ║   HIPPO USB Edition — 本地 GUI 模式                  ║")
    print(f"  ║{'':56}║")
    print(f"  ╠{'═'*56}╣")
    print(f"  ║   服务器地址: http://127.0.0.1:{port:<24}║")
    print(f"  ║   按 Ctrl+C 停止服务器                               ║")
    print(f"  ║{'':56}║")
    print(f"  ╚{'═'*56}╝")
    print()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[BrainDump] 服务器已停止，感谢使用 Hippocampus！")
        server.shutdown()


# ============================================================================
# 入口
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Hippocampus BrainDump Server (HIPPO USB Edition)")
    parser.add_argument("--port", "-p", type=int, default=None,
                        help="指定端口（默认自动选择）")
    
    args = parser.parse_args()
    start_server(port=args.port)
