# Hippocampus (Photon Version) — ClawHub Edition

> Version: 4.0.0
> Target: ClawHub one-click install, end-user deployment
> This package is the for-clawhub edition; functionally identical to for-github after installation

---

## Core Philosophy

Human memory is inherently flawed: **it forgets, distorts, and cannot precisely retrieve**.

Hippocampus's philosophy: **use AI to fix these flaws, not emulate them**. AI never forgets. That's the point.

---

## Core Features

### 🔥 Schema — AI Task Progress Table (v4.0 New Core)

**Task management system that forces AI to follow rules and take accountability.**

```
AI: "I want to mark task HIPPO-XXX as done"
        ↓
validator.py: "Are ALL your file_refs[].verified=true?"
        ↓
AI: verifies each file path → can only write done if files actually exist
        ↓
Can't write it if it doesn't pass. No arguments.
```

- **Enforced check-off rule** — `status=done` requires ALL `file_refs[].verified=true`
- **Path validation** — `verified=true` requires the file to actually exist on disk
- **Dependency chain** — `depends_on`, upstream not done → downstream can't be done
- **Real-time tracking** — any AI can query the table to see exactly where things are blocked

### 🔍 AI Tool Auto-Discovery (v3.0+)

Automatically detects installed AI tools and their memory files:
```bash
python3 scripts/detector.py
```

### 📦 Full-Coverage Backup Engine (v3.0+)

SHA256 incremental backup with dual-end logging:
```bash
python3 scripts/scanner.py scan
python3 scripts/scanner.py scan --usb <path>
```

### 🧠 Dual-Layer Memory System (Since v1.0)

- **Chronicle**: Automatically saves conversation records with timestamps
- **Monograph**: Important topics with rich metadata

### ⏰ Auto-Save (v2.0+)

Cron jobs run automatically; no manual operation required.

---

## Package Contents

```
hippocampus-for-clawhub/
├── CLAWHUB.yaml          # ClawHub listing metadata
├── CHANGELOG.md          # Changelog
├── PROMPT.md             # AI deployment instructions
├── SKILL.md              # This file (ClawHub skill definition)
├── SPEC.md               # Specification
├── VERSION              # Content: 4.0.0
├── gui_main.py          # PyQt6 GUI entry point (644 lines)
├── scripts/             # Core scripts (3523 lines)
│   ├── memory.py        # Core memory engine (1366 lines)
│   ├── detector.py      # AI tool auto-discovery (299 lines)
│   ├── scanner.py       # Full-coverage backup engine (495 lines)
│   ├── rules_engine.py  # Rule matching engine (387 lines)
│   ├── usb_detector.py  # USB detection (364 lines)
│   ├── streamlit_app.py # Web UI (612 lines)
│   └── task_schema/     # Schema AI task progress table (256 lines)
│       ├── schema_models.py
│       ├── validator.py
│       ├── registry.py
│       └── registry.yaml
```

**Total code: ~4400+ lines**

---

## Installation

### Method 1: ClawHub One-Click Install (Recommended)

```bash
openclaw skill install hippocampus
```

### Method 2: Manual Install

```bash
# Clone this repo
git clone https://github.com/Gabe-luv-Nancy/hippocampus.git hippocampus-for-clawhub
cd hippocampus-for-clawhub

# Initialize
python3 scripts/memory.py init

# Verify
python3 scripts/memory.py status
```

---

## Command Reference

| Command | Description |
|---------|-------------|
| `memory.py init` | Initialize (must run first) |
| `memory.py status` | View memory status |
| `memory.py recall <keyword>` | Precise recall |
| `scanner.py scan` | Full AI tool scan |
| `detector.py` | Detect installed AI tools |
| `task_schema/registry.py list` | View Schema task table |
| `gui_main.py --mode local` | Launch local GUI |

---

## Feature Evolution Log

### v4.0.0 — Schema AI Task Progress Table
**2026-04-22**

- New Schema module (256 lines): `schema_models.py` / `validator.py` / `registry.py`
- `registry.yaml` as AI task registry with enforced check-off mechanism
- validator rule: only all file_refs verified=true allows marking done
- Task dependency chain: depends_on, upstream not done → downstream can't be done
- Dual-end logging: client log + USB log fully traceable
- README rewritten with Schema as the headline feature
- **Technical innovation: YAML-based registry, zero external dependencies, stdlib only**

### v3.1.0 — USB Edition + GUI Enhancement
**2026-03-25**

- Commands unified to `hippo` (from `photon`)
- Context-aware triggering: high-frequency heartbeat / instant trigger / threshold trigger
- PyQt6 GUI, local mode and USB mode
- USB pre-built SQLite, supports offline browsing

### v3.0.0 — AI Tool Auto-Discovery + Full-Coverage Backup
**2026-02-**

- `detector.py` (299 lines): auto-detects AI tools
- `scanner.py` (495 lines): full-coverage backup, SHA256 incremental
- `rules_engine.py` (387 lines): rule matching engine
- Supports 12+ AI tools

### v2.0.0 — Knowledge Graph + Auto-Analysis
**2025-**

- Knowledge graph: Skill → Project → Goal
- Auto-analysis + keyword indexing

### v1.0.0 — Dual-Layer Memory System
**2024-**

- Chronicle (event stream) + Monograph (topic)
- `memory.py` core engine (1366 lines)

---

## Version

4.0.0 | MIT License | by GabetopZ
