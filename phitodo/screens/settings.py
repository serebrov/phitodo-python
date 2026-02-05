"""Settings screen - configuration view."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Button, Input, Label, Static, TextArea


class SettingsScreen(Screen):
    """Screen for configuring app settings."""

    DEFAULT_CSS = """
    SettingsScreen {
        height: 100%;
        padding: 1;
    }

    SettingsScreen .settings-section {
        background: $surface;
        padding: 1 2;
        margin-bottom: 1;
    }

    SettingsScreen .section-title {
        text-style: bold;
        padding-bottom: 1;
        border-bottom: solid $surface-darken-2;
        margin-bottom: 1;
    }

    SettingsScreen .field-row {
        height: auto;
        margin-bottom: 1;
    }

    SettingsScreen .field-label {
        color: $text-muted;
        padding-bottom: 0;
    }

    SettingsScreen .field-hint {
        color: $text-muted;
        padding-top: 0;
    }

    SettingsScreen Input {
        width: 100%;
    }

    SettingsScreen TextArea {
        width: 100%;
        height: 4;
    }

    SettingsScreen .button-row {
        padding-top: 1;
    }

    SettingsScreen .button-row Button {
        margin-right: 1;
    }

    SettingsScreen .status-valid {
        color: $success;
    }

    SettingsScreen .status-invalid {
        color: $error;
    }
    """

    class SettingsSaved(Message):
        """Settings were saved."""

        def __init__(
            self,
            github_token: str,
            github_repos: list[str],
            toggl_token: str,
            toggl_hidden: list[int],
        ):
            super().__init__()
            self.github_token = github_token
            self.github_repos = github_repos
            self.toggl_token = toggl_token
            self.toggl_hidden = toggl_hidden

    def __init__(
        self,
        github_token: str = "",
        github_allowed_repos: list[str] = None,
        toggl_token: str = "",
        toggl_hidden_project_ids: list[int] = None,
        github_valid: bool = None,
        toggl_valid: bool = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._github_token = github_token or ""
        self._github_repos = github_allowed_repos or []
        self._toggl_token = toggl_token or ""
        self._toggl_hidden = toggl_hidden_project_ids or []
        self._github_valid = github_valid
        self._toggl_valid = toggl_valid

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            # GitHub settings
            with Container(classes="settings-section"):
                yield Static("GitHub Integration", classes="section-title")

                with Container(classes="field-row"):
                    yield Label("Personal Access Token", classes="field-label")
                    yield Input(
                        value=self._github_token,
                        password=True,
                        placeholder="ghp_xxxxxxxxxxxx",
                        id="github-token",
                    )
                    status = self._get_status_text(self._github_valid)
                    yield Static(status, id="github-status")
                    yield Static(
                        "Create at: github.com/settings/tokens (needs repo scope)",
                        classes="field-hint",
                    )

                with Container(classes="field-row"):
                    yield Label("Allowed Repositories (one per line)", classes="field-label")
                    yield TextArea(
                        text="\n".join(self._github_repos),
                        id="github-repos",
                    )
                    yield Static(
                        "Format: owner/repo (leave empty for all)",
                        classes="field-hint",
                    )

            # Toggl settings
            with Container(classes="settings-section"):
                yield Static("Toggl Integration", classes="section-title")

                with Container(classes="field-row"):
                    yield Label("API Token", classes="field-label")
                    yield Input(
                        value=self._toggl_token,
                        password=True,
                        placeholder="xxxxxxxxxxxxxxxx",
                        id="toggl-token",
                    )
                    status = self._get_status_text(self._toggl_valid)
                    yield Static(status, id="toggl-status")
                    yield Static(
                        "Find at: track.toggl.com/profile",
                        classes="field-hint",
                    )

                with Container(classes="field-row"):
                    yield Label("Hidden Project IDs (comma-separated)", classes="field-label")
                    yield Input(
                        value=",".join(str(i) for i in self._toggl_hidden),
                        placeholder="12345, 67890",
                        id="toggl-hidden",
                    )
                    yield Static(
                        "Projects to exclude from time tracking view",
                        classes="field-hint",
                    )

            # Save button
            with Horizontal(classes="button-row"):
                yield Button("Save Settings", id="save", variant="primary")
                yield Button("Validate Tokens", id="validate")

    def _get_status_text(self, valid: bool = None) -> str:
        """Get status text based on validation state."""
        if valid is None:
            return ""
        elif valid:
            return "✓ Valid"
        else:
            return "✗ Invalid"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "save":
            self._save_settings()
        elif event.button.id == "validate":
            # Would trigger token validation
            pass

    def _save_settings(self) -> None:
        """Save settings and emit message."""
        github_token = self.query_one("#github-token", Input).value.strip()
        github_repos_text = self.query_one("#github-repos", TextArea).text
        github_repos = [
            r.strip()
            for r in github_repos_text.split("\n")
            if r.strip()
        ]

        toggl_token = self.query_one("#toggl-token", Input).value.strip()
        toggl_hidden_text = self.query_one("#toggl-hidden", Input).value
        toggl_hidden = []
        for part in toggl_hidden_text.split(","):
            part = part.strip()
            if part.isdigit():
                toggl_hidden.append(int(part))

        self.post_message(
            self.SettingsSaved(
                github_token=github_token,
                github_repos=github_repos,
                toggl_token=toggl_token,
                toggl_hidden=toggl_hidden,
            )
        )

        self.notify("Settings saved!")

    def update_validation(self, github_valid: bool = None, toggl_valid: bool = None) -> None:
        """Update validation status display."""
        if github_valid is not None:
            self._github_valid = github_valid
            status = self.query_one("#github-status", Static)
            status.update(self._get_status_text(github_valid))
            status.set_class(github_valid, "status-valid")
            status.set_class(not github_valid, "status-invalid")

        if toggl_valid is not None:
            self._toggl_valid = toggl_valid
            status = self.query_one("#toggl-status", Static)
            status.update(self._get_status_text(toggl_valid))
            status.set_class(toggl_valid, "status-valid")
            status.set_class(not toggl_valid, "status-invalid")
