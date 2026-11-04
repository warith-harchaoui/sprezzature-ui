"""
A command this package installs has to be able to start.

``pip install`` puts five commands on ``$PATH``. Each is a one-line wrapper
generated from ``[project.scripts]``: it imports a module and calls a function.
Three things can break that before any argument is parsed —

* an import at module load that needs an extra the user did not install;
* an entry point naming a function that moved or was renamed;
* a ``prog=`` naming the module instead of the command, so the help a reader
  gets back is about a file they cannot run.

None of them shows up in a unit test of the code underneath, because the code
underneath is fine. All three show up the first time somebody types the command
with ``--help``, which is why this runs exactly that.

Why it arrived late
-------------------
The monorepo asked, from the one place that sees all nine bricks, whether each
one's suite ever runs a command it installs. Four did not, this among them, and
the comment in the monorepo had been asserting the opposite — "its own suite
checks their --help there". It is this suite's job and it was not being done.

One outcome is accepted: exit 0 with a help text that names the command. What
is refused is everything else — a non-zero exit, a traceback, silence, or a
usage line about a module.

Why a refusal is no longer among them
-------------------------------------
Until 2026-10-25 this package shipped two parsers over one table and ``click``
was an extra, so a Click front door refusing with exit 1 and an install line
was correct behaviour, and this file accepted it as long as the output named a
``pip install``. argparse is gone and click is a **base** dependency now:
nothing is left for a front door to be missing.

That tolerance was also blind in a shape worth recording. Measured here on
2026-10-31, with ``sprezzature_ui.cli`` made to exit 1 printing exactly what
the tolerance asked for — an install line naming a ``[click]`` extra, no traceback
— the old case **passed** for ``sprezzature-ui`` and failed only for
``make-ui``. A refusal has to name the distribution to be useful, the Click
front door is named after the distribution, so the one assertion left standing,
that the help names the command, was satisfied by the refusal message itself.
The front door the tolerance existed for was the one it could not see.

The premise that makes exit 0 the right demand is asserted just below rather
than assumed, so the day click moves back under
``[project.optional-dependencies]`` it fails there and names what to revisit.

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import ast
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PACKAGE = "sprezzature-ui"

#: ``name = "module:function"`` under ``[project.scripts]``. Read from the
#: manifest rather than from the installed metadata: the manifest is what a
#: release will ship, and it is readable from a checkout that was never
#: installed.
_ENTRY_POINT = re.compile(r'^([\w.-]+)\s*=\s*"([\w.]+):(\w+)"', re.M)


def _commands() -> list[tuple[str, str, str]]:
    """Every (command, module, function) this package declares."""
    text = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    block = re.search(r"^\[project\.scripts\]\n(.*?)(?=^\[|\Z)", text, re.M | re.S)
    if block is None:
        return []
    return _ENTRY_POINT.findall(block.group(1))


def _run(command: str, module: str, function: str) -> subprocess.CompletedProcess:
    """`command --help`, through the wrapper if installed, as it would be if not.

    On ``$PATH`` the real wrapper runs, which is the thing being tested. In a
    checkout where the package is importable but its scripts directory is not
    on the path, the same three lines the wrapper would contain are run instead,
    so the test says the same thing in both places.
    """
    found = shutil.which(command)
    if found is not None:
        return subprocess.run([found, "--help"], capture_output=True, text=True)
    code = (
        "import sys\n"
        f"sys.argv = [{command!r}, '--help']\n"
        f"from {module} import {function}\n"
        f"raise SystemExit({function}())\n"
    )
    return subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)


#: The ``[project]`` table proper — where base ``dependencies`` live, as
#: opposed to the ``name = [...]`` entries of ``[project.optional-dependencies]``.
_PROJECT_BLOCK = re.compile(r"^\[project\]\n(.*?)(?=^\[|\Z)", re.M | re.S)
_BASE_DEPENDENCIES = re.compile(r"^dependencies\s*=\s*\[(.*?)\]", re.M | re.S)
_OPTIONAL_BLOCK = re.compile(r"^\[project\.optional-dependencies\]\n(.*?)(?=^\[|\Z)", re.M | re.S)
#: ``click>=8.1`` -> ``click``. A distribution name, stripped of its specifier.
_DISTRIBUTION = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")


def _manifest() -> str:
    """The manifest as text. Read rather than parsed: ``tomllib`` is 3.11+.

    This package supports 3.10, where importing it at module scope would raise
    at **collection** and take every case in the file down with it.
    """
    return (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")


def test_the_front_door_library_is_a_base_dependency() -> None:
    """The premise of the case below: ``--help`` has nothing to refuse over.

    See the file docstring. This holds the tolerance that used to be in that
    case, so the day it stops being true is the day this fails and says so.
    """
    text = _manifest()
    project = _PROJECT_BLOCK.search(text)
    assert project is not None, f"{PACKAGE}/pyproject.toml has no [project] table"

    declared = _BASE_DEPENDENCIES.search(project.group(1))
    base = {
        match.group(0).lower()
        for line in (declared.group(1).splitlines() if declared else [])
        if (match := _DISTRIBUTION.match(line.strip().strip("\"'")))
    }
    assert "click" in base, (
        f"click is not a base dependency of {PACKAGE} any more (base: "
        f"{sorted(base)}). The case below demands exit 0 from every command "
        f"because every front door's library is always installed. If click "
        f"went back to being an extra, that demand is wrong and the refusal "
        f"branch removed on 2026-10-31 is what should come back."
    )

    optional = _OPTIONAL_BLOCK.search(text)
    extras = re.findall(r"^([\w.-]+)\s*=\s*\[", optional.group(1), re.M) if optional else []
    assert "click" not in extras, (
        f"{PACKAGE} declares both a base click and a [click] extra. Every "
        f"README line reading pip install '{PACKAGE}[click]' then documents an "
        f"extra that installs what the package already pulls in."
    )


def test_the_manifest_declares_commands() -> None:
    """An empty table would make every case below vacuous."""
    found = _commands()
    assert found, (
        f"{PACKAGE}/pyproject.toml declares no [project.scripts]. Either the "
        f"table moved or this package stopped installing commands; both make "
        f"the cases below collect nothing, which pytest reports as a skip and "
        f"a reader takes for a pass."
    )


@pytest.mark.parametrize("command,module,function", _commands(), ids=lambda v: v)
def test_the_command_starts_and_names_itself(command: str, module: str, function: str) -> None:
    """``--help`` is the cheapest proof that a command is callable at all."""
    proc = _run(command, module, function)
    output = proc.stdout + proc.stderr

    # "This package is not installed in this environment" is the one condition
    # that is about the machine rather than the code. Read off the outcome
    # rather than asked in advance: ``find_spec`` raises ValueError for a
    # package whose ``__spec__`` is None, which is the case for the ``scripts/``
    # directory this project maps to an importable name at build time.
    top = module.split(".")[0]
    if f"No module named '{top}'" in output:
        pytest.skip(f"{PACKAGE} is not installed here: pip install -e '.[dev]'")

    assert "Traceback" not in output, f"{command} --help raised:\n{output}"
    assert output.strip(), f"{command} --help printed nothing (exit {proc.returncode})"

    assert proc.returncode == 0, (
        f"{command} --help exited {proc.returncode}. Every library a front "
        f"door needs is a base dependency, so there is nothing left for it to "
        f"refuse over:\n{output}"
    )

    assert command in output, (
        f"{command} --help does not name {command}. A usage line that names "
        f"the module instead sends the reader to a file they cannot run:\n"
        f"{output.splitlines()[0] if output.splitlines() else ''}"
    )

    # click, not argparse: the two spell the usage line differently, and the
    # spelling is the cheapest outside proof of which parser answered.
    first = output.lstrip().splitlines()[0]
    assert first.startswith("Usage: "), (
        f"{command} --help does not answer with a click usage line. Every "
        f"command of this suite parses with click since 2026-11-04; a line "
        f"starting with lowercase 'usage:' is an argparse parser come back:\n"
        f"{first}"
    )


def _imports_argparse(path: Path) -> bool:
    """Does `path` import argparse, at any depth, in either spelling?"""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import) and any(
            alias.name.split(".")[0] == "argparse" for alias in node.names
        ):
            return True
        if isinstance(node, ast.ImportFrom) and (node.module or "").split(".")[0] == "argparse":
            return True
    return False


def test_no_module_of_the_package_imports_argparse() -> None:
    """Every command line here is click; argparse coming back is a regression.

    Read off the source rather than off ``sys.modules`` after an import: a
    parser built lazily inside ``main`` (the way ``mcp.py`` built its own until
    2026-11-04) is invisible to an import and plain in the syntax tree. Both
    trees that ship are walked, ``sprezzature_ui/`` and ``scripts/``, so a new
    module is covered the day it is written.
    """
    shipped = sorted(
        path
        for folder in ("sprezzature_ui", "scripts")
        for path in (REPO_ROOT / folder).rglob("*.py")
        if "__pycache__" not in path.parts
    )
    assert shipped, "no Python module found under sprezzature_ui/ or scripts/"
    offenders = [str(path.relative_to(REPO_ROOT)) for path in shipped if _imports_argparse(path)]
    assert not offenders, (
        f"these modules import argparse: {offenders}. The suite parses every "
        f"command with click, through scripts/_click.py (sprezzature_command "
        f"+ run_command)."
    )
