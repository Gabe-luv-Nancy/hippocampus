#!/usr/bin/env python3
"""
Hippocampus Analyzer Module
===========================
本地 AI 记忆分析模块。

在 U 盘上运行，使用内嵌的轻量模型进行：
- 记忆文件索引和检索
- 记忆内容摘要
- 知识图谱构建
- 关联分析

依赖：
- SQLite（内置）
- 可选：Ollama / LM Studio 本地模型
"""

import os
import re
import json
import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import Counter

# ============================================================================
# 配置
# ============================================================================

DEFAULT_CONFIG = {
    "db_path": "./db/hippocampus.db",
    "capture_dir": "./capture",
    "output_dir": "./output",
    "model_provider": "local",  # local | ollama | lmstudio
    "model_name": "qwen2.5-7b",
    "embedding_model": "nomic-embed-text",
    "chunk_size": 512,
    "chunk_overlap": 50,
}


# ============================================================================
# 向量化 & 检索
# ============================================================================

class SimpleVectorDB:
    """
    简易向量数据库（基于 TF-IDF + 关键词匹配）
    
    对于没有本地模型的环境，提供基础的语义检索能力。
    未来可扩展支持 ChromaDB / FAISS / sqlite-vss
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 文档表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_id TEXT UNIQUE NOT NULL,
                source TEXT NOT NULL,
                file_path TEXT,
                content TEXT NOT NULL,
                chunk_index INTEGER DEFAULT 0,
                keywords TEXT,
                vector_id TEXT,
                created_at TEXT NOT NULL
            )
        ''')
        
        # 向量表（预留）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vectors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_id TEXT NOT NULL,
                chunk_text TEXT NOT NULL,
                vector BLOB,
                FOREIGN KEY (doc_id) REFERENCES documents(doc_id)
            )
        ''')
        
        # 索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_doc_source ON documents(source)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_doc_keywords ON documents(keywords)')
        
        conn.commit()
        conn.close()
    
    def add_document(self, doc_id: str, source: str, content: str, file_path: str = None):
        """添加文档"""
        keywords = self._extract_keywords(content)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO documents (doc_id, source, file_path, content, keywords, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (doc_id, source, file_path, content, ",".join(keywords), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return doc_id
    
    def search(self, query: str, limit: int = 10, sources: List[str] = None) -> List[Dict]:
        """
        搜索文档
        
        Args:
            query: 查询文本
            limit: 返回数量
            sources: 限定来源
            
        Returns:
            [{doc_id, source, content, score}]
        """
        query_keywords = set(self._extract_keywords(query))
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        sql = "SELECT * FROM documents WHERE 1=1"
        params = []
        
        if sources:
            placeholders = ','.join(['?' for _ in sources])
            sql += f" AND source IN ({placeholders})"
            params.extend(sources)
        
        cursor.execute(sql, params)
        results = []
        
        for row in cursor.fetchall():
            doc_keywords = set(row['keywords'].split(',')) if row['keywords'] else set()
            score = len(query_keywords & doc_keywords) / max(len(query_keywords), 1)
            
            if score > 0:
                results.append({
                    "doc_id": row['doc_id'],
                    "source": row['source'],
                    "file_path": row['file_path'],
                    "content": row['content'],
                    "score": score,
                    "keywords": row['keywords']
                })
        
        conn.close()
        
        # 按分数排序
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 停用词
        stopwords = {
            '的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
            '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好',
            'this', 'that', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'
        }
        
        words = re.findall(r'[\w]+', text.lower())
        filtered = [w for w in words if len(w) > 1 and w not in stopwords]
        
        # 词频统计
        freq = Counter(filtered)
        return [w for w, _ in freq.most_common(20)]


# ============================================================================
# 分析引擎
# ============================================================================

class Analyzer:
    """记忆分析引擎"""
    
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        config = DEFAULT_CONFIG.copy()
        config["db_path"] = str(self.base_dir / config["db_path"])
        config["capture_dir"] = str(self.base_dir / config["capture_dir"])
        config["output_dir"] = str(self.base_dir / config["output_dir"])
        
        self.db = SimpleVectorDB(config["db_path"])
        self.config = config
        
        # 确保输出目录存在
        Path(config["output_dir"]).mkdir(parents=True, exist_ok=True)
    
    def index_captured_files(self) -> Dict[str, Any]:
        """
        为抓取的文件建立索引
        
        Returns:
            索引结果统计
        """
        capture_dir = Path(self.config["capture_dir"])
        
        if not capture_dir.exists():
            return {"error": f"Capture directory not found: {capture_dir}"}
        
        stats = {
            "total": 0,
            "by_source": {},
            "errors": []
        }
        
        # 遍历抓取目录
        for ai_dir in capture_dir.iterdir():
            if not ai_dir.is_dir():
                continue
            
            source = ai_dir.name
            stats["by_source"][source] = 0
            
            for file_path in ai_dir.rglob("*"):
                if not file_path.is_file():
                    continue
                
                # 只处理文本文件
                if file_path.suffix.lower() in ['.md', '.txt', '.json', '.yaml', '.yml']:
                    try:
                        content = file_path.read_text(encoding='utf-8', errors='ignore')
                        
                        # 生成 doc_id
                        doc_id = hashlib.md5(
                            f"{source}:{file_path.name}".encode()
                        ).hexdigest()[:12]
                        
                        self.db.add_document(
                            doc_id=doc_id,
                            source=source,
                            content=content[:5000],  # 限制长度
                            file_path=str(file_path)
                        )
                        
                        stats["total"] += 1
                        stats["by_source"][source] += 1
                        
                    except Exception as e:
                        stats["errors"].append({
                            "file": str(file_path),
                            "error": str(e)
                        })
        
        return stats
    
    def query(self, query: str, sources: List[str] = None) -> List[Dict]:
        """
        查询记忆
        
        Args:
            query: 查询文本
            sources: 限定来源（AI 类型）
            
        Returns:
            相关记忆列表
        """
        return self.db.search(query, limit=20, sources=sources)
    
    def generate_summary(self) -> Dict[str, Any]:
        """
        生成记忆摘要报告
        
        Returns:
            摘要数据
        """
        summary = {
            "generated_at": datetime.now().isoformat(),
            "total_memories": 0,
            "by_source": {},
            "top_keywords": [],
            "recent_memories": []
        }
        
        conn = sqlite3.connect(self.db.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 总数
        cursor.execute("SELECT COUNT(*) FROM documents")
        summary["total_memories"] = cursor.fetchone()[0]
        
        # 按来源统计
        cursor.execute("""
            SELECT source, COUNT(*) as count 
            FROM documents 
            GROUP BY source 
            ORDER BY count DESC
        """)
        for row in cursor.fetchall():
            summary["by_source"][row['source']] = row['count']
        
        # 关键词统计
        cursor.execute("SELECT keywords FROM documents")
        all_keywords = []
        for row in cursor.fetchall():
            if row['keywords']:
                all_keywords.extend(row['keywords'].split(','))
        
        keyword_freq = Counter(all_keywords)
        summary["top_keywords"] = [
            {"keyword": k, "count": c}
            for k, c in keyword_freq.most_common(20)
        ]
        
        # 最近记忆
        cursor.execute("""
            SELECT doc_id, source, content, keywords, created_at 
            FROM documents 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        for row in cursor.fetchall():
            summary["recent_memories"].append({
                "doc_id": row['doc_id'],
                "source": row['source'],
                "preview": row['content'][:200] + "..." if len(row['content']) > 200 else row['content'],
                "keywords": row['keywords'],
                "created_at": row['created_at']
            })
        
        conn.close()
        return summary
    
    def export_report(self, format: str = "json") -> str:
        """
        导出分析报告
        
        Args:
            format: 报告格式 (json | markdown | html)
            
        Returns:
            报告文件路径
        """
        summary = self.generate_summary()
        output_dir = Path(self.config["output_dir"])
        
        if format == "json":
            report_file = output_dir / f"memory_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
        
        elif format == "markdown":
            report_file = output_dir / f"memory_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            content = f"""# Hippocampus 记忆分析报告

