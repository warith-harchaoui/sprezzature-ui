"""
The catalogue's three mechanisms, and the rule prompts do not share with labels.

Three things were missing from the i18n rule until 2026-10-20, and the first
two were missing *while a reference in this suite taught them*:
``sprezzature-publish/references/i18n.md`` says plurals must go through
``Intl.PluralRules``, says "don't try to encode this with ``if (n === 1)``",
warns "never assume just one/other" because Arabic has six — and the runtime
``i18n_make`` emitted had no plural handling at all, and no interpolation.

The third is not a mechanism but a rule: **a prompt is not a label.** A label
that goes missing can fall back to any locale, or to its own id, because a
human reads it and sees something is wrong. A prompt that goes missing falls
into a model, which reads whatever it is handed and does something plausible
with it. ``t("summarize.system")`` returning the string ``summarize.system`` to
a screen is a visible bug; the same string reaching a model is a silent one.

So the two resolvers differ on purpose, and these are the differences:

=========================  ==========================  =========================
                           ``t(id, params)``           ``prompt(id, locale)``
=========================  ==========================  =========================
locale missing             first declared locale       the **validated** locale
nothing at all             the id, visibly             raises
unvalidated translation    not a concept               returned, and flagged
=========================  ==========================  =========================

The behavioural half runs the emitted JavaScript under node; the structural
half reads the emitted source, so the mechanisms are checked even where node is
absent. Why both: a test that only reads the source cannot tell
``Intl.PluralRules`` wired up from ``Intl.PluralRules`` mentioned in a comment,
and a test that only runs node skips entirely on a machine without it — which
reads like a pass.

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import i18n_make  # noqa: E402 — via tests/conftest.py sys.path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

#: Drives the emitted ES module under node. `fetch` and `document` are the only
#: two browser globals the loader touches, so stubbing them is the whole shim —
#: which is itself a property worth keeping: a loader that needed more of a
#: browser than this could not be tested without one.
_HARNESS = """
import { readFileSync } from "node:fs";
globalThis.fetch = async (url) => ({
  json: async () => JSON.parse(readFileSync(new URL(url), "utf-8")),
});
globalThis.document = { documentElement: { getAttribute: () => null } };

