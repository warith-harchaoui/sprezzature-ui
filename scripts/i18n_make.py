#!/usr/bin/env python3
"""
i18n_make
=========

Make half of the sprezzature-ui unified-i18n rule: establish
``locales/i18n.yaml`` as the single per-project source of truth for
translatable strings — GUI labels and LLM prompts — and emit the glue so a
vanilla-JS front end and a Python prompt loader read from it instead of
hardcoding strings.

Four deterministic steps (all run by default; select one with a flag):

1. scaffold — create ``locales/i18n.yaml`` if it is missing, with the
   declared ``locales`` and example ``gui:`` / ``prompts:`` entries.
2. compile — read ``locales/i18n.yaml`` and write ``locales/i18n.json``
   (browsers cannot parse YAML; the JS runtime fetches the JSON).
3. emit-loader — write ``locales/i18n.js``, a small framework-free ES module
   that fetches ``i18n.json`` and exposes ``initI18n(locale)``,
   ``t(id, params)`` and ``prompt(id, locale)``.
4. emit-python — write ``locales/i18n_prompts.py``, the stdlib-only prompt
   loader that reads the same compiled catalogue. Promised by this module's
   own docstring since the rule was written, and absent until 2026-10-20: the
   prose described a runtime that did not exist.

Its counterpart is :mod:`audit_i18n` (the audit half), which flags strings that
live in code instead of ``locales/i18n.yaml`` — and, with ``--fix``, moves them.

Plurals
-------

A message that counts things cannot be one string. English has two forms,
French two with different boundaries, Russian three, Arabic six, Japanese one.
So an entry may map a locale to **CLDR plural categories** instead of to a
string::

    results.count:
      en: {one: "{count} result",   other: "{count} results"}
      fr: {one: "{count} résultat", other: "{count} résultats"}

and the runtime picks the category with ``Intl.PluralRules``, which carries the
CLDR data in every browser. ``sprezzature-publish/references/i18n.md`` has
taught exactly this — "don't try to encode this with ``if (n === 1)``", "never
assume just one/other" — while the runtime emitted here had no plural handling
at all. A rule a reference teaches has to be one the emitted runtime can obey.

Named interpolation
-------------------

``{name}`` placeholders, filled from the params object: ``t("greet", {name})``.
Named, not positional, because a translator reorders words and ``%s %s`` gives
them no way to know which is which. A placeholder with no matching param is
left visible rather than blanked — a missing value should look wrong, the same
way a missing message id falls back to the id.

Prompts have a validated locale
-------------------------------

A prompt is not a UI label. It has one language in which it was engineered and
tested, and translating it changes what the model does: a reordered clause or a
softened imperative moves the output. So every ``prompts:`` entry declares the
locale it was validated in::

    summarize.system:
      validated: en
      en: "You are a concise assistant. Summarise the input in three bullets."
      fr: "Vous êtes un assistant concis. Résumez l'entrée en trois puces."

and the resolution rules differ from the GUI's on purpose:

* a locale with no entry falls back to the **validated** text — never to the
  first declared locale, and never to the message id, which as a prompt would
  hand the model the string ``summarize.system``;
* a locale that *has* an entry gets it, and the caller is told it is not the
  validated one, so an application can log it or refuse;
* nothing is translated at call time. A machine translation of a prompt is a
  behavioural change nobody measured.

``tests/eval/test_prompt_locale_eval.py`` is where that last claim stops being
an assertion about taste and becomes a measurement.

Usage
-----
::

    # Full scaffold in ./locales (init if missing, compile, both loaders)
    python i18n_make.py

    # Point at a project root; only re-compile YAML -> JSON
    python i18n_make.py --dir path/to/project --compile

    # In the browser:  import { initI18n, t } from "./locales/i18n.js";
    #                   await initI18n();
    #                   el.textContent = t("results.count", {count: 3});

    # In Python:       from locales.i18n_prompts import prompt
    #                   p = prompt("summarize.system", "fr")
    #                   if not p.validated_locale_used: log.warning(...)

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as _exc:  # pragma: no cover - dependency guard
    raise SystemExit(
        "the catalogue tools read and write YAML, which is the [i18n] extra: "
        "pip install 'sprezzature-ui[i18n]'"
    ) from _exc

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _argparse import make_parser  # noqa: E402

#: CLDR plural categories, in the order the specification lists them. An entry
#: whose locale maps to a dict of these is a plural message; a dict with any
#: other key is a mistake, which the audit half reports.
PLURAL_CATEGORIES: tuple[str, ...] = ("zero", "one", "two", "few", "many", "other")

#: The key naming the locale a prompt was engineered and tested in.
VALIDATED_KEY: str = "validated"

#: Starter catalog written by --init. One namespace for GUI strings, one for
#: prompts — both are the same message in language X, with different rules for
#: what happens when language X is missing.
_STARTER: dict[str, Any] = {
    "locales": ["en", "fr"],
    "gui": {
        "app.title": {"en": "My App", "fr": "Mon application"},
        "action.save": {"en": "Save", "fr": "Enregistrer"},
        "empty.no_results": {"en": "No results yet", "fr": "Aucun résultat pour l'instant"},
        # A counting message and a named placeholder. Both shapes go in the
        # starter so the first thing a reader copies is the right one.
        "results.count": {
            "en": {"one": "{count} result", "other": "{count} results"},
            "fr": {"one": "{count} résultat", "other": "{count} résultats"},
        },
        "greet.user": {"en": "Hello, {name}", "fr": "Bonjour {name}"},
    },
    "prompts": {
        "summarize.system": {
            VALIDATED_KEY: "en",
            "en": "You are a concise assistant. Summarise the input in three bullet points.",
            "fr": "Vous êtes un assistant concis. Résumez l'entrée en trois puces.",
        },
    },
}

#: The vanilla-JS runtime emitted by --emit-loader. Framework-free ES module;
#: reads the compiled JSON, honours <html lang>, selects plural forms through
#: Intl.PluralRules, fills named placeholders, and resolves prompts against
#: their validated locale. Kept as source here so the make step is
#: deterministic.
_LOADER_JS = """\
// i18n.js — load locales/i18n.json (compiled from locales/i18n.yaml, the single
// source of truth for GUI strings AND prompts) and translate by message id.
// Strings live in YAML, never hardcoded here. Generated by sprezzature-ui i18n_make.
let CATALOG = { locales: ["en"], gui: {}, prompts: {} };
let LOCALE = "en";

