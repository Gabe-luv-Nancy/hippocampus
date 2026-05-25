#!/usr/bin/env python3
"""
Hippocampus Rules Engine v4.0.0
=============================
规则匹配：判断文件是否为'记忆文件'。
"""

import os
import re
import fnmatch
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import IntEnum


class Confidence(IntEnum):
    """匹配置信度"""
    REJECT = 0      # 明确排除
    LOW = 1         # 低置信度（通用匹配）
    MEDIUM = 2      # 中置信度（工具路径匹配）
    HIGH = 3        # 高置信度（精确路径匹配）


@dataclass
class MatchResult:
    """匹配结果"""
    matched: bool
    confidence: Confidence
    source: str
    reason: str
    rule_name: str = ""


@dataclass
class Rule:
    """规则定义"""
    name: str
    path_pattern: str = ""
    exclude_paths: List[str] = None
    exclude_names: List[str] = None
    confidence: Confidence = Confidence.LOW
    source: str = "generic"
    require_content_match: List[str] = None
    min_size: int = 0
    max_size: int = 10 * 1024 * 1024  # 10MB
    
    def __post_init__(self):
        if self.exclude_paths is None:
            self.exclude_paths = []
        if self.exclude_names is None:
            self.exclude_names = []
        if self.require_content_match is None:
            self.require_content_match = []


# ============================================================================
# 内容特征关键词
# ============================================================================

MEMORY_KEYWORDS = [
    "memory", "remember", "recall", "note", "log",
    "chronicle", "monograph", "diary", "journal",
    "checkpoint", "backup", "record", "history",
    "thought", "idea", "plan", "todo", "task",
]

CODE_KEYWORDS = [
    "import", "def ", "class ", "function", "const ",
    "package", "module", "script", "#!/",
]

EXCLUDE_INDICATORS = [
    "node_modules", ".git", "__pycache__", ".venv",
    "dist", "build", "cache", ".cache",
    "package-lock", "yarn.lock", "poetry.lock",
]


# ============================================================================
# 规则引擎
# ============================================================================

