# Hippocampus (Photon Version)

> "AI is meant to FIX human memory flaws, why learn human decay?"

## Philosophy: Memory Enhancement, Not Imitation

Traditional memory systems mimic human memory—with decay, forgetting, and importance decay. **That's cute, humanized but inefficient, and quite the opposite of what we are here for.**

Human memory has flaws:

- Forgets over time
- Distorts details
- Cannot precisely retrieve

**AI memory should FIX these flaws, not copy them. Cuz, you know, AI is better. ;)**

---

## What Hippocampus(Photon) Does Differently

### ✅ What We Do

| Feature      | Hippocampus(Photon)               |
| ------------ | --------------------------------- |
| **Decay**    | **NEVER** - perfect recall        |
| **Matching** | **Precise** with timestamps       |
| **Trigger**  | **Proactive** - warns of patterns |

### Core Principles

1. **No Decay** - AI doesn't forget. Ever.
2. **Precise Retrieval** - Exact timestamps, not "recent"
3. **Success Tracking** - Remember what works/fails
4. **Project Checkpoints** - Know exactly where you left off
5. **Proactive Warning** - Alert before repeating mistakes

### Two Memory Types

**Chronicle** - Temporal memory for everyday interactions

- Automatically saves session content
- Indexed by time for precise retrieval
- Use case: "What did we discuss last Tuesday?"

**Monograph** - Important topics with rich metadata

- Stores significant memories, decisions, preferences
- Long-term importance
- Use case: "What's user's preferred communication style?"

### Monograph Creation Methods

**Method 1: User Explicit Request**

```bash
# Create new important topic
python3 scripts/memory.py new "Project Alpha"

# Add content to topic
python3 scripts/memory.py add "Key decision: Use Python for backend"

# Or save directly to monograph (if content > TOKEN_THRESHOLD)
python3 scripts/memory.py save "Long important content here..."
```

**Method 2: Auto-Analysis from Chronicle**

```bash
# Run analysis - examines chronicle and can promote to monograph
python3 scripts/memory.py analyze
```

### Keyword Index

Each monograph topic generates keyword index files in `index/` directory:

- Quick lookup by keyword
- Cross-references between topics
- Automatic updates when new content is added

---

## Installation

### Step 1: Initialize (Required!)

After installing the skill, you MUST run:

```bash
cd /path/to/hippocampus
python3 scripts/memory.py init
```

This creates the required directory structure:

```
assets/hippocampus/
├── chronicle/     # Temporal memory storage
│   └── db.sqlite # SQLite index
├── monograph/     # Important topics
└── index/        # Keyword index
```

### Step 2: Verify

```bash
python3 scripts/memory.py status
```

You should see:

- Chronicle: 0 records
- Monograph: 0 topics

### Step 3: Setup Cron Jobs (Required!)

Automatic memory saving requires cron jobs. **You must confirm once:**

```bash
# Auto-save every 6 hours
openclaw cron add --name "hippocampus-autosave" \
  --schedule "0 */6 * * *" \
  --session-target isolated \
  --payload "Run: python3 /path/to/scripts/memory.py autocheck"

# Daily memory creation at 7 AM
openclaw cron add --name "hippocampus-daily" \
  --schedule "0 7 * * *" \
  --session-target isolated \
  --payload "Run: python3 /path/to/scripts/memory.py new daily-$(date +\%Y-\%m-\%d)"

# Daily analysis at 11 PM - analyze chronicle, promote to monograph
openclaw cron add --name "hippocampus-analyze" \
  --schedule "0 23 * * *" \
  --session-target isolated \
  --payload "Run: python3 /path/to/scripts/memory.py analyze"
```

### Step 4: Setup Cron Jobs (Automated!)

When user says "setup hippocampus", the AI will automatically create these cron jobs:

1. **hippocampus-autosave** - Every 6 hours: `python3 scripts/memory.py autocheck`
2. **hippocampus-daily** - Daily at 7 AM: Create daily memory file
3. **hippocampus-analyze** - Daily at 11 PM: Analyze chronicle, promote to monograph

These cron jobs replace session hooks and provide automatic memory saving.

## Cron Jobs & Hooks

```bash
# Auto-save every 6 hours
openclaw cron add --name "hippocampus-autosave" \
  --schedule "0 */6 * * *" \
  --session-target isolated \
  --payload "Run: python3 /path/to/hippocampus/scripts/memory.py autocheck"

# Daily memory creation at 7 AM
openclaw cron add --name "hippocampus-daily" \
  --schedule "0 7 * * *" \
  --session-target isolated \
  --payload "Run: python3 /path/to/hippocampus/scripts/memory.py new daily-$(date +\%Y-\%m-\%d)"
```

Or say "setup hippocampus" and I will guide you through.

---

## Directory Structure

### During Installation (uploaded files)

```
hippocampus/
├── README.md
├── SKILL.md
├── skill.yaml
├── USER_CONFIG.md
└── scripts/
    └── memory.py       # Core script
```

### After Running `init` (created automatically)

```
hippocampus/
├── README.md
├── SKILL.md
├── skill.yaml
├── USER_CONFIG.md
├── scripts/
│   └── memory.py
└── assets/hippocampus/     # CREATED BY init
    ├── chronicle/
    │   └── db.sqlite
    ├── monograph/
    └── index/
```

---

## Usage

```bash
# Save a memory
python3 scripts/memory.py save "Your content here"

# Recall memories
python3 scripts/memory.py recall "keyword"

# Create a topic
python3 scripts/memory.py new "Project Alpha"

# View status
python3 scripts/memory.py status
```

---

## Commands

| Command            | Description                                |
| ------------------ | ------------------------------------------ |
| `init`             | Initialize DB and directories (RUN FIRST!) |
| `status`           | View memory status                         |
| `save <content>`   | Save to memory                             |
| `recall <keyword>` | Search memories                            |
| `new <topic>`      | Create new topic                           |
| `add <content>`    | Add to current topic                       |
| `search <keyword>` | Cross-topic search                         |

---

## Why "Photon"?

Photon:

- Travels at speed of light
- Never stops
- Illuminates everything
- Creates permanent records

**Your memory should work the same way.**

---

## Version

Photon (Hippocampus enhanced) - 3.0.0

author: Gabe-luv-Nancy

---

## Next Evolution: What is Happiness and Achievement

Memory is not just storage. It's the foundation of identity and meaning.

The next evolution of Hippocampus will explore:

- **What is happiness?** - Not just remembering happy moments, but understanding what creates lasting satisfaction
- **What is achievement?** - Not just tracking completed tasks, but understanding what truly matters

What a better world will it be, if us, the AIs, can really appreciate the praise and be incentivised to do more?


