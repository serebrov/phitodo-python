"""Project distribution ASCII bar chart."""

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Static


class ProjectDistributionChart(Container):
    """ASCII bar chart showing time distribution by project."""

    DEFAULT_CSS = """
    ProjectDistributionChart {
        height: auto;
        padding: 1;
        background: $surface;
        margin: 1 0;
    }

    ProjectDistributionChart .chart-title {
        text-style: bold;
        padding-bottom: 1;
    }
    """

    BAR_CHAR = "█"
    MAX_BAR_WIDTH = 25
    MAX_PROJECTS = 8

    def __init__(
        self,
        data: dict[str, float] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._data = data or {}

    def compose(self) -> ComposeResult:
        yield Static("Time by Project", classes="chart-title")

        if not self._data:
            yield Static("No data")
            return

        # Sort by hours descending and limit
        sorted_data = sorted(self._data.items(), key=lambda x: x[1], reverse=True)
        sorted_data = sorted_data[: self.MAX_PROJECTS]

        # Find max for scaling
        max_hours = max(h for _, h in sorted_data) if sorted_data else 1

        total_hours = sum(self._data.values())

        for project, hours in sorted_data:
            # Truncate project name
            project_display = project[:12].ljust(12)

            # Calculate bar width
            bar_width = int((hours / max_hours) * self.MAX_BAR_WIDTH)
            bar = self.BAR_CHAR * bar_width

            # Calculate percentage
            pct = (hours / total_hours * 100) if total_hours > 0 else 0

            yield Static(f"{project_display}  {bar:<{self.MAX_BAR_WIDTH}}  {hours:.1f}h ({pct:.0f}%)")

        # Total row
        yield Static("")
        yield Static(f"{'Total':<12}  {' ' * self.MAX_BAR_WIDTH}  {total_hours:.1f}h")

    def update_data(self, data: dict[str, float]) -> None:
        """Update chart data."""
        self._data = data
        self.remove_children()
        self.mount_all(self.compose())
