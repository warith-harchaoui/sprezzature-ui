"""
conftest.py — fixtures for the opt-in prompt-locale evaluation suite.

Every test in :mod:`tests.eval` is marked ``@pytest.mark.eval`` and excluded
from the default run (see ``pyproject.toml``). Run it with::

    pytest -m eval

These fixtures keep the suite friendly to a machine with no daemon and no
models: :func:`ollama_available` skips rather than fails when nothing answers,
and :func:`text_model` resolves the pulled tag to use. They deliberately do not
start a daemon or pull anything — that is an installer's job, not a test
session's.

Two things worth knowing before reading the tests:

**One model, named once.** The house rule is a single authorised VLM,
``qwen3-vl``, and every call in this suite routes through
``best_engine_ai_helper.llm.chat`` like every other call in the project. The tag
is resolved from what Ollama actually holds, matched on the ``qwen3-vl`` prefix,
so a 4b on a laptop and an 8b on a workstation both work and neither is
hardcoded.

**The safety scan is off here, on purpose.** ``chat()`` has scanned every prompt
and response through an NSFW classifier since 1.4. With ``transformers``
installed that pulls a 270 MB model and adds minutes per call, to classify
sentences this suite wrote itself. The scan belongs to the dependency and is
tested there; what is measured here is whether a translated prompt behaves like
the one it was translated from.

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from collections.abc import Callable
from pathlib import Path

import pytest

# ``tests/eval/conftest.py`` → repo root is three levels up.
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent

#: The one authorised VLM family. A tag is accepted when it starts with this,
#: so the size suffix is the machine's business.
MODEL_PREFIX = "qwen3-vl"

# Module-level cache so the daemon is probed at most once per session. The
# sentinel distinguishes "not asked yet" from "asked, nothing there".
_SENTINEL: object = object()
_TAGS: object | dict | None = _SENTINEL


@pytest.fixture(scope="session")
def eval_repo_root() -> Path:
    """The repository root."""
    return _REPO_ROOT


def _tags_url() -> str:
    """The daemon's tags endpoint, honouring ``OLLAMA_HOST``."""
    base = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
    if not base.startswith(("http://", "https://")):
        base = f"http://{base}"
    return f"{base}/api/tags"


def _fetch_tags(timeout: float = 1.5) -> dict | None:
    """Probe the daemon once. Unreachable, slow and malformed all mean None."""
    global _TAGS
    if _TAGS is not _SENTINEL:
        return _TAGS  # type: ignore[return-value]
    try:
        with urllib.request.urlopen(_tags_url(), timeout=timeout) as resp:
            _TAGS = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError):
        _TAGS = None
    return _TAGS  # type: ignore[return-value]


@pytest.fixture(scope="session")
def ollama_available() -> dict:
    """Skip cleanly when no daemon answers; return its ``/api/tags`` payload."""
    tags = _fetch_tags()
    if tags is None:
        pytest.skip(
            f"no Ollama daemon at {_tags_url()}. Start it with `ollama serve`, "
            f"or pull the model with `ollama pull {MODEL_PREFIX}:8b`."
        )
    return tags


@pytest.fixture(scope="session")
def text_model(ollama_available: dict) -> str:
    """The pulled ``qwen3-vl`` tag to use, or a skip naming what to pull.

    Resolved rather than hardcoded: ``best_engine_ai_helper`` defaults to a tag
    this machine may not hold, and a test that fails on that is reporting the
    machine's inventory, not the prompt's behaviour.
    """
    pulled = [m.get("name", "") for m in ollama_available.get("models", [])]
    for name in pulled:
        if name.startswith(MODEL_PREFIX):
            return name
    pytest.skip(
        f"no {MODEL_PREFIX} tag pulled (Ollama holds: {', '.join(pulled) or 'nothing'}). "
        f"Pull one with `ollama pull {MODEL_PREFIX}:8b`."
    )
    raise AssertionError("unreachable")  # pragma: no cover - pytest.skip raises


@pytest.fixture(scope="session")
def ask(text_model: str) -> Callable[..., str]:
    """Return ``ask(prompt, system=None)`` → the model's text.

    Routed through ``best_engine_ai_helper.llm.chat`` like the rest of the
    project, at temperature 0 so a difference between two runs is a difference
    between two prompts, and with the content-safety scan off (see this
    module's docstring).
    """
    llm = pytest.importorskip(
        "best_engine_ai_helper.llm",
        reason="best-engine-ai-helper is not installed; it is what routes every "
        "model call in this project",
    )
    # A judge call is longer than the answer it judges: DeepEval's rubric plus
    # its JSON instruction is several times the size of a summarisation prompt,
    # and a small local model spends minutes on it. The 120 s default cut the
    # first run off mid-sentence, which arrives as a connection error and reads
    # like the daemon died. `setdefault`, so a value set outside wins.
    os.environ.setdefault("SPREZZATURE_LLM_TIMEOUT", "900")

    def _ask(prompt: str, system: str | None = None) -> str:
        return llm.chat(
            prompt,
            system=system,
            model=text_model,
            temperature=0.0,
            safety=False,
        )

    return _ask
