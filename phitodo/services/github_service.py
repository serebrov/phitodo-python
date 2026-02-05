"""GitHub API service."""

from typing import Optional

import httpx

from phitodo.domain.models import GitHubIssueItem

GITHUB_API_BASE = "https://api.github.com"


class GitHubService:
    """Service for GitHub API integration."""

    def __init__(self, token: str):
        """Initialize with GitHub personal access token."""
        self.token = token
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=GITHUB_API_BASE,
                headers={
                    "Authorization": f"token {self.token}",
                    "Accept": "application/vnd.github.v3+json",
                },
                timeout=30.0,
            )
        return self._client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def get_assigned_issues(
        self, allowed_repos: Optional[list[str]] = None
    ) -> list[GitHubIssueItem]:
        """
        Fetch issues assigned to the authenticated user.

        Args:
            allowed_repos: Optional list of repo full names to filter by

        Returns:
            List of assigned issues (excluding PRs)
        """
        client = await self._get_client()
        response = await client.get(
            "/issues",
            params={
                "filter": "assigned",
                "state": "open",
                "per_page": 100,
            },
        )
        response.raise_for_status()

        items = []
        for issue_data in response.json():
            item = GitHubIssueItem.from_api_response(issue_data)

            # Filter out PRs
            if item.is_pull_request:
                continue

            # Filter by allowed repos if specified
            if allowed_repos and item.repository_full_name not in allowed_repos:
                continue

            items.append(item)

        return items

    async def get_review_requested_prs(
        self, allowed_repos: Optional[list[str]] = None
    ) -> list[GitHubIssueItem]:
        """
        Fetch PRs where review is requested from the authenticated user.

        Args:
            allowed_repos: Optional list of repo full names to filter by

        Returns:
            List of PRs awaiting review
        """
        client = await self._get_client()
        response = await client.get(
            "/search/issues",
            params={
                "q": "review-requested:@me is:open is:pr",
                "per_page": 100,
            },
        )
        response.raise_for_status()

        items = []
        for issue_data in response.json().get("items", []):
            item = GitHubIssueItem.from_api_response(issue_data)

            # Filter by allowed repos if specified
            if allowed_repos and item.repository_full_name not in allowed_repos:
                continue

            items.append(item)

        return items

    async def get_my_prs(
        self, allowed_repos: Optional[list[str]] = None
    ) -> list[GitHubIssueItem]:
        """
        Fetch open PRs authored by the authenticated user.

        Args:
            allowed_repos: Optional list of repo full names to filter by

        Returns:
            List of user's open PRs
        """
        client = await self._get_client()
        response = await client.get(
            "/search/issues",
            params={
                "q": "author:@me is:open is:pr",
                "per_page": 100,
            },
        )
        response.raise_for_status()

        items = []
        for issue_data in response.json().get("items", []):
            item = GitHubIssueItem.from_api_response(issue_data)

            # Filter by allowed repos if specified
            if allowed_repos and item.repository_full_name not in allowed_repos:
                continue

            items.append(item)

        return items

    async def fetch_all(
        self, allowed_repos: Optional[list[str]] = None
    ) -> tuple[list[GitHubIssueItem], list[GitHubIssueItem], list[GitHubIssueItem]]:
        """
        Fetch all GitHub data: assigned issues, review PRs, and my PRs.

        Returns:
            Tuple of (assigned_issues, review_prs, my_prs)
        """
        import asyncio

        assigned, review_prs, my_prs = await asyncio.gather(
            self.get_assigned_issues(allowed_repos),
            self.get_review_requested_prs(allowed_repos),
            self.get_my_prs(allowed_repos),
        )

        return assigned, review_prs, my_prs

    async def validate_token(self) -> bool:
        """Check if the token is valid."""
        try:
            client = await self._get_client()
            response = await client.get("/user")
            return response.status_code == 200
        except httpx.HTTPError:
            return False
