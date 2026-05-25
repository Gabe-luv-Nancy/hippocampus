# Hippocampus Deployment Instructions

> Version: 4.0.0
> Purpose: AI reads this file to automatically complete full Hippocampus installation

---

## Product Overview

**Hippocampus (Photon)** — AI-enhanced memory system. Core philosophy: AI's purpose is to FIX human memory flaws, not emulate human forgetting.

Human memory is inherently flawed: it forgets, distorts, and cannot precisely retrieve. Hippocampus uses AI to fix these flaws — **never forget, precise retrieval, rules-based accountability**.

**Core features:**
- **Schema (AI Task Progress Table)** — Task status only marked done if files provably exist; AI cannot cheat
- **AI Tool Auto-Discovery** — Automatically detects installed AI tools: OpenClaw / Kimi / Doubao / ChatGLM / Zhipu / Tongyi / Wenxin / Gemini / Claude (Mac) / etc.
- **Full-Coverage Backup Engine** — SHA256 incremental backup, dual-end logs fully traceable
- **Dual-Layer Memory System** — Chronicle (event stream) + Monograph (topic)
- **Proactive Warning** — Detects failure patterns and warns before repeating
- **Auto-Extract File Memory** — Detects and backs up new AI-generated memory files

**After installation, users can:**
- `/photon status` — View memory status
- `/photon recall <keyword>` — Precise recall
- `/photon schema list` — View AI task progress table
- `python3 scripts/scanner.py scan` — Full AI tool memory file scan

---

## 🆕 V4.2 新功能：Auto-Extract File Memory

### 功能说明
自动识别用户通过 AI 指导新形成的记忆文件（.md / .yaml / .json 等），并备份到 HIPPO 的 Monograph 层。

### 核心机制
- **base_schema.yaml**：官方路径骨架（固定不变）
- **user_schema.yaml**：用户实际路径（自动扫描生成）
- **差异对比**：不在官方骨架中的路径 = 用户新增文件
- **备份策略**：
  - 同名文件：加时间戳备份（如 `model_20260423.json`）
  - 全新文件：直接复制到 `assets/hippocampus/monograph/file_memory/`

### 使用方式

**触发扫描（dry-run 预览）：**
> `/hippo extract --dry-run`

**执行备份：**
> `/hippo extract`

**扫描目标目录：**
- `~/.openclaw/workspace/`（所有 .md / .yaml / .json / .txt / .sql 文件）
- HIPPO 项目目录（排除 assets/ 运行时生成目录）

### 命令示例
```
/hippo extract --dry-run
# 输出：发现 3 个新文件，2 个已修改

/hippo extract
# 输出：✅ 已备份 5 个文件到 monograph/file_memory/
```

### 注意事项
- 完全不改用户文件，只读扫描
- 备份目标为 HIPPO 自己的数据目录
- 支持 cron 定时执行（每日自动备份）

---

## Installation Target Path

```
~/.openclaw/workspace/skills/hippocampus/
```

---

## Execution Steps

### Step 1: Create Directory Structure

```bash
mkdir -p ~/.openclaw/workspace/skills/hippocampus/
mkdir -p ~/.openclaw/workspace/skills/hippocampus/scripts/
mkdir -p ~/.openclaw/workspace/skills/hippocampus/scripts/task_schema/
mkdir -p ~/.openclaw/workspace/skills/hippocampus/scripts/config/
mkdir -p ~/.openclaw/workspace/skills/hippocampus/assets/hippocampus/chronicle/
mkdir -p ~/.openclaw/workspace/skills/hippocampus/assets/hippocampus/monograph/
mkdir -p ~/.openclaw/workspace/skills/hippocampus/assets/hippocampus/index/
```

### Step 2: Deploy Python Scripts (Complete Code — Copy Directly)

Copy the contents of the `scripts/` directory in this package to `~/.openclaw/workspace/skills/hippocampus/scripts/`.

Includes:
```
scripts/
├── memory.py          # Core memory engine (1366 lines)
├── detector.py        # AI tool auto-discovery (299 lines)
├── scanner.py        # Full-coverage backup engine (495 lines)
├── rules_engine.py   # Rule matching engine (387 lines)
├── usb_detector.py   # USB detection (364 lines)
├── streamlit_app.py  # Web UI (612 lines)
├── task_schema/      # Schema AI task progress table
│   ├── schema_models.py  # Data models
│   ├── validator.py      # Rule engine
│   ├── registry.py       # YAML read/write
│   └── registry.yaml    # Task registry
└── config/
```

### Step 3: Copy GUI Main File

Copy `gui_main.py` to `~/.openclaw/workspace/skills/hippocampus/gui_main.py`

### Step 4: Generate Metadata Files

#### 4.1 VERSION

File path: `~/.openclaw/workspace/skills/hippocampus/VERSION`

```
4.0.0
```

#### 4.2 skill.yaml

File path: `~/.openclaw/workspace/skills/hippocampus/skill.yaml`

