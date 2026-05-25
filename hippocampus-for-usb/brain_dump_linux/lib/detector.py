#!/usr/bin/env python3
"""
Hippocampus Detector v4.0.0
=========================
检测主机上安装的 AI 工具。
"""

import os
import platform
from pathlib import Path
from typing import Dict, List, Optional, Any

# ============================================================================
# AI 工具签名库
# ============================================================================

TOOL_SIGNATURES = {
    "hermes": {
        "name": "hermes",
        "display_name": "Hermes Agent",
        "priority": "high",
        "paths": [
            "~/.hermes/",
        ],
        "marker_files": [
            "~/.hermes/config.yaml",
            "~/.hermes/hermes-agent/",
        ],
        "description": "Hermes Agent AI 助手 (赫墨)"
    },
    "openclaw": {
        "name": "openclaw",
        "display_name": "OpenClaw",
        "priority": "high",
        "paths": [
            "~/.openclaw/",
            "~/.openclaw/workspace/",
        ],
        "marker_files": [
            "~/.openclaw/workspace/MEMORY.md",
            "~/.openclaw/workspace/SOUL.md",
            "~/.openclaw/workspace/USER.md",
        ],
        "description": "OpenClaw AI 助手"
    },
    "doubao": {
        "name": "doubao",
        "display_name": "豆包",
        "priority": "medium",
        "paths": [
            "~/.doubao/",
            "~/.doubao/memory/",
            "~/Library/Application Support/doubao/",
            "~/Library/Application Support/doubao/memory/",
        ],
        "marker_files": [],
        "description": "字节跳动豆包"
    },
    "kimi": {
        "name": "kimi",
        "display_name": "Kimi",
        "priority": "medium",
        "paths": [
            "~/.kimi/",
            "~/.kimi/memory/",
        ],
        "marker_files": [],
        "description": "月之暗面 Kimi"
    },
    "qwen": {
        "name": "qwen",
        "display_name": "通义千问",
        "priority": "medium",
        "paths": [
            "~/.qwen/",
            "~/.qwen/memory/",
        ],
        "marker_files": [],
        "description": "阿里通义千问"
    },
    "yuanbao": {
        "name": "yuanbao",
        "display_name": "元宝",
        "priority": "low",
        "paths": [
            "~/.yuanbao/",
            "~/.yuanbao/memory/",
        ],
        "marker_files": [],
        "description": "腾讯元宝"
    },
    "xfyun": {
        "name": "xfyun",
        "display_name": "讯飞星火",
        "priority": "low",
        "paths": [
            "~/.xfyun/",
            "~/.xfyun/memory/",
        ],
        "marker_files": [],
        "description": "科大讯飞星火"
    },
    "deepseek": {
        "name": "deepseek",
        "display_name": "DeepSeek",
        "priority": "medium",
        "paths": [
            "~/.deepseek/",
            "~/.deepseek/memory/",
        ],
        "marker_files": [],
        "description": "DeepSeek"
    },
    "claude": {
        "name": "claude",
        "display_name": "Claude",
        "priority": "medium",
        "paths": [
            "~/.claude/",
            "~/Library/Application Support/Claude/",
        ],
        "marker_files": [
            "~/.claude/settings.json",
        ],
        "description": "Anthropic Claude"
    },
    "chatgpt": {
        "name": "chatgpt",
        "display_name": "ChatGPT",
        "priority": "medium",
        "paths": [
            "~/Library/Application Support/ChatGPT/",
            "~/AppData/Roaming/ChatGPT/",
            "~/.chatgpt/",
        ],
        "marker_files": [],
        "description": "OpenAI ChatGPT"
    },
    "gemini": {
        "name": "gemini",
        "display_name": "Gemini",
        "priority": "low",
        "paths": [
            "~/.gemini/",
        ],
        "marker_files": [],
        "description": "Google Gemini"
    }
}


# ============================================================================
# 检测器
# ============================================================================