const m = await import("file://%(loader)s");
await m.initI18n("en");
const out = %(expression)s;
process.stdout.write(JSON.stringify(out));
"""


@pytest.fixture(scope="module")
def project(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """A scaffolded project: catalogue, compiled JSON, both loaders."""
    root = tmp_path_factory.mktemp("i18n-project")
    catalog = root / "locales" / "i18n.yaml"
    i18n_make.scaffold(catalog)
    i18n_make.compile_json(catalog)
    i18n_make.emit_loader(catalog)
    i18n_make.emit_python(catalog)
    return root


def _js(project: Path, expression: str) -> object:
    """Evaluate `expression` against the emitted loader, or skip without node."""
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not on PATH; the structural tests still check the source")
    loader = project / "locales" / "i18n.js"
    script = _HARNESS % {"loader": loader, "expression": expression}
    proc = subprocess.run(
        [node, "--input-type=module", "-e", script],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, f"node failed:\n{proc.stdout}\n{proc.stderr}"
    return json.loads(proc.stdout)


def _prompts(project: Path):
    """Import the emitted Python loader out of the scaffolded project."""
    sys.path.insert(0, str(project / "locales"))
    try:
        import i18n_prompts  # noqa: PLC0415 — the module under test is generated
        return i18n_prompts
    finally:
        sys.path.pop(0)


# ── Plurals ────────────────────────────────────────────────────────────────


def test_french_zero_is_singular_and_english_zero_is_not(project: Path) -> None:
    """The case a hand-written count check gets wrong, in the two shipped locales.

    ``Intl.PluralRules("fr").select(0)`` is ``one``; in English it is ``other``.
    So the same zero reads "0 résultat" and "0 results". Any implementation
    built on ``count === 1`` returns "0 résultats" here — grammatical in
    neither language's rules, and invisible to a reviewer who only speaks one.
    """
    got = _js(project, '[0,1,2].map(n => [m.t("results.count", {count:n}, "en"),'
                       ' m.t("results.count", {count:n}, "fr")])')
    assert got == [
        ["0 results", "0 résultat"],
        ["1 result", "1 résultat"],
        ["2 results", "2 résultats"],
    ]


def test_the_emitted_runtime_asks_cldr_rather_than_counting(project: Path) -> None:
    """Structural half: the mechanism is wired, not mentioned.

    Runs without node. ``Intl.PluralRules`` has to appear in a position where
    it selects a category, and the comparison the reference forbids has to be
    absent — a loader could name the API in a comment and still branch on
    ``=== 1`` underneath.
    """
    source = (project / "locales" / "i18n.js").read_text(encoding="utf-8")
    assert "new Intl.PluralRules(" in source
    assert ".select(" in source
    for forbidden in ("count === 1", "count == 1", "n === 1", "n == 1"):
        assert forbidden not in source, (
            f"the emitted loader branches on `{forbidden}`. "
            f"sprezzature-publish/references/i18n.md forbids exactly that: "
            f"plural categories come from CLDR, which Intl.PluralRules carries."
        )


def test_a_plural_entry_falls_back_to_other(project: Path) -> None:
    """``other`` is the one category every language defines, so it is the floor."""
    got = _js(project, 'm.t("results.count", {count: 7}, "ja")')
    # Japanese has a single category, `other`; the entry has en/fr only, so the
    # source locale's forms are used and `other` is the category selected.
    assert got == "7 results"


# ── Named interpolation ────────────────────────────────────────────────────


def test_a_named_placeholder_is_filled_from_params(project: Path) -> None:
    """Named, not positional: a translator reorders words, ``%s %s`` cannot."""
    assert _js(project, 'm.t("greet.user", {name: "Warith"}, "fr")') == "Bonjour Warith"
    assert _js(project, 'm.t("greet.user", {name: "Warith"}, "en")') == "Hello, Warith"


def test_a_placeholder_with_no_value_stays_visible(project: Path) -> None:
    """A missing value should look wrong, like a missing id falling back to the id.

    Blanking it would render "Bonjour ," — which looks like a design choice.
    """
    assert _js(project, 'm.t("greet.user", {}, "fr")') == "Bonjour {name}"


def test_a_missing_id_degrades_to_the_id(project: Path) -> None:
    """The GUI's floor: visible, not thrown, not empty."""
    assert _js(project, 'm.t("no.such.message")') == "no.such.message"


# ── Prompts: the validated locale ──────────────────────────────────────────


def test_a_missing_prompt_locale_falls_back_to_the_validated_one(project: Path) -> None:
    """Not to the first declared locale, which is only the validated one by luck."""
    got = _js(project, 'm.prompt("summarize.system", "de")')
    assert got["locale"] == "en"
    assert got["validatedLocale"] == "en"
    assert got["validatedLocaleUsed"] is True
    assert got["text"].startswith("You are a concise assistant")


def test_a_translated_prompt_is_returned_and_flagged(project: Path) -> None:
    """The caller has to be able to know, because the model's behaviour moved.

    The translation is not withheld — refusing it would make the catalogue
    useless for anyone who did validate a second language. What is refused is
    returning it *silently*.
    """
    got = _js(project, 'm.prompt("summarize.system", "fr")')
    assert got["locale"] == "fr"
    assert got["validatedLocaleUsed"] is False
    assert got["text"].startswith("Vous êtes un assistant concis")


def test_an_unknown_prompt_raises_rather_than_returning_its_id(project: Path) -> None:
    """``t()`` returns the id; ``prompt()`` must not, and this is why.

    A label reading "summarize.system" on screen is caught by the first person
    who looks. The same string reaching a model is a prompt — a short, strange
    one that it will answer anyway, plausibly, with no error anywhere.
    """
    got = _js(project, '(() => { try { m.prompt("absent"); return null; }'
                       ' catch (e) { return e.message; } })()')
    assert got is not None, "prompt() returned instead of raising for an unknown id"
    assert "absent" in got


