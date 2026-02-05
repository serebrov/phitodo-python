"""Central application state management."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from textual.reactive import reactive

from phitodo.domain.enums import TaskStatus
from phitodo.domain.filters import (
    get_anytime_tasks,
    get_completed_tasks,
    get_inbox_tasks,
    get_overdue_tasks,
    get_project_tasks,
    get_tag_tasks,
    get_today_tasks,
    get_upcoming_tasks,
    search_tasks,
)
from phitodo.domain.models import (
    GitHubIssueItem,
    Project,
    StateSnapshot,
    Tag,
    Task,
    TogglTimeEntry,
)


class ViewType(str, Enum):
    """Application view types."""

    INBOX = "inbox"
    TODAY = "today"
    UPCOMING = "upcoming"
    ANYTIME = "anytime"
    COMPLETED = "completed"
    REVIEW = "review"
    GITHUB = "github"
    TOGGL = "toggl"
    SETTINGS = "settings"
    PROJECT = "project"
    TAG = "tag"


@dataclass
class AppState:
    """Central application state."""

    # Core data
    tasks: dict[str, Task] = field(default_factory=dict)
    projects: dict[str, Project] = field(default_factory=dict)
    tags: dict[str, Tag] = field(default_factory=dict)

    # GitHub state
    github_token: Optional[str] = None
    github_assigned_issues: list[GitHubIssueItem] = field(default_factory=list)
    github_review_prs: list[GitHubIssueItem] = field(default_factory=list)
    github_my_prs: list[GitHubIssueItem] = field(default_factory=list)
    github_loading: bool = False
    github_error: Optional[str] = None
    github_allowed_repos: list[str] = field(default_factory=list)

    # Toggl state
    toggl_token: Optional[str] = None
    toggl_entries: list[TogglTimeEntry] = field(default_factory=list)
    toggl_loading: bool = False
    toggl_error: Optional[str] = None
    toggl_hidden_project_ids: list[int] = field(default_factory=list)

    # UI state
    current_view: ViewType = ViewType.INBOX
    viewing_project_id: Optional[str] = None
    viewing_tag_id: Optional[str] = None
    viewing_task_id: Optional[str] = None
    search_query: Optional[str] = None
    show_task_modal: bool = False
    show_project_modal: bool = False
    show_search_modal: bool = False
    show_standup_modal: bool = False
    editing_task_id: Optional[str] = None
    editing_project_id: Optional[str] = None

    # Computed properties
    @property
    def all_tasks(self) -> list[Task]:
        """Get all non-deleted tasks."""
        return [t for t in self.tasks.values() if not t.deleted]

    @property
    def all_projects(self) -> list[Project]:
        """Get all non-deleted projects."""
        return sorted(
            [p for p in self.projects.values() if not p.deleted],
            key=lambda p: p.order_index,
        )

    @property
    def all_tags(self) -> list[Tag]:
        """Get all non-deleted tags."""
        return sorted(
            [t for t in self.tags.values() if not t.deleted], key=lambda t: t.name
        )

    @property
    def inbox_tasks(self) -> list[Task]:
        """Get inbox tasks."""
        return get_inbox_tasks(self.all_tasks)

    @property
    def today_tasks(self) -> list[Task]:
        """Get today's tasks."""
        return get_today_tasks(self.all_tasks)

    @property
    def upcoming_tasks(self) -> list[Task]:
        """Get upcoming scheduled tasks."""
        return get_upcoming_tasks(self.all_tasks)

    @property
    def anytime_tasks(self) -> list[Task]:
        """Get unscheduled active tasks."""
        return get_anytime_tasks(self.all_tasks)

    @property
    def completed_tasks(self) -> list[Task]:
        """Get completed tasks."""
        return get_completed_tasks(self.all_tasks)

    @property
    def overdue_tasks(self) -> list[Task]:
        """Get overdue tasks."""
        return get_overdue_tasks(self.all_tasks)

    @property
    def current_tasks(self) -> list[Task]:
        """Get tasks for the current view."""
        if self.search_query:
            return search_tasks(self.all_tasks, self.search_query)

        match self.current_view:
            case ViewType.INBOX:
                return self.inbox_tasks
            case ViewType.TODAY:
                return self.today_tasks
            case ViewType.UPCOMING:
                return self.upcoming_tasks
            case ViewType.ANYTIME:
                return self.anytime_tasks
            case ViewType.COMPLETED:
                return self.completed_tasks
            case ViewType.REVIEW:
                return self.overdue_tasks
            case ViewType.PROJECT:
                if self.viewing_project_id:
                    return get_project_tasks(self.all_tasks, self.viewing_project_id)
                return []
            case ViewType.TAG:
                if self.viewing_tag_id:
                    return get_tag_tasks(self.all_tasks, self.viewing_tag_id)
                return []
            case _:
                return []

    @property
    def selected_task(self) -> Optional[Task]:
        """Get the currently viewed task."""
        if self.viewing_task_id:
            return self.tasks.get(self.viewing_task_id)
        return None

    @property
    def selected_project(self) -> Optional[Project]:
        """Get the currently viewed project."""
        if self.viewing_project_id:
            return self.projects.get(self.viewing_project_id)
        return None

    # State mutations
    def set_view(self, view: ViewType) -> None:
        """Change the current view."""
        self.current_view = view
        self.viewing_project_id = None
        self.viewing_tag_id = None
        self.search_query = None

    def view_project(self, project_id: str) -> None:
        """Switch to project view."""
        self.current_view = ViewType.PROJECT
        self.viewing_project_id = project_id
        self.viewing_tag_id = None

    def view_tag(self, tag_id: str) -> None:
        """Switch to tag view."""
        self.current_view = ViewType.TAG
        self.viewing_tag_id = tag_id
        self.viewing_project_id = None

    def add_task(self, task: Task) -> None:
        """Add or update a task."""
        self.tasks[task.id] = task

    def remove_task(self, task_id: str) -> None:
        """Soft delete a task."""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.deleted = True
            self.tasks[task_id] = task

    def add_project(self, project: Project) -> None:
        """Add or update a project."""
        self.projects[project.id] = project

    def remove_project(self, project_id: str) -> None:
        """Soft delete a project."""
        if project_id in self.projects:
            project = self.projects[project_id]
            project.deleted = True
            self.projects[project_id] = project

    def add_tag(self, tag: Tag) -> None:
        """Add or update a tag."""
        self.tags[tag.id] = tag

    def remove_tag(self, tag_id: str) -> None:
        """Soft delete a tag."""
        if tag_id in self.tags:
            tag = self.tags[tag_id]
            tag.deleted = True
            self.tags[tag_id] = tag

    def load_snapshot(self, snapshot: StateSnapshot) -> None:
        """Load state from a snapshot."""
        self.tasks = dict(snapshot.tasks)
        self.projects = dict(snapshot.projects)
        self.tags = dict(snapshot.tags)

    def to_snapshot(self) -> StateSnapshot:
        """Convert current state to a snapshot."""
        from phitodo.domain.models import Section, Reminder

        return StateSnapshot(
            tasks=dict(self.tasks),
            projects=dict(self.projects),
            sections={},
            tags=dict(self.tags),
            reminders={},
        )

    # GitHub mutations
    def set_github_data(
        self,
        issues: list[GitHubIssueItem],
        review_prs: list[GitHubIssueItem],
        my_prs: list[GitHubIssueItem],
    ) -> None:
        """Set GitHub data from API response."""
        self.github_assigned_issues = issues
        self.github_review_prs = review_prs
        self.github_my_prs = my_prs
        self.github_loading = False
        self.github_error = None

    def set_github_error(self, error: str) -> None:
        """Set GitHub error state."""
        self.github_error = error
        self.github_loading = False

    # Toggl mutations
    def set_toggl_entries(self, entries: list[TogglTimeEntry]) -> None:
        """Set Toggl time entries."""
        self.toggl_entries = entries
        self.toggl_loading = False
        self.toggl_error = None

    def set_toggl_error(self, error: str) -> None:
        """Set Toggl error state."""
        self.toggl_error = error
        self.toggl_loading = False
