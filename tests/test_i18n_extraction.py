"""
Finding a string in code is half the job; ``--fix`` is the other half.

``audit_i18n`` has always said which strings live in code instead of the
catalogue. Copying them across by hand is where a rule quietly stops being
followed — so ``--fix`` writes them in, and prints the call to paste at each
site. It does not rewrite the call site, on purpose and with precedent:
``pybabel extract`` writes the catalogue and leaves marking the string to the
author, because only the author knows which id the call should use and whether
the surrounding code wants a plural or a placeholder.

What these tests mostly defend is the part that is easy to get wrong in a
silent direction. An extractor reports "4 strings moved", and the reader hears
"the file is clean now". It is only true if everything the audit flagged was
either moved or **named as still needing a hand**. Two versions of the JS loop
failed that, both passing their own tests at the time:

1. the unreadable-value branch tested ``len(entries[bucket]) < 1`` *after*
   filling the bucket, which can never be true — so the list of things needing
   a hand was always empty;
2. ``en: {`` matches the entry-header pattern exactly as well as
   ``"app.title": {`` does, so a locale mapping to a plural object was read as
   the start of a new message and dropped without a word.

Both are tested below by the shape that triggered them, not by the symptom.

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

from pathlib import Path

import audit_i18n  # noqa: E402 — via tests/conftest.py sys.path
import pytest
import yaml


def _catalog(root: Path) -> dict:
    """The catalogue ``--fix`` wrote under `root`."""
    path = root / "locales" / "i18n.yaml"
    assert path.is_file(), f"--fix wrote no catalogue at {path}"
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


# ── Python prompts ─────────────────────────────────────────────────────────


def test_a_prompt_constant_is_moved_with_its_validated_locale(tmp_path: Path) -> None:
    """The language it was written in is the language it was tried in.

    Nothing else is known to work, so ``validated:`` claims nothing else. A
    second locale is a translation somebody has to validate before the
    resolver stops flagging it.
    """
    (tmp_path / "engine.py").write_text(
        'SUMMARIZE_SYSTEM_PROMPT = "You are terse. Answer in one sentence."\n',
        encoding="utf-8",
    )
    written, notes = audit_i18n.fix(
        [tmp_path / "engine.py"], tmp_path / "locales" / "i18n.yaml"
    )
    assert written == 1
    entry = _catalog(tmp_path)["prompts"]["summarize.system.prompt"]
    assert entry["validated"] == "en"
    assert entry["en"].startswith("You are terse")
    assert any("prompt(" in note for note in notes), (
        "--fix moved the string and did not say what to call instead"
    )


def test_the_id_is_dotted_and_lower_case(tmp_path: Path) -> None:
    """``ALT_TEXT_INSTRUCTION`` → ``alt.text.instruction``.

    The shape matters beyond taste: a dotted id is self-disambiguating, which
    is why this catalogue needs no equivalent of gettext's ``pgettext``. There,
    the key *is* the English text, so two identical labels in different parts
    of a screen collide and need a context argument to separate them.
    """
    (tmp_path / "e.py").write_text('ALT_TEXT_INSTRUCTION = "Describe it."\n', encoding="utf-8")
    audit_i18n.fix([tmp_path / "e.py"], tmp_path / "locales" / "i18n.yaml")
    assert "alt.text.instruction" in _catalog(tmp_path)["prompts"]


def test_an_f_string_prompt_is_not_moved(tmp_path: Path) -> None:
    """Its placeholders are code, and the catalogue would make them literal.

    ``f"Summarise {doc}"`` carries a Python expression. Lifted verbatim it
    becomes the characters ``{doc}`` in a model's input — a prompt that reads
    almost right, which is the worst kind.
    """
    (tmp_path / "e.py").write_text(
        'DOC = "x"\nSUMMARY_PROMPT = f"Summarise {DOC} in one line."\n', encoding="utf-8"
    )
    written, _ = audit_i18n.fix([tmp_path / "e.py"], tmp_path / "locales" / "i18n.yaml")
    assert written == 0


def test_an_existing_id_is_left_alone(tmp_path: Path) -> None:
    """Re-running ``--fix`` must not overwrite a validated prompt with a raw one."""
    catalog = tmp_path / "locales" / "i18n.yaml"
    catalog.parent.mkdir(parents=True)
    catalog.write_text(
        "locales: [en, fr]\nprompts:\n  summarize.prompt:\n"
        "    validated: fr\n    fr: Résume.\n",
        encoding="utf-8",
    )
    (tmp_path / "e.py").write_text('SUMMARIZE_PROMPT = "Summarise."\n', encoding="utf-8")
    written, notes = audit_i18n.fix([tmp_path / "e.py"], catalog)
    assert written == 0
    assert any("already in the catalogue" in note for note in notes)
    assert _catalog(tmp_path)["prompts"]["summarize.prompt"]["validated"] == "fr"


# ── JS locale tables ───────────────────────────────────────────────────────


def test_a_locale_table_is_lifted_under_its_message_id(tmp_path: Path) -> None:
    """Both locales, under the id the table used, not under a line number."""
    (tmp_path / "app.js").write_text(
        'const i18n = {\n'
        '  "app.title": {\n'
        '    en: "Dashboard", fr: "Tableau de bord"\n'
        '  }\n'
        '};\n',
        encoding="utf-8",
    )
    written, notes = audit_i18n.fix(
        [tmp_path / "app.js"], tmp_path / "locales" / "i18n.yaml"
    )
    assert written == 1
    assert _catalog(tmp_path)["gui"]["app.title"] == {
        "en": "Dashboard", "fr": "Tableau de bord"
    }
    assert any('t("app.title")' in note for note in notes)


def test_a_locale_mapping_to_a_plural_object_is_reported_not_dropped(
    tmp_path: Path,
) -> None:
    """The bug that made this test exist, by its shape.

    ``en: {`` matches the entry-header pattern, so the line was read as the
    start of a new message, ``continue``d past, and never reached the branch
    that reports what cannot be read. The table left the audit's output
    counted, and the catalogue without it.
    """
    (tmp_path / "app.js").write_text(
        'const messages = {\n'
        '  "results.count": {\n'
        '    en: { one: "1 result", other: "many" }\n'
        '  },\n'
        '  "action.save": {\n'
        '    en: "Save", fr: "Enregistrer"\n'
        '  }\n'
        '};\n',
        encoding="utf-8",
    )
    entries, unparsed = audit_i18n.extract_js(tmp_path / "app.js")
    assert "action.save" in entries
    assert unparsed, (
        "the plural line was neither extracted nor reported — which is the "
        "silent half of a half-done extraction"
    )
    written, notes = audit_i18n.fix(
        [tmp_path / "app.js"], tmp_path / "locales" / "i18n.yaml"
    )
    assert written == 1
    assert any("by hand" in note for note in notes)


def test_a_value_built_by_code_is_not_invented(tmp_path: Path) -> None:
    """``en: makeLabel()`` has no string to move, and none is guessed at."""
    (tmp_path / "app.js").write_text(
        'const i18n = {\n  "a.b": {\n    en: makeLabel(), fr: makeLabel()\n  }\n};\n',
        encoding="utf-8",
    )
    entries, _ = audit_i18n.extract_js(tmp_path / "app.js")
    assert entries == {}


def test_nothing_is_written_when_there_is_nothing_to_move(tmp_path: Path) -> None:
    """A catalogue is not created as a side effect of a clean run."""
    (tmp_path / "clean.py").write_text(
        'from locales.i18n_prompts import prompt\nP = prompt("a.b", "en").text\n',
        encoding="utf-8",
    )
    written, _ = audit_i18n.fix(
        [tmp_path / "clean.py"], tmp_path / "locales" / "i18n.yaml"
    )
    assert written == 0
    assert not (tmp_path / "locales" / "i18n.yaml").exists()


# ── What --fix is honest about ─────────────────────────────────────────────


def test_fix_leaves_the_audit_failing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The string is in the catalogue and still in the code: not clean yet.

    Exiting 0 after ``--fix`` would tell a pre-commit hook the file complies
    while the literal is still the one being used. The run goes green when the
    call site reads from the catalogue — the one edit this tool does not make.
    """
    (tmp_path / "engine.py").write_text('SYSTEM_PROMPT = "Be terse."\n', encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "sys.argv", ["audit_i18n", "--fix", "engine.py"]
    )
    assert audit_i18n.main() == 1
    assert "system.prompt" in _catalog(tmp_path)["prompts"]


def test_the_two_halves_spell_the_validated_key_the_same_way() -> None:
    """A string extracted here has to be resolvable by the emitted runtime.

    Two spellings of this key would mean ``--fix`` writing prompts that the
    loader refuses — and the refusal would read as the author's mistake.
    """
    import i18n_make  # noqa: PLC0415 — compared on purpose, not imported for use

    assert audit_i18n.VALIDATED_KEY == i18n_make.VALIDATED_KEY
