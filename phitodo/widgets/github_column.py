"""GitHub column widget for displaying issues/PRs."""

from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll
from textual.message import Message
from textual.widgets import Label, ListItem, ListView, Static

from phitodo.domain.models import GitHubIssueItem


class GitHubItem(ListItem):
    """Single GitHub issue or PR item."""

    def __init__(self, item: GitHubIssueItem, **kwargs):
        super().__init__(**kwargs)
        self.item = item

    def compose(self) -> ComposeResult:
        prefix = "PR" if self.item.is_pull_request else "#"
        repo = self.item.repository_full_name or ""
        if repo:
            repo = repo.split("/")[-1][:15]  # Just repo name, truncated

        with Container():
            yield Label(f"{prefix}{self.item.number}: {self.item.title[:40]}")
            if repo:
                yield Static(repo, classes="github-repo")


class GitHubColumn(Container):
    """Column displaying GitHub issues or PRs."""

    DEFAULT_CSS = """
    GitHubColumn {
        width: 1fr;
        height: 100%;
        border: solid $surface-darken-2;
        padding: 0 1;
    }

    GitHubColumn .column-title {
        text-style: bold;
        padding: 1 0;
        border-bottom: solid $surface-darken-2;
    }

    GitHubColumn .column-count {
        color: $text-muted;
    }

    GitHubColumn ListView {
        height: 1fr;
        background: transparent;
    }

    GitHubColumn ListItem {
        height: 3;
        padding: 0 1;
    }

    GitHubColumn ListItem:hover {
        background: $primary 20%;
    }

    GitHubColumn .github-repo {
        color: $text-muted;
        padding-left: 2;
    }

    GitHubColumn .empty-message {
        color: $text-muted;
        padding: 2;
        text-align: center;
    }
    """

    class ItemSelected(Message):
        """A GitHub item was selected."""

        def __init__(self, item: GitHubIssueItem):
            super().__init__()
            self.item = item

    def __init__(
        self,
        title: str,
        items: list[GitHubIssueItem] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._title = title
        self._items = items or []

    def compose(self) -> ComposeResult:
        # Title with count
        count_text = f" ({len(self._items)})" if self._items else ""
        yield Static(f"{self._title}{count_text}", classes="column-title")

        if not self._items:
            yield Static("No items", classes="empty-message")
        else:
            with ListView():
                for item in self._items:
                    yield GitHubItem(item)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle item selection."""
        if isinstance(event.item, GitHubItem):
            self.post_message(self.ItemSelected(event.item.item))

    def update_items(self, items: list[GitHubIssueItem]) -> None:
        """Update the items in the column."""
        self._items = items
        self.remove_children()
        self.mount_all(self.compose())
