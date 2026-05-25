"""
HIPPO Task Schema - Validator
Enforces schema rules and validation logic
Zero external dependencies - standard library only
"""

from pathlib import Path
from schema_models import TaskSchema, FileRef


def validate_file_ref(file_ref: FileRef) -> list[str]:
    """Validate a single FileRef object.
    
    Rules:
    - verified=true requires the file to actually exist at the path
    """
    errors = []
    if file_ref.verified:
        if not Path(file_ref.path).exists():
            errors.append(f"FileRef verified=true but path does not exist: {file_ref.path}")
    return errors


def validate_task(task: TaskSchema) -> list[str]:
    """Validate a complete TaskSchema object.
    
    Rules:
    - status=done requires all file_refs[].verified=true
    - All file_refs with verified=true must have existing paths
    - ID must match HIPPO-YYYYMMDD-NNN format
    - Status must be a valid value
    - Assignee must be a valid value
    - Phase must be a valid value
    """
    errors = []

    # Validate ID format
    if not TaskSchema.validate_id(task.id):
        errors.append(f"Invalid task ID format: {task.id} (expected HIPPO-YYYYMMDD-NNN)")

    # Validate status
    if task.status not in TaskSchema.VALID_STATUSES:
        errors.append(f"Invalid status: {task.status} (valid: {TaskSchema.VALID_STATUSES})")

    # Validate assignee
    if task.assignee not in TaskSchema.VALID_ASSIGNEES:
        errors.append(f"Invalid assignee: {task.assignee} (valid: {TaskSchema.VALID_ASSIGNEES})")

    # Validate phase
    if task.phase not in TaskSchema.VALID_PHASES:
        errors.append(f"Invalid phase: {task.phase} (valid: {TaskSchema.VALID_PHASES})")

    # Validate file_refs
    if task.status == "done":
        unverified = [fr for fr in task.file_refs if not fr.verified]
        if unverified:
            paths = [fr.path for fr in unverified]
            errors.append(f"status=done but unverified file_refs: {paths}")

    # Check each FileRef
    for fr in task.file_refs:
        errors.extend(validate_file_ref(fr))

    return errors


def validate_all(tasks: list[TaskSchema]) -> dict[str, list[str]]:
    """Validate all tasks, return error report as {task_id: [errors]}."""
    report = {}
    for task in tasks:
        errors = validate_task(task)
        if errors:
            report[task.id] = errors
    return report