// Fetch the compiled catalog once. Call before the first t(); returns the
// catalog so callers can also read prompts (CATALOG.prompts[id][locale]).
export async function initI18n(locale) {
  const res = await fetch(new URL("./i18n.json", import.meta.url));
  CATALOG = await res.json();
  LOCALE = locale
    || document.documentElement.getAttribute("lang")
    || (CATALOG.locales && CATALOG.locales[0])
    || "en";
  return CATALOG;
}

// Fill {name} placeholders from params. A placeholder with no matching param is
// left as written: a missing value should look wrong rather than vanish, the
// same way a missing id falls back to the id.
function interpolate(text, params) {
  if (!params) return text;
  return text.replace(/\\{(\\w+)\\}/g, (match, key) =>
    Object.prototype.hasOwnProperty.call(params, key) ? String(params[key]) : match
  );
}

// Pick a CLDR plural category for `count` in `locale`. Intl.PluralRules carries
// the CLDR data, so French gets its own boundaries and Arabic its six forms;
// a hand-written count check would be English with extra steps. Falls back to
// "other", the one category every language defines.
function plural(forms, count, locale) {
  const category = new Intl.PluralRules(locale).select(Number(count));
  return forms[category] ?? forms.other ?? forms[Object.keys(forms)[0]];
}

