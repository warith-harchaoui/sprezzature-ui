#!/usr/bin/env python3
"""
audit_i18n
==========

Static audit half of the sprezzature-ui unified-i18n rule: translatable strings
— GUI labels and LLM prompts — belong in one per-project catalog,
``locales/i18n.yaml``, never embedded in JavaScript or inlined in Python.

This script flags the two violations of that rule, deterministically and
without a browser, a model, or the network:

- I18N001 — a translation dictionary embedded in JS / HTML: an object
  literal that maps locale codes (``en``, ``fr``, …) to strings, or a variable
  named ``i18n`` / ``translations`` / ``messages`` / ``locales`` / ``strings``
  assigned an object literal. Those belong in ``locales/i18n.yaml``.
- I18N002 — an LLM prompt inlined in Python: a module- or class-level
  constant whose name contains ``PROMPT`` / ``TEMPLATE`` / ``SYSTEM`` /
  ``INSTRUCTION`` assigned a string literal, instead of being loaded from
  ``locales/i18n.yaml`` (or a ``prompts/*.yaml`` catalog).

It is the counterpart to :mod:`i18n_make` (the make half). Output is a JSON
array of findings (``--json``) or human-readable lines, plus an exit code
(0 clean, 1 on any finding) — suitable for ``pre-commit`` and CI.

Extraction (``--fix``)
----------------------

Finding a string in code is half the job; the other half is getting it into the
catalogue, and copying it by hand is how a rule stops being followed.
``--fix`` writes every string it can read confidently into
``locales/i18n.yaml`` — Python prompt constants under ``prompts:``, with
``validated:`` set to the catalogue's source locale, because the language the
prompt was written in *is* the language it was tried in; JS locale tables under
``gui:``.

It does **not** rewrite the call site, and that is deliberate rather than
unfinished. ``pybabel extract`` does not either: it writes the catalogue and
leaves marking the string to the author, because only the author knows which id
the call should use and whether the surrounding code wants a plural form or a
placeholder. So ``--fix`` prints the line to paste for each string it moved,
and anything it could not parse with certainty is reported as needing a hand —
never dropped in silence.

Usage
-----
::

    # Audit a project tree (or explicit files) for i18n-in-code violations
    python audit_i18n.py app.js index.html engine.py
    python audit_i18n.py --json src/            # machine-readable, recurse dirs

    # Move what it finds into locales/i18n.yaml, and say what to paste
    python audit_i18n.py --fix src/

    # 0 = clean, 1 = at least one finding
    python audit_i18n.py src/ && echo "i18n clean"

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # the audit half is stdlib-only; only --fix writes YAML
    yaml = None  # type: ignore[assignment]

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _argparse import make_parser  # noqa: E402

#: File extensions treated as GUI code (checked for I18N001).
JS_EXTS: tuple[str, ...] = (".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx", ".html", ".htm")

#: File extensions treated as Python (checked for I18N002).
PY_EXTS: tuple[str, ...] = (".py",)

#: Variable names that, when assigned an object literal in JS, are a
#: translation catalog living in code rather than in locales/i18n.yaml.
_JS_I18N_NAMES = r"(?:i18n|translations?|messages|locales|strings|dictionary|langs?|LOCALES|I18N|TRANSLATIONS|MESSAGES)"

#: `const i18n = {`, `let translations = {`, `window.MESSAGES = {`, … — a
#: named translation table declared in JS.
_JS_NAMED_TABLE = re.compile(
    r"(?:const|let|var|window\.\w*\.?|\bexport\s+const)\s*" + _JS_I18N_NAMES + r"\s*=\s*\{",
    re.IGNORECASE,
)

#: An object literal whose keys are locale codes mapping to string/object
#: values — e.g. ``{ en: "Save", fr: "Enregistrer" }`` — regardless of the
#: variable name. We require at least TWO distinct locale keys so a lone
#: ``{ en: ... }`` config object is not mistaken for a catalog.
_LOCALE_KEY = re.compile(
    r"""["']?\b(en|fr|es|de|it|pt|nl|ja|zh|ko|ru|ar|hi)\b["']?\s*:\s*["'{]""",
    re.IGNORECASE,
)

#: Python constant names that signal an LLM prompt (I18N002) when assigned a
#: string literal directly rather than loaded from a catalog. Deliberately
#: narrow to ``PROMPT`` / ``INSTRUCTION``: a bare ``*_TEMPLATE`` matches HTML /
#: string templates (e.g. ``PAGE_TEMPLATE``) that are NOT prompts, so it is
#: excluded to keep the rule precise (prompts are ~always named ``*PROMPT*``).
_PY_PROMPT_NAME = re.compile(r"(PROMPT|INSTRUCTION)", re.IGNORECASE)

#: The key naming the locale a prompt was engineered and tested in. Same
#: spelling as :mod:`i18n_make`, because a string extracted here has to be
#: resolvable by the runtime that module emits.
VALIDATED_KEY: str = "validated"


def _finding(rule: str, severity: str, path: str, line: int, message: str, snippet: str) -> dict[str, Any]:
    """Build one finding dict in the shared auditor shape.

    Parameters
    ----------
    rule : str
        Stable rule id (``I18N001`` / ``I18N002``).
    severity : str
        ``"error"`` — every i18n-in-code hit blocks by default.
    path : str
        File the finding is in.
    line : int
        1-based line number.
    message : str
        Human-readable explanation + the fix ("move to locales/i18n.yaml").
    snippet : str
        The offending source line, stripped.

    Returns
    -------
    dict
        A single finding, JSON-serialisable.
    """
    return {"rule": rule, "severity": severity, "path": path, "line": line,
            "message": message, "snippet": snippet}


def audit_js(path: Path) -> list[dict[str, Any]]:
    """Flag GUI translation dictionaries embedded in a JS / HTML file (I18N001).

    Two detectors, deduplicated per line: a translation table declared under a
    telltale name (``const i18n = {``), and any object literal that maps two or
    more locale codes to values (``{ en: …, fr: … }``).

    Parameters
    ----------
    path : pathlib.Path
        A ``.js`` / ``.ts`` / ``.html`` (etc.) file.

    Returns
    -------
    list of dict
        Findings; empty when the file keeps its strings out of code.

    Examples
    --------
    >>> import tempfile, pathlib
    >>> p = pathlib.Path(tempfile.mkstemp(suffix=".js")[1])
    >>> _ = p.write_text('const i18n = { en: "Save", fr: "Enregistrer" };')
    >>> [f["rule"] for f in audit_js(p)]
    ['I18N001']
    """
    findings: list[dict[str, Any]] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    flagged_lines: set[int] = set()
    for i, line in enumerate(text.splitlines(), start=1):
        # Detector 1: a named translation table (const i18n = { … ).
        if _JS_NAMED_TABLE.search(line):
            flagged_lines.add(i)
            continue
        # Detector 2: an inline object literal keyed by >= 2 locale codes.
        # Count DISTINCT locale keys on the line so `{ en: x }` alone (a
        # plausible non-catalog config) does not trip the rule.
        distinct = {m.group(1).lower() for m in _LOCALE_KEY.finditer(line)}
        if len(distinct) >= 2:
            flagged_lines.add(i)
    lines = text.splitlines()
    for i in sorted(flagged_lines):
        findings.append(_finding(
            "I18N001", "error", str(path), i,
            "GUI translations embedded in JS/HTML — move them to locales/i18n.yaml "
            "and load via the compiled locales/i18n.json (see i18n_make.py).",
            lines[i - 1].strip()[:160],
        ))
    return findings


def audit_py(path: Path) -> list[dict[str, Any]]:
    """Flag LLM prompts inlined in a Python file (I18N002).

    Walks the AST for module- or class-level assignments whose target name
    looks like a prompt (``*PROMPT*`` / ``*INSTRUCTION*``, case-insensitive)
    and whose value is a string literal. Loading a prompt
    from a catalog (``load_prompt(...)`` / ``render_prompt(...)``) is a call,
    not a constant string, so compliant code is never flagged.

    Parameters
    ----------
    path : pathlib.Path
        A ``.py`` file.

    Returns
    -------
    list of dict
        Findings; empty when prompts are loaded from a catalog.
    """
    findings: list[dict[str, Any]] = []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        # Not valid Python (a template, a fragment) — nothing to audit.
        return findings

    def check(name: str, value: ast.expr, lineno: int) -> None:
        # Only string-literal values count; a ``load_prompt(...)`` call is fine.
        """Flag a string-literal GUI/prompt value that should live in ``locales/i18n.yaml``."""
        is_str = isinstance(value, ast.Constant) and isinstance(value.value, str)
        # A joined f-string (ast.JoinedStr) built inline is also an inlined prompt.
        is_fstr = isinstance(value, ast.JoinedStr)
        if (is_str or is_fstr) and _PY_PROMPT_NAME.search(name):
            findings.append(_finding(
                "I18N002", "error", str(path), lineno,
                f"LLM prompt '{name}' inlined in Python — move it to "
                "locales/i18n.yaml (prompts:) or a prompts/*.yaml catalog and load it.",
                name,
            ))

    # Only module top-level + class-body assignments (constants), not locals.
    bodies: list[ast.stmt] = list(tree.body)
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            bodies.extend(node.body)
    for node in bodies:
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name):
                    check(tgt.id, node.value, node.lineno)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.value is not None:
            check(node.target.id, node.value, node.lineno)
    return findings


def audit_path(path: Path) -> list[dict[str, Any]]:
    """Audit a single file by extension, dispatching to the JS or Python check.

    Parameters
    ----------
    path : pathlib.Path
        File to audit.

    Returns
    -------
    list of dict
        Findings for the file (empty if the extension is not audited).
    """
    suffix = path.suffix.lower()
    if suffix in JS_EXTS:
        return audit_js(path)
    if suffix in PY_EXTS:
        return audit_py(path)
    return []


# ── Extraction (--fix) ──────────────────────────────────────────────────────

#: A locale-keyed pair inside a JS object literal: ``en: "Save"``. Only the
#: single-line string form is lifted; a nested object or a template literal is
#: reported for a hand instead of guessed at.
_JS_PAIR = re.compile(
    r"""["']?\b(?P<locale>[a-z]{2}(?:-[A-Za-z]{2})?)\b["']?\s*:\s*"""
    r"""(?P<quote>["'])(?P<text>(?:[^"'\\]|\\.)*?)(?P=quote)"""
)

#: The id a JS table entry sits under: ``"app.title": {`` or ``save: {``.
_JS_ENTRY_ID = re.compile(r"""^\s*["']?(?P<id>[\w.\-]+)["']?\s*:\s*\{""")

#: The locale codes :data:`_LOCALE_KEY` recognises, on their own. Needed
#: because ``en: {`` matches :data:`_JS_ENTRY_ID` exactly as well as
#: ``"app.title": {`` does: a locale mapping to an object is a plural entry,
#: not the header of a new message. Without this check the line was read as a
#: header and skipped, so a plural table was dropped without a word.
_LOCALE_CODES: frozenset[str] = frozenset(
    "en fr es de it pt nl ja zh ko ru ar hi".split()
)


def _message_id(constant: str) -> str:
    """A catalogue id for a Python constant name.

    ``SUMMARIZE_SYSTEM_PROMPT`` becomes ``summarize.system.prompt``: dotted,
    lower case, which is the shape the rest of the catalogue uses and what
    makes an id self-disambiguating. gettext needs ``pgettext`` for context
    precisely because its key is the English text instead.
    """
    return ".".join(part.lower() for part in constant.split("_") if part)


def extract_py(path: Path) -> list[tuple[str, str, int]]:
    """Prompt constants to lift out of a Python file.

    Returns
    -------
    list of tuple
        ``(message_id, text, lineno)`` per module- or class-level constant whose
        name looks like a prompt and whose value is a plain string literal. An
        f-string is skipped on purpose: its placeholders are code, and moving it
        verbatim into the catalogue would turn a working interpolation into a
        literal ``{...}`` in a model's input.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return []

    found: list[tuple[str, str, int]] = []
    bodies: list[ast.stmt] = list(tree.body)
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            bodies.extend(node.body)
    for node in bodies:
        targets: list[ast.expr] = []
        value: ast.expr | None = None
        if isinstance(node, ast.Assign):
            targets, value = list(node.targets), node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets, value = [node.target], node.value
        if value is None or not isinstance(value, ast.Constant) or not isinstance(value.value, str):
            continue
        for tgt in targets:
            if isinstance(tgt, ast.Name) and _PY_PROMPT_NAME.search(tgt.id):
                found.append((_message_id(tgt.id), value.value, node.lineno))
    return found


def extract_js(path: Path) -> tuple[dict[str, dict[str, str]], list[int]]:
    """Locale tables to lift out of a JS/HTML file.

    Returns
    -------
    tuple
        ``(entries, unparsed_lines)``. `entries` maps a message id to a
        ``{locale: text}`` dict, read from the single-line string pairs this
        can be sure of. `unparsed_lines` are the lines that matched the audit
        but held no readable pair — a nested object, a template literal, a
        value built by code. Those are returned rather than skipped so the
        caller can say so out loud: a tool that quietly extracts 9 of 12
        strings leaves three in the source and a reader believing otherwise.
    """
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    entries: dict[str, dict[str, str]] = {}
    unparsed: list[int] = []
    current_id: str | None = None
    for number, line in enumerate(lines, 1):
        header = _JS_ENTRY_ID.match(line)
        if header and header.group("id").lower() not in _LOCALE_CODES:
            current_id = header.group("id")
            continue
        pairs = list(_JS_PAIR.finditer(line))
        if not pairs:
            # A locale key whose value this cannot read: a plural object, a
            # template literal, a value built by code. Reported, not skipped.
            # Two versions of this loop got that wrong: the first tested
            # `len(entries[bucket]) < 1` after filling it, which can never be
            # true; the second let `en: {` match the entry-header pattern, so
            # a plural table was read as a header and dropped. Both times the
            # output said "N strings moved" and meant "N of the ones I could".
            if _LOCALE_KEY.search(line):
                unparsed.append(number)
            continue
        # `en: "Save", fr: "Enregistrer"` on one line, under an id or not.
        bucket = current_id or f"line{number}"
        for match in pairs:
            entries.setdefault(bucket, {})[match.group("locale").lower()] = (
                match.group("text").replace('\\"', '"').replace("\\'", "'")
            )
    return entries, unparsed


def fix(paths: list[Path], catalog: Path) -> tuple[int, list[str]]:
    """Move every confidently-readable string into `catalog`.

    Parameters
    ----------
    paths : list of pathlib.Path
        Files already audited.
    catalog : pathlib.Path
        ``locales/i18n.yaml``; created with a minimal head if absent.

    Returns
    -------
    tuple
        ``(count_written, notes)`` — how many ids were added, and one line per
        string the author still has to place by hand or call by id.
    """
    if yaml is None:  # pragma: no cover - dependency guard
        return 0, [
            "--fix writes YAML, which is the [i18n] extra: "
            "pip install 'sprezzature-ui[i18n]'"
        ]

    data: dict[str, Any] = {}
    if catalog.is_file():
        data = yaml.safe_load(catalog.read_text(encoding="utf-8")) or {}
    locales: list[str] = list(data.get("locales") or ["en"])
    source = locales[0]
    gui: dict[str, Any] = data.setdefault("gui", {})
    prompts: dict[str, Any] = data.setdefault("prompts", {})
    data.setdefault("locales", locales)

    written = 0
    notes: list[str] = []

    for path in paths:
        suffix = path.suffix.lower()
        if suffix in PY_EXTS:
            for id_, text, lineno in extract_py(path):
                if id_ in prompts:
                    notes.append(f"{path}:{lineno}: {id_} already in the catalogue — left alone")
                    continue
                # The language it was written in is the language it was tried
                # in. Nothing else is known to work, so nothing else is claimed.
                prompts[id_] = {VALIDATED_KEY: source, source: text}
                written += 1
                notes.append(
                    f"{path}:{lineno}: moved to prompts.{id_} (validated: {source}) — "
                    f'replace the constant with prompt("{id_}", locale).text'
                )
        elif suffix in JS_EXTS:
            entries, unparsed = extract_js(path)
            for id_, by_locale in entries.items():
                if id_ in gui:
                    notes.append(f"{path}: {id_} already in the catalogue — left alone")
                    continue
                gui[id_] = by_locale
                written += 1
                notes.append(
                    f"{path}: moved to gui.{id_} ({', '.join(sorted(by_locale))}) — "
                    f'replace the literal with t("{id_}")'
                )
            for number in unparsed:
                notes.append(
                    f"{path}:{number}: a locale here maps to something this cannot "
                    f"read — a plural object, a template literal, or a value built "
                    f"by code. Move it by hand: a locale mapping to "
                    f"{{one: …, other: …}} is a plural entry, which the catalogue "
                    f"takes as-is under its message id."
                )

    if written:
        catalog.parent.mkdir(parents=True, exist_ok=True)
        catalog.write_text(
            yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
    return written, notes


def gather(paths: list[str]) -> list[Path]:
    """Expand the CLI path arguments into a sorted list of auditable files.

    Directories are walked recursively; the two audited extension groups
    (JS-family, Python) are kept, everything else is dropped. Common vendor /
    build dirs are skipped so a bundled third-party translation file does not
    produce noise.

    Parameters
    ----------
    paths : list of str
        Files and/or directories from the command line.

    Returns
    -------
    list of pathlib.Path
        Deduplicated, sorted files to audit.
    """
    skip = {"node_modules", ".git", "__pycache__", "dist", "build", "vendor", ".venv"}
    out: set[Path] = set()
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            for f in p.rglob("*"):
                if f.is_file() and f.suffix.lower() in JS_EXTS + PY_EXTS \
                        and not (set(f.parts) & skip):
                    out.add(f)
        elif p.is_file():
            out.add(p)
    return sorted(out)


def main() -> int:
    """CLI entry point. Returns 0 when clean, 1 on any finding.

    Returns
    -------
    int
        Process exit code (0 clean, 1 findings).
    """
    p = make_parser(
        prog="sprezzature-ui-i18n-audit",
        description="Flag GUI translations embedded in JS/HTML and LLM prompts "
                    "inlined in Python — both belong in locales/i18n.yaml.",
        epilog=__doc__,
    )
    p.add_argument("paths", nargs="+", help="Files and/or directories to audit.")
    p.add_argument("--json", action="store_true", help="Emit findings as a JSON array.")
    p.add_argument(
        "--fix", action="store_true",
        help="Move the strings into locales/i18n.yaml and print the call to paste. "
             "Does not rewrite the call site — see the module docstring.",
    )
    p.add_argument(
        "--catalog", default="locales/i18n.yaml",
        help="Catalogue --fix writes to (default: locales/i18n.yaml).",
    )
    args = p.parse_args()

    files = gather(args.paths)
    findings: list[dict[str, Any]] = []
    for f in files:
        findings.extend(audit_path(f))

    if args.fix:
        # Only the files that actually tripped the audit: extracting from a
        # clean file would lift strings nobody said were translatable.
        offending = sorted({Path(fd["path"]) for fd in findings})
        written, notes = fix(offending, Path(args.catalog))
        for note in notes:
            print(note)
        print()
        print(f"{written} string(s) moved into {args.catalog}.")
        if written:
            print("Re-run `sprezzature-ui-i18n-make --compile` to rebuild the JSON.")
        # Still non-zero: the strings are in the catalogue and still in the
        # code. The fix is complete when the call sites read from the
        # catalogue, and this tool deliberately does not do that for you.
        return 0 if not findings else 1

    if args.json:
        json.dump(findings, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    else:
        for fd in findings:
            # `path:line: RULE message` — one grep-friendly line per finding.
            print(f"{fd['path']}:{fd['line']}: {fd['rule']} {fd['message']}")
        print()
        print(f"{len(findings)} finding(s)." if findings else "0 findings.")

    return 0 if not findings else 1


if __name__ == "__main__":
    sys.exit(main())
