"""Standup report generation."""

from datetime import date, timedelta
from typing import Optional

from phitodo.domain.models import Task, TogglTimeEntry


def generate_standup_report(
    completed_tasks: list[Task],
    today_tasks: list[Task],
    toggl_entries: Optional[list[TogglTimeEntry]] = None,
    days_back: int = 1,
) -> str:
    """
    Generate a standup report.

    Args:
        completed_tasks: Recently completed tasks
        today_tasks: Tasks due/planned for today
        toggl_entries: Optional Toggl time entries
        days_back: Number of days to look back for completed work

    Returns:
        Formatted standup report string
    """
    lines = []
    cutoff_date = (date.today() - timedelta(days=days_back)).isoformat()

    # Yesterday's work
    lines.append("## Yesterday")
    lines.append("")

    yesterday_tasks = [
        t
        for t in completed_tasks
        if t.completed_at and t.completed_at[:10] >= cutoff_date
    ]

    if yesterday_tasks:
        for task in yesterday_tasks[:10]:  # Limit to 10
            lines.append(f"- {task.title}")
    else:
        lines.append("- No tasks completed")

    # Toggl time if available
    if toggl_entries:
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        yesterday_entries = [e for e in toggl_entries if e.start[:10] == yesterday]

        if yesterday_entries:
            total_hours = sum(
                e.duration_hours for e in yesterday_entries if e.duration > 0
            )
            lines.append("")
            lines.append(f"_Total tracked time: {total_hours:.1f}h_")

    lines.append("")

    # Today's plan
    lines.append("## Today")
    lines.append("")

    if today_tasks:
        for task in today_tasks[:10]:  # Limit to 10
            prefix = "- [ ]"
            if task.due_date and task.due_date[:10] < date.today().isoformat():
                prefix = "- [ ] ⚠️"  # Overdue marker
            lines.append(f"{prefix} {task.title}")
    else:
        lines.append("- No tasks scheduled")

    lines.append("")

    # Blockers section
    lines.append("## Blockers")
    lines.append("")
    lines.append("- None")

    return "\n".join(lines)


def format_report_for_clipboard(report: str) -> str:
    """Format the report for clipboard copying (plain text)."""
    # Remove markdown formatting
    plain = report.replace("## ", "").replace("- [ ] ", "- ").replace("_", "")
    return plain
