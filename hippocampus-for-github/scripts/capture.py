#!/usr/bin/env python3
"""
Hippocampus Capture Module
==========================
抓取用户电脑上各路 AI 工具的内存/记忆文件。

支持：
- OpenClaw (workspace/memory/*.md)
- 豆包 (本地存储路径)
- 元宝 (本地存储路径)  
- 讯飞星火 (本地存储路径)
- 其他本地 AI (可配置)

Philosophy: 即使无法解码，也要先保存下来。
"""

import os
import re
import json
import yaml
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# ============================================================================
# 配置
# ============================================================================

# 默认抓取路径配置（按 AI 类型）
DEFAULT_CAPTURE_CONFIGS = {
    "openclaw": {
        "name": "OpenClaw",
        "paths": [
            "~/.openclaw/workspace/MEMORY.md",
            "~/.openclaw/workspace/memory/*.md",
            "~/.openclaw/workspace/AGEN*.md",
            "~/.openclaw/workspace/SOUL.md",
            "~/.openclaw/workspace/USER.md",
        ],
        "priority": 1,  # 1=最高
        "description": "OpenClaw AI 助手记忆文件"
    },
    "doubao": {
        "name": "豆包",
        "paths": [
            "~/.doubao/memory/",
            "~/.local/share/doubao/memory/",
            "~/Library/Application Support/doubao/memory/",
        ],
        "priority": 2,
        "description": "字节跳动豆包 AI"
    },
    "yuanbao": {
        "name": "元宝",
        "paths": [
            "~/.yuanbao/memory/",
            "~/.local/share/yuanbao/memory/",
        ],
        "priority": 2,
        "description": "腾讯元宝 AI"
    },
    "spark": {
        "name": "讯飞星火",
        "paths": [
            "~/.iflytek/spark/memory/",
            "~/Library/Application Support/iflytek/spark/",
        ],
        "priority": 3,
        "description": "科大讯飞星火认知大模型"
    },
    "kimi": {
        "name": "Kimi",
        "paths": [
            "~/.kimi/memory/",
            "~/.local/share/kimi/",
        ],
        "priority": 3,
        "description": "月之暗面 Kimi AI"
    },
    "tongyi": {
        "name": "通义千问",
        "paths": [
            "~/.tongyi/memory/",
            "~/.local/share/tongyi/",
        ],
        "priority": 3,
        "description": "阿里通义千问"
    },
    "deepseek": {
        "name": "DeepSeek",
        "paths": [
            "~/.deepseek/memory/",
            "~/.config/deepseek/",
        ],
        "priority": 3,
        "description": "深度求索 DeepSeek"
    }
}

# 文件类型优先级
FILE_PRIORITY = {
    ".md": 1,   # Markdown 记忆文件 - 最高
    ".json": 2,  # JSON 配置
    ".yaml": 2,
    ".yml": 2,
    ".txt": 3,   # 文本
    ".db": 4,    # 数据库
    ".sqlite": 4,
    "*": 5       # 其他
}

# 忽略模式
IGNORE_PATTERNS = [
    "node_modules",
    ".git",
    "__pycache__",
    ".cache",
    "Cache",
    "cache",
    "temp",
    "tmp",
    ".tmp"
]


# ============================================================================
# 抓取引擎
# ============================================================================

