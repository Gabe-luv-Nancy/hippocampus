"""
HIPPO Task Schema - YAML Registry
Manages task read/write/validation via YAML backend.
Zero external dependencies - standard library only
"""

import yaml
from pathlib import Path
from typing import Optional

from schema_models import TaskSchema, FileRef


def _task_to_dict(task: TaskSchema) -> dict:
    """Convert TaskSchema to a plain dict for YAML serialization."""
    return {
        "id": task.id,
        "title": task.title,
        "status": task.status,
        "assignee": task.assignee,
        "phase": task.phase,
        "file_refs": [{"path": fr.path, "verified": fr.verified} for fr in task.file_refs],
        "depends_on": task.depends_on,
    }


def _dict_to_task(data: dict) -> TaskSchema:
    """Convert a plain dict (from YAML) to a TaskSchema."""
    file_refs = [FileRef(path=fr["path"], verified=fr.get("verified", False)) for fr in data.get("file_refs", [])]
    return TaskSchema(
        id=data["id"],
        title=data["title"],
        status=data["status"],
        assignee=data["assignee"],
        phase=data["phase"],
        file_refs=file_refs,
        depends_on=data.get("depends_on", []),
    )


def load_registry(path: str | Path) -> list[TaskSchema]:
    """Load all tasks from a YAML registry file."""
    p = Path(path)
    if not p.exists():
        return []
    with open(p, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or []
    # Support both flat list and {"tasks": [...]} wrapper
    if isinstance(raw, dict):
        raw = raw.get("tasks", [])
    return [_dict_to_task(item) for item in raw]


def save_registry(tasks: list[TaskSchema], path: str | Path) -> None:
    """Save all tasks to a YAML registry file."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        yaml.safe_dump({"tasks": [_task_to_dict(t) for t in tasks]}, f, allow_unicode=True, sort_keys=False, default_flow_style=False)


def add_task(task: TaskSchema, registry_path: str | Path) -> None:
    """Add a new task to the registry."""
    tasks = load_registry(registry_path)
    if any(t.id == task.id for t in tasks):
        raise ValueError(f"Task with id {task.id} already exists")
    tasks.append(task)
    save_registry(tasks, registry_path)


def update_task(task_id: str, registry_path: str | Path, **kwargs) -> TaskSchema:
    """Update a task's fields. Returns the updated TaskSchema."""
    tasks = load_registry(registry_path)
    for i, task in enumerate(tasks):
        if task.id == task_id:
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            tasks[i] = task
            save_registry(tasks, registry_path)
            return task
    raise KeyError(f"Task {task_id} not found in registry")


def get_task(task_id: str, registry_path: str | Path) -> Optional[TaskSchema]:
    """Retrieve a single task by ID, or None if not found."""
    tasks = load_registry(registry_path)
    for task in tasks:
        if task.id == task_id:
            return task
    return None


def list_tasks(registry_path: str | Path, status: Optional[str] = None) -> list[TaskSchema]:
    """List all tasks, optionally filtered by status."""
    tasks = load_registry(registry_path)
    if status is not None:
        tasks = [t for t in tasks if t.status == status]
    return tasks


def _validate_all_internal(tasks: list[TaskSchema]) -> dict[str, list[str]]:
    """Internal validation across all tasks."""
    from validator import validate_task
    report = {}
    for task in tasks:
        errors = validate_task(task)
        if errors:
            report[task.id] = errors
    return report


def validate_all(registry_path: str | Path) -> dict[str, list[str]]:
    """Validate all tasks in the registry. Returns {task_id: [errors]}."""
    tasks = load_registry(registry_path)
    return _validate_all_internal(tasks)