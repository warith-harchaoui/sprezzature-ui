"""
The example this package sets has to pass the suite's own lint.

This is the package whose job is to say what an interface should look like,
and it ships markup: a starter page, component snippets, chart fragments. If
*that* markup fails the accessibility lint of the sibling package next door,
the advice is worth nothing — and the failure is silent, because nothing was
checking.

It was not hypothetical. `assets/components/card.html` failed
`body-text-tracking-tight` on a KPI figure at `text-4xl tracking-tight`.
Investigating it sharpened the rule rather than the card: a 4xl number in a
tile is one glance, not a paragraph, and the evidence behind that rule is
about continuous reading. The exemption had been promised in the rule's own
docstring and never implemented.

Skipped when the sibling is not installed — this reaches across packages on
purpose, and a developer with only this one checked out should not see a
failure that is about their checkout.

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
MARKUP = sorted(ROOT.joinpath("assets").rglob("*.html"))


@pytest.fixture(scope="module")
def lint():
    """The sibling's linter, or a skip naming what would install it."""
    try:
        from sprezzature_accessibility import lint_file
    except ImportError:
        pytest.skip("needs the sibling linter: pip install sprezzature-accessibility")
    return lint_file


def test_this_package_actually_ships_markup() -> None:
    """An empty glob would make every check below pass by testing nothing.

    The directory could be renamed, the assets could stop shipping, and the
    parametrised test would quietly collect zero cases and report green.
    """
    assert MARKUP, f"no HTML under {ROOT / 'assets'} — did the assets move?"


@pytest.mark.parametrize("page", MARKUP, ids=lambda p: p.name)
def test_every_shipped_page_passes_the_suite_lint(page: Path, lint) -> None:
    """The exemplar must not fail the standard it exemplifies."""
    findings = lint(page, frozenset())
    assert not findings, "\n".join(f"{page.name}:{f.line} {f.rule}: {f.message}" for f in findings)


def _is_document(text: str) -> bool:
    """Whether this file is a whole page rather than a fragment.

    Decided on what the file *starts* with, after comments, not on whether
    the string ``<html`` appears somewhere: the theme-toggle component
    explains `document.documentElement` in its header comment, and a
    substring check called that a document.
    """
    import re

    stripped = re.sub(r"<!--.*?-->", "", text, flags=re.S).lstrip()
    return stripped[:200].lower().lstrip().startswith(("<!doctype", "<html"))


def test_every_shipped_page_declares_its_language() -> None:
    """`lang` is the one attribute a screen reader cannot guess.

    Checked separately from the lint above because a component fragment
    legitimately has no ``<html>`` element — only whole pages are asked.
    """
    documents = [p for p in MARKUP if _is_document(p.read_text(encoding="utf-8"))]
    assert documents, "no whole page among the shipped markup — all fragments?"
    for page in documents:
        head = page.read_text(encoding="utf-8")
        assert "lang=" in head, f"{page.name} is a document without lang="
