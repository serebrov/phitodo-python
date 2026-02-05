"""Project screen - tasks in a specific project."""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static

from phitodo.domain.models import Project, Task
from phitodo.widgets.task_list import TaskList


class ProjectScreen(Screen):
    """Screen showing tasks in a specific project."""

    DEFAULT_CSS = """
    ProjectScreen {
        height: 100%;
    }

    ProjectScreen .project-header {
        height: 3;
        background: $surface;
        padding: 1;
        border-bottom: solid $primary;
    }

    ProjectScreen .project-name {
        text-style: bold;
    }

    ProjectScreen .project-description {
        color: $text-muted;
    }
    """

    def __init__(
        self,
        project: Project = None,
        tasks: list[Task] = None,
        projects_dict: dict[str, Project] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._project = project
        self._tasks = tasks or []
        self._projects_dict = projects_dict or {}

    def compose(self) -> ComposeResult:
        if not self._project:
            yield Static("No project selected")
            return

        # Project header
        with Static(classes="project-header"):
            yield Static(self._project.name, classes="project-name")
            if self._project.description:
                yield Static(self._project.description, classes="project-description")

        # Task list
        yield TaskList(
            tasks=self._tasks,
            projects=self._projects_dict,
            empty_message=f"No tasks in {self._project.name}",
            id="task-list",
        )

    def update_data(
        self,
        project: Project = None,
        tasks: list[Task] = None,
        projects_dict: dict[str, Project] = None,
    ) -> None:
        """Update project data."""
        if project is not None:
            self._project = project
        if tasks is not None:
            self._tasks = tasks
        if projects_dict is not None:
            self._projects_dict = projects_dict

        # Refresh by recomposing
        self.remove_children()
        self.mount_all(self.compose())
