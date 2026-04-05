---
name: hippocampus
version: 3.2.0
description: >
  Hippocampus: AI-enhanced memory system that FIXES human memory flaws.
  NO DECAY - AI never forgets.
  Features: memory capture, dual storage, precise retrieval, knowledge graph, USB support.
  Philosophy: "AI is meant to FIX human memory flaws, why learn human decay?"

author: GabetopZ
homepage: https://github.com/Gabe-luv-Nancy/hippocampus
license: MIT
tags:
  - memory
  - photon
  - capture
  - checkpoint
  - success-tracking
  - failure-warning
  - knowledge-graph

triggers:
  - remember
  - recall
  - checkpoint
  - warn
  - capture

type: skill

runtime:
  mode: instruction-first
  code_on_demand: true
  instruction: |
    ## HIPPOCAMPUS v3.2 - ENHANCED MEMORY
    
    Philosophy: AI should ENHANCE human memory, not imitate its flaws.
    Traditional memory systems use decay (0.99^days) - THIS IS WRONG.
    AI NEVER FORGETS. That's the point.
    
    ### Core Features (No Decay)
    
    1. **Memory Capture**
       - Auto-scan and capture memory files from multiple AI sources
       - Supported: OpenClaw, 豆包, 元宝, 讯飞星火, etc.
    
    2. **Dual Storage**
       - Chronicle: Temporal memory for everyday interactions
       - Monograph: Important events with rich metadata
    
    3. **Precise Retrieval**
       - Exact timestamps, not "recent"
       - Keyword-based search across all memory
    
    4. **Knowledge Graph**
       - Networked: Skill → Project → Goal
       - Association generation
    
    5. **USB Product Support**
       - Portable memory stick version
       - Cross-platform autorun
    
    ### Trigger Keywords
    When user says:
    - remember, recall, checkpoint
    - capture, 抓取
    - where did we leave off
    - what was i working on
    - warn me about
    
    ### Available Commands
    - /photon status - View status
    - /photon save - Save context
    - /photon recall <query> - Precise recall
    - /photon checkpoint - Save project state
    - /photon capture - Capture AI memories
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
  - name: capture
    pattern: "/photon capture"
    description: Capture AI memories
  - name: warn
    pattern: "/photon warn"
    description: Check failure patterns
  - name: graph
    pattern: "/photon graph"
    description: View knowledge graph
  - name: analyze
    pattern: "/photon analyze"
    description: Analyze memory
---

# Hippocampus v3.2

> "AI is meant to FIX human memory flaws, why learn human decay?"

## What's New in v3.2

- **Memory Capture**: Auto-scan AI memory files from multiple sources
- **USB Product**: Portable memory stick with auto-run
- **Local Analyzer**: Built-in TF-IDF search without cloud dependency

## Features

| Feature | Description |
|---------|-------------|
| **No Decay** | AI never forgets |
| **Capture** | Auto-scan memories from OpenClaw, 豆包, 元宝, etc. |
| **Dual Storage** | Chronicle (temporal) + Monograph (important) |
| **Checkpoints** | Know exactly where project left off |
| **USB Support** | Portable version with autorun |

## Commands

- `/photon status` - View status
- `/photon save` - Save context  
- `/photon recall <query>` - Recall
- `/photon checkpoint` - Save state
- `/photon capture` - Capture AI memories
- `/photon warn` - Check patterns
- `/photon analyze` - Analyze memory

## Setup

After installing, run initialization:

```bash
cd /path/to/hippocampus
python3 scripts/memory.py init
python3 scripts/capture.py --scan  # Scan for AI memories
```

## Philosophy

**Traditional memory = Human memory imitation = DECAY = WRONG**

AI should FIX human memory flaws:
- ❌ Forgetting → ✅ Perfect recall
- ❌ Fuzzy matching → ✅ Precise timestamps  
- ❌ Passive triggers → ✅ Proactive warnings
- ❌ Importance decay → ✅ Never lose anything

## Version

3.2.0 (Photon)
