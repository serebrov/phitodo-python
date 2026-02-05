"""Enums for domain models."""

from enum import Enum


class TaskStatus(str, Enum):
    """Task status values."""

    INBOX = "inbox"
    ACTIVE = "active"
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Task priority values."""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskKind(str, Enum):
    """Task kind/type values."""

    TASK = "task"
    BUG = "bug"
    FEATURE = "feature"
    CHORE = "chore"


class TaskSize(str, Enum):
    """Task size estimation values."""

    XS = "xs"
    S = "s"
    M = "m"
    L = "l"
