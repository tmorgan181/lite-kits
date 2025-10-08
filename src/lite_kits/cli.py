#!/usr/bin/env python3
"""
CLI for lite-kits

Provides commands to add/remove enhancement kits for vanilla dev tools.
"""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import __version__
from .installer import Installer

# Constants
APP_NAME = "lite-kits"
APP_DESCRIPTION = "Lightweight enhancement kits for vanilla dev tools"
HELP_TIP = "Tip: Run 'lite-kits COMMAND --help' for detailed help on each command"

# Kit names
KIT_PROJECT = "project"
KIT_GIT = "git"
KIT_MULTIAGENT = "multiagent"
KITS_ALL = [KIT_PROJECT, KIT_GIT, KIT_MULTIAGENT]
KITS_RECOMMENDED = [KIT_PROJECT, KIT_GIT]

# Help panel names
PANEL_KIT_MANAGEMENT = "Kit Management"
PANEL_PACKAGE_MANAGEMENT = "Package Management"

# Kit descriptions
KIT_DESC_PROJECT = "/orient command, project orientation features"
KIT_DESC_GIT = "/commit, /pr, /cleanup commands with smart workflows"
KIT_DESC_MULTIAGENT = "/sync, collaboration directories, memory guides"

# Status indicators
STATUS_OK = "[green][OK][/green]"
STATUS_NOT_FOUND = "[dim][--][/dim]"
STATUS_ERROR = "[red][X][/red]"

# Marker files for kit detection
MARKER_PROJECT_KIT = ".claude/commands/orient.md"
MARKER_GIT_KIT = ".claude/commands/commit.md"
MARKER_MULTIAGENT_KIT = ".specify/memory/pr-workflow-guide.md"

# Error messages
ERROR_NO_TARGET = "Either --here or a target directory must be specified"
ERROR_NOT_SPEC_KIT = "does not appear to be a spec-kit project"
ERROR_SPEC_KIT_HINT = "Looking for one of: .specify/, .claude/, or .github/prompts/"

app = typer.Typer(
    name=APP_NAME,
    help=f"{APP_DESCRIPTION}\n\n[dim]{HELP_TIP}[/dim]",
    no_args_is_help=True,
    add_completion=False,  # Disable shell completion to avoid modifying user profiles
    rich_markup_mode="rich",
)
console = Console()


def version_callback(value: bool):
    """Print version and exit."""
    if value:
        console.print(f"{APP_NAME} version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True,
    ),
):
    f"""{APP_NAME}: {APP_DESCRIPTION}"""
    pass


@app.command(name="add", rich_help_panel=PANEL_KIT_MANAGEMENT)
def add_kits(
    here: bool = typer.Option(
        False,
        "--here",
        help="Add to current directory",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview changes without applying them",
    ),
    kit: Optional[str] = typer.Option(
        None,
        "--kit",
        help=f"Comma-separated list of kits to add: {','.join(KITS_ALL)} (default: {KIT_PROJECT})",
    ),
    recommended: bool = typer.Option(
        False,
        "--recommended",
        help=f"Add recommended kits: {' + '.join(KITS_RECOMMENDED)}",
    ),
    target: Optional[Path] = typer.Argument(
        None,
        help="Target directory (defaults to current directory)",
    ),
):
    """Add enhancement kits to a spec-kit project."""
    if not here and target is None:
        console.print(
            f"[red]Error:[/red] {ERROR_NO_TARGET}",
            style="bold",
        )
        raise typer.Exit(1)

    target_dir = Path.cwd() if here else target

    # Determine which kits to install
    kits = None
    if recommended:
        kits = KITS_RECOMMENDED
    elif kit:
        kits = [k.strip() for k in kit.split(',')]
    # else: kits=None will use default [KIT_PROJECT] in Installer

    try:
        installer = Installer(target_dir, kits=kits)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)

    # Validate target is a spec-kit project
    if not installer.is_spec_kit_project():
        console.print(
            f"[red]Error:[/red] {target_dir} {ERROR_NOT_SPEC_KIT}",
            style="bold",
        )
        console.print(
            f"\n{ERROR_SPEC_KIT_HINT}",
            style="dim",
        )
        raise typer.Exit(1)

    # Check if already installed
    if installer.is_multiagent_installed():
        console.print(
            "[yellow]Warning:[/yellow] Enhancement kits appear to be already installed",
            style="bold",
        )
        if not typer.confirm("Reinstall anyway?"):
            raise typer.Exit(0)

    # Preview or install
    if dry_run:
        console.print("\n[bold cyan]Dry run - no changes will be made[/bold cyan]\n")
        changes = installer.preview_installation()
        _display_changes(changes)
    else:
        console.print(f"\n[bold green]Adding enhancement kits to {target_dir}[/bold green]\n")

        with console.status("[bold green]Adding kits..."):
            result = installer.install()

        if result["success"]:
            console.print("\n[bold green][OK] Kits added successfully![/bold green]\n")
            _display_installation_summary(result)
        else:
            console.print(f"\n[bold red][X] Failed to add kits:[/bold red] {result['error']}\n")
            raise typer.Exit(1)


