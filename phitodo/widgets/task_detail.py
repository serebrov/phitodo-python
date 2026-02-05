"""Task detail panel widget."""

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.message import Message
from textual.widgets import Button, Label, Markdown, Static

from phitodo.domain.enums import TaskStatus
from phitodo.domain.models import Project, Task
from phitodo.utils.date_format import format_date, format_relative_date


class TaskDetailPanel(Container):
    """Panel showing task details."""

    DEFAULT_CSS = """
    TaskDetailPanel {
        width: 40;
        background: $surface;
        border-left: solid $primary;
        padding: 1;
    }

    TaskDetailPanel .detail-title {
        text-style: bold;
        padding-bottom: 1;
    }

    TaskDetailPanel .detail-section {
        padding: 1 0;
        border-bottom: solid $surface-darken-2;
    }

    TaskDetailPanel .detail-label {
        color: $text-muted;
        padding-bottom: 0;
    }

    TaskDetailPanel .detail-value {
        padding-left: 1;
    }

    TaskDetailPanel .detail-notes {
        padding: 1;
        background: $surface-darken-1;
    }

    TaskDetailPanel .button-row {
        padding-top: 1;
    }

    TaskDetailPanel .button-row Button {
        margin-right: 1;
    }

    TaskDetailPanel .empty {
        color: $text-muted;
        padding: 2;
        text-align: center;
    }
    """

    class EditRequested(Message):
        """Request to edit the task."""

        def __init__(self, task: Task):
            super().__init__()
            self.task = task

    class DeleteRequested(Message):
        """Request to delete the task."""

        def __init__(self, task: Task):
            super().__init__()
            self.task = task

    class CompleteRequested(Message):
        """Request to toggle task completion."""

        def __init__(self, task: Task):
            super().__init__()
            self.task = task

    def __init__(
        self,
        task: Task = None,
        project: Project = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._task = task
        self._project = project

    def compose(self) -> ComposeResult:
        if not self._task:
            yield Static("Select a task to view details", classes="empty")
            return

        with Vertical():
            # Title
            yield Static(self._task.title, classes="detail-title")

            # Status section
            with Container(classes="detail-section"):
                yield Label("Status", classes="detail-label")
                status_text = self._task.status.value.title()
                if self._task.status == TaskStatus.COMPLETED and self._task.completed_at:
                    status_text += f" ({format_date(self._task.completed_at)})"
                yield Static(status_text, classes="detail-value")

            # Project section
            if self._project:
                with Container(classes="detail-section"):
                    yield Label("Project", classes="detail-label")
                    yield Static(self._project.name, classes="detail-value")

            # Priority section
            if self._task.priority.value != "none":
                with Container(classes="detail-section"):
                    yield Label("Priority", classes="detail-label")
                    yield Static(self._task.priority.value.title(), classes="detail-value")

            # Due date section
            if self._task.due_date:
                with Container(classes="detail-section"):
                    yield Label("Due Date", classes="detail-label")
                    due_text = f"{format_date(self._task.due_date)} ({format_relative_date(self._task.due_date)})"
                    yield Static(due_text, classes="detail-value")

            # Start date section
            if self._task.start_date:
                with Container(classes="detail-section"):
                    yield Label("Start Date", classes="detail-label")
                    yield Static(format_date(self._task.start_date), classes="detail-value")

            # Kind and Size
            if self._task.kind or self._task.size:
                with Container(classes="detail-section"):
                    if self._task.kind:
                        yield Label("Kind", classes="detail-label")
                        yield Static(self._task.kind.value.title(), classes="detail-value")
                    if self._task.size:
                        yield Label("Size", classes="detail-label")
                        yield Static(self._task.size.value.upper(), classes="detail-value")

            # Notes section
            if self._task.notes:
                with Container(classes="detail-section"):
                    yield Label("Notes", classes="detail-label")
                    yield Markdown(self._task.notes, classes="detail-notes")

            # Created/Updated
            with Container(classes="detail-section"):
                yield Label("Created", classes="detail-label")
                yield Static(format_date(self._task.created_at), classes="detail-value")
                if self._task.updated_at != self._task.created_at:
                    yield Label("Updated", classes="detail-label")
                    yield Static(format_date(self._task.updated_at), classes="detail-value")

            # Action buttons
            with Container(classes="button-row"):
                complete_label = "Uncomplete" if self._task.status == TaskStatus.COMPLETED else "Complete"
                yield Button(complete_label, id="complete", variant="success")
                yield Button("Edit", id="edit", variant="primary")
                yield Button("Delete", id="delete", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if not self._task:
            return

        if event.button.id == "edit":
            self.post_message(self.EditRequested(self._task))
        elif event.button.id == "delete":
            self.post_message(self.DeleteRequested(self._task))
        elif event.button.id == "complete":
            self.post_message(self.CompleteRequested(self._task))

    def update_task(self, task: Task = None, project: Project = None) -> None:
        """Update displayed task."""
        self._task = task
        self._project = project
        self.remove_children()
        self.mount_all(self.compose())
