# sprezzature-ui

The deterministic half of a frontend skill: find the strings that should be
in a translation catalogue, and scaffold the catalogue they belong in.

The other half — writing the interface, in semantic HTML with Tailwind
utilities and plain ES modules, no framework runtime, with dark-mode peers,
focus rings and reduced-motion guards — is the model's work, guided by the
[`SKILL.md`](https://github.com/warith-harchaoui/sprezzature) that ships with
the suite. No HTTP route can carry "make this dashboard legible", and this
package does not pretend otherwise.

---

## How it works

![Flow diagram. At the top, your source tree feeds two lanes. The left lane audits: it walks the tree, finds sentences hardcoded in JavaScript, in HTML attributes and in Python prompt templates, and returns findings with exit code 1. The right lane makes: it scaffolds a single locales file, compiles it to JSON and emits the loader that reads it. Both meet in one outcome, an interface that can take a second language the day it is asked for.](https://raw.githubusercontent.com/warith-harchaoui/sprezzature-ui/main/assets/how-it-works.svg)

## What's here

| | |
|---|---|
| `sprezzature-ui-i18n-audit` | **audit** — translations embedded in JavaScript and HTML, LLM prompts inlined in Python. Both belong in `locales/i18n.yaml`. Standard library only. |
| `sprezzature-ui-i18n-make` | **make** — scaffold that catalogue, compile it to JSON, emit the loader that reads it. |

One front door over both, in click, under two names: `make-ui <tool>` and
`sprezzature-ui <tool>` resolve to the same callable, so they cannot drift.
The argparse twin was removed on 2026-10-25 — two parsers meant every
sub-command written twice.

## Why it matters sooner than it seems

A hardcoded sentence in a template costs nothing on the day it is written.
It costs a week the day somebody needs a second language and discovers the
strings are scattered through the source — in JavaScript string literals, in
HTML attributes, in prompt templates buried in Python. The audit is cheap
enough to put in a pre-commit hook, which is where it catches them one at a
time instead of all at once.

## Install

```sh
pip install sprezzature-ui              # the audit
pip install "sprezzature-ui[i18n]"      # + the catalogue tools (PyYAML)
pip install "sprezzature-ui[api,mcp]"   # + the HTTP and agent surfaces
```

## Use

```sh
sprezzature-ui-i18n-audit src/            # exit 1 on any finding
sprezzature-ui-i18n-make locales/i18n.yaml
```

### As a pre-commit hook

```yaml
repos:
  - repo: https://github.com/warith-harchaoui/sprezzature-ui
    rev: v1.0.0
    hooks:
      - id: sprezzature-ui-i18n-audit
```

### From Python

```python
from sprezzature_ui import audit_path, gather

for file in gather(["src/"]):
    for finding in audit_path(file):
        print(finding["rule"], finding["path"], finding["line"])
```

`gather` walks the tree and drops what is not auditable; `audit_path`
reads one file. They are separate because a pre-commit hook already knows
which files changed and should not pay for a walk.

### Over HTTP

```sh
pip install "sprezzature-ui[api]"
uvicorn sprezzature_ui.api:app --port 8000
```

One route, `POST /v1/i18n-audit`: source in, findings out. The narrowness is
the point rather than an omission — see the first paragraph.

## The boundary, said plainly

This package is **small**, and it will stay small. Its job is the aesthetic
judgement written in prose — the three-Roboto rule, the design tokens, what an
interface has to respect — plus the part of that judgement which can be
mechanised. The i18n audit is that part. The temptation will be to add routes
for the sake of the count; that would be mistaking breadth for value.

## See also

- **[sprezzature-accessibility](https://github.com/warith-harchaoui/sprezzature-accessibility)** — lint the HTML you emit, and draft the alt text it says is missing.
- **[sprezzature-colors](https://github.com/warith-harchaoui/sprezzature-colors)** — contrast and colour-vision checks on the palette.
- **[sprezzature-ux-laws](https://github.com/warith-harchaoui/sprezzature-ux-laws)** — audit how the interface feels, by the named heuristics.
- **[sprezzature](https://github.com/warith-harchaoui/sprezzature)** — the suite, and the skills that drive it from Claude.

## License

BSD-3-Clause. See `LICENSE`.

## Author

[Warith HARCHAOUI, Ph.D.](https://www.linkedin.com/in/warith-harchaoui/)
