"""Data models for the application."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from phitodo.domain.enums import TaskKind, TaskPriority, TaskSize, TaskStatus


@dataclass
class Task:
    """Task model."""

    id: str
    title: str
    created_at: str
    updated_at: str
    order_index: float = 0.0
    notes: Optional[str] = None
    due_date: Optional[str] = None
    start_date: Optional[str] = None
    completed_at: Optional[str] = None
    project_id: Optional[str] = None
    section_id: Optional[str] = None
    parent_task_id: Optional[str] = None
    priority: TaskPriority = TaskPriority.NONE
    tags: list[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.INBOX
    repeat_rule: Optional[str] = None
    deleted: bool = False
    kind: Optional[TaskKind] = None
    size: Optional[TaskSize] = None
    assignee: Optional[str] = None
    context_url: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "notes": self.notes,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "dueDate": self.due_date,
            "startDate": self.start_date,
            "completedAt": self.completed_at,
            "projectId": self.project_id,
            "sectionId": self.section_id,
            "parentTaskId": self.parent_task_id,
            "priority": self.priority.value,
            "tags": self.tags,
            "status": self.status.value,
            "repeatRule": self.repeat_rule,
            "orderIndex": self.order_index,
            "deleted": self.deleted,
            "kind": self.kind.value if self.kind else None,
            "size": self.size.value if self.size else None,
            "assignee": self.assignee,
            "contextUrl": self.context_url,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Task":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            notes=data.get("notes"),
            created_at=data.get("createdAt", data.get("created_at", "")),
            updated_at=data.get("updatedAt", data.get("updated_at", "")),
            due_date=data.get("dueDate", data.get("due_date")),
            start_date=data.get("startDate", data.get("start_date")),
            completed_at=data.get("completedAt", data.get("completed_at")),
            project_id=data.get("projectId", data.get("project_id")),
            section_id=data.get("sectionId", data.get("section_id")),
            parent_task_id=data.get("parentTaskId", data.get("parent_task_id")),
            priority=TaskPriority(data.get("priority", "none")),
            tags=data.get("tags", []),
            status=TaskStatus(data.get("status", "inbox")),
            repeat_rule=data.get("repeatRule", data.get("repeat_rule")),
            order_index=data.get("orderIndex", data.get("order_index", 0.0)),
            deleted=data.get("deleted", False),
            kind=TaskKind(data["kind"]) if data.get("kind") else None,
            size=TaskSize(data["size"]) if data.get("size") else None,
            assignee=data.get("assignee"),
            context_url=data.get("contextUrl", data.get("context_url")),
            metadata=data.get("metadata", {}),
        )


@dataclass
class Reminder:
    """Reminder model."""

    id: str
    task_id: str
    at: str
    created_at: str
    updated_at: str
    cancelled_at: Optional[str] = None
    deleted: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "taskId": self.task_id,
            "at": self.at,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "cancelledAt": self.cancelled_at,
            "deleted": self.deleted,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Reminder":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            task_id=data.get("taskId", data.get("task_id", "")),
            at=data["at"],
            created_at=data.get("createdAt", data.get("created_at", "")),
            updated_at=data.get("updatedAt", data.get("updated_at", "")),
            cancelled_at=data.get("cancelledAt", data.get("cancelled_at")),
            deleted=data.get("deleted", False),
        )


@dataclass
class Project:
    """Project model."""

    id: str
    name: str
    created_at: str
    updated_at: str
    order_index: float = 0.0
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    is_inbox: bool = False
    deleted: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "color": self.color,
            "icon": self.icon,
            "orderIndex": self.order_index,
            "isInbox": self.is_inbox,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "deleted": self.deleted,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Project":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            color=data.get("color"),
            icon=data.get("icon"),
            order_index=data.get("orderIndex", data.get("order_index", 0.0)),
            is_inbox=data.get("isInbox", data.get("is_inbox", False)),
            created_at=data.get("createdAt", data.get("created_at", "")),
            updated_at=data.get("updatedAt", data.get("updated_at", "")),
            deleted=data.get("deleted", False),
        )


@dataclass
class Section:
    """Section model for grouping tasks within a project."""

    id: str
    project_id: str
    name: str
    created_at: str
    updated_at: str
    order_index: float = 0.0
    deleted: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "projectId": self.project_id,
            "name": self.name,
            "orderIndex": self.order_index,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "deleted": self.deleted,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Section":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            project_id=data.get("projectId", data.get("project_id", "")),
            name=data["name"],
            order_index=data.get("orderIndex", data.get("order_index", 0.0)),
            created_at=data.get("createdAt", data.get("created_at", "")),
            updated_at=data.get("updatedAt", data.get("updated_at", "")),
            deleted=data.get("deleted", False),
        )


@dataclass
class Tag:
    """Tag model."""

    id: str
    name: str
    created_at: str
    updated_at: str
    color: Optional[str] = None
    deleted: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "deleted": self.deleted,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Tag":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            color=data.get("color"),
            created_at=data.get("createdAt", data.get("created_at", "")),
            updated_at=data.get("updatedAt", data.get("updated_at", "")),
            deleted=data.get("deleted", False),
        )


@dataclass
class GitHubIssueItem:
    """GitHub issue or PR item."""

    id: int
    number: int
    title: str
    html_url: str
    state: str
    repository_full_name: Optional[str] = None
    repository_url: Optional[str] = None
    user_login: Optional[str] = None
    is_pull_request: bool = False

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> "GitHubIssueItem":
        """Create from GitHub API response."""
        repo_name = None
        if data.get("repository"):
            repo_name = data["repository"].get("full_name")
        elif data.get("repository_url"):
            repo_name = data["repository_url"].split("/")[-2:]
            repo_name = "/".join(repo_name) if repo_name else None

        return cls(
            id=data["id"],
            number=data["number"],
            title=data["title"],
            html_url=data["html_url"],
            state=data["state"],
            repository_full_name=repo_name,
            repository_url=data.get("repository_url"),
            user_login=data.get("user", {}).get("login"),
            is_pull_request=bool(data.get("pull_request")),
        )


@dataclass
class TogglTimeEntry:
    """Toggl time entry."""

    id: int
    duration: int
    start: str
    description: Optional[str] = None
    stop: Optional[str] = None
    project_id: Optional[int] = None
    project_name: Optional[str] = None

    @property
    def duration_hours(self) -> float:
        """Get duration in hours."""
        if self.duration < 0:
            # Running timer - calculate from start
            start_dt = datetime.fromisoformat(self.start.replace("Z", "+00:00"))
            now = datetime.now(start_dt.tzinfo)
            return (now - start_dt).total_seconds() / 3600
        return self.duration / 3600

    @property
    def duration_formatted(self) -> str:
        """Get human-readable duration."""
        hours = int(self.duration_hours)
        minutes = int((self.duration_hours - hours) * 60)
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> "TogglTimeEntry":
        """Create from Toggl API response."""
        return cls(
            id=data["id"],
            description=data.get("description"),
            duration=data["duration"],
            start=data["start"],
            stop=data.get("stop"),
            project_id=data.get("project_id"),
            project_name=data.get("project_name"),
        )


@dataclass
class StateSnapshot:
    """Complete application state snapshot for persistence."""

    tasks: dict[str, Task]
    projects: dict[str, Project]
    sections: dict[str, Section]
    tags: dict[str, Tag]
    reminders: dict[str, Reminder]
    version: int = 1

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "tasks": {k: v.to_dict() for k, v in self.tasks.items()},
            "projects": {k: v.to_dict() for k, v in self.projects.items()},
            "sections": {k: v.to_dict() for k, v in self.sections.items()},
            "tags": {k: v.to_dict() for k, v in self.tags.items()},
            "reminders": {k: v.to_dict() for k, v in self.reminders.items()},
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StateSnapshot":
        """Create from dictionary."""
        return cls(
            tasks={k: Task.from_dict(v) for k, v in data.get("tasks", {}).items()},
            projects={
                k: Project.from_dict(v) for k, v in data.get("projects", {}).items()
            },
            sections={
                k: Section.from_dict(v) for k, v in data.get("sections", {}).items()
            },
            tags={k: Tag.from_dict(v) for k, v in data.get("tags", {}).items()},
            reminders={
                k: Reminder.from_dict(v) for k, v in data.get("reminders", {}).items()
            },
            version=data.get("version", 1),
        )

    @classmethod
    def empty(cls) -> "StateSnapshot":
        """Create an empty snapshot."""
        return cls(
            tasks={},
            projects={},
            sections={},
            tags={},
            reminders={},
            version=1,
        )
