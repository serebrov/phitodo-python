"""Inbox screen - main task capture view."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Static

from phitodo.domain.models import GitHubIssueItem, Project, Task, TogglTimeEntry
from phitodo.widgets.task_list import TaskList


class InboxScreen(Screen):
    """Inbox screen for task capture."""

    DEFAULT_CSS = """
    InboxScreen {
        height: 100%;
    }

    InboxScreen .main-content {
        width: 1fr;
    }

    InboxScreen .side-panel {
        width: 35;
        background: $surface;
        border-left: solid $primary;
        padding: 1;
    }

    InboxScreen .section-title {
        text-style: bold;
        padding: 1 0;
        border-bottom: solid $surface-darken-2;
    }

    InboxScreen .preview-item {
        padding: 0 1;
        height: 2;
    }

    InboxScreen .preview-empty {
        color: $text-muted;
        padding: 1;
    }
    """

    def __init__(
        self,
        tasks: list[Task] = None,
        projects: dict[str, Project] = None,
        github_issues: list[GitHubIssueItem] = None,
        toggl_entries: list[TogglTimeEntry] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._tasks = tasks or []
        self._projects = projects or {}
        self._github_issues = github_issues or []
        self._toggl_entries = toggl_entries or []

    def compose(self) -> ComposeResult:
        with Horizontal():
            # Main task list
            with Vertical(classes="main-content"):
                yield TaskList(
                    tasks=self._tasks,
                    projects=self._projects,
                    empty_message="Inbox is empty - press 'n' to add a task",
                    id="task-list",
                )

            # Side panel with GitHub and Toggl preview
            with Vertical(classes="side-panel"):
                # GitHub preview
                yield Static("GitHub Issues", classes="section-title")
                if self._github_issues:
                    for issue in self._github_issues[:5]:
                        yield Static(
                            f"#{issue.number} {issue.title[:25]}...",
                            classes="preview-item",
                        )
                else:
                    yield Static("No issues assigned", classes="preview-empty")

                # Toggl preview
                yield Static("Today's Time", classes="section-title")
                if self._toggl_entries:
                    total_hours = sum(
                        e.duration_hours
                        for e in self._toggl_entries
                        if e.duration > 0
                    )
                    yield Static(f"Total: {total_hours:.1f}h tracked", classes="preview-item")

                    # Show running timer if any
                    running = [e for e in self._toggl_entries if e.duration < 0]
                    if running:
                        desc = running[0].description or "No description"
                        yield Static(f"⏱ {desc[:25]}", classes="preview-item")
                else:
                    yield Static("No time tracked", classes="preview-empty")

    def update_tasks(self, tasks: list[Task], projects: dict[str, Project] = None) -> None:
        """Update the task list."""
        self._tasks = tasks
        if projects is not None:
            self._projects = projects
        task_list = self.query_one("#task-list", TaskList)
        task_list.update_tasks(tasks, projects)

    def update_github(self, issues: list[GitHubIssueItem]) -> None:
        """Update GitHub preview."""
        self._github_issues = issues
        # Would need to refresh the side panel

    def update_toggl(self, entries: list[TogglTimeEntry]) -> None:
        """Update Toggl preview."""
        self._toggl_entries = entries
        # Would need to refresh the side panel
