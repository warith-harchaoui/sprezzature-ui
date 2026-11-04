# sprezzature-ui

[Français](https://github.com/warith-harchaoui/sprezzature-ui/blob/main/LISEZMOI.md)

The deterministic half of a frontend skill: find the strings that should be
in a translation catalogue, and scaffold the catalogue they belong in.

The other half is writing the interface: semantic HTML, Tailwind utilities
and plain ES modules, no framework runtime, with dark-mode peers, focus
rings and reduced-motion guards. That half is the model's work, guided by
the [`SKILL.md`](https://github.com/warith-harchaoui/sprezzature/blob/main/sprezzature-ui/SKILL.md)
that ships with the suite and by the prose in `references/`. No HTTP route
can carry "make this dashboard legible", and this package does not pretend
otherwise.

---

## How it works

![Flow diagram. At the top, your source tree feeds two lanes. The left lane audits: it walks the tree, finds sentences hardcoded in JavaScript, in HTML attributes and in Python prompt templates, and returns findings with exit code 1. The right lane makes: it scaffolds a single locales file, compiles it to JSON and emits the loader that reads it. Both meet in one outcome, an interface that can take a second language the day it is asked for.](https://raw.githubusercontent.com/warith-harchaoui/sprezzature-ui/main/assets/how-it-works.svg)

## What's here

| Command | What it does |
|---|---|
| `sprezzature-ui-i18n-audit` | **audit.** Finds translation tables embedded in JavaScript or HTML (rule `I18N001`) and LLM (large language model) prompts inlined in Python (rule `I18N002`). Both belong in `locales/i18n.yaml`. With `--fix`, moves what it can read into that catalogue. The audit itself imports only the standard library. |
| `sprezzature-ui-i18n-make` | **make.** Scaffolds `locales/i18n.yaml`, compiles it to `locales/i18n.json`, and emits two loaders: `locales/i18n.js` for the browser and `locales/i18n_prompts.py` for Python. |

One front door over both, written in click, under two names:
`make-ui <tool>` and `sprezzature-ui <tool>` are the same callable, so they
cannot drift. `sprezzature-ui tools` lists the tools and says whether each
can run on this machine. The argparse front door was removed on 2026-10-25,
and since 2026-11-04 no command parses with argparse: the per-tool commands
and `sprezzature-ui-mcp` are click too, and `-V` prints the package version.
Each tool keeps its own command, which is what a script or a pre-commit hook
should call.

## Five surfaces

| Surface | Entry point | What it exposes |
|---|---|---|
| Library | `from sprezzature_ui import …` | `audit_js`, `audit_py`, `audit_path`, `gather`, `scaffold`, `compile_json`, `emit_loader` |
| CLI (command-line interface) | `sprezzature-ui`, `make-ui`, `sprezzature-ui-i18n-audit`, `sprezzature-ui-i18n-make` | both tools |
| HTTP | `uvicorn sprezzature_ui.api:app`, or the `Dockerfile` and `docker-compose.yml` (which also serve `/mcp`) | `GET /health`, `POST /v1/i18n-audit` |
| MCP (Model Context Protocol) | `sprezzature-ui-mcp` | tools `health` and `audit_i18n`, at `/mcp` |
| Skill | [`SKILL.md`](https://github.com/warith-harchaoui/sprezzature/blob/main/sprezzature-ui/SKILL.md) in the suite | the design prose, plus the two commands |

Only the audit crosses a network boundary. The make tool writes files into a
project, so it has no route and no MCP tool.

## Why it matters sooner than it seems

A hardcoded sentence in a template costs nothing on the day it is written.
It costs a week the day somebody needs a second language and discovers the
strings are scattered through the source: in JavaScript string literals, in
inline scripts, in prompt templates buried in Python. The audit is cheap
enough to put in a pre-commit hook, which is where it catches them one at a
time instead of all at once.

## Install

```sh
pip install sprezzature-ui
```

One line installs every surface: the audit, the catalogue tools (PyYAML),
the click front door, the HTTP app and the MCP server. There are no feature
extras. `[dev]` holds only the test toolchain.

## Use

```sh
sprezzature-ui-i18n-audit src/                 # exit 1 on any finding
sprezzature-ui-i18n-audit src/ --json          # findings as a JSON array
sprezzature-ui-i18n-audit src/ --fix           # move strings into locales/i18n.yaml
sprezzature-ui-i18n-make                       # scaffold, compile, emit both loaders
sprezzature-ui-i18n-make --dir ../my-project --compile
```

`sprezzature-ui-i18n-audit` takes files and directories. Directories are
walked recursively, skipping `node_modules`, `.git`, `__pycache__`, `dist`,
`build`, `vendor` and `.venv`. `--catalog PATH` changes the catalogue
`--fix` writes to.

`--fix` writes the catalogue and prints, for each string it moved, the call
to paste in its place. It does not rewrite the call site, and it still exits
1, because the strings are still in the code until the author replaces them.

`sprezzature-ui-i18n-make` runs four steps by default. `--init`, `--compile`,
`--emit-loader` and `--emit-python` each run one step alone. `--dir` points
at the project root; the catalogue is always `<dir>/locales/i18n.yaml`. The
compile step refuses a prompt that declares no `validated:` locale, or one
with no text in it.

### As a pre-commit hook

```yaml
repos:
  - repo: https://github.com/warith-harchaoui/sprezzature-ui
    rev: v1.0.0
    hooks:
      - id: sprezzature-ui-i18n-audit
```

The hook runs on `.js`, `.mjs`, `.ts`, `.jsx`, `.tsx`, `.html` and `.py`
files.

### From Python

```python
from sprezzature_ui import audit_path, gather

for file in gather(["src/"]):
    for finding in audit_path(file):
        print(finding["rule"], finding["path"], finding["line"])
```

`gather` walks the tree and drops what is not auditable; `audit_path`
reads one `pathlib.Path`. They are separate because a pre-commit hook already
knows which files changed and should not pay for a walk. Each finding is a
dict with `rule`, `severity`, `path`, `line`, `message` and `snippet`.

### Over HTTP

```sh
uvicorn sprezzature_ui.api:app --port 8000
curl -s localhost:8000/health
curl -s localhost:8000/v1/i18n-audit -H 'Content-Type: application/json' \
  -d '{"source": "const i18n = { en: \"Save\", fr: \"Enregistrer\" };", "filename": "app.js"}'
```

`POST /v1/i18n-audit` takes `source` (the file's text) and `filename`
(default `app.js`, whose extension decides which rule runs). It returns
`findings_total` and `findings`, with your filename in each `path`.
`GET /health` returns the status and the version. `/` redirects to `/docs`.

### Over MCP

```sh
sprezzature-ui-mcp                       # 127.0.0.1:8000
sprezzature-ui-mcp --host 0.0.0.0 --port 9000
```

It serves the same FastAPI app with the MCP endpoint mounted at `/mcp`. The
tool names are the routes' `operation_id`: `health` and `audit_i18n`.
`SPREZZATURE_UI_HOST` and `SPREZZATURE_UI_PORT` set the defaults.

### In containers

```sh
docker compose up -d
curl -s localhost:8000/health
docker compose run --rm api make-ui i18n-audit /work/src
```

The image serves the HTTP routes and the MCP endpoint on port 8000, from
one process: its default command is `sprezzature-ui-mcp --host 0.0.0.0`, so
`/v1/...` and `/mcp` both answer. Compose mounts `./work` at `/work`, so the
source to audit and the catalogue written beside it stay on the host.

## What the audit sees

| Rule | Files | What fires |
|---|---|---|
| `I18N001` | `.js`, `.mjs`, `.cjs`, `.jsx`, `.ts`, `.tsx`, `.html`, `.htm` | a line declaring a table under a telltale name (`const i18n = {`, `translations`, `messages`, `locales`, `strings`, `dictionary`, `lang`, …), or an object literal with two or more locale keys (`{ en: …, fr: … }`) |
| `I18N002` | `.py` | a module-level or class-level constant whose name contains `PROMPT` or `INSTRUCTION`, assigned a string literal or an f-string |

It reads JavaScript and HTML line by line, and Python through its AST
(abstract syntax tree). It cannot tell whether a translation is good, or
whether a string is user-facing at all. "0 findings" means that neither
shape was found, not that the interface is ready to ship.

## The design half

`references/` holds the prose the skill reads: the Tailwind and vanilla-JS
stack, the checklist, anti-patterns, dashboards, charts in SVG (Scalable
Vector Graphics), colour psychology, a Material Design mapping, and
platform guidelines under `references/ui-guidelines/`. `assets/` holds a
starter page, seven HTML components, two SVG charts, eight snippets indexed
by a Law of UX in `assets/snippets/INDEX.md`, and the three Roboto families
under `assets/fonts/`.

The default typography is the three-Roboto rule: Roboto for the interface
and body, Roboto Serif for long-form text, Roboto Mono for code. All three
are self-hosted. These files live in this repository and in the skill
folder; the Python wheel does not carry them.

## The boundary, said plainly

This package is **small**, and it will stay small. Its job is the aesthetic
judgement written in prose (the three-Roboto rule, the design tokens, what an
interface has to respect) plus the part of that judgement which can be
mechanised. The i18n audit is that part. Adding routes to raise the count
would be mistaking breadth for value.

## See also

- **[sprezzature-accessibility](https://github.com/warith-harchaoui/sprezzature-accessibility)**: lint the HTML you emit, and draft the alt text it says is missing.
- **[sprezzature-colors](https://github.com/warith-harchaoui/sprezzature-colors)**: contrast and colour-vision checks on the palette.
- **[sprezzature-ux-laws](https://github.com/warith-harchaoui/sprezzature-ux-laws)**: audit how the interface feels, by the named heuristics.
- **[sprezzature-cli-gui](https://github.com/warith-harchaoui/sprezzature-cli-gui)**: when there is a command-line tool behind the screen.
- **[sprezzature](https://github.com/warith-harchaoui/sprezzature)**: the suite, and the skills that drive it from Claude.

## License

BSD-3-Clause. See `LICENSE`.

## Author

[Warith HARCHAOUI, Ph.D.](https://www.linkedin.com/in/warith-harchaoui/)
