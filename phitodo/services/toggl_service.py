"""Toggl Track API service."""

import base64
from datetime import date, datetime, timedelta
from typing import Optional

import httpx

from phitodo.domain.models import TogglTimeEntry

TOGGL_API_BASE = "https://api.track.toggl.com/api/v9"


class TogglService:
    """Service for Toggl Track API integration."""

    def __init__(self, token: str):
        """Initialize with Toggl API token."""
        self.token = token
        self._client: Optional[httpx.AsyncClient] = None
        self._projects: dict[int, str] = {}

    def _get_auth_header(self) -> str:
        """Get Basic auth header value."""
        credentials = f"{self.token}:api_token"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=TOGGL_API_BASE,
                headers={
                    "Authorization": self._get_auth_header(),
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
        return self._client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def get_projects(self) -> dict[int, str]:
        """Fetch user's Toggl projects."""
        client = await self._get_client()
        response = await client.get("/me/projects")
        response.raise_for_status()

        self._projects = {}
        for project in response.json() or []:
            self._projects[project["id"]] = project["name"]

        return self._projects

    async def get_time_entries(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        hidden_project_ids: Optional[list[int]] = None,
    ) -> list[TogglTimeEntry]:
        """
        Fetch time entries within a date range.

        Args:
            start_date: Start of date range (default: 7 days ago)
            end_date: End of date range (default: today)
            hidden_project_ids: Project IDs to exclude

        Returns:
            List of time entries
        """
        if start_date is None:
            start_date = date.today() - timedelta(days=7)
        if end_date is None:
            end_date = date.today()

        # Toggl API expects ISO format with timezone
        start_str = datetime.combine(start_date, datetime.min.time()).isoformat() + "Z"
        end_str = (
            datetime.combine(end_date, datetime.max.time()).isoformat()[:19] + "Z"
        )

        client = await self._get_client()
        response = await client.get(
            "/me/time_entries",
            params={
                "start_date": start_str,
                "end_date": end_str,
                "meta": "true",
            },
        )
        response.raise_for_status()

        # Ensure we have project names
        if not self._projects:
            await self.get_projects()

        entries = []
        for entry_data in response.json() or []:
            entry = TogglTimeEntry.from_api_response(entry_data)

            # Add project name if available
            if entry.project_id and entry.project_id in self._projects:
                entry.project_name = self._projects[entry.project_id]

            # Filter hidden projects
            if hidden_project_ids and entry.project_id in hidden_project_ids:
                continue

            entries.append(entry)

        return entries

    async def get_entries_grouped_by_project(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        hidden_project_ids: Optional[list[int]] = None,
    ) -> dict[str, list[TogglTimeEntry]]:
        """
        Fetch time entries grouped by project.

        Returns:
            Dict mapping project name to list of entries
        """
        entries = await self.get_time_entries(start_date, end_date, hidden_project_ids)

        grouped: dict[str, list[TogglTimeEntry]] = {}
        for entry in entries:
            project_name = entry.project_name or "No Project"
            if project_name not in grouped:
                grouped[project_name] = []
            grouped[project_name].append(entry)

        return grouped

    async def get_duration_by_day(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        hidden_project_ids: Optional[list[int]] = None,
    ) -> dict[str, float]:
        """
        Get total duration by day.

        Returns:
            Dict mapping date string to total hours
        """
        entries = await self.get_time_entries(start_date, end_date, hidden_project_ids)

        by_day: dict[str, float] = {}
        for entry in entries:
            if entry.duration < 0:
                # Running timer - skip
                continue
            day = entry.start[:10]
            by_day[day] = by_day.get(day, 0) + entry.duration_hours

        return by_day

    async def get_duration_by_project(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        hidden_project_ids: Optional[list[int]] = None,
    ) -> dict[str, float]:
        """
        Get total duration by project.

        Returns:
            Dict mapping project name to total hours
        """
        entries = await self.get_time_entries(start_date, end_date, hidden_project_ids)

        by_project: dict[str, float] = {}
        for entry in entries:
            if entry.duration < 0:
                continue
            project_name = entry.project_name or "No Project"
            by_project[project_name] = (
                by_project.get(project_name, 0) + entry.duration_hours
            )

        return by_project

    async def validate_token(self) -> bool:
        """Check if the token is valid."""
        try:
            client = await self._get_client()
            response = await client.get("/me")
            return response.status_code == 200
        except httpx.HTTPError:
            return False
