"""
``sprezzature-ui`` — the command line over this package's tools.

One front door. Until 2026-10-25 there were two, an argparse one and a click
one kept in step by sharing a table; the click module imported ``TOOLS`` from
the argparse module, so neither could be removed without the other and every
sub-command had to be written twice. The catalogue now lives in
:mod:`sprezzature_ui._tools`, and this is the only parser.

``make-ui`` and ``sprezzature-ui`` both land here. The first name is kept because it is what the
skill, the README and years of notes tell people to type; they are two
spellings of one command, not two commands.

Each tool below is also its own console script, which is what a script or a
pre-commit hook should call. This front door is for a person who does not
remember the exact name.

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import importlib
import sys

import click

from sprezzature_ui._tools import TOOLS

#: Shown under the command list. Completion is click's, and worth saying out
#: loud: a front door with several tools is exactly where tab completion pays
#: off, and nobody discovers it by guessing.
_EPILOG = """\
Shell completion:

  \b
  eval "$(_SPREZZATURE_UI_COMPLETE=bash_source sprezzature-ui)"   # bash
  eval "$(_SPREZZATURE_UI_COMPLETE=zsh_source sprezzature-ui)"    # zsh

Run `sprezzature-ui tools` to see which tools are ready on this machine
and which need an extra installed.
"""


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    epilog=_EPILOG,
    help=("The deterministic half of sprezzature-ui. Each tool below is also its own command."),
)
@click.version_option(package_name="sprezzature-ui")
def main() -> None:  # pragma: no cover - click dispatches
    """Front door over the two tools this package ships."""


@main.command(name="tools")
def list_tools() -> None:
    """
    List the tools, and say which ones can run here.

    The second half is the point: "installed" and "will run" are different
    questions when a tool needs an extra, and a reader should not have to
    discover the difference from a traceback.
    """
    width = max(len(name) for name in TOOLS)
    for name, entry in TOOLS.items():
        _module, extra = (entry[0], entry[1]) if len(entry) == 3 else (entry[0], "")
        target = f"sprezzature_ui_scripts.{_module}"
        try:
            importlib.import_module(target)
            mark = "ready"
        except ImportError:
            mark = f"needs [{extra}]" if extra else "unavailable"
        summary = entry[-1].split(".")[0]
        click.echo(f"  {name:<{width}}  {mark:<14}  {summary}.")


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
