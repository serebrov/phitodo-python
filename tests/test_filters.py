"""Tests for task filtering."""

from datetime import date, timedelta

import pytest

from phitodo.domain.enums import TaskPriority, TaskStatus
from phitodo.domain.filters import (
    ViewCriteria,
    filter_tasks,
    get_inbox_tasks,
    get_overdue_tasks,
    get_today_tasks,
    search_tasks,
)
from phitodo.domain.models import Task


def make_task(
    id: str,
    title: str,
    status: TaskStatus = TaskStatus.INBOX,
    due_date: str = None,
    deleted: bool = False,
) -> Task:
    """Helper to create a task."""
    return Task(
        id=id,
        title=title,
        status=status,
        due_date=due_date,
        deleted=deleted,
        created_at="2024-01-01T00:00:00",
        updated_at="2024-01-01T00:00:00",
    )


def test_filter_by_status():
    """Test filtering tasks by status."""
    tasks = [
        make_task("1", "Inbox Task", TaskStatus.INBOX),
        make_task("2", "Active Task", TaskStatus.ACTIVE),
        make_task("3", "Completed Task", TaskStatus.COMPLETED),
    ]

    criteria = ViewCriteria(statuses=[TaskStatus.INBOX])
    result = filter_tasks(tasks, criteria)

    assert len(result) == 1
    assert result[0].id == "1"


def test_filter_excludes_deleted():
    """Test that deleted tasks are excluded by default."""
    tasks = [
        make_task("1", "Normal Task"),
        make_task("2", "Deleted Task", deleted=True),
    ]

    criteria = ViewCriteria()
    result = filter_tasks(tasks, criteria)

    assert len(result) == 1
    assert result[0].id == "1"


def test_get_inbox_tasks():
    """Test getting inbox tasks."""
    tasks = [
        make_task("1", "Inbox 1", TaskStatus.INBOX),
        make_task("2", "Active", TaskStatus.ACTIVE),
        make_task("3", "Inbox 2", TaskStatus.INBOX),
    ]

    result = get_inbox_tasks(tasks)
    assert len(result) == 2
    assert all(t.status == TaskStatus.INBOX for t in result)


def test_get_today_tasks():
    """Test getting today's tasks."""
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    tasks = [
        make_task("1", "Due Today", TaskStatus.ACTIVE, due_date=today),
        make_task("2", "Overdue", TaskStatus.ACTIVE, due_date=yesterday),
        make_task("3", "Future", TaskStatus.ACTIVE, due_date=tomorrow),
        make_task("4", "No Date", TaskStatus.ACTIVE),
    ]

    result = get_today_tasks(tasks)
    assert len(result) == 2  # Today + Overdue
    assert {t.id for t in result} == {"1", "2"}


def test_get_overdue_tasks():
    """Test getting overdue tasks."""
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    today = date.today().isoformat()

    tasks = [
        make_task("1", "Overdue", TaskStatus.ACTIVE, due_date=yesterday),
        make_task("2", "Due Today", TaskStatus.ACTIVE, due_date=today),
        make_task("3", "Completed Overdue", TaskStatus.COMPLETED, due_date=yesterday),
    ]

    result = get_overdue_tasks(tasks)
    assert len(result) == 1
    assert result[0].id == "1"


def test_search_tasks():
    """Test searching tasks by title and notes."""
    tasks = [
        make_task("1", "Buy groceries"),
        make_task("2", "Review code"),
        make_task("3", "Write documentation"),
    ]
    # Add notes to one task
    tasks[2].notes = "Need to buy time to write"

    result = search_tasks(tasks, "buy")
    assert len(result) == 2  # "Buy groceries" and task with "buy" in notes
