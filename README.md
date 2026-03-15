# Hippocampus 🧠

Brain-inspired memory system for OpenClaw AI assistant.

## Features

- **Dual Storage**: Chronicle (temporal) + Monograph (important topics)
- **SQLite Index**: Fast keyword search
- **Auto-Save**: Configurable triggers (time/rounds/tokens)
- **Proactive Memory**: AI remembers things without explicit commands
- **One-Click Setup**: Single confirmation to enable all cron jobs

## Quick Start

```bash
# Install via ClawdHub
clawdhub install hippocampus

# Or manually
git clone https://github.com/Gabe-luv-Nancy/hippocampus.git
```

## Configuration

Edit `USER_CONFIG.md` to customize:

```markdown
TIME_HOURS = 6
ROUND_THRESHOLD = 25
TOKEN_THRESHOLD = 10000
AUTO_SAVE = true
```

## Commands

| Command | Description |
|---------|-------------|
| `/hip setup` | One-click setup all cron jobs |
| `/hip setup-hooks` | Configure session hooks |
| `/hip sync-memory` | Sync to MEMORY.md |
| `/hip new <topic>` | Create new topic |
| `/hip add <content>` | Add content |
| `/hip recall <keyword>` | Search memory |
| `/hip status` | View status |

## Natural Language

Just talk naturally - AI will proactively save important things:

- "remember what we discussed today"
- "what did I say before?"
- "this is important, remember it"

## Files

```
hippocampus/
├── SKILL.md           # Skill documentation
├── USER_CONFIG.md     # User configuration
├── skill.yaml         # Metadata
└── scripts/
    └── memory.py      # Core engine

assets/hippocampus/    # User data directory
├── chronicle/         # Temporal memory (daily sessions)
│   ├── 2026-03-15-project-planning.md
│   └── 2026-03-10-technical-research.md
└── monograph/         # Important topics
    ├── memory-system-architecture.md
    └── automated-workflow-patterns.md
```

## File Formats

### Chronicle Files
Temporal memory stored as markdown files with YAML frontmatter:
- Filename format: `YYYY-MM-DD-topic.md` (uses dashes, not colons)
- Frontmatter includes: date, time, participants, topic, tags

### Monograph Files
Important topics with rich metadata:
- Frontmatter includes: keywords (word frequency based), associations (AI generated)
- Body includes: creator, type, digest, key steps, duration, errors, conclusions, to-do, principles, key info

## License

MIT
