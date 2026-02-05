"""Tests for services."""

import pytest

from phitodo.domain.enums import TaskPriority, TaskStatus
from phitodo.services.task_service import TaskService


def test_create_task():
    """Test creating a task."""
    task = TaskService.create_task(
        title="Test Task",
        notes="Some notes",
        priority=TaskPriority.HIGH,
    )

    assert task.title == "Test Task"
    assert task.notes == "Some notes"
    assert task.priority == TaskPriority.HIGH
    assert task.status == TaskStatus.INBOX
    assert task.id is not None
    assert task.created_at is not None


def test_update_task():
    """Test updating a task."""
    task = TaskService.create_task(title="Original")
    updated = TaskService.update_task(task, title="Updated", priority=TaskPriority.LOW)

    assert updated.title == "Updated"
    assert updated.priority == TaskPriority.LOW
    assert updated.id == task.id
    assert updated.updated_at != task.updated_at


def test_complete_task():
    """Test completing a task."""
    task = TaskService.create_task(title="Test")
    completed = TaskService.complete_task(task)

    assert completed.status == TaskStatus.COMPLETED
    assert completed.completed_at is not None


def test_uncomplete_task():
    """Test uncompleting a task."""
    task = TaskService.create_task(title="Test")
    completed = TaskService.complete_task(task)
    uncompleted = TaskService.uncomplete_task(completed)

    assert uncompleted.status == TaskStatus.INBOX
    assert uncompleted.completed_at is None


def test_toggle_completed():
    """Test toggling task completion."""
    task = TaskService.create_task(title="Test")

    toggled = TaskService.toggle_completed(task)
    assert toggled.status == TaskStatus.COMPLETED

    toggled_back = TaskService.toggle_completed(toggled)
    assert toggled_back.status == TaskStatus.INBOX


def test_delete_task():
    """Test soft deleting a task."""
    task = TaskService.create_task(title="Test")
    deleted = TaskService.delete_task(task)

    assert deleted.deleted is True


def test_create_project():
    """Test creating a project."""
    project = TaskService.create_project(
        name="Test Project",
        description="A test project",
        color="#ff0000",
    )

    assert project.name == "Test Project"
    assert project.description == "A test project"
    assert project.color == "#ff0000"
    assert project.id is not None


def test_create_tag():
    """Test creating a tag."""
    tag = TaskService.create_tag(name="urgent", color="#ff0000")

    assert tag.name == "urgent"
    assert tag.color == "#ff0000"
    assert tag.id is not None


def test_get_order_index_between():
    """Test calculating order index between tasks."""
    task1 = TaskService.create_task(title="Task 1", order_index=1.0)
    task2 = TaskService.create_task(title="Task 2", order_index=2.0)

    # Between two tasks
    index = TaskService.get_order_index_between(task1, task2)
    assert index == 1.5

    # At the beginning
    index = TaskService.get_order_index_between(None, task1)
    assert index == 0.5

    # At the end
    index = TaskService.get_order_index_between(task2, None)
    assert index == 3.0
