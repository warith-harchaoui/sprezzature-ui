# Changelog

All notable changes to `sprezzature-ui` are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
