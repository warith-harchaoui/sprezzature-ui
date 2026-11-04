# CODING.md

Coding standards for sprezzature-ui.

Key rules: NumPy-style docstrings on every function, full typing
(`from __future__ import annotations` at the top of every file), roughly
25-30% comment density explaining *why* a non-obvious line does what it
does, ruff-clean (`ruff check .`), no bare `except Exception` without a
comment saying why the broad catch is intentional.

## Standard library only in the audit

`scripts/audit_i18n.py` imports nothing outside the standard library. It
parses JavaScript, HTML and Python with the tools already in the
interpreter, which is what makes it cheap enough to put in a pre-commit
hook. PyYAML is imported only by `--fix` and by `i18n_make`, because the
catalogue is YAML and the audit that finds what belongs in it is not. PyYAML
is a base dependency, like every other runtime dependency of this package:
there are no feature extras.

An import added to the audit is a review question, not a detail.

## The emitted code has standards too

`i18n_make` writes JavaScript and Python into somebody else's project.
That output is held to the same rules as the interface this package
teaches: no framework runtime, plain ES modules, no build step required to
read it. A loader that needs bundling would contradict the stack the skill
prescribes, and a reference that teaches a rule the runtime cannot hold is
the defect the suite watches for.

## The two names share one table

`make-ui` and `sprezzature-ui` are two spellings of one click front door,
`sprezzature_ui.cli:main`. The argparse front door was dropped on
2026-10-25. Both names resolve against one table of tools, `TOOLS` in
`sprezzature_ui/_tools.py`, so a tool cannot reach one name and miss the
other. A new tool is an entry in that table plus its own console script in
`pyproject.toml`; `tests/test_the_surfaces_agree.py` checks that every
declared command imports and announces the name that installs it.

## Small on purpose

The package will stay small. Its job is the prose judgement plus the part
of that judgement a machine can run, which today is the i18n audit. Adding
routes to raise the count would mistake breadth for value, and `README.md`
says so to a reader; this file says it to whoever is about to add one.
