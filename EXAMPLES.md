# Examples

Two tools, because two is what can be run deterministically. Writing the
interface is the model's work, guided by `SKILL.md` and the files in
`references/`; nothing below pretends to do that part.

## Find the strings that should be in a catalogue

```bash
sprezzature-ui-i18n-audit src/
sprezzature-ui-i18n-audit src/ templates/ static/js/
sprezzature-ui-i18n-audit src/ --json
```

Exit 1 on any finding, which is what makes it usable as a gate. Standard
library only, so it runs in a minimal container in milliseconds.

Two things are flagged, and they are the same mistake in two languages: a
translation dictionary embedded in JavaScript or HTML, and an LLM prompt
inlined in Python. Both belong in `locales/i18n.yaml`.

## Move them there

```bash
sprezzature-ui-i18n-audit src/ --fix
sprezzature-ui-i18n-audit src/ --fix --catalog locales/strings.yaml
```

`--fix` writes the strings into the catalogue and prints the call to
paste. It does not rewrite the call site. That restraint is deliberate:
replacing a string literal with a lookup changes what the surrounding code
means, and a tool that guesses at it wrongly is harder to clean up than
the original.

## Scaffold the catalogue and the glue that reads it

```bash
sprezzature-ui-i18n-make
sprezzature-ui-i18n-make --dir ../my-project
```

Four steps run by default: scaffold `locales/i18n.yaml` if it is missing,
compile it to `locales/i18n.json` because browsers do not parse YAML, emit
`locales/i18n.js` as a framework-free ES module, and emit
`locales/i18n_prompts.py` as the standard-library prompt loader.

## One step at a time

```bash
sprezzature-ui-i18n-make --init
sprezzature-ui-i18n-make --compile
sprezzature-ui-i18n-make --emit-loader
sprezzature-ui-i18n-make --emit-python
```

`--compile` is the one that belongs in a build: the YAML is what a human
edits, the JSON is what ships, and running it is how the two stay in step.

## Either front door

```bash
make-ui i18n-audit src/
make-ui i18n-make --compile
sprezzature-ui i18n-audit src/
```

`make-ui <tool>` reads its flags with argparse, `sprezzature-ui <tool>`
with click, and both resolve against one table. A tool cannot appear in
one and be missing from the other.

## As a pre-commit hook

```yaml
repos:
  - repo: https://github.com/warith-harchaoui/sprezzature-ui
    rev: v1.0.0
    hooks:
      - id: sprezzature-ui-i18n-audit
```

This is where the audit earns its keep. A hardcoded sentence costs nothing
the day it is written and a week the day a second language is needed; the
hook catches them one at a time instead of all at once.

## From Python

```python
from sprezzature_ui import audit_path, gather

for file in gather(["src/"]):
    for finding in audit_path(file):
        print(finding["rule"], finding["path"], finding["line"])
```

`gather` is the half that walks a directory and drops what is not
auditable, skipping `node_modules`, `dist`, `vendor` and the rest;
`audit_path` reads one file and dispatches on its extension. They are
separate because a caller with its own file list, a pre-commit hook for
instance, already knows which files changed and should not pay for a walk.

## Over HTTP

```bash
pip install "sprezzature-ui[api]"
uvicorn sprezzature_ui.api:app --port 8000
curl -s localhost:8000/health
```

One route, `POST /v1/i18n-audit`: source in, findings out. The narrowness
is the point. No HTTP route can carry "make this dashboard legible", and
this package does not invent one that pretends to.

## In containers

```bash
docker compose up -d
curl -s localhost:8000/health
```
