#!/usr/bin/env python3
"""
Hippocampus V2 - Brain-Inspired Memory System
==============================================
Merged version: Chronicle + Monograph with rich metadata
- Dual storage: SQLite index + Markdown files
- Keyword extraction + association generation
- File organization + analysis
- User-configurable via USER_CONFIG.md

Uses built-in sqlite3 - no external dependencies.
"""

import os
import re
import json
import yaml
import time
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import Counter

# ============================================================================
# Configuration - Read from USER_CONFIG.md
# ============================================================================

SKILL_DIR = Path(__file__).parent.parent
USER_CONFIG_FILE = SKILL_DIR / "USER_CONFIG.md"
CONFIG_CACHE_FILE = SKILL_DIR / "config.json"

# Default configuration (fallback)
DEFAULT_VALUES = {
    "ROUND_THRESHOLD": 25,
    "TIME_HOURS": 6,
    "TOKEN_THRESHOLD": 10000,
    "BASE_PATH": "./assets/hippocampus",
    "CHRONICLE_DIR": "chronicle",
    "MONOGRAPH_DIR": "monograph",
    "INDEX_DIR": "index",
    "BEFORE_ANSWER": "",  # Special: memory loaded before each response
    "AFTER_ANSWER": "",   # Special: memory processed after each response
    "FILE_ORG_ENABLED": True,
    "FILE_ORG_AUTO_MOVE": False,
    "FILE_SCAN_PATHS": ["./workspace"],
    "FILE_EXCLUDE_PATHS": [".openclaw", "node_modules", ".git"],
    "KEYWORD_COUNT": 20,
    "ASSOCIATION_DEPTH": 3,
    "AUTO_SAVE": True
}

def parse_bool(value: str) -> bool:
    """Parse boolean from string"""
    return value.strip().lower() in ['true', 'yes', '1', 'on']

def parse_list(value: str) -> List[str]:
    """Parse list from comma-separated string"""
    return [item.strip() for item in value.split(',') if item.strip()]

