"""Textual screens for different views."""

from phitodo.screens.anytime import AnytimeScreen
from phitodo.screens.completed import CompletedScreen
from phitodo.screens.github import GitHubScreen
from phitodo.screens.inbox import InboxScreen
from phitodo.screens.project import ProjectScreen
from phitodo.screens.review import ReviewScreen
from phitodo.screens.settings import SettingsScreen
from phitodo.screens.tag import TagScreen
from phitodo.screens.today import TodayScreen
from phitodo.screens.toggl import TogglScreen
from phitodo.screens.upcoming import UpcomingScreen

__all__ = [
    "InboxScreen",
    "TodayScreen",
    "UpcomingScreen",
    "AnytimeScreen",
    "CompletedScreen",
    "ReviewScreen",
    "GitHubScreen",
    "TogglScreen",
    "SettingsScreen",
    "ProjectScreen",
    "TagScreen",
]