```yaml
name: hippocampus
version: 4.0.0
description: >
  AI-enhanced memory system that FIXES human memory flaws.
  NO DECAY - AI never forgets.
  Features: Schema (AI task progress table), AI tool auto-discovery,
  full-coverage backup engine, tool success tracking, project checkpoints.
  Philosophy: "AI is meant to FIX human memory flaws, why learn human decay?"
author: GabetopZ
homepage: https://github.com/Gabe-luv-Nancy/hippocampus
license: MIT
tags:
  - memory
  - schema
  - task-management
  - checkpoint
  - backup
triggers:
  - remember
  - recall
  - checkpoint
  - warn
  - schema
  - task
type: skill
runtime:
  mode: instruction-first
  code_on_demand: true
permissions:
  - read
  - write
  - exec
dependencies:
  - python3 >= 3.8
```

#### 4.3 USER_CONFIG.md

File path: `~/.openclaw/workspace/skills/hippocampus/USER_CONFIG.md`

```markdown
# Hippocampus User Configuration

## Basic Settings

| Setting | Default | Description |
|---------|---------|-------------|
| language | en | Language preference |
| auto_save_interval | 6h | Auto-save interval |
| chronicle_retention | 90d | Event stream retention days |
| monograph_auto_promote | true | Auto-promote important content to topic |

## AI Tool Monitoring Config

```yaml
tools:
  openclaw:
    enabled: true
    paths:
      - ~/.openclaw/workspace/
      - ~/.openclaw/memory/
    patterns:
      - "*.md"
      - "*.json"
      - "*.yaml"

  kimi:
    enabled: false
    paths:
      - ~/Library/Application Support/Kimi/
    patterns:
      - "*.txt"
      - "conversation*.json"
```

## USB Backup Config

```yaml
usb:
  auto_backup: true
  marker: "HIPPOCAMPUS_BRAINDUMP_v4.0"
  incremental: true
  log_dual: true
```

## Schema Config

```yaml
schema:
  registry_path: scripts/task_schema/registry.yaml
  enforce_validation: true
  auto_check_depends: true
```

## Command Aliases

```yaml
aliases:
  s: status
  r: recall
  s: save
  s: scan
```
```

#### 4.4 README.md

File path: `~/.openclaw/workspace/skills/hippocampus/README.md`

```markdown
# Hippocampus (Photon Version)

> "AI is meant to FIX human memory flaws, why learn human decay?"

## Core Philosophy

Human memory is inherently flawed: **it forgets, distorts, and cannot precisely retrieve**.

Hippocampus uses AI to fix these flaws — never forget, precise retrieval, rules-based accountability.

## Core Features

### 🔥 Schema — AI Task Progress Table (v4.0 New Core)

Task management system that forces AI to follow rules and take accountability.

```
AI: "I want to mark task HIPPO-XXX as done"
        ↓
validator.py: "Are ALL your file_refs[].verified=true?"
        ↓
Can't write it if it doesn't pass. No arguments.
```

### 🔍 AI Tool Auto-Discovery (v3.0+)

```bash
python3 scripts/detector.py
```

### 📦 Full-Coverage Backup Engine (v3.0+)

```bash
python3 scripts/scanner.py scan
python3 scripts/scanner.py scan --usb <path>
```

### 🧠 Dual-Layer Memory System (Since v1.0)

- **Chronicle**: Automatically saves conversation records with timestamps
- **Monograph**: Important topics with rich metadata

## Quick Start

```bash
# After installation, verify with:
python3 scripts/memory.py status
```

## Command Reference

| Command | Description |
|---------|-------------|
| `memory.py init` | Initialize (must run first) |
| `memory.py status` | View memory status |
| `memory.py recall <keyword>` | Precise recall |
| `scanner.py scan` | Full AI tool scan |
| `detector.py` | Detect installed AI tools |
| `task_schema/registry.py list` | View Schema task table |

## Version

4.0.0 | MIT License | by GabetopZ
```

#### 4.5 SKILL.md (Most Critical — AI Reads This for Instructions)

File path: `~/.openclaw/workspace/skills/hippocampus/SKILL.md`