// Translate a GUI message id. `params` fills {placeholders}; a `count` in it
// also selects the plural form when the entry has one. Falls back to the source
// locale, then the id itself, so a missing key degrades visibly.
export function t(id, params = null, locale = LOCALE) {
  const entry = (CATALOG.gui && CATALOG.gui[id]) || {};
  const src = (CATALOG.locales && CATALOG.locales[0]) || "en";
  const value = entry[locale] ?? entry[src];
  if (value === undefined) return id;
  const text = typeof value === "string"
    ? value
    : plural(value, params && params.count, locale);
  return interpolate(text, params);
}

// Resolve a prompt. Unlike t(), this never falls back to the first declared
// locale and never returns the id: handing a model the string "summarize.system"
// is a silent and expensive failure. A locale with no entry gets the validated
// text, and the caller is told which locale it actually got.
export function prompt(id, locale = LOCALE) {
  const entry = (CATALOG.prompts && CATALOG.prompts[id]) || null;
  if (!entry) {
    throw new Error(`i18n: no prompt "${id}" in the catalog`);
  }
  const validated = entry.validated;
  if (!validated || entry[validated] === undefined) {
    throw new Error(
      `i18n: prompt "${id}" declares no validated locale, or none with text. ` +
      `A prompt without a language it was tested in has no safe fallback.`
    );
  }
  const asked = entry[locale];
  const used = asked === undefined ? validated : locale;
  return {
    id,
    text: entry[used],
    locale: used,
    validatedLocale: validated,
    validatedLocaleUsed: used === validated,
  };
}

// Current locale (read-only helper for callers that render lang-dependent UI).
export function currentLocale() { return LOCALE; }
"""

#: The Python prompt loader emitted by --emit-python. Standard library only, so
#: it runs wherever the project assembles its prompts.
#:
#: Prompts only, on purpose. A GUI string with plural forms needs CLDR data to
#: pick a category and the standard library has none, while the browser runtime
#: beside it has the lot through Intl.PluralRules. A hand-rolled count check
#: here would be the exact rule the reference tells people not to write,
#: shipped by the tool that tells them.
_LOADER_PY = '''\
"""
i18n_prompts — read the compiled catalogue and resolve a prompt for a locale.

Generated by sprezzature-ui i18n_make. Standard library only.

Prompts only, deliberately. A GUI string with plural forms needs CLDR data to
choose a category; the standard library has none, and the browser runtime beside
this file has it through ``Intl.PluralRules``. A hand-rolled count check here
would be the very rule the i18n reference tells you not to write.

A prompt has one language it was engineered and tested in, named by
``validated:`` in the catalogue. Translating a prompt changes what the model
does, so:

* a locale with no entry resolves to the **validated** text;
* a locale that has an entry gets it, and ``validated_locale_used`` is False so
  the caller can log it or refuse;
* nothing is translated here. A machine translation of a prompt is a
  behavioural change nobody measured.

Usage
-----
::

    from locales.i18n_prompts import prompt

    p = prompt("summarize.system", "fr")
    if not p.validated_locale_used:
        log.warning("prompt %s: using unvalidated %s", p.id, p.locale)
    reply = llm.chat(p.text)
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

#: The key naming the locale a prompt was engineered and tested in.
VALIDATED_KEY = "validated"

_HERE = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Prompt:
    """One resolved prompt, and which locale it actually came from."""

    id: str
    text: str
    locale: str
    validated_locale: str
    validated_locale_used: bool


def _catalog(directory=None):
    """Read the compiled catalogue beside this file.

    The JSON is read rather than the YAML: it is what ``i18n_make --compile``
    writes for the browser, the standard library can parse it without the
    [i18n] extra, and reading the same artefact both runtimes read is what
    keeps them from disagreeing.
    """
    path = (Path(directory) if directory else _HERE) / "i18n.json"
    if not path.is_file():
        raise FileNotFoundError(
            "%s is missing. Run `sprezzature-ui-i18n-make --compile` to write "
            "it from locales/i18n.yaml." % path
        )
    return json.loads(path.read_text(encoding="utf-8"))


