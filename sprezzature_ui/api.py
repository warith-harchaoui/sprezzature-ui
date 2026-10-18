"""
The HTTP surface — narrow on purpose.

Two routes, and the narrowness is the point rather than an omission. This
brick's main job is writing interfaces, and that is the model's work guided
by ``SKILL.md``: no HTTP route can carry "make this dashboard legible", and
offering one would be the forced surface the house contract (``SURFACES.md``)
exists to prevent. The exemption is declared there by name.

What *can* cross a network boundary is the i18n audit: source in, findings
out. So that is what is here.

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import tempfile
from pathlib import Path

try:
    from fastapi import FastAPI
    from fastapi.responses import RedirectResponse
except ImportError as exc:  # pragma: no cover - dependency guard
    raise ImportError(
        "The FastAPI HTTP surface requires the [api] extra. "
        "Install with: pip install 'sprezzature-ui[api]'"
    ) from exc

from pydantic import BaseModel, Field

from sprezzature_ui import __version__

app = FastAPI(
    title="sprezzature-ui",
    version=__version__,
    summary="The deterministic half: find the strings that should be in a catalogue.",
    description=(
        "Writing an interface is the skill's work, not an endpoint's. What "
        "is served here is the part a machine can check: translations "
        "embedded in JavaScript and HTML, and LLM prompts inlined in Python."
    ),
)


class AuditRequest(BaseModel):
    """One source file, as text."""

    source: str = Field(description="The file's contents.")
    filename: str = Field(
        default="app.js",
        description="Name the source is reported under. Its **extension "
                    "decides which rules run** — .js and .html are read for "
                    "embedded translations, .py for inlined prompts.",
    )


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")


@app.get(
    "/health",
    tags=["meta"],
    operation_id="health",
    summary="Check that this i18n-audit server is up",
)
def health() -> dict:
    """Liveness."""
    return {"status": "ok", "version": __version__}


@app.post(
    "/v1/i18n-audit",
    tags=["actions"],
    operation_id="audit_i18n",
    summary="Find strings that belong in the translation catalogue",
)
def audit(request: AuditRequest) -> dict:
    """Report every string that should live in ``locales/i18n.yaml``.

    Invisible until somebody needs a second language and discovers the
    sentences are scattered through the source — which is late, and is the
    reason this is a gate rather than a chore.
    """
    from sprezzature_ui_scripts.audit_i18n import audit_path

    with tempfile.TemporaryDirectory() as scratch:
        path = Path(scratch) / Path(request.filename).name
        path.write_text(request.source, encoding="utf-8")
        findings = audit_path(path)

    # The scratch path is an implementation detail of serving text over HTTP.
    # A caller who posted a string should get their own filename back, not
    # `/var/folders/…` — which is noise at best and a leak of the server's
    # layout at worst.
    for finding in findings:
        finding["path"] = request.filename

    return {"findings_total": len(findings), "findings": findings}
