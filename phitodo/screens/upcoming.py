"""Upcoming screen - scheduled future tasks."""

from textual.app import ComposeResult
from textual.screen import Screen

from phitodo.domain.models import Project, Task
from phitodo.widgets.task_list import TaskList


class UpcomingScreen(Screen):
    """Screen showing upcoming scheduled tasks."""

    DEFAULT_CSS = """
    UpcomingScreen {
        height: 100%;
    }
    """

    def __init__(
        self,
        tasks: list[Task] = None,
        projects: dict[str, Project] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._tasks = tasks or []
        self._projects = projects or {}

    def compose(self) -> ComposeResult:
        yield TaskList(
            tasks=self._tasks,
            projects=self._projects,
            empty_message="No upcoming tasks scheduled",
            id="task-list",
        )

    def update_tasks(self, tasks: list[Task], projects: dict[str, Project] = None) -> None:
        """Update the task list."""
        self._tasks = tasks
        if projects is not None:
            self._projects = projects
        task_list = self.query_one("#task-list", TaskList)
        task_list.update_tasks(tasks, projects)