def prompt(id, locale, directory=None):
    """Resolve prompt `id` for `locale`.

    Raises
    ------
    KeyError
        If the catalogue has no such prompt. Deliberately not a fallback to the
        id: handing a model the string ``summarize.system`` is a silent and
        expensive failure.
    ValueError
        If the prompt declares no validated locale, or declares one with no
        text. A prompt without a language it was tested in has no safe
        fallback, so there is nothing honest to return.
    """
    prompts = _catalog(directory).get("prompts") or {}
    entry = prompts.get(id)
    if entry is None:
        raise KeyError("no prompt %r in the catalogue" % id)
    validated = entry.get(VALIDATED_KEY)
    if not validated or entry.get(validated) is None:
        raise ValueError(
            "prompt %r declares no validated locale, or none with text. Add "
            "`%s: <locale>` naming the language it was engineered and tested "
            "in." % (id, VALIDATED_KEY)
        )
    used = locale if entry.get(locale) is not None else validated
    return Prompt(
        id=id,
        text=entry[used],
        locale=used,
        validated_locale=validated,
        validated_locale_used=used == validated,
    )


def locales(directory=None):
    """The locales the catalogue declares, source locale first."""
    return list(_catalog(directory).get("locales") or [])
'''


def scaffold(catalog: Path) -> bool:
    """Create ``locales/i18n.yaml`` with the starter catalog if it is absent.

    Parameters
    ----------
    catalog : pathlib.Path
        Target ``locales/i18n.yaml`` path.

    Returns
    -------
    bool
        ``True`` if the file was created, ``False`` if it already existed
        (never overwrite a real catalog).
    """
    if catalog.exists():
        return False
    catalog.parent.mkdir(parents=True, exist_ok=True)
    header = (
        "# locales/i18n.yaml — single source of truth for translatable strings.\n"
        "# One entry per message id; one sub-key per declared locale. Serves the\n"
        "# GUI (gui:) AND the LLM prompts (prompts:). Never hardcode a string in\n"
        "# JS or inline a prompt in Python — add it here and load it.\n"
        "#\n"
        "# A counting message maps a locale to CLDR plural categories instead of\n"
        "# to a string (one/other below; zero/two/few/many exist too). The\n"
        "# runtime picks the category with Intl.PluralRules, so each language\n"
        "# gets its own boundaries. {name} placeholders come from the params.\n"
        "#\n"
        "# Every prompt declares `validated:` — the one language it was\n"
        "# engineered and tested in. A missing translation falls back to that\n"
        "# text, never to the first locale and never to the message id.\n"
    )
    catalog.write_text(
        header + yaml.safe_dump(_STARTER, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return True


def check_prompts(data: dict[str, Any]) -> list[str]:
    """Reasons `data`'s ``prompts:`` section cannot be resolved safely.

    Parameters
    ----------
    data : dict
        A parsed catalogue.

    Returns
    -------
    list of str
        One message per prompt that declares no ``validated:`` locale, names
        one absent from ``locales:``, or names one with no text. Empty when
        every prompt can be resolved.
    """
    declared = list(data.get("locales") or [])
    problems: list[str] = []
    for id_, entry in sorted((data.get("prompts") or {}).items()):
        if not isinstance(entry, dict):
            problems.append(f"prompt {id_!r} is not a mapping of locale to text")
            continue
        validated = entry.get(VALIDATED_KEY)
        if not validated:
            problems.append(
                f"prompt {id_!r} declares no `{VALIDATED_KEY}:` locale. Name the "
                f"language it was engineered and tested in — a translation that "
                f"goes missing has nothing else safe to fall back to."
            )
            continue
        if declared and validated not in declared:
            problems.append(
                f"prompt {id_!r} is validated in {validated!r}, which is not in locales: {declared}"
            )
        if entry.get(validated) is None:
            problems.append(f"prompt {id_!r} is validated in {validated!r} and has no text for it")
    return problems


def compile_json(catalog: Path) -> Path:
    """Compile ``locales/i18n.yaml`` to ``locales/i18n.json`` for the browser.

    Parameters
    ----------
    catalog : pathlib.Path
        Source ``locales/i18n.yaml``.

    Returns
    -------
    pathlib.Path
        The written ``locales/i18n.json`` path.

    Raises
    ------
    SystemExit
        If the catalog does not exist (run ``--init`` first), or if a prompt
        cannot be resolved safely. The second is a compile error on purpose:
        neither runtime has a safe fallback for such a prompt, so letting it
        through would only move the failure to the first call that needs it —
        where it arrives as a model doing something subtly different.
    """
    if not catalog.exists():
        sys.exit(f"No catalog at {catalog}. Run with --init first.")
    data = yaml.safe_load(catalog.read_text(encoding="utf-8")) or {}
    problems = check_prompts(data)
    if problems:
        sys.exit("\n".join(f"{catalog}: {message}" for message in problems))
    out = catalog.with_suffix(".json")
    # Sort keys for a deterministic, diff-stable build artifact.
    out.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return out


def emit_loader(catalog: Path) -> Path:
    """Write the framework-free ``locales/i18n.js`` runtime next to the catalog.

    Parameters
    ----------
    catalog : pathlib.Path
        The catalog path (used only to locate the ``locales/`` dir).

    Returns
    -------
    pathlib.Path
        The written ``locales/i18n.js`` path.
    """
    js = catalog.parent / "i18n.js"
    js.parent.mkdir(parents=True, exist_ok=True)
    js.write_text(_LOADER_JS, encoding="utf-8")
    return js


def emit_python(catalog: Path) -> Path:
    """Write the stdlib-only ``locales/i18n_prompts.py`` loader next to the catalog.

    Parameters
    ----------
    catalog : pathlib.Path
        The catalog path (used only to locate the ``locales/`` dir).

    Returns
    -------
    pathlib.Path
        The written ``locales/i18n_prompts.py`` path.
    """
    py = catalog.parent / "i18n_prompts.py"
    py.parent.mkdir(parents=True, exist_ok=True)
    py.write_text(_LOADER_PY, encoding="utf-8")
    return py


def main() -> int:
    """CLI entry point.

    Returns
    -------
    int
        Always 0 on success (make operations either act or no-op idempotently).
    """
    p = make_parser(
        prog="sprezzature-ui-i18n-make",
        description="Scaffold + compile locales/i18n.yaml (GUI strings + prompts) "
        "and emit the vanilla-JS and Python loaders — the make half "
        "of the i18n rule.",
        epilog=__doc__,
    )
    p.add_argument("--dir", default=".", help="Project root (catalog is <dir>/locales/i18n.yaml).")
    p.add_argument("--init", action="store_true", help="Only scaffold the catalog if missing.")
    p.add_argument("--compile", action="store_true", help="Only compile YAML -> JSON.")
    p.add_argument("--emit-loader", action="store_true", help="Only emit locales/i18n.js.")
    p.add_argument(
        "--emit-python",
        action="store_true",
        help="Only emit locales/i18n_prompts.py (the stdlib prompt loader).",
    )
    args = p.parse_args()

    catalog = Path(args.dir) / "locales" / "i18n.yaml"
    # No explicit step flag => do the whole scaffold (init + compile + loaders).
    do_all = not (
        args.init or args.compile or getattr(args, "emit_loader") or getattr(args, "emit_python")
    )

    if args.init or do_all:
        created = scaffold(catalog)
        print(f"{'created' if created else 'kept existing'} {catalog}")
    if args.compile or do_all:
        out = compile_json(catalog)
        print(f"compiled {out}")
    if getattr(args, "emit_loader") or do_all:
        js = emit_loader(catalog)
        print(f"emitted {js}")
    if getattr(args, "emit_python") or do_all:
        py = emit_python(catalog)
        print(f"emitted {py}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
