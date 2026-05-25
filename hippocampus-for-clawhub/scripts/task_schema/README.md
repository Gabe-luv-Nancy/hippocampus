# HIPPO V4 — Task Schema System

> Schema-core for HIPPO V4.1. Manages structured task registry with YAML backend and zero-external-dependency validation.

## File Layout

```
scripts/task_schema/
├── schema_models.py   # Data models (TaskSchema, FileRef)
├── validator.py       # Schema validation logic
├── registry.py        # YAML registry read/write/interface
├── registry.yaml      # Task registry (ED-managed)
└── README.md          # This file
```

## Quick Start

```python
import sys
sys.path.insert(0, "scripts/task_schema")

from schema_models import TaskSchema, FileRef
from registry import load_registry, save_registry, get_task, list_tasks

# Load all tasks
registry_path = "scripts/task_schema/registry.yaml"
all_tasks = load_registry(registry_path)
print(f"Loaded {len(all_tasks)} tasks")

# List tasks by status
in_progress = list_tasks(registry_path, status="in_progress")

# Get specific task
task = get_task("HIPPO-20260420-002", registry_path)
print(task.title, task.status)
```

## Data Models

### FileRef

| Field | Type | Description |
|-------|------|-------------|
| `path` | `str` | Real file path (POSIX) |
| `verified` | `bool` | `True` if file existence confirmed |

### TaskSchema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `str` | ✅ | Format: `HIPPO-YYYYMMDD-NNN` |
| `title` | `str` | ✅ | Task title, ≤100 chars |
| `status` | `str` | ✅ | `proposed`/`approved`/`in_progress`/`done`/`pending` |
| `assignee` | `str` | ✅ | `ddb`/`ssm`/`fdm`/`test`/`ran`/`fep`/`bes`/`ed` |
| `phase` | `str` | ✅ | `v4.1`/`v4.2`/`v4.3` |
| `file_refs` | `list[FileRef]` | ❌ | List of file references |
| `depends_on` | `list[str]` | ❌ | List of task IDs this depends on |

## Validation Rules

```python
from validator import validate_task

errors = validate_task(task)
if errors:
    print("Validation failed:", errors)
```

**Rules enforced:**

| Scenario | Valid? | Reason |
|----------|--------|--------|
| `status="proposed"`, no `file_refs` | ✅ | Nothing to verify |
| `status="done"`, all `file_refs[].verified=true` | ✅ | All files confirmed |
| `status="done"`, some `file_refs[].verified=false` | ❌ | Unverified files remain |
| `file_ref.verified=true` but path doesn't exist | ❌ | File not found |
| Invalid `id` format | ❌ | Must match `HIPPO-YYYYMMDD-NNN` |
| Invalid `status`/`assignee`/`phase` | ❌ | Must be in valid set |

## Registry Operations

```python
from registry import (
    load_registry, save_registry,
    add_task, update_task,
    get_task, list_tasks,
    validate_all,
)

registry_path = "scripts/task_schema/registry.yaml"

# Load / Save
tasks = load_registry(registry_path)
save_registry(tasks, registry_path)

# Add a new task
new_task = TaskSchema(
    id="HIPPO-20260422-001",
    title="Example task",
    status="proposed",
    assignee="bes",
    phase="v4.1",
    file_refs=[],
    depends_on=[],
)
add_task(new_task, registry_path)

# Update a task
updated = update_task("HIPPO-20260422-001", registry_path, status="in_progress")

# Query
task = get_task("HIPPO-20260420-001", registry_path)
pending = list_tasks(registry_path, status="pending")

# Validate all tasks
report = validate_all(registry_path)
if report:
    print("Errors found:", report)
else:
    print("All tasks valid ✓")
```

## YAML Registry Format

```yaml
# HIPPO V4 Task Registry
tasks:
  - id: HIPPO-20260420-001
    title: 双版本自检
    status: done
    assignee: ran
    phase: v4.1
    file_refs:
      - path: /mnt/x/CLABIN/HIPPO/hippocampus-for-clawhub/PROMPT.md
        verified: true
    depends_on: []
```

## Constraints

- **Zero external dependencies** — standard library only (`dataclasses`, `pathlib`, `re`, `yaml`)
- All paths are **POSIX-compatible** (no Windows backslash)
- YAML output is human-readable and human-editable
- ED owns `registry.yaml`; programmers do not modify directly