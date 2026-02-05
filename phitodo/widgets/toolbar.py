"""Toolbar widget with action buttons."""

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import Button, Static


class Toolbar(Static):
    """Toolbar with action buttons."""

    DEFAULT_CSS = """
    Toolbar {
        height: 3;
        background: $surface;
        border-bottom: solid $primary;
        padding: 0 1;
    }

    Toolbar Horizontal {
        height: 100%;
        align: left middle;
    }

    Toolbar Button {
        min-width: 10;
        margin-right: 1;
    }

    Toolbar .title {
        padding: 0 2;
        text-style: bold;
        color: $text;
    }

    Toolbar .spacer {
        width: 1fr;
    }

    Toolbar .hint {
        color: $text-muted;
        padding: 0 1;
    }
    """

    class NewTask(Message):
        """Request to create a new task."""

    class NewProject(Message):
        """Request to create a new project."""

    class Search(Message):
        """Request to open search."""

    class Refresh(Message):
        """Request to refresh data."""

    def __init__(self, title: str = "Inbox", show_refresh: bool = False, **kwargs):
        super().__init__(**kwargs)
        self._title = title
        self._show_refresh = show_refresh

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Static(self._title, classes="title")
            yield Static("", classes="spacer")
            yield Button("New Task (n)", id="new-task", variant="primary")
            yield Button("New Project (N)", id="new-project")
            yield Button("Search (/)", id="search")
            if self._show_refresh:
                yield Button("Refresh (r)", id="refresh")
            yield Static("[j/k] Navigate  [space] Complete  [q] Quit", classes="hint")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id
        if button_id == "new-task":
            self.post_message(self.NewTask())
        elif button_id == "new-project":
            self.post_message(self.NewProject())
        elif button_id == "search":
            self.post_message(self.Search())
        elif button_id == "refresh":
            self.post_message(self.Refresh())

    def set_title(self, title: str) -> None:
        """Update toolbar title."""
        self._title = title
        title_widget = self.query_one(".title", Static)
        title_widget.update(title)
