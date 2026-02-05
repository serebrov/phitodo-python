"""Search modal widget."""

from typing import Optional

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Input, Label, ListView, Static

from phitodo.domain.filters import search_tasks
from phitodo.domain.models import Task
from phitodo.widgets.task_item import TaskItem


class SearchModal(ModalScreen[Optional[Task]]):
    """Modal for searching tasks."""

    DEFAULT_CSS = """
    SearchModal {
        align: center middle;
    }

    SearchModal > Container {
        width: 80;
        height: 30;
        background: $surface;
        border: solid $primary;
        padding: 1 2;
    }

    SearchModal .modal-title {
        text-style: bold;
        padding-bottom: 1;
    }

    SearchModal Input {
        width: 100%;
        margin-bottom: 1;
    }

    SearchModal ListView {
        height: 1fr;
        background: $background;
    }

    SearchModal .hint {
        color: $text-muted;
        padding: 1 0;
    }

    SearchModal .no-results {
        color: $text-muted;
        padding: 2;
        text-align: center;
    }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("enter", "select", "Select"),
    ]

    def __init__(self, tasks: list[Task] = None, **kwargs):
        super().__init__(**kwargs)
        self._tasks = tasks or []
        self._filtered_tasks: list[Task] = []

    def compose(self) -> ComposeResult:
        with Container():
            yield Static("Search Tasks", classes="modal-title")
            yield Input(placeholder="Type to search...", id="search-input")
            yield Static("Press Enter to select, Escape to cancel", classes="hint")
            yield ListView(id="search-results")

    def on_mount(self) -> None:
        """Focus the search input on mount."""
        self.query_one("#search-input", Input).focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        query = event.value.strip()
        results_view = self.query_one("#search-results", ListView)

        # Clear existing results
        results_view.clear()

        if not query:
            self._filtered_tasks = []
            return

        # Filter tasks
        self._filtered_tasks = search_tasks(self._tasks, query)[:20]  # Limit results

        # Add results to list
        for task in self._filtered_tasks:
            results_view.mount(TaskItem(task))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle task selection from list."""
        if isinstance(event.item, TaskItem):
            self.dismiss(event.item.task)

    def action_cancel(self) -> None:
        """Cancel search."""
        self.dismiss(None)

    def action_select(self) -> None:
        """Select the highlighted task."""
        results_view = self.query_one("#search-results", ListView)
        if results_view.index is not None and 0 <= results_view.index < len(self._filtered_tasks):
            self.dismiss(self._filtered_tasks[results_view.index])
