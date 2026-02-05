"""Toggl time entry list widget."""

from collections import defaultdict
from datetime import date

from textual.app import ComposeResult
from textual.containers import Container, Vertical, VerticalScroll
from textual.widgets import Label, Static

from phitodo.domain.models import TogglTimeEntry


class TogglEntryGroup(Container):
    """Group of Toggl entries by project."""

    DEFAULT_CSS = """
    TogglEntryGroup {
        height: auto;
        padding: 1 0;
        border-bottom: solid $surface-darken-2;
    }

    TogglEntryGroup .group-header {
        text-style: bold;
        padding-bottom: 1;
    }

    TogglEntryGroup .group-total {
        color: $primary;
    }

    TogglEntryGroup .entry-item {
        padding: 0 2;
        height: 2;
    }

    TogglEntryGroup .entry-description {
        width: 1fr;
    }

    TogglEntryGroup .entry-duration {
        color: $text-muted;
        text-align: right;
        width: 10;
    }
    """

    def __init__(
        self,
        project_name: str,
        entries: list[TogglTimeEntry],
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.project_name = project_name
        self.entries = entries
        self.total_hours = sum(e.duration_hours for e in entries if e.duration > 0)

    def compose(self) -> ComposeResult:
        # Header with total
        total_str = f"{self.total_hours:.1f}h"
        yield Static(
            f"{self.project_name} [{total_str}]",
            classes="group-header",
        )

        # Individual entries
        for entry in self.entries[:10]:  # Limit displayed entries
            description = entry.description or "No description"
            if len(description) > 40:
                description = description[:37] + "..."

            with Container(classes="entry-item"):
                yield Label(description, classes="entry-description")
                yield Static(entry.duration_formatted, classes="entry-duration")


class TogglEntryList(VerticalScroll):
    """Widget for displaying Toggl time entries grouped by project."""

    DEFAULT_CSS = """
    TogglEntryList {
        height: 1fr;
        padding: 1;
    }

    TogglEntryList .empty-message {
        color: $text-muted;
        padding: 2;
        text-align: center;
    }

    TogglEntryList .summary {
        padding: 1;
        background: $surface;
        margin-bottom: 1;
    }

    TogglEntryList .summary-title {
        text-style: bold;
    }
    """

    def __init__(
        self,
        entries: list[TogglTimeEntry] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._entries = entries or []

    def compose(self) -> ComposeResult:
        if not self._entries:
            yield Static("No time entries", classes="empty-message")
            return

        # Calculate summary
        total_hours = sum(e.duration_hours for e in self._entries if e.duration > 0)
        running = [e for e in self._entries if e.duration < 0]

        # Summary section
        with Container(classes="summary"):
            yield Static(f"Total: {total_hours:.1f}h tracked", classes="summary-title")
            if running:
                yield Static(f"Timer running: {running[0].description or 'No description'}")

        # Group by project
        by_project: dict[str, list[TogglTimeEntry]] = defaultdict(list)
        for entry in self._entries:
            project = entry.project_name or "No Project"
            by_project[project].append(entry)

        # Sort projects by total time
        sorted_projects = sorted(
            by_project.items(),
            key=lambda x: sum(e.duration_hours for e in x[1] if e.duration > 0),
            reverse=True,
        )

        for project_name, entries in sorted_projects:
            yield TogglEntryGroup(project_name, entries)

    def update_entries(self, entries: list[TogglTimeEntry]) -> None:
        """Update displayed entries."""
        self._entries = entries
        self.remove_children()
        self.mount_all(self.compose())