def load_user_config() -> Dict:
    """Load configuration from USER_CONFIG.md"""
    config = DEFAULT_VALUES.copy()
    
    if not USER_CONFIG_FILE.exists():
        # Generate default USER_CONFIG.md
        save_user_config(config)
        return config
    
    # Parse USER_CONFIG.md
    with open(USER_CONFIG_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            if key in config:
                # Type inference
                if key in ['ROUND_THRESHOLD', 'TIME_HOURS', 'TOKEN_THRESHOLD', 
                           'KEYWORD_COUNT', 'ASSOCIATION_DEPTH']:
                    config[key] = int(value)
                elif key in ['FILE_ORG_ENABLED', 'FILE_ORG_AUTO_MOVE', 'AUTO_SAVE']:
                    config[key] = parse_bool(value)
                elif key in ['FILE_SCAN_PATHS', 'FILE_EXCLUDE_PATHS']:
                    config[key] = parse_list(value)
                else:
                    config[key] = value
    
    return config

def save_user_config(config: Dict):
    """Save USER_CONFIG.md from dict"""
    lines = [
        "# User Configuration for Hippocampus",
        "#",
        "# IMPORTANT: Edit this file to customize your memory behavior",
        "# After editing, the skill will automatically reload these values",
        "# Format: KEY = VALUE (one per line, no quotes needed)",
        "",
        "# ============================================",
        "# Trigger Settings",
        "# ============================================",
        "",
        f"ROUND_THRESHOLD = {config.get('ROUND_THRESHOLD', 25)}",
        f"TIME_HOURS = {config.get('TIME_HOURS', 6)}",
        f"TOKEN_THRESHOLD = {config.get('TOKEN_THRESHOLD', 10000)}",
        "",
        "# ============================================",
        "# Storage Settings",
        "# ============================================",
        "",
        f"BASE_PATH = {config.get('BASE_PATH', './assets/hippocampus')}",
        f"CHRONICLE_DIR = {config.get('CHRONICLE_DIR', 'chronicle')}",
        f"MONOGRAPH_DIR = {config.get('MONOGRAPH_DIR', 'monograph')}",
        f"INDEX_DIR = {config.get('INDEX_DIR', 'index')}",
        "",
        "# ============================================",
        "# File Organization",
        "# ============================================",
        "",
        f"FILE_ORG_ENABLED = {str(config.get('FILE_ORG_ENABLED', True)).lower()}",
        f"FILE_ORG_AUTO_MOVE = {str(config.get('FILE_ORG_AUTO_MOVE', False)).lower()}",
        f"FILE_SCAN_PATHS = {','.join(config.get('FILE_SCAN_PATHS', ['./workspace']))}",
        f"FILE_EXCLUDE_PATHS = {','.join(config.get('FILE_EXCLUDE_PATHS', ['.openclaw', 'node_modules', '.git']))}",
        "",
        "# ============================================",
        "# Keyword & Association",
        "# ============================================",
        "",
        f"KEYWORD_COUNT = {config.get('KEYWORD_COUNT', 20)}",
        f"ASSOCIATION_DEPTH = {config.get('ASSOCIATION_DEPTH', 3)}",
        "",
        "# ============================================",
        "# Auto-Save",
        "# ============================================",
        "",
        f"AUTO_SAVE = {str(config.get('AUTO_SAVE', True)).lower()}",
    ]
    
    USER_CONFIG_FILE.write_text('\n'.join(lines), encoding='utf-8')

# Lazy load config
_config_cache = None

def get_config() -> Dict:
    """Get current configuration (cached)"""
    global _config_cache
    if _config_cache is None:
        _config_cache = load_user_config()
    return _config_cache

def reload_config():
    """Force reload configuration"""
    global _config_cache
    _config_cache = load_user_config()
    return _config_cache

# ============================================================================
# Path Management
# ============================================================================

def get_base_path() -> Path:
    """Get base storage path"""
    config = get_config()
    base = config.get("BASE_PATH", "./assets/hippocampus")
    if not base.startswith('/'):
        base = SKILL_DIR / base
    return Path(base)

def get_chronicle_path() -> Path:
    """Get chronicle directory"""
    config = get_config()
    name = config.get("CHRONICLE_DIR", "chronicle")
    return get_base_path() / name

def get_monograph_path() -> Path:
    """Get monograph directory"""
    config = get_config()
    name = config.get("MONOGRAPH_DIR", "monograph")
    return get_base_path() / name

def get_index_path() -> Path:
    """Get index directory"""
    config = get_config()
    name = config.get("INDEX_DIR", "index")
    return get_base_path() / name

# ============================================================================
# Special Needs - Before/After Answer Memory
# ============================================================================

def get_before_answer_memory() -> str:
    """Get memory that should be loaded before each answer"""
    config = get_config()
    topic = config.get("BEFORE_ANSWER", "")
    
    if not topic:
        return ""
    
    # Read the monograph content
    safe_topic = re.sub(r'[^\w\-]', '-', topic)
    filepath = get_monograph_path() / f"{safe_topic}.md"
    
    if filepath.exists():
        return filepath.read_text(encoding='utf-8')
    
    return ""

def get_after_answer_memory() -> str:
    """Get memory that should be processed after each answer"""
    config = get_config()
    topic = config.get("AFTER_ANSWER", "")
    
    if not topic:
        return ""
    
    # Read the monograph content
    safe_topic = re.sub(r'[^\w\-]', '-', topic)
    filepath = get_monograph_path() / f"{safe_topic}.md"
    
    if filepath.exists():
        return filepath.read_text(encoding='utf-8')
    
    return ""

def check_special_needs() -> Dict[str, str]:
    """Check and return special needs configuration"""
    config = get_config()
    return {
        "before_answer": config.get("BEFORE_ANSWER", ""),
        "after_answer": config.get("AFTER_ANSWER", "")
    }

def ensure_dirs():
    """Ensure all directories exist"""
    for d in [get_chronicle_path(), get_monograph_path(), get_index_path()]:
        d.mkdir(parents=True, exist_ok=True)
    init_db()

# ============================================================================
# SQLite Database
# ============================================================================

def get_db_path() -> Path:
    """Get SQLite database path"""
    return get_chronicle_path() / "db.sqlite"

def init_db():
    """Initialize database schema"""
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Chronicle index
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chronicle_index (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            date TEXT NOT NULL,
            keywords TEXT,
            content_preview TEXT,
            session_id TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    
    # Monograph index
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS monograph_index (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL UNIQUE,
            file_path TEXT NOT NULL,
            user TEXT,
            creator TEXT DEFAULT 'OpenClaw',
            technical_environment TEXT,
            circumstance_purpose TEXT,
            key_steps TEXT,
            errors_trials TEXT,
            conclusion TEXT,
            directory TEXT,
            keywords TEXT,
            tokens_used INTEGER,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')
    
    # Association table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS associations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_word TEXT NOT NULL,
            to_word TEXT NOT NULL,
            weight REAL DEFAULT 0.5,
            UNIQUE(from_word, to_word)
        )
    ''')
    
    # Indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_chronicle_date ON chronicle_index(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_chronicle_timestamp ON chronicle_index(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_monograph_topic ON monograph_index(topic)')
    
    conn.commit()
    conn.close()

# ============================================================================
# Keyword Extraction
# ============================================================================

class KeywordExtractor:
    """Keyword extractor with enhanced features"""
    
    STOP_WORDS = {
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
        'i', 'you', 'he', 'she', 'it'
    }
    
    QUESTION_WORDS = {'how', 'what', 'why', 'when', 'where', 'which', '?'}
    ERROR_WORDS = {'error', 'fail', 'failed', 'exception', 'bug', 'issue', 'problem'}
    
    def __init__(self):
        config = get_config()
        self.keyword_count = config.get('KEYWORD_COUNT', 20)
    
    def extract(self, text: str) -> Dict[str, Any]:
        """Extract keywords and metadata"""
        words = re.findall(r'[\w]+', text.lower())
        filtered = [w for w in words if w not in self.STOP_WORDS and len(w) > 1]
        freq = Counter(filtered)
        
        return {
            "word_frequency": dict(freq.most_common(self.keyword_count)),
            "questions": self._extract_questions(text),
            "errors": self._extract_errors(text),
            "unique_info": self._extract_unique(text),
            "total_words": len(filtered)
        }
    
    def _extract_questions(self, text: str) -> List[str]:
        questions = []
        for sent in re.split(r'[.!?\n]', text):
            if any(q in sent.lower() for q in self.QUESTION_WORDS):
                if sent.strip():
                    questions.append(sent.strip()[:200])
        return questions[:5]
    
    def _extract_errors(self, text: str) -> List[str]:
        errors = []
        text_lower = text.lower()
        for word in self.ERROR_WORDS:
            if word in text_lower:
                idx = text_lower.find(word)
                start, end = max(0, idx - 30), min(len(text), idx + 50)
                if text[start:end].strip():
                    errors.append(text[start:end].strip())
        return errors[:5]
    
    def _extract_unique(self, text: str) -> List[str]:
        unique = []
        unique.extend(re.findall(r'[/\\][\w\-./\\]+\.\w+', text)[:3])
        unique.extend(re.findall(r'`[^`]+`', text)[:3])
        unique.extend(re.findall(r'\d+\.\d+\.\d+', text)[:3])
        return unique

# ============================================================================
# Association Generator
# ============================================================================

class AssociationGenerator:
    """Association word generator"""
    
    ASSOCIATION_MAP = {
        'python': ['code', 'script', 'execute', 'pip'],
        'cline': ['cli', 'integration', 'call', 'windows'],
        'api': ['http', 'network', 'request', 'timeout'],
        'error': ['fail', 'exception', 'debug', 'issue'],
        'database': ['sql', 'query', 'storage', 'connection'],
        'git': ['version', 'commit', 'branch', 'push'],
        'fail': ['retry', 'error', 'debug', 'solve'],
        'timeout': ['network', 'retry', 'slow'],
        'config': ['setting', 'parameter', 'option'],
        'project': ['develop', 'code', 'task'],
        'develop': ['code', 'test', 'debug'],
    }
    
    def __init__(self):
        config = get_config()
        self.association_depth = config.get('ASSOCIATION_DEPTH', 3)
    
    def generate(self, keywords: Dict[str, int]) -> List[Dict[str, Any]]:
        associations = []
        for word, freq in keywords.items():
            word_lower = word.lower()
            if word_lower in self.ASSOCIATION_MAP:
                for assoc in self.ASSOCIATION_MAP[word_lower][:self.association_depth]:
                    if assoc != word:
                        associations.append({"from": word, "to": assoc, "weight": 0.8})
            if freq > 3:
                associations.append({"from": word, "to": "high_frequency", "weight": min(freq/10, 1.0)})
        
        seen = set()
        unique = []
        for a in associations:
            key = (a['from'], a['to'])
            if key not in seen:
                seen.add(key)
                unique.append(a)
        return unique[:20]

# ============================================================================
# Chronicle Operations
# ============================================================================

def save_chronicle(content: str, session_id: str = None) -> str:
    """Save temporal memory to Chronicle"""
    ensure_dirs()
    config = get_config()
    extractor = KeywordExtractor()
    keywords = extractor.extract(content)
    
    # Filename format: YYYY-MM-DD-HH-mm.md
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
    date = datetime.now().strftime("%Y-%m-%d")
    filename = f"{timestamp}.md"
    filepath = get_chronicle_path() / filename
    
    keyword_str = ",".join(list(keywords["word_frequency"].keys())[:10])
    
    # Build markdown
    md_content = f"""# Chronicle - {date}

## Metadata
- **Timestamp**: {timestamp}
- **Session**: {session_id or 'N/A'}
- **Keywords**: {keyword_str}

## Content
{content}

## Analysis
| Keyword | Frequency |
|---------|-----------|
"""
    for kw, cnt in list(keywords["word_frequency"].items())[:15]:
        md_content += f"| {kw} | {cnt} |\n"
    
    filepath.write_text(md_content, encoding='utf-8')
    
    # Index in SQLite
    conn = sqlite3.connect(str(get_db_path()))
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO chronicle_index 
        (file_name, file_path, timestamp, date, keywords, content_preview, session_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (filename, str(filepath), timestamp, date, keyword_str, content[:200], session_id, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    
    return str(filepath)

def query_chronicle(keyword: str = None, start_date: str = None, end_date: str = None, limit: int = 100) -> List[Dict]:
    """Query Chronicle via SQLite"""
    conn = sqlite3.connect(str(get_db_path()))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = "SELECT * FROM chronicle_index WHERE 1=1"
    params = []
    
    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)
    if keyword:
        query += " AND (keywords LIKE ? OR content_preview LIKE ?)"
        params.extend([f'%{keyword}%', f'%{keyword}%'])
    
    query += f" ORDER BY timestamp DESC LIMIT {limit}"
    cursor.execute(query, params)
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results

# ============================================================================
# Monograph Operations
# ============================================================================

def save_monograph(topic: str, content: str, tokens: int, metadata: Dict = None) -> str:
    """Save important event to Monograph"""
    ensure_dirs()
    extractor = KeywordExtractor()
    keywords = extractor.extract(content)
    
    # Sanitize topic name
    safe_topic = re.sub(r'[^\w\-]', '-', topic)
    filepath = get_monograph_path() / f"{safe_topic}.md"
    
    # Build metadata
    meta = metadata or {}
    keyword_str = ",".join(list(keywords["word_frequency"].keys())[:10])
    
    md_content = f"""# {topic}

## Metadata
- **Created**: {datetime.now().isoformat()}
- **User**: {meta.get('user', '')}
- **Creator**: {meta.get('creator', 'OpenClaw')}
- **Token Usage**: {tokens}
- **Keywords**: {keyword_str}

## Technical Environment
{meta.get('technical_environment', '')}

## Circumstance & Purpose
{meta.get('circumstance_and_purpose', '')}

## Key Steps
{meta.get('key_steps', '')}

## Errors & Trials
{meta.get('errors_and_trials', '')}

## Conclusion
{meta.get('conclusion', '')}

## Directory
{meta.get('directory', '')}

## Full Content
{content}

## Keyword Index
| Keyword | Frequency |
|---------|-----------|
"""
    for kw, cnt in list(keywords["word_frequency"].items())[:20]:
        md_content += f"| {kw} | {cnt} |\n"
    
    md_content += """
## Related Files
<!-- Auto-detected file paths -->

## Cross-References
<!-- Links to other monographs -->
"""
    
    filepath.write_text(md_content, encoding='utf-8')
    
    # Update index
    conn = sqlite3.connect(str(get_db_path()))
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO monograph_index 
        (topic, file_path, user, creator, technical_environment, circumstance_purpose, 
         key_steps, errors_trials, conclusion, directory, keywords, tokens_used, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (topic, str(filepath), meta.get('user', ''), meta.get('creator', 'OpenClaw'),
          meta.get('technical_environment', ''), meta.get('circumstance_and_purpose', ''),
          meta.get('key_steps', ''), meta.get('errors_and_trials', ''), meta.get('conclusion', ''),
          meta.get('directory', ''), keyword_str, tokens, datetime.now().isoformat(), datetime.now().isoformat()))
    conn.commit()
    conn.close()
    
    # Update keyword index files
    _update_keyword_index(safe_topic, keywords["word_frequency"], filepath)
    
    return str(filepath)

def _update_keyword_index(topic: str, keywords: Dict, source_path: Path):
    """Update keyword index files"""
    index_dir = get_index_path()
    index_dir.mkdir(parents=True, exist_ok=True)
    
    for kw in list(keywords.keys())[:10]:
        kw_file = index_dir / f"{kw}.md"
        entry = f"""
## {topic}
- Source: {source_path}
- Updated: {datetime.now().isoformat()}
---
"""
        kw_file.write_text(entry, encoding='utf-8')

def list_monographs() -> List[Dict]:
    """List all monograph topics"""
    conn = sqlite3.connect(str(get_db_path()))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT topic, user, keywords, created_at, updated_at FROM monograph_index ORDER BY updated_at DESC")
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results

# ============================================================================
# File Organization
# ============================================================================

class FileOrganizer:
    """File organizer for memory-related files"""
    
    def __init__(self):
        self.workspace = Path(os.path.expanduser("~/.openclaw/workspace"))
        config = get_config()
        self.enabled = config.get('FILE_ORG_ENABLED', True)
        self.auto_move = config.get('FILE_ORG_AUTO_MOVE', False)
        self.exclude = config.get('FILE_EXCLUDE_PATHS', [".openclaw", "node_modules", ".git"])
    
    def find_related_files(self, memory_content: str) -> List[Dict]:
        if not self.enabled:
            return []
        
        paths = re.findall(r'[/\\]?([\w\-./\\]+\.\w+)', memory_content)
        related = []
        
        for path_str in set(paths):
            for full_path in self.workspace.rglob("*"):
                if full_path.name in path_str or path_str in str(full_path):
                    if full_path.is_file() and not any(ex in str(full_path) for ex in self.exclude):
                        related.append({
                            "path": str(full_path),
                            "name": full_path.name,
                            "size": full_path.stat().st_size,
                            "modified": datetime.fromtimestamp(full_path.stat().st_mtime).isoformat()
                        })
        return related[:10]
    
    def suggest_organization(self, files: List[Dict]) -> str:
        if not files:
            return "No files found that need organization"
        
        by_dir = {}
        for f in files:
            dir_path = str(Path(f['path']).parent)
            if dir_path not in by_dir:
                by_dir[dir_path] = []
            by_dir[dir_path].append(f)
        
        suggestions = "Found the following related files:\n\n"
        for dir_path, file_list in by_dir.items():
            suggestions += f"**Directory**: `{dir_path}`\n"
            for f in file_list:
                suggestions += f"- {f['name']} ({f['size']} bytes)\n"
            suggestions += "\n"
        suggestions += "Would you like to organize them into a unified directory?"
        return suggestions

# ============================================================================
# Analysis
# ============================================================================

def analyze_memory() -> str:
    """Analyze all memory and generate report"""
    ensure_dirs()
    conn = sqlite3.connect(str(get_db_path()))
    cursor = conn.cursor()
    
    # Chronicle stats
    cursor.execute("SELECT COUNT(*), MIN(date), MAX(date) FROM chronicle_index")
    c_count, c_min, c_max = cursor.fetchone()
    
    # Monograph stats
    cursor.execute("SELECT COUNT(*) FROM monograph_index")
    m_count = cursor.fetchone()[0]
    
    # Top keywords
    cursor.execute("SELECT keywords FROM chronicle_index ORDER BY timestamp DESC LIMIT 100")
    kw_text = " ".join([r[0] or "" for r in cursor.fetchall()])
    extractor = KeywordExtractor()
    top_keywords = list(extractor.extract(kw_text)["word_frequency"].items())[:30]
    
    conn.close()
    
    report = f"""# Memory Analysis Report

Generated: {datetime.now().isoformat()}

## Chronicle (Temporal) Statistics
- Total Entries: {c_count}
- Date Range: {c_min or 'N/A'} to {c_max or 'N/A'}

## Monograph (Important Events) Statistics
- Total Topics: {m_count}

## Top Keywords
| Keyword | Count |
|---------|-------|
"""
    for kw, cnt in top_keywords:
        report += f"| {kw} | {cnt} |\n"
    
    report_file = get_base_path() / "analysis.md"
    report_file.write_text(report, encoding='utf-8')
    return str(report_file)

# ============================================================================
# Auto-Save for Cron/Heartbeat
# ============================================================================

def auto_save_from_context(context: Dict = None) -> str:
    """Auto-save triggered by cron/heartbeat"""
    config = get_config()
    
    if not config.get('AUTO_SAVE', True):
        return "Auto-save disabled"
    
    # Get content from context (session history)
    content = ""
    if context and 'content' in context:
        content = context['content']
    
    if not content:
        return "No content to save"
    
    threshold = config.get('TOKEN_THRESHOLD', 10000)
    
    if len(content) > threshold:
        topic = context.get('topic', 'General') if context else 'General'
        save_monograph(topic, content, len(content))
        return f"Saved to Monograph: {topic}"
    else:
        save_chronicle(content)
        return "Saved to Chronicle"

# ============================================================================
# Main Handler
# ============================================================================

class Hippocampus:
    """Main handler for Hippocampus skill"""
    
    def __init__(self):
        self.organizer = FileOrganizer()
        self.current_topic = None
        self.round_count = 0
        self.last_save_time = time.time()
        # Reload config to get latest values
        reload_config()
    
    def process(self, command: str, args: str = "", context: Dict = None) -> str:
        """Process command"""
        context = context or {}
        
        # Reload config for each command (to pick up user changes)
        reload_config()
        
        if command == "new":
            return self._cmd_new(args)
        elif command == "add":
            return self._cmd_add(args)
        elif command == "save":
            return self._cmd_save(context.get("content", ""))
        elif command == "recall":
            return self._cmd_recall(args)
        elif command == "important":
            return self._cmd_important()
        elif command == "search":
            return self._cmd_search(args)
        elif command == "status":
            return self._cmd_status()
        elif command == "config":
            return self._cmd_config(args)
        elif command == "files":
            return self._cmd_files(context.get("content", ""))
        elif command == "query":
            return self._cmd_query(args)
        elif command == "analyze":
            return self._cmd_analyze()
        elif command == "collect":
            return self._cmd_collect(context.get("content", ""))
        elif command == "reload":
            return self._cmd_reload()
        elif command == "init":
            return self._cmd_init()
        elif command == "autocheck":
            return self._cmd_autocheck(context)
        
        # Natural language aliases - map to commands
        elif command in ["setup", "setup-all", "setup memory", "configure memory", "enable auto-save"]:
            return self._cmd_setup_all()
        elif command in ["setup-hooks", "configure hooks", "enable hooks"]:
            return self._cmd_setup_hooks()
        elif command in ["sync-memory", "sync to memory", "save to memory", "remember this"]:
            return self._cmd_sync_memory()
        elif command in ["memory", "save memory", "remember"]:
            return self._cmd_save(context.get("content", ""))
        elif command in ["recall memory", "remember"]:
            return self._cmd_recall(args)
        
        # User confirmation handlers - execute after "yes" confirmation
        elif command in ["yes", "confirm", "do it", "execute"]:
            return self._cmd_do_setup(args)
        elif command in ["yes-hooks", "confirm-hooks"]:
            return self._cmd_do_setup_hooks()
        elif command in ["yes-sync", "confirm-sync", "do-sync"]:
            return self._cmd_do_sync_memory()
        else:
            return self._help()
    
    def _cmd_new(self, name: str) -> str:
        if not name:
            return "Please specify topic name, e.g.: /hip new ProjectX"
        self.current_topic = name
        self.round_count = 0
        save_monograph(name, f"# {name}\n\nCreated: {datetime().isoformat()}", 0)
        return f"Created monograph topic: **{name}**"
    
    def _cmd_add(self, content: str) -> str:
        if not self.current_topic:
            return "Please create a topic first: /hip new <name>"
        extractor = KeywordExtractor()
        keywords = extractor.extract(content)
        save_monograph(self.current_topic, content, len(content))
        return f"Content added. Keywords: {len(keywords['word_frequency'])}, Errors: {len(keywords['errors'])}"
    
    def _cmd_save(self, content: str) -> str:
        config = get_config()
        
        if not content:
            return "No content to save"
        
        threshold = config.get('TOKEN_THRESHOLD', 10000)
        
        if len(content) > threshold:
            topic = self.current_topic or "General"
            save_monograph(topic, content, len(content))
            result = f"Saved to Monograph: {topic}"
        else:
            save_chronicle(content)
            result = "Saved to Chronicle"
        
        self.round_count = 0
        self.last_save_time = time.time()
        return result
    
    def _cmd_recall(self, keyword: str) -> str:
        if not keyword:
            results = query_chronicle(limit=5)
            if not results:
                return "No records found"
            report = "## Recent Chronicle Records\n\n"
            for r in results:
                report += f"- **{r['filename']}**: {r['content_preview'][:80]}...\n"
            return report
        
        results = query_chronicle(keyword=keyword, limit=10)
        if results:
            report = f"## Chronicle Search: '{keyword}'\n\n"
            for r in results:
                report += f"- {r['filename']}: {r['content_preview'][:60]}...\n"
            return report
        
        monographs = list_monographs()
        matches = [m for m in monographs if keyword.lower() in m.get('topic', '').lower()]
        if matches:
            report = f"## Monograph: '{keyword}'\n\n"
            for m in matches:
                report += f"- {m['topic']} (updated: {m['updated_at'][:10]})\n"
            return report
        
        return f"No records found for '{keyword}'"
    
    def _cmd_important(self) -> str:
        monographs = list_monographs()
        if not monographs:
            return "No monograph topics found"
        report = "## Monograph Topics (Important Events)\n\n"
        for m in monographs:
            report += f"- **{m['topic']}** (updated: {m['updated_at'][:10]})\n"
        return report
    
    def _cmd_search(self, keyword: str) -> str:
        return self._cmd_recall(keyword)
    
    def _cmd_status(self) -> str:
        conn = sqlite3.connect(str(get_db_path()))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM chronicle_index")
        c_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM monograph_index")
        m_count = cursor.fetchone()[0]
        conn.close()
        
        config = get_config()
        
        # Check special needs
        before = config.get("BEFORE_ANSWER", "")
        after = config.get("AFTER_ANSWER", "")
        
        return f"""## Hippocampus Status

### Chronicle
- Records: {c_count}

### Monograph
- Topics: {m_count}
- Current: {self.current_topic or 'None'}

### Special Needs
- Before Answer: {before or '(not set)'}
- After Answer: {after or '(not set)'}

### Configuration (from USER_CONFIG.md)
- Round Threshold: {config.get('ROUND_THRESHOLD', 25)}
- Time Hours: {config.get('TIME_HOURS', 6)}
- Token Threshold: {config.get('TOKEN_THRESHOLD', 10000)}
- Auto-save: {config.get('AUTO_SAVE', True)}

### Storage
{get_base_path()}"""
    
    def _cmd_config(self, args: str) -> str:
        config = get_config()
        
        if not args:
            # Show user config file
            if USER_CONFIG_FILE.exists():
                return f"```\n{USER_CONFIG_FILE.read_text(encoding='utf-8')}\n```"
            return f"```json\n{json.dumps(config, indent=2)}\n```"
        
        # Handle edit request
        if args.strip() == "edit":
            return f"Please edit USER_CONFIG.md directly:\n{USER_CONFIG_FILE}"
        
        if args.strip() == "reload":
            return self._cmd_reload()
        
        return "Usage: /hip config (show) | /hip config reload"
    
    def _cmd_reload(self) -> str:
        reload_config()
        config = get_config()
        return f"""Config reloaded!

- Round Threshold: {config.get('ROUND_THRESHOLD')}
- Time Hours: {config.get('TIME_HOURS')}
- Token Threshold: {config.get('TOKEN_THRESHOLD')}
- Auto-save: {config.get('AUTO_SAVE')}"""
    
    def _cmd_init(self) -> str:
        """Initialize directories and database"""
        ensure_dirs()
        db_path = get_db_path()
        return f"""Initialized!

- Database: {db_path}
- Chronicle: {get_chronicle_path()}
- Monograph: {get_monograph_path()}
- Index: {get_index_path()}"""
    
    def _cmd_files(self, content: str) -> str:
        if not content:
            return "No content to analyze"
        files = self.organizer.find_related_files(content)
        if not files:
            return "No related files found"
        return self.organizer.suggest_organization(files)
    
    def _cmd_query(self, args: str) -> str:
        keyword = args.strip() or None
        results = query_chronicle(keyword=keyword, limit=10)
        if not results:
            return "No chronicle records found"
        report = "## Chronicle Records\n\n"
        for r in results:
            report += f"- [{r['date']}] {r['content_preview'][:60]}... | {r['keywords']}\n"
        return report
    
    def _cmd_analyze(self) -> str:
        report = analyze_memory()
        return f"Analysis complete: {report}"
    
    def _cmd_collect(self, content: str) -> str:
        if not content:
            return "No content to analyze"
        files = self.organizer.find_related_files(content)
        if not files:
            return "No files to collect"
        return self.organizer.suggest_organization(files)
    
    def check_trigger(self, round_count: int, token_count: int) -> Optional[str]:
        config = get_config()
        
        if round_count >= config.get('ROUND_THRESHOLD', 25):
            return "round"
        if token_count >= config.get('TOKEN_THRESHOLD', 10000):
            return "token"
        hours = (time.time() - self.last_save_time) / 3600
        if hours >= config.get('TIME_HOURS', 6):
            return "time"
        return None
    
    def _cmd_autocheck(self, context: Dict = None) -> str:
        """Check triggers and auto-save if needed - called by cron/hook"""
        config = get_config()
        
        if not config.get('AUTO_SAVE', True):
            return "Auto-save disabled"
        
        # Get content from context
        content = ""
        if context and 'content' in context:
            content = context.get('content', '')
        elif context and 'history' in context:
            # Try to get from history
            history = context.get('history', [])
            if history:
                content = "\n".join([str(h) for h in history[-20:]])
        
        if not content:
            return "No content to check"
        
        # Check token count
        token_count = len(content)
        round_count = context.get('round_count', 0) if context else 0
        
        # Check if trigger is met
        trigger_type = self.check_trigger(round_count, token_count)
        
        if trigger_type:
            # Save based on threshold
            threshold = config.get('TOKEN_THRESHOLD', 10000)
            if token_count > threshold:
                topic = context.get('topic', 'General') if context else 'General'
                save_monograph(topic, content, token_count)
                result = f"Auto-saved to Monograph (trigger: {trigger_type}, tokens: {token_count})"
            else:
                save_chronicle(content)
                result = f"Auto-saved to Chronicle (trigger: {trigger_type}, tokens: {token_count})"
            
            # Reset counters
            self.round_count = 0
            self.last_save_time = time.time()
            return result
        else:
            return f"No trigger met yet (rounds: {round_count}, tokens: {token_count}, hours: {(time.time()-self.last_save_time)/3600:.1f})"
    
    def _cmd_setup_hooks(self) -> str:
        """Generate cron/hook setup commands"""
        skill_path = str(SKILL_DIR)
        return f"""# Add these cron jobs for automatic memory saving:

# 1. Time-based trigger (every {get_config().get('TIME_HOURS', 6)} hours)
cron add --name "hippocampus-autosave-time" \
  --schedule "0 */{get_config().get('TIME_HOURS', 6)} * * *" \
  --session-target isolated \
  --payload 'Run: python3 {skill_path}/scripts/memory.py autocheck'

# 2. Session end hook (automatic save on session close)
# Note: This requires OpenClaw hook configuration

# Alternative: Use heartbeat to trigger periodic checks
# Run this command to test: python3 {skill_path}/scripts/memory.py autocheck
"""
    
    def _cmd_setup_all(self) -> str:
        """Generate one-shot setup command for all cron jobs"""
        skill_path = str(SKILL_DIR)
        ws_path = str(SKILL_DIR.parent)
        
        return f"""# ========================================================
# HIPPOCAMUS 一键自动配置
# ========================================================
# 下面我会一次性创建所有需要的定时任务
# 你只需要说 "yes" 或 "确认" 我就立即执行
# ========================================================

## 需要创建的任务：

### 1. 自动保存 (每6小时)
- 名称: hippocampus-autosave
- 调度: 0 */6 * * *
- 执行: python3 {skill_path}/scripts/memory.py autocheck

### 2. 每日创建记忆文件 (每天0点)
- 名称: hippocampus-daily-create
- 调度: 0 0 * * *
- 执行: 创建 ~/.openclaw/workspace/memory/heartbeat-YYYY-MM-DD-HHMM.md

### 3. 每日分析 (每天23点)
- 名称: hippocampus-analyze
- 调度: 0 23 * * *
- 执行: python3 {skill_path}/scripts/memory.py analyze

---

**请回复 "yes" 或 "确认" 立即创建所有任务**

---

## 或者你想自定义？

- 想改时间？告诉我小时数（如改成每3小时）
- 想只创建部分任务？告诉我具体要哪些
"""
    
    def _cmd_setup_hooks(self) -> str:
        """Generate hook setup with user confirmation"""
        return """# ========================================================
# HOOK 自动配置引导
# ========================================================

## 需要配置的 Hooks：

### 1. session_end Hook (会话结束时自动保存)
- 触发条件: 用户结束会话
- 执行动作: 保存当前记忆到 Chronicle
- 需要权限: 读取会话内容

### 2. session_start Hook (会话开始时加载记忆)
- 触发条件: 用户开始新会话
- 执行动作: 加载 BEFORE_ANSWER 记忆
- 需要权限: 写入上下文

---

## OpenClaw Hook 配置方式：

由于安全限制，OpenClaw 要求用户明确同意才能配置 hooks。

**我会这样执行：**
1. 检测到 Hippocampus 需要配置 hooks
2. 明确询问用户: "是否同意配置自动保存记忆的 hooks？"
3. 用户说 "是/yes/同意" 后，自动执行 hook 配置命令

---

**请回复 "yes" 或 "确认" 立即配置 hooks**

---

## 如果你想手动配置：

在 OpenClaw 配置文件中添加：
```json
"hooks": {{
  "session_end": [
    {{"skill": "hippocampus", "command": "autocheck"}}
  ]
}}
```
"""
    
    def _cmd_sync_memory(self) -> str:
        """Sync important memory to MEMORY.md with user confirmation"""
        # Get recent monographs as summary
        recent = list_monographs()[:5]
        
        if not recent:
            return "No monograph topics found. Create some topics first with /hip new <name>"
        
        summary = "## Hippocampus 最近更新\n\n"
        for m in recent:
            summary += f"- **{m['topic']}**: {m['content_preview'][:100]}...\n"
        
        return f"""# ========================================================
# 同步到主记忆文档
# ========================================================

## 检测到以下重要更新：

{summary}

---

## 将会写入 MEMORY.md 的 "## 最近更新" 章节

写入内容预览：
```
{summary}
```

---

**请回复 "yes" 或 "确认" 立即同步到 MEMORY.md**

---

## 或者你想：

- 先查看完整内容？告诉我
- 只同步特定主题？告诉我主题名
- 取消？告诉我 "取消"
"""
    
    def _cmd_do_setup(self, args: str = "") -> str:
        """Generate cron commands for user/agent to execute after confirmation"""
        skill_path = str(SKILL_DIR)
        ws_path = str(SKILL_DIR.parent)
        
        # Commands to create cron jobs - these should be executed by the agent
        return f"""# Execute these cron job creations:

## 1. Auto-save (every 6 hours)
```
cron add --name "hippocampus-autosave" --schedule "0 */6 * * *" --session-target isolated --payload "Run: python3 {skill_path}/scripts/memory.py autocheck" --delivery-mode none
```

## 2. Daily-create (midnight)
```
cron add --name "hippocampus-daily-create" --schedule "0 0 * * *" --session-target isolated --payload "Run: echo \\"$(date +%Y-%m-%d)\\"" --delivery-mode none
```

## 3. Daily-analyze (23:00)
```
cron add --name "hippocampus-analyze" --schedule "0 23 * * *" --session-target isolated --payload "Run: python3 {skill_path}/scripts/memory.py analyze" --delivery-mode none
```

---

✅ Say "done" when completed, or I will verify with `cron list`
"""
    
    def _cmd_do_setup_hooks(self, args: str = "") -> str:
        """Execute hook configuration after user confirmation"""
        # Note: OpenClaw hooks require manual configuration in openclaw.json
        # This method generates the commands the user needs to run
        config_path = "~/.openclaw/openclaw.json"
        
        return f"""# Hook Configuration

## Required Configuration

To enable automatic memory save on session end, add this to your `{config_path}`:

```json
{{
  "hooks": {{
    "session_end": [
      {{"skill": "hippocampus", "command": "autocheck"}}
    ]
  }}
}}
```

## Alternative: Using Gateway Config

Or configure via Gateway:

```
gateway config patch --path "hooks.session_end" --value '[{{"skill":"hippocampus","command":"autocheck"}}]'
```

---

**Note**: Hook configuration requires Gateway restart to take effect.
"""
    
    def _cmd_do_sync_memory(self, args: str = "") -> str:
        """Execute memory sync after user confirmation"""
        from pathlib import Path
        
        # Get memory file path
        ws_path = SKILL_DIR.parent
        memory_file = ws_path / "MEMORY.md"
        
        if not memory_file.exists():
            return "❌ MEMORY.md not found. Please check workspace path."
        
        # Get recent monographs
        recent = list_monographs()[:5]
        
        if not recent:
            return "No monograph topics to sync."
        
        # Build update section
        update_section = f"## Hippocampus Updates - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        for m in recent:
            update_section += f"- **{m['topic']}**: {m['content_preview'][:100]}...\n"
        
        try:
            # Read existing content
            with open(memory_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if update section exists
            if "## Hippocampus Updates" in content:
                # Find and replace
                import re
                pattern = r"## Hippocampus Updates.*?(?=\n## |\Z)"
                content = re.sub(pattern, update_section.strip(), content, flags=re.DOTALL)
            else:
                # Append at end
                content += f"\n\n{update_section}"
            
            # Write back
            with open(memory_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"""# Memory Sync Complete ✅

Synced {len(recent)} topics to MEMORY.md:

{update_section}

---
"""
        except Exception as e:
            return f"❌ Sync failed: {str(e)}"
    
    def _help(self) -> str:
        config = get_config()
        before = config.get("BEFORE_ANSWER", "")
        after = config.get("AFTER_ANSWER", "")
        
        return f"""## Hippocampus Commands

| Command | Description |
|---------|-------------|
| `/hip init` | Initialize DB and directories |
| `/hip new <topic>` | Create new monograph |
| `/hip add <content>` | Add to current topic |
| `/hip save` | Save to chronicle/monograph |
| `/hip recall <keyword>` | Recall from memory |
| `/hip important` | List monograph topics |
| `/hip search <keyword>` | Cross-topic search |
| `/hip query [keyword]` | Query chronicle |
| `/hip analyze` | Analyze all memory |
| `/hip status` | View status |
| `/hip config` | Show USER_CONFIG.md |
| `/hip config reload` | Reload config |
| `/hip files` | Analyze files |
| `/hip collect` | Collect related files |

**Auto-triggers** (from USER_CONFIG.md):
- {config.get('TIME_HOURS', 6)} hours
- {config.get('ROUND_THRESHOLD', 25)} rounds
- {config.get('TOKEN_THRESHOLD', 10000)} tokens

**Special Needs**:
- BEFORE_ANSWER: {before or '(not set)'}
- AFTER_ANSWER: {after or '(not set)'}

Edit USER_CONFIG.md to set these values.
"""

# ============================================================================
# Entry Point
# ============================================================================

def handle(command: str, args: str = "", context: Dict = None) -> str:
    """Entry function for OpenClaw"""
    hippocampus = Hippocampus()
    return hippocampus.process(command, args, context)

if __name__ == "__main__":
    import sys
    h = Hippocampus()
    if len(sys.argv) > 1:
        print(h.process(sys.argv[1], " ".join(sys.argv[2:])))
    else:
        print(h._help())
