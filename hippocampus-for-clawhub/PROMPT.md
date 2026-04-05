# Hippocampus for Clawhub - 安装提示词
> 本文件是 Hippocampus 的 Clawhub 发行版安装指令
> 当用户说"安装 Hippocampus"或"/photon install"时，AI 读取本文件并执行安装

---

## 概述

**Hippocampus** — AI 记忆增强系统，核心理念：AI 应修复人类记忆缺陷，而非模仿它们。

本提示词版本通过 AI 自我注入方式，在用户 OpenClaw 环境中自动生成完整代码。

---

## 执行步骤

### Step 1: 创建目录结构

在 `~/.openclaw/workspace/skills/hippocampus/` 下创建以下结构：

```
hippocampus/
├── SKILL.md              ← 技能定义
├── USER_CONFIG.md        ← 用户配置
├── skill.yaml           ← 元数据
├── VERSION              ← 版本号
├── scripts/
│   ├── memory.py         ← 核心记忆引擎
│   ├── capture.py        ← AI记忆抓取
│   └── analyzer.py       ← 本地分析
├── capture/              ← 抓取配置
│   └── openclaw.yaml
└── assets/              ← 数据存储（运行时生成）
    └── hippocampus/
        ├── chronicle/   ← 时序记忆
        ├── monograph/   ← 重要事件
        └── index/       ← 关键词索引
```

**执行命令：**
```bash
mkdir -p ~/.openclaw/workspace/skills/hippocampus/scripts
mkdir -p ~/.openclaw/workspace/skills/hippocampus/capture
mkdir -p ~/.openclaw/workspace/skills/hippocampus/assets/hippocampus/{chronicle,monograph,index}
```

---

### Step 2: 生成 SKILL.md

写入以下内容到 `SKILL.md`：

```markdown
---
name: hippocampus
version: 3.2.0
description: >
  Hippocampus: AI 记忆增强系统。
  核心理念：AI 应修复人类记忆缺陷，而非模仿它们。
  特性：记忆抓取、精确检索、知识图谱、失败预警。
  Philosophy: "AI is meant to FIX human memory flaws, why learn human decay?"
author: GabetopZ
tags:
  - memory
  - photon
  - capture
  - knowledge-graph
type: skill
runtime:
  mode: instruction-first
  code_on_demand: true
triggers:
  - remember
  - recall
  - checkpoint
  - capture
commands:
  - name: status
    pattern: "/photon status"
  - name: capture
    pattern: "/photon capture"
  - name: recall
    pattern: "/photon recall"
---

# Hippocampus v3.2

## 命令

- `/photon status` - 查看状态
- `/photon capture` - 抓取 AI 记忆
- `/photon recall <关键词>` - 精确检索

## Philosophy

**传统记忆 = 人类记忆模仿 = 衰退 = 错误**

AI 应该修复人类记忆缺陷：
- ❌ 遗忘 → ✅ 永不遗忘
- ❌ 模糊匹配 → ✅ 精确时间戳
- ❌ 被动触发 → ✅ 主动预警
```

---

### Step 3: 生成 scripts/memory.py

核心记忆引擎，实现：
- 双存储：SQLite 索引 + Markdown 文件
- 关键词提取
- 关联生成
- Chronicle（时序记忆）& Monograph（重要事件）

**关键函数：**
```python
def save_chronicle(content: str, session_id: str = None) -> str:
    """保存到时序记忆"""

def save_monograph(topic: str, content: str, tokens: int, metadata: Dict = None) -> str:
    """保存到重要事件记忆"""

def query_chronicle(keyword: str = None, start_date: str = None, end_date: str = None) -> List[Dict]:
    """精确检索记忆"""

def list_monographs() -> List[Dict]:
    """列出重要事件"""
```

---

### Step 4: 生成 scripts/capture.py

AI 记忆抓取模块，支持：
- OpenClaw 记忆文件扫描
- 其他 AI 工具路径配置
- 抓取清单生成

