"""Project creation/editing modal."""

from typing import Optional

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select, Static, TextArea

from phitodo.domain.models import Project
from phitodo.services.task_service import TaskService


# Common project colors
PROJECT_COLORS = [
    ("Red", "#ef4444"),
    ("Orange", "#f97316"),
    ("Yellow", "#eab308"),
    ("Green", "#22c55e"),
    ("Blue", "#3b82f6"),
    ("Purple", "#a855f7"),
    ("Pink", "#ec4899"),
    ("Gray", "#6b7280"),
]


class ProjectModal(ModalScreen[Optional[Project]]):
    """Modal for creating or editing a project."""

    DEFAULT_CSS = """
    ProjectModal {
        align: center middle;
    }

    ProjectModal > Container {
        width: 60;
        height: auto;
        max-height: 30;
        background: $surface;
        border: solid $primary;
        padding: 1 2;
    }

    ProjectModal .modal-title {
        text-style: bold;
        padding-bottom: 1;
    }

    ProjectModal .field-label {
        padding: 1 0 0 0;
        color: $text-muted;
    }

    ProjectModal Input, ProjectModal TextArea, ProjectModal Select {
        width: 100%;
        margin-bottom: 1;
    }

    ProjectModal TextArea {
        height: 4;
    }

    ProjectModal .button-row {
        padding-top: 1;
        align: right middle;
    }

    ProjectModal .button-row Button {
        margin-left: 1;
    }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("ctrl+s", "save", "Save"),
    ]

    def __init__(self, project: Optional[Project] = None, **kwargs):
        super().__init__(**kwargs)
        self._project = project
        self._is_editing = project is not None

    def compose(self) -> ComposeResult:
        title = "Edit Project" if self._is_editing else "New Project"

        with Container():
            yield Static(title, classes="modal-title")

            # Name
            yield Label("Name", classes="field-label")
            yield Input(
                value=self._project.name if self._project else "",
                placeholder="Project name...",
                id="project-name",
            )

            # Description
            yield Label("Description", classes="field-label")
            yield TextArea(
                text=self._project.description or "" if self._project else "",
                id="project-description",
            )

            # Color
            yield Label("Color", classes="field-label")
            color_options = [("No Color", "")] + list(PROJECT_COLORS)
            current_color = self._project.color if self._project else ""
            yield Select(
                color_options,
                value=current_color or "",
                id="project-color",
            )

            # Buttons
            with Horizontal(classes="button-row"):
                yield Button("Cancel", id="cancel")
                yield Button("Save", id="save", variant="primary")

    def on_mount(self) -> None:
        """Focus the name input on mount."""
        self.query_one("#project-name", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "cancel":
            self.dismiss(None)
        elif event.button.id == "save":
            self._save_project()

    def action_cancel(self) -> None:
        """Cancel and close modal."""
        self.dismiss(None)

    def action_save(self) -> None:
        """Save the project."""
        self._save_project()

    def _save_project(self) -> None:
        """Validate and save the project."""
        name_input = self.query_one("#project-name", Input)
        name = name_input.value.strip()

        if not name:
            name_input.focus()
            return

        desc_area = self.query_one("#project-description", TextArea)
        description = desc_area.text.strip() or None

        color_select = self.query_one("#project-color", Select)
        color = color_select.value if color_select.value else None

        if self._is_editing and self._project:
            # Update existing project
            from phitodo.services.task_service import now_iso

            project = Project(
                id=self._project.id,
                name=name,
                description=description,
                color=color,
                icon=self._project.icon,
                order_index=self._project.order_index,
                is_inbox=self._project.is_inbox,
                created_at=self._project.created_at,
                updated_at=now_iso(),
                deleted=self._project.deleted,
            )
        else:
            # Create new project
            project = TaskService.create_project(
                name=name,
                description=description,
                color=color,
            )

        self.dismiss(project)
