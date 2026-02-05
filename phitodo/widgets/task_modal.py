"""Task creation/editing modal."""

from typing import Optional

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select, Static

from phitodo.domain.enums import TaskPriority
from phitodo.domain.models import Project, Tag, Task
from phitodo.services.task_service import TaskService


class TaskModal(ModalScreen[Optional[Task]]):
    """Modal for creating or editing a task."""

    DEFAULT_CSS = """
    TaskModal {
        align: center middle;
    }

    TaskModal > Vertical {
        width: 70;
        height: auto;
        max-height: 35;
        background: $surface;
        border: solid $primary;
        padding: 1 2;
    }

    TaskModal .modal-title {
        text-style: bold;
        padding-bottom: 1;
    }

    TaskModal .field-label {
        padding: 0;
        color: $text-muted;
    }

    TaskModal Input, TaskModal Select {
        width: 100%;
    }

    TaskModal TextArea {
        height: 3;
        width: 100%;
    }

    TaskModal .button-row {
        height: 3;
        padding-top: 1;
        align: right middle;
    }

    TaskModal .button-row Button {
        margin-left: 1;
    }

    TaskModal Horizontal {
        height: auto;
    }

    TaskModal .half-width {
        width: 50%;
        padding-right: 1;
    }

    TaskModal .form-scroll {
        height: auto;
        max-height: 25;
    }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("ctrl+s", "save", "Save"),
    ]

    def __init__(
        self,
        task: Optional[Task] = None,
        projects: list[Project] = None,
        tags: list[Tag] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._task = task
        self._projects = projects or []
        self._tags = tags or []
        self._is_editing = task is not None

    def compose(self) -> ComposeResult:
        title = "Edit Task" if self._is_editing else "New Task"

        with Vertical():
            yield Static(f"{title} (Ctrl+S to save, Esc to cancel)", classes="modal-title")

            # Title
            yield Label("Title", classes="field-label")
            yield Input(
                value=self._task.title if self._task else "",
                placeholder="Task title...",
                id="task-title",
            )

            # Project and Priority row
            with Horizontal():
                with Vertical(classes="half-width"):
                    yield Label("Project", classes="field-label")
                    project_options = [(p.name, p.id) for p in self._projects if not p.is_inbox]
                    project_options.insert(0, ("No Project", ""))
                    current_project = self._task.project_id if self._task else ""
                    yield Select(
                        project_options,
                        value=current_project or "",
                        id="task-project",
                    )

                with Vertical(classes="half-width"):
                    yield Label("Priority", classes="field-label")
                    priority_options = [
                        ("None", TaskPriority.NONE.value),
                        ("Low", TaskPriority.LOW.value),
                        ("Medium", TaskPriority.MEDIUM.value),
                        ("High", TaskPriority.HIGH.value),
                    ]
                    current_priority = self._task.priority.value if self._task else TaskPriority.NONE.value
                    yield Select(
                        priority_options,
                        value=current_priority,
                        id="task-priority",
                    )

            # Due date
            yield Label("Due Date (YYYY-MM-DD)", classes="field-label")
            due_date = ""
            if self._task and self._task.due_date:
                due_date = self._task.due_date[:10]
            yield Input(
                value=due_date,
                placeholder="YYYY-MM-DD or leave empty",
                id="task-due-date",
            )

            # Buttons
            with Horizontal(classes="button-row"):
                yield Button("Cancel [Esc]", id="cancel")
                yield Button("Save [Ctrl+S]", id="save", variant="primary")

    def on_mount(self) -> None:
        """Focus the title input on mount."""
        self.query_one("#task-title", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "cancel":
            self.dismiss(None)
        elif event.button.id == "save":
            self._save_task()

    def action_cancel(self) -> None:
        """Cancel and close modal."""
        self.dismiss(None)

    def action_save(self) -> None:
        """Save the task."""
        self._save_task()

    def _save_task(self) -> None:
        """Validate and save the task."""
        title_input = self.query_one("#task-title", Input)
        title = title_input.value.strip()

        if not title:
            title_input.focus()
            return

        project_select = self.query_one("#task-project", Select)
        project_id = project_select.value if project_select.value else None

        priority_select = self.query_one("#task-priority", Select)
        priority = TaskPriority(priority_select.value)

        due_date_input = self.query_one("#task-due-date", Input)
        due_date = due_date_input.value.strip() or None

        if self._is_editing and self._task:
            # Update existing task
            task = TaskService.update_task(
                self._task,
                title=title,
                project_id=project_id,
                priority=priority,
                due_date=due_date,
            )
        else:
            # Create new task
            task = TaskService.create_task(
                title=title,
                project_id=project_id,
                priority=priority,
                due_date=due_date,
            )

        self.dismiss(task)
