---
name: hippocampus
version: 3.0.0
description: >
  Photon: AI-enhanced memory system that FIXES human memory flaws.
  NO DECAY - AI never forgets.
  Features: tool success tracking, project checkpoints, failure pattern warning, knowledge graph.
  Philosophy: "AI is meant to FIX human memory flaws, why learn human decay?"

author: GabetopZ
homepage: https://github.com/Gabe-luv-Nancy/hippocampus
license: MIT
tags:
  - memory
  - photon
  - checkpoint
  - success-tracking
  - failure-warning
  - knowledge-graph

# Note: session hooks require manual configuration
# See README.md for cron-based alternatives

triggers:
  - remember
  - recall
  - checkpoint
  - warn

type: skill

runtime:
  mode: instruction-first
  code_on_demand: true
  instruction: |
    ## HIPPOCAMPUS PHOTON - ENHANCED MEMORY
    
    Philosophy: AI should ENHANCE human memory, not imitate its flaws.
    Traditional memory systems use decay (0.99^days) - THIS IS WRONG.
    AI NEVER FORGETS. That's the point.
    
    ### Core Features (No Decay)
    
    1. **Tool/Command Success Tracking**
       - Remember which commands work/fail
       - Track model performance on tasks
    
    2. **Project Checkpoints**
       - Not "recent discussion" but "exactly where we left off"
       - Precise project state storage
    
    3. **Failure Pattern Warning**
       - Remember what causes failures
       - Warn proactively before repeating
    
    4. **Session Continuity**
       - Know what was being done, not just discussed
    
    5. **Knowledge Graph**
       - Networked: Skill → Project → Goal
    
    ### Trigger Keywords
    When user says:
    - remember, recall, checkpoint
    - where did we leave off
    - what was i working on
    - warn me about
    
    ### Available Commands
    - /photon status - View status
    - /photon save - Save context
    - /photon recall <query> - Precise recall
    - /photon checkpoint - Save project state
    - /photon warn - Check failure patterns
    
    Execute: python3 scripts/memory.py <command>

permissions:
  - read
  - write
  - exec

dependencies:
  - python3 >= 3.8

commands:
  - name: status
    pattern: "/photon status"
    description: View memory status
  - name: save
    pattern: "/photon save"
    description: Save current context
  - name: recall
    pattern: "/photon recall"
    description: Precise recall
  - name: checkpoint
    pattern: "/photon checkpoint"
    description: Save project state
  - name: warn
    pattern: "/photon warn"
    description: Check failure patterns
  - name: graph
    pattern: "/photon graph"
    description: View knowledge graph
---

# Hippocampus Photon

> "AI is meant to FIX human memory flaws, why learn human decay?"

## Hooks & Automation

**Note:** OpenClaw hook system uses "hook packs" - may require manual setup.

For auto-save, use cron jobs (recommended) instead of session hooks.

## Philosophy

**Traditional memory = Human memory imitation = DECAY = WRONG**

AI should FIX human memory flaws:
- ❌ Forgetting → ✅ Perfect recall
- ❌ Fuzzy matching → ✅ Precise timestamps  
- ❌ Passive triggers → ✅ Proactive warnings
- ❌ Importance decay → ✅ Never lose anything

## Features

| Feature | Description |
|---------|-------------|
| **No Decay** | AI never forgets |
| **Checkpoints** | Know exactly where project left off |
| **Success Tracking** | Remember what works/fails |
| **Failure Warning** | Proactive pattern detection |
| **Knowledge Graph** | Networked memory |

## Setup (REQUIRED!)

After installing, you MUST run initialization:

```bash
cd /path/to/hippocampus
python3 scripts/memory.py init
```

This creates:
- assets/hippocampus/chronicle/db.sqlite
- assets/hippocampus/monograph/
- assets/hippocampus/index/

Then verify with:
```bash
python3 scripts/memory.py status
```

### Cron Jobs (Required!)

Automatic memory saving requires cron jobs. **User must confirm once:**

```bash
# Auto-save every 6 hours
openclaw cron add --name "hippocampus-autosave" \
  --schedule "0 */6 * * *" \
  --session-target isolated \
  --payload "Run: python3 /path/to/scripts/memory.py autocheck"

# Daily at 7 AM
openclaw cron add --name "hippocampus-daily" \
  --schedule "0 7 * * *" \
  --session-target isolated \
  --payload "Run: python3 /path/to/scripts/memory.py new daily-YYYY-MM-DD"

# Daily analysis at 11 PM - analyze chronicle, promote to monograph
openclaw cron add --name "hippocampus-analyze" \
  --schedule "0 23 * * *" \
  --session-target isolated \
  --payload "Run: python3 /path/to/scripts/memory.py analyze"
```

### Cron Jobs (Auto-created!)

When user runs "setup hippocampus" or "/photon setup", AI automatically creates:

1. **hippocampus-autosave** - Every 6 hours
2. **hippocampus-daily** - Daily at 7 AM  
3. **hippocampus-analyze** - Daily at 11 PM

These cron jobs provide automatic memory saving (replaces session hooks).

### Two Memory Types

**Chronicle** - Temporal memory for everyday interactions
- Automatically saves session content
- Indexed by time

**Monograph** - Important topics with rich metadata
- Stores significant memories, decisions, preferences
- Created via user request or auto-analysis

### Monograph Creation

**1. User Explicit:**
```bash
python3 scripts/memory.py new "Important Topic"
python3 scripts/memory.py add "Key content..."
```

**2. Auto-Analysis:**
```bash
python3 scripts/memory.py analyze  # Examines chronicle, promotes to monograph
```

### Keyword Index

- Auto-generated in `index/` directory
- Each keyword creates a .md reference file
- Enables fast cross-topic search

## Commands

- `/photon status` - View status
- `/photon save` - Save context  
- `/photon recall <query>` - Recall
- `/photon checkpoint` - Save state
- `/photon warn` - Check patterns

## Version

3.0.0 (Photon)