@app.command(rich_help_panel=PANEL_KIT_MANAGEMENT)
def remove(
    here: bool = typer.Option(
        False,
        "--here",
        help="Remove from current directory",
    ),
    kit: Optional[str] = typer.Option(
        None,
        "--kit",
        help=f"Comma-separated list of kits to remove: {','.join(KITS_ALL)}",
    ),
    all_kits: bool = typer.Option(
        False,
        "--all",
        help="Remove all kits",
    ),
    target: Optional[Path] = typer.Argument(
        None,
        help="Target directory (defaults to current directory)",
    ),
):
    """
    Remove enhancement kits from a spec-kit project.

    Returns the project to vanilla spec-kit state.

    Examples:
        lite-kits remove --here --kit git                # Remove git-kit only
        lite-kits remove --here --kit project,git        # Remove specific kits
        lite-kits remove --here --all                    # Remove all kits
    """
    if not here and target is None:
        console.print(
            "[red]Error:[/red] Either --here or a target directory must be specified",
            style="bold",
        )
        raise typer.Exit(1)

    target_dir = Path.cwd() if here else target

    # Determine which kits to remove
    kits = None
    if all_kits:
        kits = KITS_ALL
    elif kit:
        kits = [k.strip() for k in kit.split(',')]
    else:
        console.print("[yellow]Error:[/yellow] Specify --kit or --all", style="bold")
        console.print("\nExamples:", style="dim")
        console.print(f"  {APP_NAME} remove --here --kit {KIT_GIT}", style="dim")
        console.print(f"  {APP_NAME} remove --here --all", style="dim")
        raise typer.Exit(1)

    try:
        installer = Installer(target_dir, kits=kits)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)

    # Check if kits are installed
    if not installer.is_multiagent_installed():
        console.print("[yellow]Warning:[/yellow] No kits detected to remove", style="bold")
        raise typer.Exit(0)

    # Confirm removal
    console.print(f"\n[bold yellow]Remove kits from {target_dir}[/bold yellow]")
    console.print(f"Kits to remove: {', '.join(kits)}\n")

    if not typer.confirm("Continue with removal?"):
        console.print("Cancelled")
        raise typer.Exit(0)

    # Remove kits
    console.print("\n[bold]Removing kits...[/bold]\n")
    with console.status("[bold yellow]Removing..."):
        result = installer.remove()

    if result["success"]:
        console.print("[bold green]Removal complete![/bold green]\n")
        if result["removed"]:
            console.print("[bold]Removed:[/bold]")
            for item in result["removed"]:
                console.print(f"  - {item}")
        else:
            console.print("[dim]No files found to remove[/dim]")
    else:
        console.print(f"\n[bold red]Removal failed:[/bold red] {result['error']}\n")
        raise typer.Exit(1)


