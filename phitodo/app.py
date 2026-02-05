"""Main Textual application."""

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.widgets import Footer, Header

from phitodo.domain.filters import (
    get_anytime_tasks,
    get_completed_tasks,
    get_inbox_tasks,
    get_overdue_tasks,
    get_project_tasks,
    get_tag_tasks,
    get_today_tasks,
    get_upcoming_tasks,
)
from phitodo.domain.models import Project, StateSnapshot, Task
from phitodo.repository.sqlite_repository import SQLiteRepository
from phitodo.services.github_service import GitHubService
from phitodo.services.task_service import TaskService
from phitodo.services.toggl_service import TogglService
from phitodo.state.app_state import AppState, ViewType
from phitodo.utils.config import Config
from phitodo.widgets.project_modal import ProjectModal
from phitodo.widgets.search_modal import SearchModal
from phitodo.widgets.sidebar import Sidebar
from phitodo.widgets.standup_modal import StandupModal
from phitodo.widgets.task_detail import TaskDetailPanel
from phitodo.widgets.task_list import TaskList
from phitodo.widgets.task_modal import TaskModal
from phitodo.widgets.toolbar import Toolbar


class PhitodoApp(App):
    """Phitodo TUI application."""

    TITLE = "Phitodo"
    CSS_PATH = "css/app.tcss"

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("1", "view_inbox", "Inbox", show=False),
        Binding("2", "view_today", "Today", show=False),
        Binding("3", "view_upcoming", "Upcoming", show=False),
        Binding("4", "view_anytime", "Anytime", show=False),
        Binding("5", "view_completed", "Completed", show=False),
        Binding("6", "view_review", "Review", show=False),
        Binding("7", "view_github", "GitHub", show=False),
        Binding("8", "view_toggl", "Toggl", show=False),
        Binding("9", "view_settings", "Settings", show=False),
        Binding("n", "new_task", "New Task"),
        Binding("N", "new_project", "New Project", show=False),
        Binding("/", "search", "Search"),
        Binding("ctrl+k", "search", "Search", show=False),
        Binding("j", "move_down", "Down", show=False),
        Binding("k", "move_up", "Up", show=False),
        Binding("space", "toggle_complete", "Complete", show=False),
        Binding("enter", "select_task", "Select", show=False),
        Binding("e", "edit_task", "Edit", show=False),
        Binding("d", "delete_task", "Delete", show=False),
        Binding("r", "refresh", "Refresh", show=False),
        Binding("s", "standup", "Standup", show=False),
    ]

    def __init__(self):
        super().__init__()
        self.state = AppState()
        self.config = Config.load()
        self.repository = SQLiteRepository()
        self.github_service = None
        self.toggl_service = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main-container"):
            yield Sidebar(
                projects=self.state.all_projects,
                tags=self.state.all_tags,
                task_counts=self._get_task_counts(),
                id="sidebar",
            )
            with Container(id="content-area"):
                yield Toolbar(title="Inbox", id="toolbar")
                yield TaskList(
                    tasks=self.state.inbox_tasks,
                    projects=self.state.projects,
                    empty_message="Inbox is empty - press 'n' to add a task",
                    id="main-task-list",
                )
        yield Footer()

    async def on_mount(self) -> None:
        """Initialize app on mount."""
        # Load config
        if self.config.github_token:
            self.state.github_token = self.config.github_token
            self.state.github_allowed_repos = self.config.github_allowed_repos
            self.github_service = GitHubService(self.config.github_token)

        if self.config.toggl_token:
            self.state.toggl_token = self.config.toggl_token
            self.state.toggl_hidden_project_ids = self.config.toggl_hidden_project_ids
            self.toggl_service = TogglService(self.config.toggl_token)

        # Initialize database and load data
        await self.repository.init_db()
        snapshot = await self.repository.get_snapshot()
        self.state.load_snapshot(snapshot)

        # Update UI
        self._refresh_task_list()
        self._refresh_sidebar()

    async def on_unmount(self) -> None:
        """Cleanup on unmount."""
        # Save state
        await self._save_state()

        # Close services
        await self.repository.close()
        if self.github_service:
            await self.github_service.close()
        if self.toggl_service:
            await self.toggl_service.close()

    def _get_task_counts(self) -> dict[str, int]:
        """Get task counts for sidebar."""
        counts = {
            "inbox": len(self.state.inbox_tasks),
            "today": len(self.state.today_tasks),
            "upcoming": len(self.state.upcoming_tasks),
            "anytime": len(self.state.anytime_tasks),
            "review": len(self.state.overdue_tasks),
        }

        # Add project counts
        for project in self.state.all_projects:
            tasks = get_project_tasks(self.state.all_tasks, project.id)
            counts[f"project:{project.id}"] = len(tasks)

        # Add tag counts
        for tag in self.state.all_tags:
            tasks = get_tag_tasks(self.state.all_tasks, tag.id)
            counts[f"tag:{tag.id}"] = len(tasks)

        return counts

    def _get_view_title(self) -> str:
        """Get title for current view."""
        titles = {
            ViewType.INBOX: "Inbox",
            ViewType.TODAY: "Today",
            ViewType.UPCOMING: "Upcoming",
            ViewType.ANYTIME: "Anytime",
            ViewType.COMPLETED: "Completed",
            ViewType.REVIEW: "Review",
            ViewType.GITHUB: "GitHub",
            ViewType.TOGGL: "Toggl",
            ViewType.SETTINGS: "Settings",
        }

        if self.state.current_view == ViewType.PROJECT:
            project = self.state.selected_project
            return project.name if project else "Project"
        elif self.state.current_view == ViewType.TAG:
            tag = self.state.tags.get(self.state.viewing_tag_id)
            return f"#{tag.name}" if tag else "Tag"

        return titles.get(self.state.current_view, "Phitodo")

    def _get_empty_message(self) -> str:
        """Get empty message for current view."""
        messages = {
            ViewType.INBOX: "Inbox is empty - press 'n' to add a task",
            ViewType.TODAY: "No tasks for today - enjoy your day!",
            ViewType.UPCOMING: "No upcoming tasks scheduled",
            ViewType.ANYTIME: "No anytime tasks",
            ViewType.COMPLETED: "No completed tasks yet",
            ViewType.REVIEW: "Nothing to review - all caught up!",
        }
        return messages.get(self.state.current_view, "No tasks")

    def _refresh_task_list(self) -> None:
        """Refresh the main task list."""
        task_list = self.query_one("#main-task-list", TaskList)
        task_list.update_tasks(
            self.state.current_tasks,
            self.state.projects,
            self._get_empty_message(),
        )

        toolbar = self.query_one("#toolbar", Toolbar)
        toolbar.set_title(self._get_view_title())

    def _refresh_sidebar(self) -> None:
        """Refresh the sidebar."""
        sidebar = self.query_one("#sidebar", Sidebar)
        sidebar.update_counts(self._get_task_counts())

    async def _save_state(self) -> None:
        """Save current state to database."""
        snapshot = self.state.to_snapshot()
        await self.repository.save_snapshot(snapshot)

    def _switch_view(self, view: ViewType) -> None:
        """Switch to a different view."""
        self.state.set_view(view)
        self._refresh_task_list()

    # View actions
    def action_view_inbox(self) -> None:
        self._switch_view(ViewType.INBOX)

    def action_view_today(self) -> None:
        self._switch_view(ViewType.TODAY)

    def action_view_upcoming(self) -> None:
        self._switch_view(ViewType.UPCOMING)

    def action_view_anytime(self) -> None:
        self._switch_view(ViewType.ANYTIME)

    def action_view_completed(self) -> None:
        self._switch_view(ViewType.COMPLETED)

    def action_view_review(self) -> None:
        self._switch_view(ViewType.REVIEW)

    def action_view_github(self) -> None:
        self._switch_view(ViewType.GITHUB)
        if self.github_service:
            self.run_worker(self._fetch_github_data())

    def action_view_toggl(self) -> None:
        self._switch_view(ViewType.TOGGL)
        if self.toggl_service:
            self.run_worker(self._fetch_toggl_data())

    def action_view_settings(self) -> None:
        self._switch_view(ViewType.SETTINGS)

    # Task actions
    def action_new_task(self) -> None:
        """Open new task modal."""
        def handle_task_result(result: Task | None) -> None:
            if result:
                self.state.add_task(result)
                self.run_worker(self._save_state())
                self._refresh_task_list()
                self._refresh_sidebar()
                self.notify(f"Task '{result.title}' created")

        self.push_screen(
            TaskModal(projects=self.state.all_projects, tags=self.state.all_tags),
            handle_task_result,
        )

    def action_new_project(self) -> None:
        """Open new project modal."""
        def handle_project_result(result: Project | None) -> None:
            if result:
                self.state.add_project(result)
                self.run_worker(self._save_state())
                self._refresh_sidebar()
                self.notify(f"Project '{result.name}' created")

        self.push_screen(ProjectModal(), handle_project_result)

    def action_search(self) -> None:
        """Open search modal."""
        def handle_search_result(result: Task | None) -> None:
            if result:
                self.state.viewing_task_id = result.id

        self.push_screen(
            SearchModal(tasks=self.state.all_tasks),
            handle_search_result,
        )

    def action_move_down(self) -> None:
        """Move selection down in task list."""
        try:
            task_list = self.query_one("#main-task-list", TaskList)
            task_list.select_next()
        except Exception:
            pass

    def action_move_up(self) -> None:
        """Move selection up in task list."""
        try:
            task_list = self.query_one("#main-task-list", TaskList)
            task_list.select_previous()
        except Exception:
            pass

    def action_toggle_complete(self) -> None:
        """Toggle completion of selected task."""
        try:
            task_list = self.query_one("#main-task-list", TaskList)
            task = task_list.get_selected_task()
            if task:
                updated = TaskService.toggle_completed(task)
                self.state.add_task(updated)
                self.run_worker(self._save_state())
                self._refresh_task_list()
                self._refresh_sidebar()
        except Exception:
            pass

    def action_edit_task(self) -> None:
        """Edit selected task."""
        try:
            task_list = self.query_one("#main-task-list", TaskList)
            task = task_list.get_selected_task()
            if task:
                def handle_edit_result(result: Task | None) -> None:
                    if result:
                        self.state.add_task(result)
                        self.run_worker(self._save_state())
                        self._refresh_task_list()
                        self.notify(f"Task '{result.title}' updated")

                self.push_screen(
                    TaskModal(
                        task=task,
                        projects=self.state.all_projects,
                        tags=self.state.all_tags,
                    ),
                    handle_edit_result,
                )
        except Exception:
            pass

    def action_delete_task(self) -> None:
        """Delete selected task."""
        try:
            task_list = self.query_one("#main-task-list", TaskList)
            task = task_list.get_selected_task()
            if task:
                deleted = TaskService.delete_task(task)
                self.state.add_task(deleted)
                self.run_worker(self._save_state())
                self._refresh_task_list()
                self._refresh_sidebar()
                self.notify(f"Task '{task.title}' deleted")
        except Exception:
            pass

    def action_refresh(self) -> None:
        """Refresh data for current view."""
        if self.state.current_view == ViewType.GITHUB and self.github_service:
            self.run_worker(self._fetch_github_data())
        elif self.state.current_view == ViewType.TOGGL and self.toggl_service:
            self.run_worker(self._fetch_toggl_data())

    def action_standup(self) -> None:
        """Show standup report modal."""
        self.push_screen(
            StandupModal(
                completed_tasks=self.state.completed_tasks,
                today_tasks=self.state.today_tasks,
                toggl_entries=self.state.toggl_entries if self.toggl_service else None,
            )
        )

    # Data fetching
    async def _fetch_github_data(self) -> None:
        """Fetch GitHub data."""
        if not self.github_service:
            return

        self.state.github_loading = True
        try:
            issues, review_prs, my_prs = await self.github_service.fetch_all(
                self.state.github_allowed_repos or None
            )
            self.state.set_github_data(issues, review_prs, my_prs)
        except Exception as e:
            self.state.set_github_error(str(e))

    async def _fetch_toggl_data(self) -> None:
        """Fetch Toggl data."""
        if not self.toggl_service:
            return

        self.state.toggl_loading = True
        try:
            entries = await self.toggl_service.get_time_entries(
                hidden_project_ids=self.state.toggl_hidden_project_ids or None
            )
            self.state.set_toggl_entries(entries)
        except Exception as e:
            self.state.set_toggl_error(str(e))

    # Message handlers
    def on_sidebar_view_selected(self, message: Sidebar.ViewSelected) -> None:
        """Handle sidebar view selection."""
        self._switch_view(message.view_type)

    def on_sidebar_project_selected(self, message: Sidebar.ProjectSelected) -> None:
        """Handle sidebar project selection."""
        self.state.view_project(message.project_id)
        self._refresh_task_list()

    def on_sidebar_tag_selected(self, message: Sidebar.TagSelected) -> None:
        """Handle sidebar tag selection."""
        self.state.view_tag(message.tag_id)
        self._refresh_task_list()

    def on_task_list_task_toggled(self, message: TaskList.TaskToggled) -> None:
        """Handle task toggle from task list."""
        updated = TaskService.toggle_completed(message.task)
        self.state.add_task(updated)
        self.run_worker(self._save_state())
        self._refresh_task_list()
        self._refresh_sidebar()

    def on_task_list_task_selected(self, message: TaskList.TaskSelected) -> None:
        """Handle task selection from task list."""
        self.state.viewing_task_id = message.task.id

    def on_toolbar_new_task(self, message: Toolbar.NewTask) -> None:
        """Handle new task request from toolbar."""
        self.action_new_task()

    def on_toolbar_new_project(self, message: Toolbar.NewProject) -> None:
        """Handle new project request from toolbar."""
        self.action_new_project()

    def on_toolbar_search(self, message: Toolbar.Search) -> None:
        """Handle search request from toolbar."""
        self.action_search()

    def on_toolbar_refresh(self, message: Toolbar.Refresh) -> None:
        """Handle refresh request from toolbar."""
        self.action_refresh()

    def on_settings_screen_settings_saved(
        self, message
    ) -> None:
        """Handle settings save."""
        # Update config
        self.config.github_token = message.github_token
        self.config.github_allowed_repos = message.github_repos
        self.config.toggl_token = message.toggl_token
        self.config.toggl_hidden_project_ids = message.toggl_hidden
        self.config.save()

        # Update state
        self.state.github_token = message.github_token
        self.state.github_allowed_repos = message.github_repos
        self.state.toggl_token = message.toggl_token
        self.state.toggl_hidden_project_ids = message.toggl_hidden

        # Recreate services
        if message.github_token:
            if self.github_service:
                self.run_worker(self.github_service.close())
            self.github_service = GitHubService(message.github_token)
        else:
            if self.github_service:
                self.run_worker(self.github_service.close())
            self.github_service = None

        if message.toggl_token:
            if self.toggl_service:
                self.run_worker(self.toggl_service.close())
            self.toggl_service = TogglService(message.toggl_token)
        else:
            if self.toggl_service:
                self.run_worker(self.toggl_service.close())
            self.toggl_service = None
