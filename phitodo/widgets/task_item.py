"""Task item widget for task list display."""

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import Checkbox, Label, ListItem, Static

from phitodo.domain.enums import TaskPriority, TaskStatus
from phitodo.domain.models import Task
from phitodo.utils.date_format import format_relative_date, is_overdue


class TaskItem(ListItem):
    """Widget for displaying a single task in a list."""

    DEFAULT_CSS = """
    TaskItem {
        height: 3;
        padding: 0 1;
    }

    TaskItem Horizontal {
        height: 100%;
        align: left middle;
    }

    TaskItem .task-checkbox {
        width: 4;
    }

    TaskItem .task-title {
        width: 1fr;
    }

    TaskItem .task-title.completed {
        text-style: strike;
        color: $text-muted;
    }

    TaskItem .task-priority {
        width: 3;
        color: $warning;
    }

    TaskItem .task-priority.high {
        color: $error;
    }

    TaskItem .task-priority.medium {
        color: $warning;
    }

    TaskItem .task-priority.low {
        color: $success;
    }

    TaskItem .task-date {
        width: 12;
        text-align: right;
        color: $text-muted;
    }

    TaskItem .task-date.overdue {
        color: $error;
    }

    TaskItem .task-project {
        width: 15;
        color: $primary;
    }

    TaskItem:hover {
        background: $primary 20%;
    }

    TaskItem.-active {
        background: $primary 40%;
    }
    """

    class Selected(Message):
        """Task was selected."""

        def __init__(self, task: Task):
            super().__init__()
            self.task = task

    class Toggled(Message):
        """Task completion was toggled."""

        def __init__(self, task: Task):
            super().__init__()
            self.task = task

    def __init__(self, task: Task, project_name: str = "", **kwargs):
        super().__init__(**kwargs)
        self.task = task
        self.project_name = project_name

    def compose(self) -> ComposeResult:
        is_completed = self.task.status == TaskStatus.COMPLETED

        with Horizontal():
            # Checkbox
            yield Checkbox(
                value=is_completed,
                classes="task-checkbox",
            )

            # Priority indicator
            priority_icon = self._get_priority_icon()
            priority_class = f"task-priority {self.task.priority.value}"
            yield Static(priority_icon, classes=priority_class)

            # Title
            title_classes = "task-title"
            if is_completed:
                title_classes += " completed"
            yield Label(self.task.title, classes=title_classes)

            # Project name
            if self.project_name:
                yield Static(self.project_name[:14], classes="task-project")

            # Due date
            if self.task.due_date:
                date_classes = "task-date"
                if is_overdue(self.task.due_date):
                    date_classes += " overdue"
                yield Static(
                    format_relative_date(self.task.due_date), classes=date_classes
                )

    def _get_priority_icon(self) -> str:
        """Get priority indicator icon."""
        match self.task.priority:
            case TaskPriority.HIGH:
                return "!!!"
            case TaskPriority.MEDIUM:
                return "!!"
            case TaskPriority.LOW:
                return "!"
            case _:
                return ""

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        """Handle checkbox toggle."""
        event.stop()
        self.post_message(self.Toggled(self.task))