class RulesEngine:
    """规则匹配引擎"""
    
    def __init__(self, rules: List[Dict] = None):
        self.rules: List[Rule] = []
        if rules:
            self.load_rules(rules)
        else:
            self._load_default_rules()
    
    def _load_default_rules(self):
        """加载默认规则"""
        # 高置信度：OpenClaw 精确路径
        self.rules.append(Rule(
            name="openclaw_memory_dir",
            path_pattern="~/.openclaw/workspace/memory/**/*.md",
            confidence=Confidence.HIGH,
            source="openclaw"
        ))
        self.rules.append(Rule(
            name="openclaw_root_md",
            path_pattern="~/.openclaw/workspace/*.md",
            confidence=Confidence.MEDIUM,
            source="openclaw"
        ))
        
        # 中置信度：AI 工具通用 memory 路径
        self.rules.append(Rule(
            name="ai_memory_dir",
            path_pattern="~/.{}/memory/**/*.md",
            confidence=Confidence.MEDIUM,
            source="ai_memory"
        ))
        
        # 低置信度：任何 .md 文件（需要内容验证）
        self.rules.append(Rule(
            name="generic_markdown",
            path_pattern="**/*.md",
            confidence=Confidence.LOW,
            source="generic",
            exclude_paths=[
                "**/node_modules/**",
                "**/.git/**",
                "**/dist/**",
                "**/build/**",
                "**/__pycache__/**",
                "**/.venv/**",
                "**/venv/**",
            ],
            exclude_names=[
                "package-lock.json",
                "yarn.lock",
                "*.lock",
                "*.log",
            ],
            require_content_match=MEMORY_KEYWORDS,
        ))
    
    def load_rules(self, rules_config: List[Dict]):
        """从配置加载规则"""
        for r in rules_config:
            rule = Rule(
                name=r.get("name", "unnamed"),
                path_pattern=r.get("path_pattern", ""),
                exclude_paths=r.get("exclude_paths", []),
                exclude_names=r.get("exclude_names", []),
                confidence=Confidence(r.get("confidence", 1)),
                source=r.get("source", "generic"),
                require_content_match=r.get("require_content_match", []),
                min_size=r.get("min_size", 0),
                max_size=r.get("max_size", 10 * 1024 * 1024),
            )
            self.rules.append(rule)
    
    def _expand_path_pattern(self, pattern: str) -> str:
        """展开路径模式"""
        return os.path.expanduser(pattern)
    
    def _match_path_pattern(self, path: Path, pattern: str) -> bool:
        """匹配路径模式"""
        path_str = str(path)
        pattern_expanded = self._expand_path_pattern(pattern)
        
        # 处理动态占位符（如 ~/.{}/memory/**/*.md）
        if "{}" in pattern_expanded:
            # 尝试匹配任何 AI 工具名称
            for tool in ["openclaw", "doubao", "kimi", "qwen", "yuanbao", "xfyun", "deepseek", "claude"]:
                expanded = pattern_expanded.format(tool)
                if fnmatch.fnmatch(path_str, expanded):
                    return True
            return False
        
        # 普通通配符匹配
        if "*" in pattern_expanded:
            return fnmatch.fnmatch(path_str, pattern_expanded)
        
        # 精确子串匹配
        return pattern_expanded in path_str
    
    def _match_exclude(self, path: Path) -> bool:
        """检查是否在排除路径中"""
        path_str = str(path)
        name = path.name
        
        for pattern in EXCLUDE_INDICATORS:
            if pattern in path_str:
                return True
        
        return False
    
    def _check_content_keywords(self, path: Path, keywords: List[str]) -> bool:
        """检查文件内容是否包含关键词"""
        if not keywords:
            return True
        
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(4096).lower()  # 只读前 4KB
                content_sample = content
        except Exception:
            return False
        
        # 至少匹配一个关键词
        for kw in keywords:
            if kw.lower() in content_sample:
                return True
        
        return False
    
    def match(self, path: Path, content: str = None) -> MatchResult:
        """判断文件是否匹配记忆文件规则"""
        
        # 基础检查：文件存在
        if not path.exists():
            return MatchResult(
                matched=False,
                confidence=Confidence.REJECT,
                source="",
                reason="文件不存在"
            )
        
        # 排除路径检查
        if self._match_exclude(path):
            return MatchResult(
                matched=False,
                confidence=Confidence.REJECT,
                source="",
                reason="路径在排除列表中"
            )
        
        # 文件大小检查
        try:
            size = path.stat().st_size
        except Exception:
            size = 0
        
        # 按置信度从高到低匹配
        sorted_rules = sorted(self.rules, key=lambda r: r.confidence, reverse=True)
        
        for rule in sorted_rules:
            # 路径模式匹配
            if rule.path_pattern and not self._match_path_pattern(path, rule.path_pattern):
                continue
            
            # 排除路径检查
            excluded = False
            for exc_pattern in rule.exclude_paths:
                exc_expanded = os.path.expanduser(exc_pattern)
                if fnmatch.fnmatch(str(path), exc_expanded):
                    excluded = True
                    break
            if excluded:
                continue
            
            # 排除文件名检查
            for exc_name in rule.exclude_names:
                if fnmatch.fnmatch(path.name, exc_name):
                    excluded = True
                    break
            if excluded:
                continue
            
            # 文件大小检查
            if size < rule.min_size or size > rule.max_size:
                continue
            
            # 内容关键词检查
            if rule.require_content_match:
                if not self._check_content_keywords(path, rule.require_content_match):
                    continue
            
            # 匹配成功
            return MatchResult(
                matched=True,
                confidence=rule.confidence,
                source=rule.source,
                reason=f"规则 {rule.name} 匹配",
                rule_name=rule.name
            )
        
        # 未匹配任何规则
        return MatchResult(
            matched=False,
            confidence=Confidence.REJECT,
            source="",
            reason="不符合任何记忆文件规则"
        )
    
    def match_batch(self, paths: List[Path]) -> Dict[Path, MatchResult]:
        """批量匹配"""
        return {p: self.match(p) for p in paths}
    
    def filter_matched(self, paths: List[Path]) -> List[Tuple[Path, MatchResult]]:
        """过滤出匹配的文件"""
        results = []
        for p in paths:
            result = self.match(p)
            if result.matched:
                results.append((p, result))
        return results
    
    def get_statistics(self, results: Dict[Path, MatchResult]) -> Dict[str, Any]:
        """获取统计信息"""
        total = len(results)
        matched = sum(1 for r in results.values() if r.matched)
        by_confidence = {c.name: 0 for c in Confidence if c != Confidence.REJECT}
        by_source: Dict[str, int] = {}
        
        for path, result in results.items():
            if result.matched:
                by_confidence[result.confidence.name] += 1
                by_source[result.source] = by_source.get(result.source, 0) + 1
        
        return {
            "total": total,
            "matched": matched,
            "rejected": total - matched,
            "by_confidence": by_confidence,
            "by_source": by_source,
        }


# ============================================================================
# 快速匹配函数
# ============================================================================

def quick_match(path_str: str) -> MatchResult:
    """快速匹配（不依赖类实例）"""
    engine = RulesEngine()
    path = Path(os.path.expanduser(path_str))
    return engine.match(path)


# ============================================================================
# 命令行入口
# ============================================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Hippocampus Rules Engine v4.0.0")
    parser.add_argument("path", nargs="?", help="要检查的文件路径")
    parser.add_argument("--batch", "-b", action="store_true", help="批量模式，每行一个路径")
    parser.add_argument("--stats", "-s", action="store_true", help="显示统计信息")
    
    args = parser.parse_args()
    
    engine = RulesEngine()
    
    if args.batch:
        import sys
        paths = [Path(line.strip()) for line in sys.stdin if line.strip()]
        results = engine.match_batch(paths)
        matched = [(p, r) for p, r in results.items() if r.matched]
        print(f"匹配: {len(matched)}/{len(paths)}")
        for p, r in matched:
            print(f"  [{r.confidence.name}] {r.source:12} {p}")
        if args.stats:
            stats = engine.get_statistics(results)
            print(f"\n统计: {stats}")
        return
    
    if args.path:
        path = Path(os.path.expanduser(args.path))
        result = engine.match(path)
        print(f"路径: {path}")
        print(f"匹配: {'是' if result.matched else '否'}")
        print(f"置信度: {result.confidence.name}")
        print(f"来源: {result.source}")
        print(f"原因: {result.reason}")
        return
    
    # 无参数：显示规则列表
    print(f"{'='*60}")
    print(f"Hippocampus Rules Engine v4.0.0")
    print(f"{'='*60}")
    print(f"当前规则数: {len(engine.rules)}")
    print()
    for rule in engine.rules:
        print(f"  [{rule.confidence.name:6}] {rule.name}")
        print(f"           pattern: {rule.path_pattern or '(无)'}")


if __name__ == "__main__":
    main()
