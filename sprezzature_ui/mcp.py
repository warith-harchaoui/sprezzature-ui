"""
sprezzature-ui — Model Context Protocol (MCP) surface.

Adapter that republishes the FastAPI app in :mod:`sprezzature_ui.api`
as MCP tools, so any MCP-aware host — an agent runtime, an IDE integration,
a custom shell — can call ``health`` and ``audit_i18n`` as first-class tools
instead of guessing at a shell command. Uses :mod:`fastapi_mcp` (https://github.com/tadata-org/fastapi_mcp):
one wrapper over the whole existing HTTP surface, so the routes serve both
plain HTTP callers and MCP hosts without being written twice.

Why a wrapper rather than a hand-written server
-----------------------------------------------
A hand-written MCP server would be a second description of the same
surface, free to drift from the routes it claims to mirror — a tool whose
argument names quietly disagree with the API is worse than no tool, because
the disagreement only shows up at call time. Deriving the tools from the
FastAPI signatures means the two cannot disagree: the ``operation_id`` on
each route *is* the tool name, and the Pydantic model *is* the schema.

Why the i18n audit is worth giving an agent
-------------------------------------------
It answers with evidence rather than an opinion: a rule id, a file and a
line for each translation table embedded in JavaScript or HTML and each
prompt inlined in Python. An assistant that just wrote such a file can check
it in one call, and be wrong in a way that is checkable.

``fastapi-mcp`` is a base dependency since 2026-11-01, so there is no
extra to ask for::

    pip install 'sprezzature-ui'

Then run the MCP server::

    sprezzature-ui-mcp          # entry point (see pyproject)
    # or, equivalently:
    python -m sprezzature_ui.mcp

Usage Example
-------------
>>> # Register the MCP endpoint (``/mcp``) in your client. It publishes:
>>> #   health / audit_i18n
>>> # ...with the same argument names as the FastAPI routes.

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import sys

try:
    from fastapi_mcp import FastApiMCP
except ImportError:  # pragma: no cover - dependency guard

    def main(argv: list[str] | None = None) -> int:
        """
        Entry point when the MCP extra is not installed.

        Takes the same ``argv`` as the real entry point and ignores it:
        the two variants are reached through the same console script, so
        a caller that passes arguments must not get a ``TypeError`` from
        the branch that happens to be missing a dependency.

        Says that fastapi-mcp is missing and stops. A broken install
        needs a one-line fix, not a stack trace.
        """
        print(
            "sprezzature-ui MCP surface could not import fastapi-mcp, which is a "
            "base dependency since 2026-11-01 -- a broken install rather than "
            "a missing extra. Reinstall with: "
            "pip install 'sprezzature-ui'",
            file=sys.stderr,
        )
        sys.exit(1)

else:
    # Reuse the exact same FastAPI app -- MCP is a thin wrapper on top.
    from sprezzature_ui import __version__
    from sprezzature_ui.api import app

    # FastApiMCP mounts an MCP endpoint on the existing FastAPI app; the wrapped
    # instance is kept at module scope so downstream code (tests, ASGI runners)
    # can reach both the FastAPI app and the MCP handler.
    mcp = FastApiMCP(
        app,
        name="sprezzature-ui",
        description=(
            "sprezzature-ui MCP tools: find translations embedded in JavaScript "
            "or HTML and LLM prompts inlined in Python, which belong in "
            "locales/i18n.yaml."
        ),
        include_tags=["meta", "actions"],
    )
    # fastapi-mcp 0.4 calls `Server(self.name, self.description)`, and the
    # second positional parameter of `Server` is the version: every host was
    # told this server's version is a sentence. Put each value back in its slot.
    mcp.server.version = __version__
    mcp.server.instructions = mcp.description

    # Newer fastapi-mcp releases split mount() into transport-specific
    # mount_http() (recommended) and mount_sse(); fall back to the legacy
    # mount() on older versions so a range of fastapi-mcp versions still work.
    if hasattr(mcp, "mount_http"):
        mcp.mount_http()
    else:  # pragma: no cover - legacy fastapi-mcp
        mcp.mount()

    def main(argv: list[str] | None = None) -> int:
        """
        Entry point for the ``sprezzature-ui-mcp`` console script.

        Serves the FastAPI app — which carries both the HTTP routes and the
        MCP endpoint — with ``uvicorn``, in single-worker mode. Meant for
        local or container use; behind a real load balancer, run ``uvicorn``
        or ``gunicorn`` directly.

        Arguments are parsed before anything is bound, so ``--help`` answers
        instead of starting a server and hanging. The parser is click, through
        the same ``sprezzature_command`` every command of this package uses.

        Parameters
        ----------
        argv : list of str or None, optional
            Arguments to parse. ``None`` reads ``sys.argv``.

        Returns
        -------
        int
            0 once the server stops, 2 on a usage error.
        """
        import os

        import click
        from sprezzature_ui_scripts._click import run_command, sprezzature_command

        @sprezzature_command(
            "sprezzature-ui-mcp",
            help=(
                "Serve the sprezzature-ui MCP tools over HTTP. Every tool is a "
                "route on the same FastAPI app, with the MCP endpoint "
                "mounted beside them."
            ),
            epilog=(
                "\b\n"
                "Defaults come from SPREZZATURE_UI_HOST and\n"
                "SPREZZATURE_UI_PORT when those are set.\n"
                "The host defaults to 127.0.0.1: pass --host 0.0.0.0\n"
                "to accept connections from outside this machine."
            ),
        )
        @click.option(
            "--host",
            default=os.environ.get("SPREZZATURE_UI_HOST", "127.0.0.1"),
            show_default=True,
            help="Interface to bind.",
        )
        @click.option(
            "--port",
            type=int,
            default=int(os.environ.get("SPREZZATURE_UI_PORT", "8000")),
            show_default=True,
            help="Port to bind.",
        )
        def _serve(host: str, port: int) -> int:
            """Bind `host`:`port` and serve until interrupted."""
            import uvicorn

            uvicorn.run(app, host=host, port=port, workers=1)
            return 0

        return run_command(_serve, argv)


if __name__ == "__main__":  # pragma: no cover
    main()
