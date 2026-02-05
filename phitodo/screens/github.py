"""GitHub screen - issues and PRs view."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Static

from phitodo.domain.models import GitHubIssueItem
from phitodo.widgets.github_column import GitHubColumn


class GitHubScreen(Screen):
    """Screen showing GitHub issues and PRs in 3 columns."""

    DEFAULT_CSS = """
    GitHubScreen {
        height: 100%;
    }

    GitHubScreen .loading {
        text-align: center;
        padding: 5;
        color: $text-muted;
    }

    GitHubScreen .error {
        text-align: center;
        padding: 5;
        color: $error;
    }

    GitHubScreen .no-token {
        text-align: center;
        padding: 5;
        color: $text-muted;
    }

    GitHubScreen Horizontal {
        height: 100%;
    }
    """

    def __init__(
        self,
        assigned_issues: list[GitHubIssueItem] = None,
        review_prs: list[GitHubIssueItem] = None,
        my_prs: list[GitHubIssueItem] = None,
        loading: bool = False,
        error: str = None,
        has_token: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._assigned_issues = assigned_issues or []
        self._review_prs = review_prs or []
        self._my_prs = my_prs or []
        self._loading = loading
        self._error = error
        self._has_token = has_token

    def compose(self) -> ComposeResult:
        if not self._has_token:
            yield Static(
                "GitHub token not configured.\nGo to Settings (9) to add your token.",
                classes="no-token",
            )
            return

        if self._loading:
            yield Static("Loading GitHub data...", classes="loading")
            return

        if self._error:
            yield Static(f"Error: {self._error}", classes="error")
            return

        with Horizontal():
            yield GitHubColumn(
                "Assigned Issues",
                self._assigned_issues,
                id="assigned-column",
            )
            yield GitHubColumn(
                "Review Requested",
                self._review_prs,
                id="review-column",
            )
            yield GitHubColumn(
                "My Pull Requests",
                self._my_prs,
                id="my-prs-column",
            )

    def update_data(
        self,
        assigned_issues: list[GitHubIssueItem] = None,
        review_prs: list[GitHubIssueItem] = None,
        my_prs: list[GitHubIssueItem] = None,
        loading: bool = False,
        error: str = None,
    ) -> None:
        """Update GitHub data."""
        if assigned_issues is not None:
            self._assigned_issues = assigned_issues
        if review_prs is not None:
            self._review_prs = review_prs
        if my_prs is not None:
            self._my_prs = my_prs
        self._loading = loading
        self._error = error

        # Refresh by recomposing
        self.remove_children()
        self.mount_all(self.compose())
