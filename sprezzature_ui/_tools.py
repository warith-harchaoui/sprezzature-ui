#!/usr/bin/env python3
"""
The catalogue of tools this package ships.

Lifted out of the command line on 2026-10-25, when the argparse front door was
removed and click became the only one. It lives here rather than in ``cli`` so
the catalogue owes nothing to whichever parser reads it — the previous
arrangement had the click module importing ``TOOLS`` from the argparse module,
which is why neither could be deleted without the other.

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

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
        "Scaffold that catalogue, compile it to JSON, and emit the loader that reads it.",
    ),
}
