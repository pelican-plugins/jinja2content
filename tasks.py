from inspect import cleandoc
import logging
import os
from pathlib import Path
from shutil import which

from invoke import task

logger = logging.getLogger(__name__)

PKG_NAME = "jinja2content"
PKG_PATH = Path(f"pelican/plugins/{PKG_NAME}")

ACTIVE_VENV = os.environ.get("VIRTUAL_ENV", None)
VENV_HOME = Path(os.environ.get("WORKON_HOME", "~/.local/share/virtualenvs"))
VENV_PATH = Path(ACTIVE_VENV) if ACTIVE_VENV else (VENV_HOME.expanduser() / PKG_NAME)
VENV = str(VENV_PATH.expanduser())
BIN_DIR = "bin" if os.name != "nt" else "Scripts"
VENV_BIN = Path(VENV) / Path(BIN_DIR)

TOOLS = ("cruft", "pre-commit")
UV = which("uv")
CMD_PREFIX = f"{VENV_BIN}/" if ACTIVE_VENV else f"{UV} run "
CRUFT = which("cruft") if which("cruft") else f"{CMD_PREFIX}cruft"
PRECOMMIT = which("pre-commit") if which("pre-commit") else f"{CMD_PREFIX}pre-commit"
PTY = os.name != "nt"


@task
def tests(c, deprecations=False):
    """Run the test suite, optionally with `--deprecations`."""
    deprecations_flag = "" if deprecations else "-W ignore::DeprecationWarning"
    c.run(f"{CMD_PREFIX}pytest {deprecations_flag}", pty=PTY)


@task
def format(c, check=False, diff=False):
    """Run Ruff's auto-formatter, optionally with `--check` or `--diff`."""
    check_flag, diff_flag = "", ""
    if check:
        check_flag = "--check"
    if diff:
        diff_flag = "--diff"
    c.run(
        f"{CMD_PREFIX}ruff format {check_flag} {diff_flag} {PKG_PATH} tasks.py", pty=PTY
    )


@task
def ruff(c, concise=False, fix=False, diff=False):
    """Run Ruff to ensure code meets project standards."""
    concise_flag, fix_flag, diff_flag = "", "", ""
    if concise:
        concise_flag = "--output-format=concise"
    if fix:
        fix_flag = "--fix"
    if diff:
        diff_flag = "--diff"
    c.run(f"{CMD_PREFIX}ruff check {concise_flag} {diff_flag} {fix_flag} .", pty=PTY)


@task
def lint(c, concise=False, fix=False, diff=False):
    """Check code style via linting tools."""
    ruff(c, concise=concise, fix=fix, diff=diff)
    format(c, check=(not fix), diff=diff)


@task
def tools(c):
    """Install development tools in the virtual environment if not already on PATH."""
    for tool in TOOLS:
        if not which(tool):
            logger.info(f"** Installing {tool} **")
            c.run(f"{UV} pip install {tool}")


@task
def precommit(c):
    """Install pre-commit hooks to .git/hooks/pre-commit."""
    logger.info("** Installing pre-commit hooks **")
    c.run(f"{PRECOMMIT} install")


@task
def update(c, check=False):
    """Apply upstream plugin template changes to this project."""
    if check:
        logger.info("** Checking for upstream template changes **")
        c.run(f"{CRUFT} check", pty=PTY)
    else:
        logger.info("** Updating project from upstream template **")
        c.run(f"{CRUFT} update", pty=PTY)


@task
def setup(c):
    """Set up the development environment."""
    if UV:
        c.run(f"{UV} sync", pty=PTY)
        tools(c)
        precommit(c)
        logger.info("\nDevelopment environment should now be set up and ready!\n")
    else:
        error_message = """
            uv is not installed. You can install uv via:

            curl -LsSf https://astral.sh/uv/install.sh | sh

            Once you have installed uv, set up project via `uvx invoke setup`.
            """
        raise SystemExit(cleandoc(error_message))