@app.command(rich_help_panel=PANEL_KIT_MANAGEMENT)
def validate(
    here: bool = typer.Option(
        True,
        "--here",
        help="Validate current directory",
    ),
    target: Optional[Path] = typer.Argument(
        None,
        help="Target directory (defaults to current directory)",
    ),
):
    """
    Validate enhancement kit installation.

    Checks:
    - Kit files are present and correctly installed
    - Collaboration directory structure (if multiagent-kit installed)
    - Required files present
    - Cross-kit consistency

    Example:
        lite-kits validate --here
    """
    target_dir = Path.cwd() if here else target

    # For validation, we don't know which kits are installed yet, so check for all
    installer = Installer(target_dir, kits=KITS_ALL)

    console.print(f"\n[bold cyan]Validating {target_dir}[/bold cyan]\n")

    # Check if it's a spec-kit project
    if not installer.is_spec_kit_project():
        console.print("[red][X] Not a spec-kit project[/red]")
        raise typer.Exit(1)

    # Check if any kits are installed
    if not installer.is_multiagent_installed():
        console.print("[yellow]⚠ No enhancement kits installed[/yellow]")
        console.print(f"  Run: {APP_NAME} add --here --recommended", style="dim")
        raise typer.Exit(1)

    # Validate structure
    with console.status("[bold cyan]Validating..."):
        validation_result = installer.validate()

    _display_validation_results(validation_result)

    if validation_result["valid"]:
        console.print("\n[bold green][OK] Validation passed![/bold green]")
        raise typer.Exit(0)
    else:
        console.print("\n[bold red][X] Validation failed[/bold red]")
        raise typer.Exit(1)


@app.command(rich_help_panel=PANEL_KIT_MANAGEMENT)
def status(
    here: bool = typer.Option(
        True,
        "--here",
        help="Check current directory",
    ),
    target: Optional[Path] = typer.Argument(
        None,
        help="Target directory (defaults to current directory)",
    ),
):
    """
    Show enhancement kit installation status for the project.

    Displays:
    - Spec-kit project detection
    - Installed kits
    - Installation health

    Example:
        lite-kits status --here
    """
    target_dir = Path.cwd() if here else target

    # For status, check for all possible kits
    installer = Installer(target_dir, kits=KITS_ALL)

    console.print(f"\n[bold cyan]Project Status: {target_dir}[/bold cyan]\n")

    # Basic checks
    is_spec_kit = installer.is_spec_kit_project()

    # Check individual kits
    project_kit_installed = (target_dir / MARKER_PROJECT_KIT).exists()
    git_kit_installed = (target_dir / MARKER_GIT_KIT).exists()
    multiagent_kit_installed = (target_dir / MARKER_MULTIAGENT_KIT).exists()

    table = Table(show_header=False, box=None)
    table.add_column("Item", style="cyan")
    table.add_column("Status")

    table.add_row("Spec-kit project", STATUS_OK if is_spec_kit else STATUS_ERROR)
    table.add_row(f"{KIT_PROJECT}-kit", STATUS_OK if project_kit_installed else STATUS_NOT_FOUND)
    table.add_row(f"{KIT_GIT}-kit", STATUS_OK if git_kit_installed else STATUS_NOT_FOUND)
    table.add_row(f"{KIT_MULTIAGENT}-kit", STATUS_OK if multiagent_kit_installed else STATUS_NOT_FOUND)

    console.print(table)
    console.print()


def _display_changes(changes: dict):
    """Display preview of changes."""
    console.print("[bold]Files to be created:[/bold]")
    for file in changes.get("new_files", []):
        console.print(f"  [green]+[/green] {file}")

    console.print("\n[bold]Files to be modified:[/bold]")
    for file in changes.get("modified_files", []):
        console.print(f"  [yellow]~[/yellow] {file}")

    console.print("\n[bold]Directories to be created:[/bold]")
    for dir in changes.get("new_directories", []):
        console.print(f"  [blue]+[/blue] {dir}")


def _display_installation_summary(result: dict):
    """Display kit addition summary."""
    console.print("[bold]Added:[/bold]")
    for item in result.get("installed", []):
        console.print(f"  [OK] {item}")

    console.print("\n[bold cyan]Next steps:[/bold cyan]")
    console.print("  1. Run: /orient (in your AI assistant)")
    console.print(f"  2. Check: {MARKER_PROJECT_KIT} or .github/prompts/orient.prompt.md")
    console.print(f"  3. Validate: {APP_NAME} validate --here")


def _display_validation_results(result: dict):
    """Display validation results."""
    for check_name, check_result in result.get("checks", {}).items():
        status = "[OK]" if check_result["passed"] else "[X]"
        color = "green" if check_result["passed"] else "red"
        console.print(f"[{color}]{status}[/{color}] {check_name}")

        if not check_result["passed"] and "message" in check_result:
            console.print(f"  {check_result['message']}", style="dim")


if __name__ == "__main__":
    app()
