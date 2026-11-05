# Changelog

All notable changes to `sprezzature-ui` are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- **The audit is stdlib-only, as the documentation said.** `audit_i18n`
  imported PyYAML at the top of the module, so `from sprezzature_ui import
  audit_path` loaded it for a caller who only audits, while the README,
  `CODING.md` and the package docstring said otherwise. PyYAML is now
  imported inside `fix()`, the only code that writes YAML, and
  `tests/test_the_surfaces_agree.py` asks a fresh interpreter whether
  `yaml` or `click` was loaded.
- **The pre-commit hook passes `.cjs` and `.htm` files**, which the audit
  reads and the hook's `files:` pattern left out.
- **`emit_python` is exported** beside `emit_loader`: the library reached
  three of the make tool's four steps.

### Docs

- **The figure, its alt text, `LANDSCAPE.md` and `PAYSAGE.md`** said the
  audit finds sentences in HTML attributes and in prompt templates. It
  finds translation tables in JavaScript and HTML and prompt constants in
  Python; the make tool emits two loaders, not one. Spec edited, figure
  redrawn. The `sprezzature-ui tools` line for `i18n-make` said one loader
  too.
- **`README.md` and `LISEZMOI.md`** list the hook's file types from the
  hook itself, and `emit_python` among the library exports, as does
  `TRIGGERS.md`.
- **`assets/snippets/INDEX.md`** names the installed commands
  (`sprezzature-ux-laws-audit`, `sprezzature-accessibility-lint`) instead
  of script paths in a clone, and places `tests/test_snippet_catalog.py`
  in the monorepo.
- **The emitted `i18n_prompts.py`** said it read JSON to avoid an `[i18n]`
  extra that no longer exists.

## [1.1.0] — 2026-11-04: click everywhere, and the documentation says what the code does

### Changed

- **Every command is click.** `sprezzature-ui-i18n-audit`,
  `sprezzature-ui-i18n-make` and `sprezzature-ui-mcp` were the last argparse
  parsers; they now go through `sprezzature_command` and `run_command` from
  `scripts/_click.py`, the helper the rest of the suite uses. Options, defaults,
  positional `PATHS`, exit codes (2 on a usage error) and `main(argv=None)` are
  unchanged. `-V` printed `1.5.0`, a version copied from another package; it
  prints the package version, `1.0.0`. `scripts/_argparse.py` is deleted.
  `tests/test_every_command_can_start.py` now demands a click `Usage:` line
  from every console script and refuses an argparse import in the package.
- **The container serves `/mcp`.** The image ran `uvicorn
  sprezzature_ui.api:app`, which never imports `sprezzature_ui.mcp` and so
  never mounts the MCP endpoint. Its command, and the compose service's, is
  now `sprezzature-ui-mcp --host 0.0.0.0 --port 8000`: one process answers
  `/health`, `/v1/i18n-audit` and `/mcp` on port 8000.
- **`CONTRIBUTING.md` says how to run `pytest -m eval`.** The eval suite
  imports `best-engine-ai-helper`, `langdetect` and `deepeval`; the exact
  install line is written there. They stay out of `[dev]`: `deepeval` brings
  `openai`, `grpcio` and three pytest plugins into every default run.

### Docs

The Markdown now says what the code does on 2026-11-04. Each claim below was
checked against the code, by `--help` or by a run.

- **`README.md` and `LISEZMOI.md`.** The install section listed three
  `pip install` lines that had become identical once the extras were folded
  in; it is one line now. `sprezzature-ui-i18n-make locales/i18n.yaml` took
  a positional argument the command does not accept: the catalogue is found
  through `--dir`. Added what was missing: the five surfaces in one table,
  the flags of both commands (`--json`, `--fix`, `--catalog`, `--dir`,
  `--init`, `--compile`, `--emit-loader`, `--emit-python`), the
  `sprezzature-ui tools` sub-command, the exit code of `--fix` (still 1),
  the request and response fields of `POST /v1/i18n-audit`, the MCP server
  with its `/mcp` endpoint and its two tools, Docker and compose, the two
  rules and the file types each reads, and the three-Roboto rule. The two
  files now have the same sections in the same order, and the French one
  has non-breaking spaces before `:` and `;`.
- **`TRIGGERS.md`.** The generalisation now routes on the domain's closed
  vocabulary instead of sample phrasings. Added a table of every tool and
  the request it answers, the `health` MCP tool, `sprezzature-ui tools`,
  `sprezzature-ui-mcp`, the HTTP and library columns, and the `.cjs`,
  `.jsx`, `.tsx` and `.htm` files the audit also reads.
- **`EXAMPLES.md`.** "One route" became one working route beside
  `GET /health`. Added the MCP server, a `POST` example and the compose
  command that runs the audit. Dropped a timing claim nobody measured.
- **`CODING.md`.** PyYAML was described as the dependency of an `i18n`
  extra that no longer exists. A new tool was said to be picked up by
  adding an entry point; it has to go in `TOOLS` in
  `sprezzature_ui/_tools.py` as well.
- **`CONTRIBUTING.md`.** Detector tests live in `tests/test_i18n.py`, not in
  the extraction tests. Said how to run the `eval` suite and what it imports
  that `[dev]` does not install.
