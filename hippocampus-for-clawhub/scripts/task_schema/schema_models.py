"""
HIPPO Task Schema - Data Models
Zero external dependencies - standard library only
"""

from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path
import re


@dataclass
class FileRef:
    """Reference to a file with verification status."""
    path: str
    verified: bool = False

    def to_dict(self) -> dict:
        return {"path": self.path, "verified": self.verified}

    @classmethod
    def from_dict(cls, data: dict) -> "FileRef":
        return cls(path=data["path"], verified=data.get("verified", False))


@dataclass
class TaskSchema:
    """HIPPO task schema with validation support."""
    id: str
    title: str
    status: str
    assignee: str
    phase: str
    file_refs: list[FileRef] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)

    VALID_STATUSES = {"proposed", "approved", "in_progress", "done", "pending"}
    VALID_ASSIGNEES = {"ddb", "ssm", "fdm", "test", "ran", "fep", "bes", "ed"}
    VALID_PHASES = {"v4.1", "v4.2", "v4.3"}

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "assignee": self.assignee,
            "phase": self.phase,
            "file_refs": [fr.to_dict() for fr in self.file_refs],
            "depends_on": self.depends_on,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TaskSchema":
        file_refs = [FileRef.from_dict(fr) for fr in data.get("file_refs", [])]
        return cls(
            id=data["id"],
            title=data["title"],
            status=data["status"],
            assignee=data["assignee"],
            phase=data["phase"],
            file_refs=file_refs,
            depends_on=data.get("depends_on", []),
        )

    @staticmethod
    def validate_id(task_id: str) -> bool:
        """Check if task ID matches HIPPO-YYYYMMDD-NNN format."""
        pattern = r"^HIPPO-\d{8}-\d{3}$"
        return bool(re.match(pattern, task_id))