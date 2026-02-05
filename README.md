# Phitodo TUI

A terminal-based todo application with GitHub and Toggl integration, built with Python and [Textual](https://textual.textualize.io/).

## Features

- **Task Management**: Create, edit, complete, and delete tasks
- **Multiple Views**: Inbox, Today, Upcoming, Anytime, Completed, Review
- **Projects & Tags**: Organize tasks with projects and tags
- **GitHub Integration**: View assigned issues and pull requests
- **Toggl Integration**: View time entries with ASCII charts
- **Keyboard-First**: Full keyboard navigation
- **SQLite Persistence**: Compatible with the Tauri web app database

## Installation

```bash
# Clone and navigate to the TUI directory
cd phitodo-tui

# Install with pip
pip install -e .

# Or with uv
uv pip install -e .
```

## Usage

```bash
# Run the app
python -m phitodo

# Or use the installed command
phitodo
```

## Keyboard Shortcuts

### Navigation
| Key | Action |
|-----|--------|
| `1` | Inbox view |
| `2` | Today view |
| `3` | Upcoming view |
| `4` | Anytime view |
| `5` | Completed view |
| `6` | Review view |
| `7` | GitHub view |
| `8` | Toggl view |
| `9` | Settings view |
| `j/k` | Navigate down/up |

### Actions
| Key | Action |
|-----|--------|
| `n` | New task |
| `N` | New project |
| `/` or `Ctrl+K` | Search |
| `Enter` | Select task |
| `Space` | Toggle task completion |
| `e` | Edit task |
| `d` | Delete task |
| `r` | Refresh (GitHub/Toggl) |
| `s` | Standup report |
| `q` | Quit |

## Configuration

Configuration is stored at `~/.config/phitodo/config.json`:

```json
{
  "github_token": "ghp_...",
  "github_allowed_repos": ["owner/repo"],
  "toggl_token": "...",
  "toggl_hidden_project_ids": []
}
```

You can also configure these in the Settings view (press `9`).

## Database

The SQLite database is stored at `~/.local/share/phitodo/phitodo.db` and is compatible with the Tauri web app for data sharing between platforms.

## Project Structure

```
phitodo/
├── domain/          # Data models and business logic
├── services/        # GitHub, Toggl, task operations
├── repository/      # SQLite persistence
├── state/           # Application state management
├── screens/         # Textual screen components
├── widgets/         # Reusable UI components
├── utils/           # Helpers and configuration
└── css/             # Textual CSS styles
```

## Requirements

- Python 3.10+
- textual >= 0.47.0
- httpx >= 0.27.0
- aiosqlite >= 0.20.0

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run the app in development mode
textual run --dev phitodo.app:PhitodoApp
```

## License

MIT