class AIToolDetector:
    """检测主机上安装的 AI 工具"""
    
    def __init__(self):
        self.system = platform.system().lower()
    
    def expand_path(self, path_str: str) -> Optional[Path]:
        """展开路径"""
        try:
            expanded = os.path.expanduser(path_str)
            return Path(expanded)
        except Exception:
            return None
    
    def check_path(self, path: Path) -> bool:
        """检查路径是否存在"""
        try:
            return path.exists()
        except Exception:
            return False
    
    def check_marker_files(self, markers: List[str]) -> List[str]:
        """检查标记文件，返回存在的文件列表"""
        found = []
        for marker_str in markers:
            path = self.expand_path(marker_str)
            if path and self.check_path(path):
                found.append(str(path))
        return found
    
    def detect_one(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """检测单个 AI 工具"""
        if tool_name not in TOOL_SIGNATURES:
            return None
        
        sig = TOOL_SIGNATURES[tool_name]
        
        # 检查所有路径
        found_paths = []
        for path_str in sig["paths"]:
            path = self.expand_path(path_str)
            if path and self.check_path(path):
                found_paths.append(str(path))
        
        # 检查标记文件
        found_markers = self.check_marker_files(sig.get("marker_files", []))
        
        installed = len(found_paths) > 0 or len(found_markers) > 0
        
        return {
            "name": tool_name,
            "display_name": sig.get("display_name", tool_name),
            "description": sig.get("description", ""),
            "priority": sig.get("priority", "medium"),
            "installed": installed,
            "found_paths": found_paths,
            "found_markers": found_markers,
        }
    
    def detect_all(self) -> List[Dict[str, Any]]:
        """检测所有 AI 工具"""
        results = []
        
        for tool_name in TOOL_SIGNATURES:
            result = self.detect_one(tool_name)
            if result:
                results.append(result)
        
        # 按优先级排序
        priority_order = {"high": 0, "medium": 1, "low": 2}
        results.sort(key=lambda x: priority_order.get(x.get("priority", "medium"), 1))
        
        return results
    
    def get_installed_only(self) -> List[Dict[str, Any]]:
        """只返回已安装的工具"""
        return [r for r in self.detect_all() if r.get("installed")]
    
    def print_results(self, results: List[Dict[str, Any]] = None):
        """打印检测结果"""
        if results is None:
            results = self.detect_all()
        
        installed = [r for r in results if r.get("installed")]
        
        print(f"{'='*60}")
        print(f"AI 工具检测报告")
        print(f"{'='*60}")
        print(f"平台: {platform.system()} {platform.release()}")
        print(f"已检测到 {len(installed)}/{len(results)} 个 AI 工具")
        print()
        
        if installed:
            print("已安装：")
            for r in installed:
                print(f"  ✓ {r['display_name']} ({r['name']})")
                for p in r.get("found_paths", [])[:2]:
                    print(f"      {p}")
                if r.get("found_markers"):
                    for m in r.get("found_markers", [])[:2]:
                        print(f"      {m}")
            print()
        
        not_installed = [r for r in results if not r.get("installed")]
        if not_installed:
            print("未检测到：")
            for r in not_installed:
                print(f"  ✗ {r['display_name']} ({r['name']})")


# ============================================================================
# 命令行入口
# ============================================================================

def main():
    detector = AIToolDetector()
    
    import argparse
    parser = argparse.ArgumentParser(description="Hippocampus Detector v4.0.0 - 检测 AI 工具")
    parser.add_argument("--installed", action="store_true",
                        help="只显示已安装的工具")
    parser.add_argument("--json", action="store_true",
                        help="以 JSON 格式输出")
    parser.add_argument("tool_name", nargs="?", default=None,
                        help="只检测指定工具")
    
    args = parser.parse_args()
    
    if args.tool_name:
        result = detector.detect_one(args.tool_name.lower())
        if result:
            if args.json:
                import json
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                status = "已安装" if result.get("installed") else "未安装"
                print(f"{result['display_name']} ({result['name']}): {status}")
                if result.get("found_paths"):
                    print("  路径:")
                    for p in result["found_paths"]:
                        print(f"    {p}")
        else:
            print(f"[错误] 未知工具: {args.tool_name}")
        return
    
    results = detector.detect_all()
    
    if args.installed:
        results = [r for r in results if r.get("installed")]
    
    if args.json:
        import json
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        detector.print_results(results)


if __name__ == "__main__":
    main()