class CaptureEngine:
    """AI 记忆抓取引擎"""
    
    def __init__(self, output_dir: str = "./capture", config_file: str = None):
        """
        初始化抓取引擎
        
        Args:
            output_dir: 抓取输出目录（通常是 U 盘的 capture 目录）
            config_file: 自定义配置文件路径
        """
        self.output_dir = Path(output_dir)
        self.config_file = config_file
        self.configs = self._load_configs()
        self.results = []
        
    def _load_configs(self) -> Dict:
        """加载配置"""
        configs = DEFAULT_CAPTURE_CONFIGS.copy()
        
        # 如果有自定义配置文件，合并
        if self.config_file and Path(self.config_file).exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                custom = yaml.safe_load(f)
                if custom:
                    configs.update(custom)
        
        return configs
    
    def _expand_path(self, path: str) -> List[Path]:
        """展开路径，支持 ~ 和通配符"""
        expanded = os.path.expanduser(path)
        
        # 处理通配符
        if '*' in expanded:
            import glob
            return [Path(p) for p in glob.glob(expanded)]
        else:
            return [Path(expanded)] if Path(expanded).exists() else []
    
    def _should_ignore(self, path: Path) -> bool:
        """检查是否应该忽略"""
        path_str = str(path)
        for pattern in IGNORE_PATTERNS:
            if pattern in path_str:
                return True
        return False
    
    def _get_file_priority(self, path: Path) -> int:
        """获取文件优先级"""
        suffix = path.suffix.lower()
        return FILE_PRIORITY.get(suffix, FILE_PRIORITY["*"])
    
    def capture_single(self, ai_type: str, force: bool = False) -> Dict[str, Any]:
        """
        抓取单个 AI 类型的记忆文件
        
        Args:
            ai_type: AI 类型 key
            force: 是否强制覆盖已存在的文件
            
        Returns:
            抓取结果字典
        """
        if ai_type not in self.configs:
            return {"success": False, "error": f"Unknown AI type: {ai_type}"}
        
        config = self.configs[ai_type]
        result = {
            "ai_type": ai_type,
            "name": config["name"],
            "captured": [],
            "skipped": [],
            "errors": [],
            "total_size": 0,
            "files_count": 0
        }
        
        for path_pattern in config.get("paths", []):
            for file_path in self._expand_path(path_pattern):
                if self._should_ignore(file_path):
                    continue
                    
                try:
                    if file_path.is_file():
                        # 复制文件
                        dest_dir = self.output_dir / ai_type / file_path.parent.name
                        dest_dir.mkdir(parents=True, exist_ok=True)
                        
                        dest_file = dest_dir / file_path.name
                        
                        # 检查是否已存在
                        if dest_file.exists() and not force:
                            # 检查 mtime
                            if dest_file.stat().st_mtime >= file_path.stat().st_mtime:
                                result["skipped"].append(str(file_path))
                                continue
                        
                        # 复制
                        shutil.copy2(file_path, dest_file)
                        
                        size = file_path.stat().st_size
                        result["captured"].append({
                            "source": str(file_path),
                            "dest": str(dest_file),
                            "size": size,
                            "mtime": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                        })
                        result["total_size"] += size
                        result["files_count"] += 1
                        
                except Exception as e:
                    result["errors"].append({
                        "path": str(file_path),
                        "error": str(e)
                    })
        
        result["success"] = len(result["errors"]) == 0
        self.results.append(result)
        return result
    
    def capture_all(self, force: bool = False) -> Dict[str, Any]:
        """
        抓取所有配置的 AI 记忆文件
        
        Args:
            force: 是否强制覆盖
            
        Returns:
            汇总结果
        """
        summary = {
            "total_captured": 0,
            "total_skipped": 0,
            "total_errors": 0,
            "total_size": 0,
            "by_ai": []
        }
        
        # 按优先级排序
        sorted_types = sorted(
            self.configs.items(),
            key=lambda x: x[1].get("priority", 99)
        )
        
        for ai_type, config in sorted_types:
            result = self.capture_single(ai_type, force=force)
            summary["total_captured"] += len(result["captured"])
            summary["total_skipped"] += len(result["skipped"])
            summary["total_errors"] += len(result["errors"])
            summary["total_size"] += result["total_size"]
            summary["by_ai"].append({
                "name": config["name"],
                "captured": len(result["captured"]),
                "errors": len(result["errors"])
            })
        
        return summary
    
    def generate_manifest(self) -> str:
        """生成抓取清单"""
        manifest = {
            "generated_at": datetime.now().isoformat(),
            "output_dir": str(self.output_dir),
            "configs_count": len(self.configs),
            "results": self.results
        }
        
        manifest_file = self.output_dir / "manifest.json"
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        return str(manifest_file)


# ============================================================================
# 路径扫描器
# ============================================================================

