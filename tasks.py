"""
Invoke tasks.

Usage:
    invoke check       # Run ruff linting
    invoke --list      # List all available tasks
"""

from invoke import task


@task
def check(c):
    """Run ruff linting on the codebase."""
    print("Running ruff check...")
    c.run("ruff check .")


@task
def lint(c):
    """Alias for check task."""
    check(c)


@task
def format(c):
    """Format code using ruff."""
    print("Formatting code with ruff...")
    c.run("ruff format .")


@task
def check_fix(c):
    """Run ruff linting with auto-fix."""
    print("Running ruff check with auto-fix...")
    c.run("ruff check . --fix")
