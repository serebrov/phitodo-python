"""Review service for finding overdue tasks and stale projects."""

from datetime import date, datetime, timedelta
from typing import Optional

from phitodo.domain.enums import TaskStatus
from phitodo.domain.models import Project, Task


class ReviewService:
    """Service for review-related functionality."""

    @staticmethod
    def get_overdue_tasks(tasks: list[Task]) -> list[Task]:
        """Get tasks that are past their due date."""
        today = date.today().isoformat()
        overdue = []

        for task in tasks:
            if task.deleted:
                continue
            if task.status in (TaskStatus.COMPLETED, TaskStatus.CANCELLED):
                continue
            if task.due_date and task.due_date[:10] < today:
                overdue.append(task)

        return sorted(overdue, key=lambda t: t.due_date or "")

    @staticmethod
    def get_stale_projects(
        projects: list[Project],
        tasks: list[Task],
        days_threshold: int = 7,
    ) -> list[tuple[Project, Optional[datetime]]]:
        """
        Find projects with no recent activity.

        Args:
            projects: List of all projects
            tasks: List of all tasks
            days_threshold: Number of days without activity to consider stale

        Returns:
            List of (project, last_activity_date) tuples
        """
        threshold = datetime.now() - timedelta(days=days_threshold)
        stale = []

        for project in projects:
            if project.deleted or project.is_inbox:
                continue

            # Find tasks in this project
            project_tasks = [
                t
                for t in tasks
                if t.project_id == project.id
                and not t.deleted
                and t.status not in (TaskStatus.COMPLETED, TaskStatus.CANCELLED)
            ]

            if not project_tasks:
                # No active tasks - check project creation date
                try:
                    created = datetime.fromisoformat(
                        project.created_at.replace("Z", "+00:00")
                    )
                    if created.replace(tzinfo=None) < threshold:
                        stale.append((project, None))
                except (ValueError, TypeError):
                    stale.append((project, None))
                continue

            # Find most recent task activity
            last_activity = None
            for task in project_tasks:
                dates = [task.updated_at, task.created_at]
                for date_str in dates:
                    if date_str:
                        try:
                            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                            if last_activity is None or dt > last_activity:
                                last_activity = dt
                        except (ValueError, TypeError):
                            pass

            if last_activity and last_activity.replace(tzinfo=None) < threshold:
                stale.append((project, last_activity))

        return stale

    @staticmethod
    def get_tasks_without_project(tasks: list[Task]) -> list[Task]:
        """Get non-inbox tasks without a project assignment."""
        orphan = []

        for task in tasks:
            if task.deleted:
                continue
            if task.status in (TaskStatus.COMPLETED, TaskStatus.CANCELLED):
                continue
            if task.status == TaskStatus.INBOX:
                continue
            if not task.project_id:
                orphan.append(task)

        return sorted(orphan, key=lambda t: t.order_index)

    @staticmethod
    def get_tasks_needing_review(tasks: list[Task]) -> list[Task]:
        """Get all tasks that need attention during review."""
        review_tasks = []

        # Overdue tasks
        review_tasks.extend(ReviewService.get_overdue_tasks(tasks))

        # Tasks without project (excluding inbox)
        review_tasks.extend(ReviewService.get_tasks_without_project(tasks))

        # Deduplicate while preserving order
        seen = set()
        unique = []
        for task in review_tasks:
            if task.id not in seen:
                seen.add(task.id)
                unique.append(task)

        return unique
