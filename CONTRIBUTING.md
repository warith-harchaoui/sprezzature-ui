# Contributing

## Setup

```bash
git clone https://github.com/warith-harchaoui/sprezzature-ui
cd sprezzature-ui
pip install -e ".[dev,i18n,api,mcp]"
```

That is the line CI runs. The development dependencies live in the `dev`
extra in `pyproject.toml` rather than in a `requirements-dev.txt`, so there
is one list and the workflow installs it by name.

## Tests

```bash
pytest
```

The `tests/eval/` suite is excluded from the default run: it calls a local
model, so it is slow and it needs one installed. Ask for it by name when
you want it.

## Lint

`ruff` is the Python linter and formatter this project uses: it reads the
source without running it and flags style issues (unused imports, wrong
quote style, and the like) in one fast pass.

```bash
ruff check .
```

## Adding a rule to the audit

1. Give it an id in the `I18N0xx` series and add the detector in
   `scripts/audit_i18n.py`, standard library only. See `CODING.md`.
2. Add a test in `tests/test_i18n_extraction.py`: at least one source that
   should trigger the finding, one that should not. The second one matters
   more; an over-eager i18n rule is worse than a missing one, because it
   trains people to pass `--fix` without reading.
3. Document it in `README.md` and `LISEZMOI.md`, in both languages, and add
   a worked invocation to `EXAMPLES.md`.

## Changing what the reference files teach

The prose in `references/` is the larger half of this package. A rule
written there has to be one the emitted code can actually hold: the suite
has a test for exactly that, because a reference that prescribes what the
runtime cannot do is a reference that will be followed into a bug. If you
change a rule, change the emitter with it.

## Code standards

See `CODING.md`. NumPy docstrings, full typing, ~25-30% comment density,
and standard library only in the audit.

## Prose standards

English prose (README, docstrings, comments) follows WRITING.md:
https://gist.github.com/warith-harchaoui/f45304d066abc81dd7d4f059a1f4e45f

French prose (LISEZMOI) follows ECRITURE.md:
https://gist.github.com/warith-harchaoui/7cc42b038e86c5195ec09f0531111ba4

No punctuation dashes, no machine tells ("Moreover", "In conclusion",
reflexive "not only X but also Y"). Acronyms glossed on first use.

## Releases

Releases live in `CHANGELOG.md`, tagged `vX.Y.Z` in git, and published as
GitHub releases.

## Authorship

Sole author: [Warith HARCHAOUI](https://www.linkedin.com/in/warith-harchaoui/).
External contributions are welcome. Open an issue or pull request on GitHub.

## License

[BSD-3-Clause](LICENSE).
