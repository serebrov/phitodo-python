"""Task filtering logic."""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional

from phitodo.domain.enums import TaskKind, TaskPriority, TaskSize, TaskStatus
from phitodo.domain.models import Task


@dataclass
class ViewCriteria:
    """Criteria for filtering tasks."""

    statuses: list[TaskStatus] = field(default_factory=list)
    project_ids: list[str] = field(default_factory=list)
    tag_ids: list[str] = field(default_factory=list)
    priorities: list[TaskPriority] = field(default_factory=list)
    kinds: list[TaskKind] = field(default_factory=list)
    sizes: list[TaskSize] = field(default_factory=list)
    assignee: Optional[str] = None
    due_date_start: Optional[str] = None
    due_date_end: Optional[str] = None
    start_date_start: Optional[str] = None
    start_date_end: Optional[str] = None
    include_deleted: bool = False
    search_query: Optional[str] = None


def filter_tasks(tasks: list[Task], criteria: ViewCriteria) -> list[Task]:
    """Filter tasks based on criteria."""
    result = []

    for task in tasks:
        if not criteria.include_deleted and task.deleted:
            continue

        if criteria.statuses and task.status not in criteria.statuses:
            continue

        if criteria.project_ids and task.project_id not in criteria.project_ids:
            continue

        if criteria.tag_ids and not any(tag in task.tags for tag in criteria.tag_ids):
            continue

        if criteria.priorities and task.priority not in criteria.priorities:
            continue

        if criteria.kinds and task.kind not in criteria.kinds:
            continue

        if criteria.sizes and task.size not in criteria.sizes:
            continue

        if criteria.assignee and task.assignee != criteria.assignee:
            continue

        if criteria.due_date_start or criteria.due_date_end:
            if not task.due_date:
                continue
            task_date = task.due_date[:10]  # Get date part
            if criteria.due_date_start and task_date < criteria.due_date_start:
                continue
            if criteria.due_date_end and task_date > criteria.due_date_end:
                continue

        if criteria.start_date_start or criteria.start_date_end:
            if not task.start_date:
                continue
            task_date = task.start_date[:10]
            if criteria.start_date_start and task_date < criteria.start_date_start:
                continue
            if criteria.start_date_end and task_date > criteria.start_date_end:
                continue

        if criteria.search_query:
            query = criteria.search_query.lower()
            if query not in task.title.lower() and (
                not task.notes or query not in task.notes.lower()
            ):
                continue

        result.append(task)

    return result


def get_inbox_tasks(tasks: list[Task]) -> list[Task]:
    """Get tasks in inbox."""
    criteria = ViewCriteria(statuses=[TaskStatus.INBOX])
    return sorted(filter_tasks(tasks, criteria), key=lambda t: t.order_index)


def get_today_tasks(tasks: list[Task]) -> list[Task]:
    """Get tasks due or starting today."""
    today = date.today().isoformat()
    result = []

    for task in tasks:
        if task.deleted:
            continue
        if task.status in (TaskStatus.COMPLETED, TaskStatus.CANCELLED):
            continue

        is_due_today = task.due_date and task.due_date[:10] == today
        is_starting_today = task.start_date and task.start_date[:10] == today
        is_overdue = task.due_date and task.due_date[:10] < today

        if is_due_today or is_starting_today or is_overdue:
            result.append(task)

    # Sort: overdue first, then by due_date
    def sort_key(t: Task) -> tuple:
        is_overdue = t.due_date and t.due_date[:10] < today
        due = t.due_date or "9999-99-99"
        return (not is_overdue, due, t.order_index)

    return sorted(result, key=sort_key)


def get_upcoming_tasks(tasks: list[Task]) -> list[Task]:
    """Get scheduled tasks with future dates."""
    today = date.today().isoformat()
    result = []

    for task in tasks:
        if task.deleted:
            continue
        if task.status in (TaskStatus.COMPLETED, TaskStatus.CANCELLED):
            continue

        has_future_date = (task.due_date and task.due_date[:10] > today) or (
            task.start_date and task.start_date[:10] > today
        )

        if has_future_date:
            result.append(task)

    # Sort by earliest date
    def sort_key(t: Task) -> str:
        dates = []
        if t.due_date:
            dates.append(t.due_date[:10])
        if t.start_date:
            dates.append(t.start_date[:10])
        return min(dates) if dates else "9999-99-99"

    return sorted(result, key=sort_key)


def get_anytime_tasks(tasks: list[Task]) -> list[Task]:
    """Get unscheduled active tasks."""
    result = []

    for task in tasks:
        if task.deleted:
            continue
        if task.status not in (TaskStatus.ACTIVE, TaskStatus.INBOX):
            continue
        if task.due_date or task.start_date:
            continue

        result.append(task)

    return sorted(result, key=lambda t: t.order_index)


def get_completed_tasks(tasks: list[Task], limit: int = 100) -> list[Task]:
    """Get recently completed tasks."""
    criteria = ViewCriteria(statuses=[TaskStatus.COMPLETED])
    result = filter_tasks(tasks, criteria)

    # Sort by completed_at descending
    return sorted(result, key=lambda t: t.completed_at or "", reverse=True)[:limit]


def get_overdue_tasks(tasks: list[Task]) -> list[Task]:
    """Get overdue tasks for review."""
    today = date.today().isoformat()
    result = []

    for task in tasks:
        if task.deleted:
            continue
        if task.status in (TaskStatus.COMPLETED, TaskStatus.CANCELLED):
            continue
        if task.due_date and task.due_date[:10] < today:
            result.append(task)

    return sorted(result, key=lambda t: t.due_date or "")


def get_project_tasks(tasks: list[Task], project_id: str) -> list[Task]:
    """Get tasks in a specific project."""
    result = []

    for task in tasks:
        if task.deleted:
            continue
        if task.status in (TaskStatus.COMPLETED, TaskStatus.CANCELLED):
            continue
        if task.project_id == project_id:
            result.append(task)

    return sorted(result, key=lambda t: t.order_index)


def get_tag_tasks(tasks: list[Task], tag_id: str) -> list[Task]:
    """Get tasks with a specific tag."""
    result = []

    for task in tasks:
        if task.deleted:
            continue
        if task.status in (TaskStatus.COMPLETED, TaskStatus.CANCELLED):
            continue
        if tag_id in task.tags:
            result.append(task)

    return sorted(result, key=lambda t: t.order_index)


def search_tasks(tasks: list[Task], query: str) -> list[Task]:
    """Search tasks by title and notes."""
    criteria = ViewCriteria(search_query=query)
    return filter_tasks(tasks, criteria)