生成时间: {summary['generated_at']}

## 概览

- **记忆总数**: {summary['total_memories']}
- **AI 来源**: {len(summary['by_source'])}

## 按来源统计

"""
            for source, count in summary['by_source'].items():
                content += f"- **{source}**: {count} 条\n"
            
            content += "\n## 热门关键词\n\n"
            for item in summary['top_keywords'][:15]:
                content += f"- {item['keyword']}: {item['count']}\n"
            
            content += "\n## 最近记忆\n\n"
            for mem in summary['recent_memories'][:5]:
                content += f"""### [{mem['source']}] {mem['created_at'][:10]}

{mem['preview']}

_keywords_: {mem['keywords']}

---
"""
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(content)
        
        else:
            report_file = output_dir / f"memory_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
        
        return str(report_file)


# ============================================================================
# 模型接口（预留）
# ============================================================================

class LocalModelInterface:
    """
    本地模型接口
    
    支持：
    - Ollama
    - LM Studio
    - 未来：更多本地模型
    """
    
    def __init__(self, provider: str = "ollama", model: str = "qwen2.5:7b"):
        self.provider = provider
        self.model = model
        self.base_url = self._get_base_url(provider)
    
    def _get_base_url(self, provider: str) -> str:
        """获取 provider 的 API 地址"""
        urls = {
            "ollama": "http://localhost:11434/api",
            "lmstudio": "http://localhost:1234/v1",
        }
        return urls.get(provider, "http://localhost:11434/api")
    
    def is_available(self) -> bool:
        """检查模型服务是否可用"""
        import urllib.request
        try:
            if self.provider == "ollama":
                urllib.request.urlopen(f"{self.base_url}/tags", timeout=2)
            return True
        except:
            return False
    
    def generate(self, prompt: str, context: str = None) -> str:
        """
        生成回答
        
        Args:
            prompt: 用户问题
            context: 上下文记忆
            
        Returns:
            生成文本
        """
        # TODO: 实现实际的 API 调用
        return "[需要配置本地模型服务]"
    
    def embed(self, text: str) -> List[float]:
        """
        生成文本嵌入向量
        
        Returns:
            向量列表
        """
        # TODO: 实现嵌入
        return []


# ============================================================================
# 命令行接口
# ============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Hippocampus Analyzer - 本地记忆分析")
    parser.add_argument("--base", "-b", default=".", help="基础目录（通常是 U 盘根目录）")
    parser.add_argument("--index", "-i", action="store_true", help="索引抓取的文件")
    parser.add_argument("--query", "-q", default=None, help="查询记忆")
    parser.add_argument("--source", "-s", nargs="+", default=None, help="限定来源")
    parser.add_argument("--report", "-r", choices=["json", "markdown", "html"], default="markdown", help="导出报告格式")
    parser.add_argument("--model-check", action="store_true", help="检查本地模型状态")
    
    args = parser.parse_args()
    
    analyzer = Analyzer(base_dir=args.base)
    
    if args.model_check:
        model = LocalModelInterface()
        if model.is_available():
            print(f"✓ 本地模型服务可用 ({model.provider})")
        else:
            print(f"✗ 本地模型服务不可用")
            print(f"  请安装 Ollama (https://ollama.ai) 并运行:")
            print(f"  ollama pull {model.model}")
        return
    
    if args.index:
        print("正在索引记忆文件...")
        result = analyzer.index_captured_files()
        print(f"\n索引完成！")
        print(f"  总文件: {result.get('total', 0)}")
        for source, count in result.get('by_source', {}).items():
            print(f"  - {source}: {count}")
        if result.get('errors'):
            print(f"  错误: {len(result['errors'])}")
        return
    
    if args.query:
        print(f"查询: {args.query}")
        if args.source:
            print(f"限定来源: {args.source}")
        
        results = analyzer.query(args.query, sources=args.source)
        
        if not results:
            print("\n未找到相关记忆")
        else:
            print(f"\n找到 {len(results)} 条相关记忆:\n")
            for i, r in enumerate(results[:5], 1):
                print(f"{i}. [{r['source']}] (匹配度: {r['score']:.2f})")
                print(f"   {r['content'][:150]}...")
                print()
        return
    
    # 默认：生成报告
    print("生成记忆分析报告...")
    report_file = analyzer.export_report(format=args.report)
    print(f"报告已生成: {report_file}")


if __name__ == "__main__":
    main()