- **`references/`.** `stack-vanilla-js.md` taught a translation table kept
  in a JavaScript object, which is what `I18N001` exists to flag; it now
  shows the emitted `locales/i18n.js` loader. `checklist.md` cited
  `tests/test_dogfood_audits.py`, which does not exist. The guards are
  `tests/test_the_shipped_markup.py` (accessibility lint, every shipped HTML
  file) and the monorepo's `tests/test_snippet_catalog.py` (both auditors,
  snippets only). `stack-tailwind.md` named `scripts/validate.py`,
  which is in no repository; the suite's validator is the monorepo's
  `scripts/validate_content.py`. `material-design.md` asked for a typeface
  "not Roboto"; it means not Roboto Flex. `ui-guidelines/foundations/images.md`
  installed alt-text drafting from a requirements file and claimed Python
  3.9; it is `pip install sprezzature-accessibility`, on Python 3.10 to 3.13.
  Two links to `alt-text-ai.md` and `meta-tags.md` now name the brick that
  holds them.
- **Docstrings and help strings.** The MCP module named three colour tools
  and three accessibility tools this server does not have, and announced
  itself to MCP hosts as "Sprezzature Accessibility". The `audit_i18n`
  docstring listed `TEMPLATE` and `SYSTEM` among the prompt names the rule
  matches; it matches `PROMPT` and `INSTRUCTION` only. Four messages and the
  `sprezzature-ui --help` epilog still spoke of an extra to install. The
  `pyproject.toml` comment said `make-ui` read its flags with argparse.
- **`sprezzature-ui tools`** lost a branch that named an extra to install.
  No entry of the tool table carries one, so the branch could not run; the
  output is unchanged. An eval-suite skip reason named a `[lang]` extra that
  does not exist.

### Changed — one `pip install`

**Everything this package does now installs with it.** 4 extras became
**one**, and it is not a feature: `[dev]` is the test toolchain.

  The i18n catalogue reader (PyYAML) and both surfaces. The base was **one**
  dependency.

Measured across the suite before touching anything: **59 extras over eleven
repositories**, and **six bricks whose base was a single dependency** — so
`pip install <brick>` installed almost nothing and did almost nothing, and
choosing the right extra was a thing a reader had to know *before* the package
could do its job. Here the base goes from **1** to **7**
dependencies.

All eleven unions were dry-run resolved in a clean venv before any manifest was
edited, so this is a measured feasibility and not an optimistic one.

### Fixed — the places that encoded the extras

Install lines, error messages, docstrings, the `Dockerfile`, the CI workflow and
the README/LISEZMOI install sections all named extras that no longer exist. pip
treats an unknown extra as a **warning and exits 0**, so none of these would
have failed loudly: they would have quietly installed nothing.

The hub's `test_no_document_promises_an_extra_that_does_not_exist` found the
cross-repository ones — a document in one brick naming another brick's extra —
which no per-repository pass would have caught.

### Added

- **`CODING.md`, `CONTRIBUTING.md`, `EXAMPLES.md` and `TRIGGERS.md`**, the
  four root documents the other bricks carry and this one went out without.
  `EXAMPLES.md` is a worked invocation per tool; `TRIGGERS.md` is the
  routing file an agent reads, and it leads with the distinction that gets
  this package mis-routed: writing an interface is the model's work, read
  from `references/`, and only the i18n audit is a command. A guard in the
  monorepo now asks the question of all nine bricks.

### Fixed

- **The Python example in `README.md` did not run as written.** It showed
  `audit_path` alone, which reads one file and takes a `Path`; pointing it
  at a directory raises `AttributeError` on `str.suffix`. `EXAMPLES.md`
  pairs it with `gather`, which is the half that walks a tree, and the
  pair was run before it was written down.
- **`LISEZMOI.md` was short two sections the English file has**, "from
  Python" and "over HTTP", and its pre-commit snippet used `repo: local`
  where the English one names the published repository and a `rev`. A
  reader of the French file could not copy a working hook. The charter asks
  for strict parity between the two; this is it.

## [1.0.0] — 2026-10-18

First release as a standalone package, and the last of the suite's ten
bricks to be extracted.

### Added

- **The i18n pair, as commands.** `sprezzature-ui-i18n-audit` finds the
  translations embedded in JavaScript and HTML and the LLM prompts inlined
  in Python; `sprezzature-ui-i18n-make` scaffolds the catalogue they belong
  in, compiles it and emits the loader. Both reachable through either front
  door — `make-ui` with argparse, `sprezzature-ui` with click.
- **A library, an HTTP route and an MCP tool** over the audit, plus a
  pre-commit hook. The audit is stdlib-only, which is what makes the hook
  worth keeping.

### Changed

- **Narrow on purpose, and declared as such.** Writing an interface is the
  model's work guided by `SKILL.md`; no route can carry it. The exemption is
  named in the monorepo's `SURFACES.md` with this as the reason, rather than
  left as a gap somebody later mistakes for an oversight.
- **`validate.py` did not come.** It validates whichever skill folder it
  sits in — a gate on the monorepo's own contents, not a tool for anyone's
  project. It stays there, beside `validate_skill.py`, which does the YAML
  half of the same job.

### Fixed

- **The HTTP route leaked the server's scratch directory.** Serving a
  text-in API over a path-based auditor means writing a temporary file, and
  the findings came back naming it. A caller who posted a string now gets
  their own filename back.

[1.0.0]: https://github.com/warith-harchaoui/sprezzature-ui/releases/tag/v1.0.0