```markdown
---
name: hippocampus
version: 4.0.0
description: >
  AI-enhanced memory system that FIXES human memory flaws.
  NO DECAY - AI never forgets.
  Features: Schema (AI task progress table), AI tool auto-discovery,
  full-coverage backup engine, tool success tracking, project checkpoints.
  Philosophy: "AI is meant to FIX human memory flaws, why learn human decay?"
author: GabetopZ
homepage: https://github.com/Gabe-luv-Nancy/hippocampus
license: MIT
tags:
  - memory
  - schema
  - task-management
  - checkpoint
  - backup
triggers:
  - remember
  - recall
  - checkpoint
  - warn
  - schema
  - task
type: skill
runtime:
  mode: instruction-first
  code_on_demand: true
  instruction: |
    ## HIPPOCAMPUS - AI ENHANCED MEMORY

    Philosophy: AI should ENHANCE human memory, not imitate its flaws.
    Traditional memory systems use decay (0.99^days) - THIS IS WRONG.
    AI NEVER FORGETS. That's the point.

    ### 🔥 Schema — AI Task Progress Table (v4.0 Core)

    Schema is a task registry where AI cannot mark tasks "done" without proving files exist.

    How it works:
    - Tasks in registry.yaml have file_refs[] listing files that must exist
    - validator.py checks: status=done requires ALL file_refs[].verified=true
    - verified=true requires the file path to actually exist on disk
    - AI says "I'm done" → validator checks → write fails if files missing

    Commands:
    - python3 scripts/task_schema/registry.py list — view all tasks
    - python3 scripts/task_schema/registry.py get <task_id> — view one task
    - python3 scripts/task_schema/validator.py check <task_id> — validate a task

    Schema files: scripts/task_schema/
    - schema_models.py — data models
    - validator.py — rule engine (must pass to mark done)
    - registry.py — YAML read/write interface
    - registry.yaml — task registry (the AI progress table)

    ### Core Features

    1. **Schema — AI Task Progress Table**
       - Tasks with file_refs must have all refs verified before done
       - Validator blocks invalid state transitions
       - Any AI can query the table to know what's blocked

    2. **AI Tool Auto-Discovery**
       - Detects: OpenClaw / Kimi / Doubao / ChatGLM / Zhipu / Tongyi / Wenxin / Gemini / Claude (Mac) / etc.
       - python3 scripts/detector.py

    3. **Full-Coverage Backup Engine**
       - SHA256 incremental comparison
       - Dual-end logging (client + USB)
       - python3 scripts/scanner.py scan

    4. **Tool/Command Success Tracking**
       - Remember which commands work/fail
       - Track model performance on tasks

    5. **Project Checkpoints**
       - Not "recent discussion" but "exactly where we left off"
       - Precise project state storage

    6. **Failure Pattern Warning**
       - Remember what causes failures
       - Warn proactively before repeating

    7. **Knowledge Graph**
       - Networked: Skill → Project → Goal

    ### Trigger Keywords
    When user says:
    - remember, recall, checkpoint
    - schema, task, registry, progress
    - where did we leave off
    - what was i working on
    - warn me about

    ### Available Commands
    - /photon status - View status
    - /photon save - Save context
    - /photon recall <query> - Precise recall
    - /photon checkpoint - Save project state
    - /photon warn - Check failure patterns
    - /photon schema list - View task registry
    - /photon schema check <task_id> - Validate a task

    Execute: python3 scripts/memory.py <command>
    Schema: python3 scripts/task_schema/registry.py <command>

permissions:
  - read
  - write
  - exec
dependencies:
  - python3 >= 3.8
```

### Step 5: Initialize

```bash
cd ~/.openclaw/workspace/skills/hippocampus
python3 scripts/memory.py init
```

### Step 6: Verify

```bash
python3 scripts/memory.py status
```

Expected output: Shows Chronicle and Monograph status, record count 0.

### Step 7: Optional Cron Jobs (Set Up After User Confirms)

```bash
# Auto-save every 6h
openclaw cron add --name "hippocampus-autosave" \
  --schedule "0 */6 * * *" --session-target isolated \
  --payload "Run: python3 ~/.openclaw/workspace/skills/hippocampus/scripts/memory.py autocheck"

# Daily analysis at 23:00
openclaw cron add --name "hippocampus-analyze" \
  --schedule "0 23 * * *" --session-target isolated \
  --payload "Run: python3 ~/.openclaw/workspace/skills/hippocampus/scripts/memory.py analyze"
```

---

## File Manifest

| File | Description |
|------|-------------|
| `scripts/memory.py` | Core memory engine |
| `scripts/detector.py` | AI tool auto-discovery |
| `scripts/scanner.py` | Full-coverage backup engine |
| `scripts/rules_engine.py` | Rule matching engine |
| `scripts/usb_detector.py` | USB detection |
| `scripts/streamlit_app.py` | Web UI |
| `scripts/task_schema/schema_models.py` | Schema data models |
| `scripts/task_schema/validator.py` | Schema rule engine |
| `scripts/task_schema/registry.py` | Schema YAML read/write |
| `scripts/task_schema/registry.yaml` | Task registry |
| `gui_main.py` | PyQt6 GUI |
| `SKILL.md` | OpenClaw skill definition |
| `skill.yaml` | Metadata |
| `USER_CONFIG.md` | User config template |
| `README.md` | User documentation |
| `VERSION` | Version (4.0.0) |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Init errors "directory exists" | Check for residual files in target path, clean and retry |
| detector.py errors | Confirm system paths are correct (Linux: ~/.config or ~/.local) |
| Permission errors | Check write permissions, chmod +x gui_main.py |
| Schema commands not responding | Confirm task_schema/ directory fully deployed |
