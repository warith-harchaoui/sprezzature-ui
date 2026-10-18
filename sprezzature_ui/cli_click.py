"""
The click command line — ``sprezzature-ui``.

The twin of ``sprezzature_ui.cli``: same tools, same dispatch, the other
parser. Both read one ``TOOLS`` table, so a tool cannot appear in one front
door and be missing from the other.

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import importlib
import sys

import click

from sprezzature_ui.cli import TOOLS


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    help=(
        "The deterministic half of sprezzature-ui. Each tool below is also "
        "its own command."
    ),
)
@click.version_option(package_name="sprezzature-ui")
def main() -> None:  # pragma: no cover - click dispatches
    """Front door over the two tools this package ships."""


def _attach(name: str, module_name: str, summary: str) -> None:
    """Register one tool as a click sub-command, from the shared table."""

    @main.command(
        name,
        help=summary,
        context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
    )
    @click.argument("rest", nargs=-1, type=click.UNPROCESSED)
    def _run(rest: tuple[str, ...], _module: str = module_name, _name: str = name) -> None:
        module = importlib.import_module(f"sprezzature_ui_scripts.{_module}")
        saved = sys.argv
        try:
            sys.argv = [f"sprezzature-ui {_name}", *rest]
            raise SystemExit(int(module.main() or 0))
        finally:
            sys.argv = saved


for _tool, (_module_name, _summary) in TOOLS.items():
    _attach(_tool, _module_name, _summary)


if __name__ == "__main__":
    main()