**关键类：**
```python
class CaptureEngine:
    def capture_single(self, ai_type: str) -> Dict[str, Any]:
        """抓取单个 AI 类型的记忆"""
    
    def capture_all(self) -> Dict[str, Any]:
        """抓取所有配置的 AI 记忆"""
```

**支持路径：**
- OpenClaw: `~/.openclaw/workspace/memory/*.md`
- 豆包: `~/.doubao/memory/`
- 元宝: `~/.yuanbao/memory/`
- 讯飞星火: `~/.iflytek/spark/memory/`

---

### Step 5: 生成 scripts/analyzer.py

本地记忆分析模块：
- SQLite 向量数据库
- TF-IDF 关键词检索
- 记忆摘要生成
- 报告导出（JSON/Markdown）

**关键类：**
```python
class SimpleVectorDB:
    def add_document(self, doc_id: str, source: str, content: str):
        """添加文档"""
    
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """语义检索"""

class Analyzer:
    def index_captured_files(self) -> Dict[str, Any]:
        """索引抓取的文件"""
    
    def generate_summary(self) -> Dict[str, Any]:
        """生成记忆摘要"""
```

---

### Step 6: 生成 capture/openclaw.yaml

OpenClaw 记忆路径配置：

```yaml
name: OpenClaw
description: 本地 AI 助手 OpenClaw 的记忆文件

paths:
  - ~/.openclaw/workspace/MEMORY.md
  - ~/.openclaw/workspace/memory/*.md
  - ~/.openclaw/workspace/SOUL.md
  - ~/.openclaw/workspace/USER.md
  - ~/.openclaw/workspace/AGENTS.md

priority: 1
enabled: true
```

---

### Step 7: 生成 USER_CONFIG.md

用户配置文件：

```markdown
# Hippocampus 用户配置

# 触发设置
ROUND_THRESHOLD = 25
TIME_HOURS = 6
TOKEN_THRESHOLD = 10000

# 存储设置
BASE_PATH = ./assets
CHRONICLE_DIR = chronicle
MONOGRAPH_DIR = monograph
INDEX_DIR = index

# 自动保存
AUTO_SAVE = true

# 抓取设置
CAPTURE_ENABLED = true
CAPTURE_INTERVAL = 24
```

---

### Step 8: 初始化数据库

执行：
```bash
cd ~/.openclaw/workspace/skills/hippocampus
python3 scripts/memory.py init
```

这将创建：
- `assets/hippocampus/chronicle/db.sqlite`
- `assets/hippocampus/monograph/`
- `assets/hippocampus/index/`

---

### Step 9: 配置 Cron 任务（可选）

自动记忆保存：

```bash
# 每6小时自动保存
openclaw cron add --name "hippocampus-autosave" \
  --schedule "0 */6 * * *" \
  --session-target isolated \
  --payload "Run: python3 ~/.openclaw/workspace/skills/hippocampus/scripts/memory.py autocheck"

# 每日抓取
openclaw cron add --name "hippocampus-capture" \
  --schedule "0 3 * * *" \
  --session-target isolated \
  --payload "Run: python3 ~/.openclaw/workspace/skills/hippocampus/scripts/capture.py"
```

---

## 验证安装

执行以下命令验证：

```bash
# 查看状态
python3 ~/.openclaw/workspace/skills/hippocampus/scripts/memory.py status

# 测试抓取
python3 ~/.openclaw/workspace/skills/hippocampus/scripts/capture.py --scan

# 测试检索
python3 ~/.openclaw/workspace/skills/hippocampus/scripts/memory.py recall test
```

---

## 版本信息

- **版本**: 3.2.0
- **发布日期**: 2026-04-05
- **GitHub**: https://github.com/Gabe-luv-Nancy/hippocampus
- **Philosophy**: AI 应修复人类记忆缺陷，而非模仿它们
