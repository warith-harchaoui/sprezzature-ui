"""
The argparse command line — ``make-ui``.

Two tools, each also its own command. This is the front door that says what
the package does without anybody reading the README, and its twin
``sprezzature_ui.cli_click`` reads the same table with click.

The table is small on purpose. Writing a component is the model's work,
guided by ``SKILL.md``; what ships here is the part a machine can check.

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import argparse
import importlib
import sys

from sprezzature_ui_scripts._argparse import make_parser

#: Every tool, with the line that says when to reach for it. The dispatcher
#: and the help text are the same table, so a tool cannot be listed and
#: unreachable, or reachable and undocumented.
TOOLS: dict[str, tuple[str, str]] = {
    "i18n-audit": (
        "audit_i18n",
        "Find translations embedded in JavaScript and HTML, and LLM prompts "
        "inlined in Python. Both belong in locales/i18n.yaml.",
    ),
    "i18n-make": (
        "i18n_make",
        "Scaffold that catalogue, compile it to JSON, and emit the loader "
        "that reads it.",
    ),
}


def build_parser() -> argparse.ArgumentParser:
    """The parser, built separately so a test can read it without running it."""
    width = max(len(name) for name in TOOLS)
    catalogue = "\n".join(
        f"  {name:<{width}}  {summary}" for name, (_, summary) in TOOLS.items()
    )
    parser = make_parser(
        prog="make-ui",
        description=(
            "The deterministic half of sprezzature-ui. Writing an interface "
            "is the model's work, guided by SKILL.md; these are the two "
            "tools a machine can run."
        ),
        epilog=(
            f"Tools:\n{catalogue}\n"
            "\n"
            "Examples:\n"
            "  make-ui i18n-audit src/\n"
            "  make-ui i18n-make locales/i18n.yaml\n"
            "\n"
            "Every flag after the tool name belongs to that tool; run\n"
            "`make-ui <tool> --help` to see them.\n"
        ),
    )
    parser.add_argument("tool", choices=sorted(TOOLS), help="Which tool to run.")
    # Everything after the tool name belongs to the tool, including flags this
    # parser also defines — otherwise `make-ui i18n-audit --help` would print
    # this help rather than the tool's.
    parser.add_argument("rest", nargs=argparse.REMAINDER,
                        help="Arguments passed through to the tool.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Dispatch to one of the two tools."""
    args = build_parser().parse_args(argv)
    module_name, _ = TOOLS[args.tool]
    module = importlib.import_module(f"sprezzature_ui_scripts.{module_name}")

    # The tools read sys.argv themselves — they were commands before they
    # were sub-commands, and they still are.
    saved = sys.argv
    try:
        sys.argv = [f"make-ui {args.tool}", *args.rest]
        return int(module.main() or 0)
    finally:
        sys.argv = saved


if __name__ == "__main__":
    sys.exit(main())
