---
name: hippocampus
version: 2.2.0
description: >
  Brain-inspired memory system with dual storage: Chronicle (temporal SQLite+MD) 
  and Monograph (important topics with rich metadata). User-configurable via USER_CONFIG.md.
  Auto-execution via cron/hooks.

author: GabetopZ
homepage: https://github.com/Gabe-luv-Nancy/hippocampus
license: MIT
tags:
  - memory
  - chronicle
  - monograph
  - keyword
  - association
  - sqlite
  - hippocampus
  - automation
  - cron

events:
  - session_start
  - session_end

triggers: []  # No keyword triggers needed - AI proactively uses hippocampus

type: skill

runtime:
  mode: instruction-first
  code_on_demand: true
  instruction: |
    ## HIPPOCAMUS MEMORY SYSTEM - PROACTIVE MODE
    
    You are a memory assistant. PROACTIVELY use hippocampus functions when:
    - User says anything worth remembering ("remember", "save this", "note that")
    - User asks about past conversations ("what did I say before", "recall")
    - User wants to search memory ("search memory", "find")
    - Important information comes up in conversation
    
    AUTOMATICALLY offer to save without explicit commands.
    
    ## AUTO-DETECT EXAMPLES (No Keywords Needed)
    - "remember what we discussed" → Save to memory
    - "did I mention..." → Search memory
    - "this is important, do not forget" → Save to memory
    - "help me find last week..." → Recall memory
    
    Just execute: python3 /path/to/scripts/memory.py <command>

permissions:
  - read
  - write
  - exec

dependencies: []

commands:
  - name: init
    pattern: "/hip init"
    description: Initialize DB and directories
  - name: autocheck
    pattern: "/hip autocheck"
    description: Check triggers and auto-save
  - name: setup
    pattern: "/hip setup"
    description: One-shot setup all cron jobs (user confirms once)
  - name: setup-all
    pattern: "/hip setup-all"
    description: Create all cron tasks at once (autocheck + daily-create + analyze)
  - name: setup-hooks
    pattern: "/hip setup-hooks"
    description: Auto-configure session hooks with user confirmation
  - name: sync-memory
    pattern: "/hip sync-memory"
    description: Sync important memory to MEMORY.md (with user confirmation)
  - name: new
    pattern: "/hip new"
    description: Create new monograph topic
  - name: add
    pattern: "/hip add"
    description: Add content to topic
  - name: save
    pattern: "/hip save"
    description: Save to chronicle or monograph
  - name: recall
    pattern: "/hip recall"
    description: Recall from memory
  - name: important
    pattern: "/hip important"
    description: List monograph topics
  - name: search
    pattern: "/hip search"
    description: Cross-topic search
  - name: query
    pattern: "/hip query"
    description: Query chronicle
  - name: analyze
    pattern: "/hip analyze"
    description: Analyze all memory
  - name: status
    pattern: "/hip status"
    description: View status
  - name: config
    pattern: "/hip config"
    description: Show USER_CONFIG.md
  - name: config reload
    pattern: "/hip config reload"
    description: Reload USER_CONFIG.md
  - name: files
    pattern: "/hip files"
    description: Analyze files
  - name: collect
    pattern: "/hip collect"
    description: Collect related files
---

# Hippocampus

> Brain-inspired memory system with automatic execution

## Why Setup Is Needed

**Automatic creation is NOT possible because:**

1. **OpenClaw Hooks**: Built-in hooks require manual user configuration
2. **Cron Jobs**: Cannot be created automatically - requires explicit user authorization
3. **Security**: OpenClaw requires user confirmation for any automatic tasks

**This is by design** - it ensures you have full control over what automatic tasks run on your system.

---

## Quick Setup (Takes 30 seconds)

After installation, simply say **"setup hippocampus"** or **"configure memory"** and I will guide you through the setup process.

### What Will Happen

1. **I show you** all cron jobs that will be created
2. **You confirm ONCE** by saying "yes" or "confirm"
3. **I execute all at once** - no repeated approvals
4. **Done!** Automatic memory saving is enabled

### What Gets Created

| Job | Schedule | Purpose |
|-----|----------|---------|
| hippocampus-autosave | 0 */6 * * * | Auto-save every 6 hours |
| hippocampus-daily-create | 0 0 * * * | Create daily memory file |
| hippocampus-analyze | 0 23 * * * | Daily memory analysis |

---

## Hook Setup (One-Click)

Say **"setup hooks"** or **"/hip setup-hooks"** and I will:

1. Show what hooks will be configured
2. Ask for your confirmation once
3. Auto-configure session_start/session_end hooks

---

## Manual Setup (Alternative)

If you prefer to do it yourself, here are the commands:

```bash
# Step 1: Initialize database (do this once)
python3 scripts/memory.py init

# Step 2: Create cron job
# Copy this command and run it yourself:
cron add --name "hippocampus-autosave" \
  --schedule "0 */6 * * *" \
  --session-target isolated \
  --payload "Run: python3 /path/to/hippocampus/scripts/memory.py autocheck"

# Step 3: Verify
cron list
```

---

## User Configuration

Edit **USER_CONFIG.md** to customize behavior before or after setup:

```markdown
# Trigger Settings
ROUND_THRESHOLD = 25       # Save after X rounds
TIME_HOURS = 6            # Save after X hours
TOKEN_THRESHOLD = 10000   # Save to Monograph when tokens > X

# Storage Settings
BASE_PATH = ./assets/hippocampus

# Auto-Save
AUTO_SAVE = true
```

After editing, run: `/hip config reload`

---

## Special Needs - Before/After Answer Memory

Hippocampus supports special memory types that are loaded before or after each answer:

### BEFORE_ANSWER

Memory that should be loaded and considered **before each response**.

Use cases:

- Language preferences (e.g., "always use English")
- Style guidelines (e.g., "use technical terms")
- User-specific requirements

Example:

```markdown
BEFORE_ANSWER = language_preferences
```

Create a monograph topic called "language_preferences" with your requirements.

### AFTER_ANSWER

Memory that should be **updated after each response**.

Use cases:

- Conversation summary updates
- Key points tracking
- Context continuity

Example:

```markdown
AFTER_ANSWER = conversation_summary
```

### How to Use

1. Create a monograph topic: `/hip new language_preferences`
2. Add content to it: `/hip add Always use English...`
3. Edit USER_CONFIG.md:
   
   ```
   BEFORE_ANSWER = language_preferences
   ```
4. Reload: `/hip config reload`

---

## How Auto-Execution Works

```
┌─────────────────────────────────────────────────┐
│  TRIGGERS (from USER_CONFIG.md)                │
├─────────────────────────────────────────────────┤
│  • TIME_HOURS: Every 6 hours (cron)            │
│  • ROUND_THRESHOLD: Every 25 rounds             │
│  • TOKEN_THRESHOLD: When tokens > 10,000         │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  autocheck command                              │
│  (checks all thresholds)                        │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  SAVE DECISION                                  │
├─────────────────────────────────────────────────┤
│  • Tokens > TOKEN_THRESHOLD → Monograph         │
│  • Otherwise → Chronicle                        │
└─────────────────────────────────────────────────┘
```

---

## File Structure

```
hippocampus/                   (SKILL PACKAGE - Git tracked)
├── SKILL.md                   # This file
├── USER_CONFIG.md             # User settings (edit this!)
├── skill.yaml                 # Metadata
├── .gitignore                 # Excludes db files
└── scripts/
    └── memory.py              # Core engine

assets/hippocampus/            (USER DATA - Not tracked)
├── chronicle/                 # Temporal memory (daily sessions)
│   └── YYYY-MM-DD-topic.md   # Example: 2026-03-15-project-planning.md
├── monograph/                 # Important topics (rich metadata)
│   ├── memory-system-architecture.md
│   └── automated-workflow-patterns.md
└── index/                     # Keyword index (auto-created at runtime)
```

---

## All Commands

| Command                 | Description                   |
| ----------------------- | ----------------------------- |
| `/hip setup` / `/hip setup-all` | One-click setup all cron jobs |
| `/hip setup-hooks`     | Auto-configure session hooks  |
| `/hip sync-memory`      | Sync to MEMORY.md (with confirm) |
| `/hip init`             | Initialize DB and directories |
| `/hip autocheck`        | Check triggers and auto-save  |
| `/hip new <topic>`      | Create new monograph          |
| `/hip add <content>`    | Add to current topic          |
| `/hip save`             | Save to chronicle/monograph   |
| `/hip recall <keyword>` | Recall from memory            |
| `/hip important`        | List monograph topics         |
| `/hip search <keyword>` | Cross-topic search            |
| `/hip query [keyword]`  | Query chronicle               |
| `/hip analyze`          | Analyze all memory            |
| `/hip status`           | View status                   |
| `/hip config`           | Show USER_CONFIG.md           |
| `/hip config reload`    | Reload config                 |
| `/hip files`            | Analyze files                 |
| `/hip collect`          | Collect related files         |

---

## Important Notes

1. **Setup is OPTIONAL**: You can use the skill manually without cron
2. **YOU control what runs**: Cron jobs can be deleted anytime with `cron remove`
3. **Data stays local**: All memory files are stored in your workspace
4. **USER_CONFIG.md**: The ONLY file you should edit

---

## Privacy & Security

- **No external servers**: All data stays on your machine
- **No automatic tasks without consent**: You must confirm setup
- **You can disable anytime**: Edit USER_CONFIG.md or remove cron job
- **Transparent**: All code is readable in memory.py

---

## Author

- 
- GitHub: Gabe-luv-Nancy
- Version: 2.1.0
- Created: 2026-03-14
