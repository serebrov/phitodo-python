"""Configuration management."""

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

CONFIG_PATH = Path.home() / ".config" / "phitodo" / "config.json"


@dataclass
class Config:
    """Application configuration."""

    github_token: Optional[str] = None
    github_allowed_repos: list[str] = field(default_factory=list)
    toggl_token: Optional[str] = None
    toggl_hidden_project_ids: list[int] = field(default_factory=list)
    db_path: Optional[str] = None

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "Config":
        """Load configuration from file."""
        config_path = path or CONFIG_PATH

        if not config_path.exists():
            return cls()

        try:
            with open(config_path) as f:
                data = json.load(f)
            return cls(
                github_token=data.get("github_token"),
                github_allowed_repos=data.get("github_allowed_repos", []),
                toggl_token=data.get("toggl_token"),
                toggl_hidden_project_ids=data.get("toggl_hidden_project_ids", []),
                db_path=data.get("db_path"),
            )
        except (json.JSONDecodeError, OSError):
            return cls()

    def save(self, path: Optional[Path] = None) -> None:
        """Save configuration to file."""
        config_path = path or CONFIG_PATH
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w") as f:
            json.dump(asdict(self), f, indent=2)