class PathScanner:
    """扫描系统中的 AI 记忆文件"""
    
    @staticmethod
    def scan_common_locations() -> Dict[str, List[str]]:
        """
        扫描常见 AI 工具的存储位置
        
        Returns:
            {ai_type: [found_paths]}
        """
        results = {}
        
        for ai_type, config in DEFAULT_CAPTURE_CONFIGS.items():
            found = []
            for path_pattern in config.get("paths", []):
                for path in PathScanner._expand_path_safe(path_pattern):
                    if path.exists():
                        found.append(str(path))
            if found:
                results[ai_type] = found
        
        return results
    
    @staticmethod
    def _expand_path_safe(path: str) -> List[Path]:
        """安全展开路径"""
        try:
            expanded = os.path.expanduser(path)
            if '*' in expanded:
                import glob
                return [Path(p) for p in glob.glob(expanded)]
            else:
                return [Path(expanded)]
        except:
            return []
    
    @staticmethod
    def detect_ai_types() -> List[Dict[str, str]]:
        """
        检测系统中安装了哪些 AI 工具
        
        Returns:
            [{"type": "openclaw", "name": "OpenClaw", "detected": True, "paths": [...]}]
        """
        detected = []
        locations = PathScanner.scan_common_locations()
        
        for ai_type, config in DEFAULT_CAPTURE_CONFIGS.items():
            item = {
                "type": ai_type,
                "name": config["name"],
                "detected": ai_type in locations,
                "paths": locations.get(ai_type, [])
            }
            detected.append(item)
        
        return detected


# ============================================================================
# 命令行接口
# ============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Hippocampus Capture - AI 记忆抓取工具")
    parser.add_argument("--output", "-o", default="./capture", help="输出目录")
    parser.add_argument("--config", "-c", default=None, help="自定义配置文件")
    parser.add_argument("--ai", "-a", default=None, help="只抓取指定 AI 类型")
    parser.add_argument("--force", "-f", action="store_true", help="强制覆盖已存在的文件")
    parser.add_argument("--scan", "-s", action="store_true", help="只扫描，不抓取")
    parser.add_argument("--list", "-l", action="store_true", help="列出支持的 AI 类型")
    
    args = parser.parse_args()
    
    if args.list:
        print("支持的 AI 类型：")
        for ai_type, config in DEFAULT_CAPTURE_CONFIGS.items():
            print(f"  {ai_type}: {config['name']} - {config['description']}")
        return
    
    if args.scan:
        print("扫描系统中已安装的 AI 工具...")
        detected = PathScanner.detect_ai_types()
        for item in detected:
            status = "✓ 已检测" if item["detected"] else "✗ 未检测"
            print(f"\n{item['name']} ({status}):")
            if item["paths"]:
                for p in item["paths"]:
                    print(f"  - {p}")
        return
    
    # 创建抓取引擎
    engine = CaptureEngine(output_dir=args.output, config_file=args.config)
    
    if args.ai:
        # 抓取单个
        print(f"抓取 {args.ai} 记忆文件...")
        result = engine.capture_single(args.ai, force=args.force)
    else:
        # 抓取全部
        print("抓取所有 AI 记忆文件...")
        result = engine.capture_all(force=args.force)
    
    # 输出结果
    print("\n" + "=" * 50)
    if "total_captured" in result:
        print(f"抓取完成！")
        print(f"  新文件: {result['total_captured']}")
        print(f"  跳过: {result['total_skipped']}")
        print(f"  错误: {result['total_errors']}")
        print(f"  总大小: {result['total_size'] / 1024:.1f} KB")
        
        print("\n按 AI 类型：")
        for item in result.get("by_ai", []):
            print(f"  {item['name']}: {item['captured']} 文件")
    else:
        print(f"  抓取 {result['name']}:")
        print(f"  新文件: {len(result['captured'])}")
        print(f"  跳过: {len(result['skipped'])}")
        print(f"  错误: {len(result['errors'])}")
    
    # 生成清单
    manifest = engine.generate_manifest()
    print(f"\n清单已生成: {manifest}")


if __name__ == "__main__":
    main()
