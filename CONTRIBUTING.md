# Contributing

## Setup

```bash
git clone https://github.com/warith-harchaoui/sprezzature-ui
cd sprezzature-ui
pip install -e ".[dev]"
```

That is the line CI (continuous integration, the checks a server runs on
every push) runs. The development dependencies live in the `dev`
extra in `pyproject.toml` rather than in a `requirements-dev.txt`, so there
is one list and the workflow installs it by name.

## Tests

```bash
pytest
```

The `tests/eval/` suite is marked `eval` and excluded from the default run:
it calls a local model through Ollama (a `qwen3-vl` tag must be pulled), so
it is slow and it needs one installed. Run it with `pytest -m eval`. It
skips, rather than fails, when no Ollama server answers.

It also imports three packages that `[dev]` does not install, and each test
that needs one skips when it is absent. To run the whole suite rather than
the part of it your machine happens to hold:

```bash
pip install -e ".[dev]" best-engine-ai-helper langdetect deepeval
ollama pull qwen3-vl:8b        # or any qwen3-vl tag; the size is the machine's choice
pytest -m eval
```

| Package | Used by |
|---|---|
| `best-engine-ai-helper` | every eval test: the model is called through `best_engine_ai_helper.llm.chat` (`tests/eval/conftest.py`) |
| `langdetect` | the check that a translated prompt answers in its own language |
| `deepeval` | the G-Eval judge that compares a translated prompt with its source |

They stay out of `[dev]` on purpose. `langdetect` is small, but `deepeval`
is not: it brings `openai`, `grpcio`, OpenTelemetry, two telemetry clients,
and three pytest plugins (`pytest-xdist`, `pytest-rerunfailures`,
`pytest-asyncio`) that would then load into every default `pytest` run, for
a suite that run excludes.

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
2. Add a test in `tests/test_i18n.py`: at least one source that should
   trigger the finding, one that should not. If `--fix` should move what the
   rule finds, the extraction tests live in `tests/test_i18n_extraction.py`. The second one matters
   more; an over-eager i18n rule is worse than a missing one, because it
   trains people to pass `--fix` without reading.
3. Document it in `README.md` and `LISEZMOI.md`, in both languages, list it
   in `TRIGGERS.md` and in `sprezzature_ui/skill/SKILL.md`, and add a worked
   invocation to `EXAMPLES.md`.

## Changing what the reference files teach

The prose in `references/` is the larger half of this package. The copy an
agent reads, and the one the wheel carries, is
`sprezzature_ui/skill/references/`, beside `sprezzature_ui/skill/SKILL.md`
and `sprezzature_ui/skill/assets/`; the `references/` and `assets/` folders
at the root of the repository hold the same files. Change both: no test
holds them in step, and `tests/test_the_shipped_markup.py` lints the HTML
under the root `assets/`. After a change, `sprezzature-ui-skill --install`
refreshes the copy your own agent reads. A rule
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

The BSD (Berkeley Software Distribution) 3-Clause licence, `BSD-3-Clause`.
See [LICENSE](LICENSE).
