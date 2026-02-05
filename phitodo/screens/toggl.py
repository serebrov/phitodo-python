"""Toggl screen - time tracking view."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Static

from phitodo.domain.models import TogglTimeEntry
from phitodo.widgets.charts.duration_by_day import DurationByDayChart
from phitodo.widgets.charts.project_distribution import ProjectDistributionChart
from phitodo.widgets.toggl_entry_list import TogglEntryList


class TogglScreen(Screen):
    """Screen showing Toggl time entries and charts."""

    DEFAULT_CSS = """
    TogglScreen {
        height: 100%;
    }

    TogglScreen .loading {
        text-align: center;
        padding: 5;
        color: $text-muted;
    }

    TogglScreen .error {
        text-align: center;
        padding: 5;
        color: $error;
    }

    TogglScreen .no-token {
        text-align: center;
        padding: 5;
        color: $text-muted;
    }

    TogglScreen Horizontal {
        height: 100%;
    }

    TogglScreen .entries-panel {
        width: 1fr;
    }

    TogglScreen .charts-panel {
        width: 45;
        background: $surface;
        border-left: solid $primary;
        padding: 1;
    }
    """

    def __init__(
        self,
        entries: list[TogglTimeEntry] = None,
        duration_by_day: dict[str, float] = None,
        duration_by_project: dict[str, float] = None,
        loading: bool = False,
        error: str = None,
        has_token: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._entries = entries or []
        self._duration_by_day = duration_by_day or {}
        self._duration_by_project = duration_by_project or {}
        self._loading = loading
        self._error = error
        self._has_token = has_token

    def compose(self) -> ComposeResult:
        if not self._has_token:
            yield Static(
                "Toggl token not configured.\nGo to Settings (9) to add your token.",
                classes="no-token",
            )
            return

        if self._loading:
            yield Static("Loading Toggl data...", classes="loading")
            return

        if self._error:
            yield Static(f"Error: {self._error}", classes="error")
            return

        with Horizontal():
            # Time entries list
            with Vertical(classes="entries-panel"):
                yield TogglEntryList(self._entries, id="entry-list")

            # Charts panel
            with Vertical(classes="charts-panel"):
                yield DurationByDayChart(self._duration_by_day, id="day-chart")
                yield ProjectDistributionChart(
                    self._duration_by_project, id="project-chart"
                )

    def update_data(
        self,
        entries: list[TogglTimeEntry] = None,
        duration_by_day: dict[str, float] = None,
        duration_by_project: dict[str, float] = None,
        loading: bool = False,
        error: str = None,
    ) -> None:
        """Update Toggl data."""
        if entries is not None:
            self._entries = entries
        if duration_by_day is not None:
            self._duration_by_day = duration_by_day
        if duration_by_project is not None:
            self._duration_by_project = duration_by_project
        self._loading = loading
        self._error = error

        # Refresh by recomposing
        self.remove_children()
        self.mount_all(self.compose())
