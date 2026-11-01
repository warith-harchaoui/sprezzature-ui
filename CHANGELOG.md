# Changelog

All notable changes to `sprezzature-ui` are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
