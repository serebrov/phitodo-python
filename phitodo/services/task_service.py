"""Task service for task CRUD operations."""

import uuid
from datetime import datetime
from typing import Optional

from phitodo.domain.enums import TaskKind, TaskPriority, TaskSize, TaskStatus
from phitodo.domain.models import Project, Tag, Task


def generate_id() -> str:
    """Generate a unique ID."""
    return str(uuid.uuid4())


def now_iso() -> str:
    """Get current time as ISO string."""
    return datetime.now().isoformat()


class TaskService:
    """Service for task operations."""

    @staticmethod
    def create_task(
        title: str,
        notes: Optional[str] = None,
        project_id: Optional[str] = None,
        due_date: Optional[str] = None,
        start_date: Optional[str] = None,
        priority: TaskPriority = TaskPriority.NONE,
        tags: Optional[list[str]] = None,
        status: TaskStatus = TaskStatus.INBOX,
        kind: Optional[TaskKind] = None,
        size: Optional[TaskSize] = None,
        order_index: float = 0.0,
    ) -> Task:
        """Create a new task."""
        now = now_iso()
        return Task(
            id=generate_id(),
            title=title,
            notes=notes,
            created_at=now,
            updated_at=now,
            project_id=project_id,
            due_date=due_date,
            start_date=start_date,
            priority=priority,
            tags=tags or [],
            status=status,
            kind=kind,
            size=size,
            order_index=order_index,
        )

    @staticmethod
    def update_task(task: Task, **updates) -> Task:
        """Update a task with new values."""
        now = now_iso()
        data = task.to_dict()

        # Map snake_case to camelCase for updates
        field_mapping = {
            "due_date": "dueDate",
            "start_date": "startDate",
            "completed_at": "completedAt",
            "project_id": "projectId",
            "section_id": "sectionId",
            "parent_task_id": "parentTaskId",
            "order_index": "orderIndex",
            "created_at": "createdAt",
            "updated_at": "updatedAt",
            "context_url": "contextUrl",
            "repeat_rule": "repeatRule",
        }

        for key, value in updates.items():
            dict_key = field_mapping.get(key, key)
            if dict_key in data:
                if key in ("priority", "status", "kind", "size") and hasattr(
                    value, "value"
                ):
                    data[dict_key] = value.value
                else:
                    data[dict_key] = value

        data["updatedAt"] = now
        return Task.from_dict(data)

    @staticmethod
    def complete_task(task: Task) -> Task:
        """Mark a task as completed."""
        now = now_iso()
        return TaskService.update_task(
            task, status=TaskStatus.COMPLETED, completed_at=now
        )

    @staticmethod
    def uncomplete_task(task: Task) -> Task:
        """Mark a completed task as inbox."""
        return TaskService.update_task(
            task, status=TaskStatus.INBOX, completed_at=None
        )

    @staticmethod
    def toggle_completed(task: Task) -> Task:
        """Toggle task completion status."""
        if task.status == TaskStatus.COMPLETED:
            return TaskService.uncomplete_task(task)
        return TaskService.complete_task(task)

    @staticmethod
    def delete_task(task: Task) -> Task:
        """Soft delete a task."""
        return TaskService.update_task(task, deleted=True)

    @staticmethod
    def create_project(
        name: str,
        description: Optional[str] = None,
        color: Optional[str] = None,
        icon: Optional[str] = None,
        is_inbox: bool = False,
        order_index: float = 0.0,
    ) -> Project:
        """Create a new project."""
        now = now_iso()
        return Project(
            id=generate_id(),
            name=name,
            description=description,
            color=color,
            icon=icon,
            is_inbox=is_inbox,
            order_index=order_index,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def create_tag(
        name: str,
        color: Optional[str] = None,
    ) -> Tag:
        """Create a new tag."""
        now = now_iso()
        return Tag(
            id=generate_id(),
            name=name,
            color=color,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def get_next_order_index(tasks: list[Task]) -> float:
        """Get the next order index for a new task."""
        if not tasks:
            return 1.0
        max_index = max(t.order_index for t in tasks)
        return max_index + 1.0

    @staticmethod
    def get_order_index_between(before: Optional[Task], after: Optional[Task]) -> float:
        """Get an order index between two tasks for reordering."""
        if before is None and after is None:
            return 1.0
        if before is None:
            return after.order_index / 2
        if after is None:
            return before.order_index + 1.0
        return (before.order_index + after.order_index) / 2
