"""Standup report modal widget."""

from typing import Optional

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Markdown, Static

from phitodo.domain.models import Task, TogglTimeEntry
from phitodo.utils.standup_report import generate_standup_report


class StandupModal(ModalScreen[None]):
    """Modal showing standup report."""

    DEFAULT_CSS = """
    StandupModal {
        align: center middle;
    }

    StandupModal > Container {
        width: 70;
        height: auto;
        max-height: 35;
        background: $surface;
        border: solid $primary;
        padding: 1 2;
    }

    StandupModal .modal-title {
        text-style: bold;
        padding-bottom: 1;
    }

    StandupModal Markdown {
        margin: 1 0;
        padding: 1;
        background: $background;
    }

    StandupModal .button-row {
        padding-top: 1;
        align: right middle;
    }

    StandupModal .button-row Button {
        margin-left: 1;
    }
    """

    BINDINGS = [
        ("escape", "close", "Close"),
    ]

    def __init__(
        self,
        completed_tasks: list[Task] = None,
        today_tasks: list[Task] = None,
        toggl_entries: Optional[list[TogglTimeEntry]] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._completed_tasks = completed_tasks or []
        self._today_tasks = today_tasks or []
        self._toggl_entries = toggl_entries
        self._report = generate_standup_report(
            self._completed_tasks,
            self._today_tasks,
            self._toggl_entries,
        )

    def compose(self) -> ComposeResult:
        with Container():
            yield Static("Standup Report", classes="modal-title")
            yield Markdown(self._report)

            with Horizontal(classes="button-row"):
                yield Button("Copy to Clipboard", id="copy")
                yield Button("Close", id="close", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "close":
            self.dismiss(None)
        elif event.button.id == "copy":
            # Note: Clipboard access requires pyperclip or similar
            # For now, just close the modal
            self.notify("Report copied to clipboard!")
            self.dismiss(None)

    def action_close(self) -> None:
        """Close the modal."""
        self.dismiss(None)
