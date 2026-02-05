"""Review screen - overdue tasks and stale projects."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Label, ListView, Static

from phitodo.domain.models import Project, Task
from phitodo.services.review_service import ReviewService
from phitodo.widgets.task_list import TaskList


class ReviewScreen(Screen):
    """Screen for reviewing overdue tasks and stale projects."""

    DEFAULT_CSS = """
    ReviewScreen {
        height: 100%;
    }

    ReviewScreen .review-section {
        height: 1fr;
        padding: 1;
    }

    ReviewScreen .section-title {
        text-style: bold;
        padding-bottom: 1;
        border-bottom: solid $surface-darken-2;
    }

    ReviewScreen .stale-list {
        height: 1fr;
        background: $surface;
    }

    ReviewScreen .stale-item {
        padding: 0 1;
        height: 2;
    }

    ReviewScreen .stale-item:hover {
        background: $primary 20%;
    }

    ReviewScreen .no-items {
        color: $text-muted;
        padding: 2;
    }
    """

    def __init__(
        self,
        tasks: list[Task] = None,
        projects: list[Project] = None,
        projects_dict: dict[str, Project] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._tasks = tasks or []
        self._projects = projects or []
        self._projects_dict = projects_dict or {}
        self._overdue_tasks = ReviewService.get_overdue_tasks(self._tasks)
        self._stale_projects = ReviewService.get_stale_projects(
            self._projects, self._tasks
        )

    def compose(self) -> ComposeResult:
        with Horizontal():
            # Overdue tasks
            with Vertical(classes="review-section"):
                yield Static(
                    f"Overdue Tasks ({len(self._overdue_tasks)})",
                    classes="section-title",
                )
                if self._overdue_tasks:
                    yield TaskList(
                        tasks=self._overdue_tasks,
                        projects=self._projects_dict,
                        empty_message="No overdue tasks!",
                        id="overdue-list",
                    )
                else:
                    yield Static("No overdue tasks - great job!", classes="no-items")

            # Stale projects
            with Vertical(classes="review-section"):
                yield Static(
                    f"Stale Projects ({len(self._stale_projects)})",
                    classes="section-title",
                )
                if self._stale_projects:
                    with ListView(classes="stale-list"):
                        for project, last_activity in self._stale_projects:
                            activity_text = ""
                            if last_activity:
                                days = (
                                    __import__("datetime").datetime.now()
                                    - last_activity.replace(tzinfo=None)
                                ).days
                                activity_text = f" ({days}d ago)"
                            yield Label(
                                f"• {project.name}{activity_text}",
                                classes="stale-item",
                            )
                else:
                    yield Static(
                        "No stale projects - all projects active!",
                        classes="no-items",
                    )

    def update_data(
        self,
        tasks: list[Task],
        projects: list[Project],
        projects_dict: dict[str, Project],
    ) -> None:
        """Update review data."""
        self._tasks = tasks
        self._projects = projects
        self._projects_dict = projects_dict
        self._overdue_tasks = ReviewService.get_overdue_tasks(tasks)
        self._stale_projects = ReviewService.get_stale_projects(projects, tasks)
        self.refresh()
