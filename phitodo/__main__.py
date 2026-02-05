"""Entry point for phitodo TUI."""

from phitodo.app import PhitodoApp


def main() -> None:
    """Run the Phitodo TUI application."""
    app = PhitodoApp()
    app.run()


if __name__ == "__main__":
    main()
