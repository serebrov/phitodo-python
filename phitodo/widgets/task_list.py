"""Task list widget."""

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.message import Message
from textual.widgets import Label, ListView, Static

from phitodo.domain.models import Project, Task
from phitodo.widgets.task_item import TaskItem


class TaskList(VerticalScroll):
    """Widget for displaying a list of tasks."""

    DEFAULT_CSS = """
    TaskList {
        height: 1fr;
        background: $background;
    }

    TaskList .empty-message {
        padding: 2;
        color: $text-muted;
        text-align: center;
    }

    TaskList ListView {
        height: auto;
    }
    """

    class TaskSelected(Message):
        """A task was selected."""

        def __init__(self, task: Task):
            super().__init__()
            self.task = task

    class TaskToggled(Message):
        """A task's completion was toggled."""

        def __init__(self, task: Task):
            super().__init__()
            self.task = task

    def __init__(
        self,
        tasks: list[Task] = None,
        projects: dict[str, Project] = None,
        empty_message: str = "No tasks",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._tasks = tasks or []
        self._projects = projects or {}
        self._empty_message = empty_message
        self._selected_index = 0

    def compose(self) -> ComposeResult:
        if not self._tasks:
            yield Static(self._empty_message, classes="empty-message")
        else:
            with ListView(id="task-list-view"):
                for task in self._tasks:
                    project_name = ""
                    if task.project_id and task.project_id in self._projects:
                        project_name = self._projects[task.project_id].name
                    yield TaskItem(task, project_name)

    def on_task_item_toggled(self, event: TaskItem.Toggled) -> None:
        """Handle task toggle from TaskItem."""
        self.post_message(self.TaskToggled(event.task))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle task selection."""
        if isinstance(event.item, TaskItem):
            self.post_message(self.TaskSelected(event.item.task))

    def update_tasks(
        self,
        tasks: list[Task],
        projects: dict[str, Project] = None,
        empty_message: str = None,
    ) -> None:
        """Update the task list."""
        self._tasks = tasks
        if projects is not None:
            self._projects = projects
        if empty_message is not None:
            self._empty_message = empty_message

        # Clear and recompose
        self.remove_children()
        self.mount_all(self.compose())

    def select_next(self) -> None:
        """Select the next task."""
        list_view = self.query_one("#task-list-view", ListView)
        if list_view.index is not None and list_view.index < len(self._tasks) - 1:
            list_view.index += 1

    def select_previous(self) -> None:
        """Select the previous task."""
        list_view = self.query_one("#task-list-view", ListView)
        if list_view.index is not None and list_view.index > 0:
            list_view.index -= 1

    def get_selected_task(self) -> Task | None:
        """Get the currently selected task."""
        try:
            list_view = self.query_one("#task-list-view", ListView)
            if list_view.index is not None and 0 <= list_view.index < len(self._tasks):
                return self._tasks[list_view.index]
        except Exception:
            pass
        return None
