"""Tag screen - tasks with a specific tag."""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static

from phitodo.domain.models import Project, Tag, Task
from phitodo.widgets.task_list import TaskList


class TagScreen(Screen):
    """Screen showing tasks with a specific tag."""

    DEFAULT_CSS = """
    TagScreen {
        height: 100%;
    }

    TagScreen .tag-header {
        height: 3;
        background: $surface;
        padding: 1;
        border-bottom: solid $primary;
    }

    TagScreen .tag-name {
        text-style: bold;
    }
    """

    def __init__(
        self,
        tag: Tag = None,
        tasks: list[Task] = None,
        projects_dict: dict[str, Project] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._tag = tag
        self._tasks = tasks or []
        self._projects_dict = projects_dict or {}

    def compose(self) -> ComposeResult:
        if not self._tag:
            yield Static("No tag selected")
            return

        # Tag header
        with Static(classes="tag-header"):
            yield Static(f"# {self._tag.name}", classes="tag-name")

        # Task list
        yield TaskList(
            tasks=self._tasks,
            projects=self._projects_dict,
            empty_message=f"No tasks tagged with #{self._tag.name}",
            id="task-list",
        )

    def update_data(
        self,
        tag: Tag = None,
        tasks: list[Task] = None,
        projects_dict: dict[str, Project] = None,
    ) -> None:
        """Update tag data."""
        if tag is not None:
            self._tag = tag
        if tasks is not None:
            self._tasks = tasks
        if projects_dict is not None:
            self._projects_dict = projects_dict

        # Refresh by recomposing
        self.remove_children()
        self.mount_all(self.compose())
