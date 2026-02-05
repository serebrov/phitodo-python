"""Sidebar navigation widget."""

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.message import Message
from textual.widgets import Label, ListItem, ListView, Static

from phitodo.domain.models import Project, Tag
from phitodo.state.app_state import ViewType


class NavItem(ListItem):
    """Navigation item in sidebar."""

    def __init__(
        self,
        label: str,
        view_type: ViewType,
        count: int = 0,
        hotkey: str = "",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.label_text = label
        self.view_type = view_type
        self.count = count
        self.hotkey = hotkey

    def compose(self) -> ComposeResult:
        content = f"{self.hotkey} {self.label_text}" if self.hotkey else self.label_text
        if self.count > 0:
            content = f"{content} ({self.count})"
        yield Label(content)


class ProjectItem(ListItem):
    """Project item in sidebar."""

    def __init__(self, project: Project, count: int = 0, **kwargs):
        super().__init__(**kwargs)
        self.project = project
        self.count = count

    def compose(self) -> ComposeResult:
        color_indicator = "●" if self.project.color else "○"
        content = f"  {color_indicator} {self.project.name}"
        if self.count > 0:
            content = f"{content} ({self.count})"
        yield Label(content)


class TagItem(ListItem):
    """Tag item in sidebar."""

    def __init__(self, tag: Tag, count: int = 0, **kwargs):
        super().__init__(**kwargs)
        self.tag = tag
        self.count = count

    def compose(self) -> ComposeResult:
        content = f"  # {self.tag.name}"
        if self.count > 0:
            content = f"{content} ({self.count})"
        yield Label(content)


class Sidebar(Container):
    """Sidebar navigation widget."""

    DEFAULT_CSS = """
    Sidebar {
        width: 28;
        background: $surface;
        border-right: solid $primary;
        padding: 1;
    }

    Sidebar ListView {
        background: transparent;
    }

    Sidebar ListItem {
        padding: 0 1;
    }

    Sidebar ListItem:hover {
        background: $primary 20%;
    }

    Sidebar ListItem.-active {
        background: $primary 40%;
    }

    Sidebar .section-header {
        color: $text-muted;
        padding: 1 0 0 1;
        text-style: bold;
    }
    """

    class ViewSelected(Message):
        """Message emitted when a view is selected."""

        def __init__(self, view_type: ViewType):
            super().__init__()
            self.view_type = view_type

    class ProjectSelected(Message):
        """Message emitted when a project is selected."""

        def __init__(self, project_id: str):
            super().__init__()
            self.project_id = project_id

    class TagSelected(Message):
        """Message emitted when a tag is selected."""

        def __init__(self, tag_id: str):
            super().__init__()
            self.tag_id = tag_id

    def __init__(
        self,
        projects: list[Project] = None,
        tags: list[Tag] = None,
        task_counts: dict[str, int] = None,
        current_view: ViewType = ViewType.INBOX,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._projects = projects or []
        self._tags = tags or []
        self._task_counts = task_counts or {}
        self._current_view = current_view

    def compose(self) -> ComposeResult:
        with Vertical():
            # Main navigation
            yield Static("VIEWS", classes="section-header")
            with ListView(id="nav-list"):
                yield NavItem("Inbox", ViewType.INBOX, self._task_counts.get("inbox", 0), "1")
                yield NavItem("Today", ViewType.TODAY, self._task_counts.get("today", 0), "2")
                yield NavItem("Upcoming", ViewType.UPCOMING, self._task_counts.get("upcoming", 0), "3")
                yield NavItem("Anytime", ViewType.ANYTIME, self._task_counts.get("anytime", 0), "4")
                yield NavItem("Completed", ViewType.COMPLETED, 0, "5")
                yield NavItem("Review", ViewType.REVIEW, self._task_counts.get("review", 0), "6")

            yield Static("INTEGRATIONS", classes="section-header")
            with ListView(id="integration-list"):
                yield NavItem("GitHub", ViewType.GITHUB, 0, "7")
                yield NavItem("Toggl", ViewType.TOGGL, 0, "8")
                yield NavItem("Settings", ViewType.SETTINGS, 0, "9")

            if self._projects:
                yield Static("PROJECTS", classes="section-header")
                with ListView(id="project-list"):
                    for project in self._projects:
                        if not project.is_inbox:
                            count = self._task_counts.get(f"project:{project.id}", 0)
                            yield ProjectItem(project, count)

            if self._tags:
                yield Static("TAGS", classes="section-header")
                with ListView(id="tag-list"):
                    for tag in self._tags:
                        count = self._task_counts.get(f"tag:{tag.id}", 0)
                        yield TagItem(tag, count)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle list item selection."""
        item = event.item
        if isinstance(item, NavItem):
            self.post_message(self.ViewSelected(item.view_type))
        elif isinstance(item, ProjectItem):
            self.post_message(self.ProjectSelected(item.project.id))
        elif isinstance(item, TagItem):
            self.post_message(self.TagSelected(item.tag.id))

    def update_counts(self, task_counts: dict[str, int]) -> None:
        """Update task counts in sidebar."""
        self._task_counts = task_counts
        # Force refresh by removing and recomposing
        self.refresh()
