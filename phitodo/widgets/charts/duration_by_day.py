"""Duration by day ASCII bar chart."""

from datetime import date, timedelta

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Static


class DurationByDayChart(Container):
    """ASCII bar chart showing duration by day."""

    DEFAULT_CSS = """
    DurationByDayChart {
        height: auto;
        padding: 1;
        background: $surface;
        margin: 1 0;
    }

    DurationByDayChart .chart-title {
        text-style: bold;
        padding-bottom: 1;
    }

    DurationByDayChart .chart-row {
        height: 1;
    }

    DurationByDayChart .day-label {
        width: 5;
    }

    DurationByDayChart .bar {
        color: $primary;
    }

    DurationByDayChart .duration-label {
        color: $text-muted;
        padding-left: 1;
    }
    """

    BAR_CHAR = "█"
    BAR_HALF = "▌"
    MAX_BAR_WIDTH = 30

    def __init__(
        self,
        data: dict[str, float] = None,
        days: int = 7,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._data = data or {}
        self._days = days

    def compose(self) -> ComposeResult:
        yield Static("Duration by Day", classes="chart-title")

        # Generate dates for the last N days
        today = date.today()
        dates = [(today - timedelta(days=i)).isoformat() for i in range(self._days - 1, -1, -1)]

        # Find max for scaling
        max_hours = max(self._data.values()) if self._data else 1
        max_hours = max(max_hours, 1)  # Avoid division by zero

        for date_str in dates:
            hours = self._data.get(date_str, 0)
            day_name = date.fromisoformat(date_str).strftime("%a")

            # Calculate bar width
            bar_width = int((hours / max_hours) * self.MAX_BAR_WIDTH)
            bar = self.BAR_CHAR * bar_width

            # Format hours
            hours_str = f"{hours:.1f}h" if hours > 0 else "-"

            yield Static(f"{day_name:>3}  {bar:<{self.MAX_BAR_WIDTH}}  {hours_str}")

    def update_data(self, data: dict[str, float]) -> None:
        """Update chart data."""
        self._data = data
        self.remove_children()
        self.mount_all(self.compose())
