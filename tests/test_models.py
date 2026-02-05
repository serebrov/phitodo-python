"""Tests for domain models."""

import pytest

from phitodo.domain.enums import TaskPriority, TaskStatus
from phitodo.domain.models import Project, Task, StateSnapshot


def test_task_creation():
    """Test creating a task."""
    task = Task(
        id="test-1",
        title="Test Task",
        created_at="2024-01-01T00:00:00",
        updated_at="2024-01-01T00:00:00",
    )
    assert task.id == "test-1"
    assert task.title == "Test Task"
    assert task.status == TaskStatus.INBOX
    assert task.priority == TaskPriority.NONE
    assert task.deleted is False


def test_task_to_dict():
    """Test task serialization."""
    task = Task(
        id="test-1",
        title="Test Task",
        notes="Some notes",
        created_at="2024-01-01T00:00:00",
        updated_at="2024-01-01T00:00:00",
        priority=TaskPriority.HIGH,
        status=TaskStatus.ACTIVE,
    )
    data = task.to_dict()
    assert data["id"] == "test-1"
    assert data["title"] == "Test Task"
    assert data["notes"] == "Some notes"
    assert data["priority"] == "high"
    assert data["status"] == "active"


def test_task_from_dict():
    """Test task deserialization."""
    data = {
        "id": "test-1",
        "title": "Test Task",
        "notes": "Some notes",
        "createdAt": "2024-01-01T00:00:00",
        "updatedAt": "2024-01-01T00:00:00",
        "priority": "high",
        "status": "active",
    }
    task = Task.from_dict(data)
    assert task.id == "test-1"
    assert task.title == "Test Task"
    assert task.priority == TaskPriority.HIGH
    assert task.status == TaskStatus.ACTIVE


def test_project_creation():
    """Test creating a project."""
    project = Project(
        id="proj-1",
        name="Test Project",
        created_at="2024-01-01T00:00:00",
        updated_at="2024-01-01T00:00:00",
    )
    assert project.id == "proj-1"
    assert project.name == "Test Project"
    assert project.is_inbox is False


def test_state_snapshot():
    """Test state snapshot serialization."""
    task = Task(
        id="test-1",
        title="Test Task",
        created_at="2024-01-01T00:00:00",
        updated_at="2024-01-01T00:00:00",
    )
    project = Project(
        id="proj-1",
        name="Test Project",
        created_at="2024-01-01T00:00:00",
        updated_at="2024-01-01T00:00:00",
    )
    snapshot = StateSnapshot(
        tasks={"test-1": task},
        projects={"proj-1": project},
        sections={},
        tags={},
        reminders={},
    )

    data = snapshot.to_dict()
    assert "test-1" in data["tasks"]
    assert "proj-1" in data["projects"]

    restored = StateSnapshot.from_dict(data)
    assert "test-1" in restored.tasks
    assert restored.tasks["test-1"].title == "Test Task"
