"""Console entry point – delegates to the CLI."""

from cli import run_cli


def run() -> None:
    """Run the application from the command line."""
    run_cli()


if __name__ == "__main__":
    run()