def test_the_python_loader_resolves_the_same_three_ways(project: Path) -> None:
    """Two runtimes, one rule. A prompt assembled in Python and the same prompt
    read in the browser must not disagree about which locale they are using."""
    loader = _prompts(project)
    validated = loader.prompt("summarize.system", "en")
    translated = loader.prompt("summarize.system", "fr")
    absent = loader.prompt("summarize.system", "de")

    assert (validated.locale, validated.validated_locale_used) == ("en", True)
    assert (translated.locale, translated.validated_locale_used) == ("fr", False)
    assert (absent.locale, absent.validated_locale_used) == ("en", True)
    assert absent.text == validated.text


def test_the_python_loader_refuses_an_unknown_prompt(project: Path) -> None:
    """Same floor as the JS side: no id-as-prompt, in either runtime."""
    loader = _prompts(project)
    with pytest.raises(KeyError):
        loader.prompt("absent", "en")


def test_the_python_loader_refuses_a_prompt_with_no_validated_locale(
    project: Path, tmp_path: Path
) -> None:
    """A prompt with no language it was tested in has nothing safe to fall back on."""
    loader = _prompts(project)
    catalog = {
        "locales": ["en"],
        "prompts": {"orphan": {"en": "do something"}},
    }
    (tmp_path / "i18n.json").write_text(json.dumps(catalog), encoding="utf-8")
    with pytest.raises(ValueError, match="validated"):
        loader.prompt("orphan", "en", directory=tmp_path)


# ── The compile step refuses what neither runtime can resolve ──────────────


def test_compile_refuses_a_prompt_without_a_validated_locale(tmp_path: Path) -> None:
    """Better here than at the first call that needs it.

    At compile time this is one line of output. At call time it is a model
    receiving a prompt from a language nobody measured, and an answer that
    looks fine.
    """
    catalog = tmp_path / "locales" / "i18n.yaml"
    catalog.parent.mkdir(parents=True)
    catalog.write_text(
        "locales: [en]\nprompts:\n  orphan:\n    en: do something\n", encoding="utf-8"
    )
    with pytest.raises(SystemExit) as raised:
        i18n_make.compile_json(catalog)
    assert "validated" in str(raised.value)


def test_check_prompts_names_each_way_a_prompt_can_be_unresolvable() -> None:
    """Three distinct faults, three distinct messages — not one generic refusal."""
    problems = i18n_make.check_prompts({
        "locales": ["en", "fr"],
        "prompts": {
            "no.validated": {"en": "x"},
            "validated.elsewhere": {"validated": "de", "en": "x"},
            "validated.empty": {"validated": "fr", "en": "x"},
            "fine": {"validated": "en", "en": "x"},
        },
    })
    joined = "\n".join(problems)
    assert "no.validated" in joined
    assert "validated.elsewhere" in joined and "locales" in joined
    assert "validated.empty" in joined
    assert "fine" not in joined


def test_a_sound_catalogue_has_nothing_to_report() -> None:
    """The other half of the previous test: no false positive on the starter."""
    assert i18n_make.check_prompts(i18n_make._STARTER) == []


def test_the_starter_catalogue_shows_both_shapes() -> None:
    """What a reader copies first should be the shape they need second.

    A starter with only flat strings teaches the flat string, and the plural
    arrives later as a surprise — which is how a project ends up with
    ``count === 1`` in it.
    """
    gui = i18n_make._STARTER["gui"]
    plural = [k for k, v in gui.items() if isinstance(v.get("en"), dict)]
    placeholder = [k for k, v in gui.items() if isinstance(v.get("en"), str) and "{" in v["en"]]
    assert plural, "no plural entry in the starter catalogue"
    assert placeholder, "no named-placeholder entry in the starter catalogue"
    for key in plural:
        assert set(gui[key]["en"]) <= set(i18n_make.PLURAL_CATEGORIES)
