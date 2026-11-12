# Triggers

When to reach for this package, and what to call.

This file is written for an agent: a Claude Code or OpenCode skill, an MCP
(Model Context Protocol, the protocol through which AI agents call tools in
English) host, anything choosing a tool on someone's behalf.
Humans are welcome, but the routing rules below are the point.

---

## The generalisation, stated once

Route on what the person is holding, named in the domain's own closed
vocabulary, not on how they phrase the request. The ways to ask are
unbounded; the things this package deals with are not.

> **A screen to build, with no framework asked for.** The nouns are a
> closed set: page, landing, component, button, card, form, form field,
> modal, dialog, nav, menu, table, dashboard, chart, settings page, theme
> toggle. The output is HTML a browser runs directly, with Tailwind
> utilities and plain ES (ECMAScript, the official name of JavaScript)
> modules: no React, no build step, no framework runtime. This half is the
> model's work, read from `SKILL.md` and `references/`, which ship inside
> the package under `sprezzature_ui/skill/`.
>
> **Source that holds strings meant for people or for a model.** The nouns
> are a closed set too: translation, locale, language code, message id,
> catalogue, plural, i18n (internationalisation), and, on the Python side,
> prompt, system prompt, instruction. When any of these sits in
> JavaScript, HTML or Python rather than in `locales/i18n.yaml`, the audit
> is the answer. The same holds right after such a file was written: a
> label just hardcoded in a JavaScript object, a prompt just put in a
> Python constant.

If the noun is neither a screen nor a string catalogue, this package is
not the answer. The neighbours below say which one is.

---

## Two halves, and only one of them is a command

This is the distinction to get right before routing anything here.

| The half | Who does it | How |
|---|---|---|
| **Writing the interface** | the model | read `SKILL.md` and the files in `references/`, copy from `assets/components/` and `assets/snippets/`, then write the HTML; `sprezzature-ui-skill --install` puts that folder where the agent reads it |
| **Finding hardcoded strings** | this package | `sprezzature-ui-i18n-audit`, or the `audit_i18n` MCP tool |
| **Building the catalogue** | this package | `sprezzature-ui-i18n-make` |

No route over HTTP (HyperText Transfer Protocol, the language a browser
speaks to fetch a page) can carry "make this dashboard legible". Asking for a tool
that does it will find nothing, because nothing here claims to. The prose
in `references/` is the larger half of the package, and reading it is how
the skill is used. Its default typography is the three-Roboto rule: Roboto,
Roboto Serif and Roboto Mono, self-hosted.

---

## Every tool, and the request it answers

| Tool | The request it answers |
|---|---|
| `sprezzature-ui-i18n-audit` | "Which strings in this tree belong in a catalogue?" Reports `I18N001` (a translation table in JavaScript or HTML) and `I18N002` (a prompt constant in Python). Exit 1 on any finding. |
| `sprezzature-ui-i18n-audit --fix` | "Move them into the catalogue." Writes `locales/i18n.yaml` (or `--catalog PATH`) and prints the call to paste. It does not rewrite the call site, and still exits 1. |
| `sprezzature-ui-i18n-make` | "Set up the catalogue and the code that reads it." Scaffolds `locales/i18n.yaml`, compiles `locales/i18n.json`, emits `locales/i18n.js` and `locales/i18n_prompts.py`. One step alone with `--init`, `--compile`, `--emit-loader` or `--emit-python`. |
| `sprezzature-ui tools` | "What does this package offer, and can it run here?" Lists both tools with their status. |
| `sprezzature-ui-mcp` | "Expose the audit to an MCP host." Serves the HTTP app with the MCP endpoint at `/mcp`. |
| `sprezzature-ui-skill` (or `sprezzature-ui skill`) | "Is the skill my agent reads the one this package ships?" Reports in step or which files differ; `--install` copies it into `~/.claude/skills/sprezzature-ui` (`--agent opencode` for `~/.opencode/skills`), `--path` prints where `pip` put it. |
| `health` (MCP tool, `GET /health`) | "Is this server up, and which version?" |
| `audit_i18n` (MCP tool, `POST /v1/i18n-audit`) | The audit over the network: one file's text and its filename in, findings out. |

---

## What to call, on every surface

The five surfaces are the library, the CLI (command-line interface, a program
you run by typing a command in a terminal) in click, the HTTP API
(application programming interface) in FastAPI, with a `Dockerfile` and a
`docker-compose.yml`, the MCP server through fastapi-mcp, and the skill.

| Job | CLI | MCP tool | HTTP route | Library |
|---|---|---|---|---|
| Find hardcoded strings | `sprezzature-ui-i18n-audit` | `audit_i18n` | `POST /v1/i18n-audit` | `gather`, `audit_path`, `audit_js`, `audit_py` |
| Move them to the catalogue | `sprezzature-ui-i18n-audit --fix` | none, it writes files | none | none |
| Scaffold and compile the catalogue, emit the loaders | `sprezzature-ui-i18n-make` | none, it writes files | none | `scaffold`, `compile_json`, `emit_loader`, `emit_python` |
| Check the server | none | `health` | `GET /health` | none |
| List the tools | `sprezzature-ui tools` | none | none | none |
| Check or install the skill | `sprezzature-ui-skill [--install]` | none | none | `skill_path()` |

The MCP tool names are the routes' `operation_id`, so the two cannot
disagree. The audit is the only tool that crosses a network boundary
cleanly: source in, findings out. The make tool writes files into a
project, so it stays a command. Call it with Bash.

Either front door works: `make-ui <tool>` and `sprezzature-ui <tool>` are
one click command under two names, with `i18n-audit` and `i18n-make` as
sub-commands. The argparse front door was removed on 2026-10-25, and since
2026-11-04 every command, `sprezzature-ui-mcp` included, parses with click.

Install is one line, `pip install sprezzature-ui`, which brings every
surface, the skill included. There are no feature extras.

---

## Which neighbour, for the question after this one

Four different questions get asked about the same page. They do not
substitute for one another, and this package answers only the first.

| The question | Package | MCP tool |
|---|---|---|
| **How should it be built?** stack, tokens, typography, layout | sprezzature-ui | the references, plus `audit_i18n` |
| **Is it accessible?** missing alt, unlabelled inputs, heading order | sprezzature-accessibility | `lint_html` |
| **Is it legible?** contrast, colour-blind safety | sprezzature-colors | `check_contrast`, `simulate_color_blindness` |
| **Is it usable?** too many choices, targets too small, no feedback | sprezzature-ux-laws | `audit_interface` |

A page can pass any one and fail the others. When someone asks a broad
"review my UI (user interface)", run the other three and say which found what; this one has
nothing mechanical to add to that review beyond the strings.

Two more boundaries. A command-line tool that needs a screen in front of it
goes to sprezzature-cli-gui. Markdown that must become a site goes to
sprezzature-publish.

---

## What this cannot see, and say so when you report

The audit reads source. It finds a translation table sitting in JavaScript
and a prompt sitting in Python, and it says where. It cannot tell whether
the translations are any good, whether a string is user-facing at all, or
whether the interface around them works.

Two findings exist, `I18N001` and `I18N002`, out of a field that is mostly
judgement. `I18N002` fires only on names containing `PROMPT` or
`INSTRUCTION`; a prompt stored under another name is not seen. Report the
findings as evidence, never as a verdict. "Nothing fired" means exactly
that, not "this interface is ready to ship".

---

## File patterns

`*.js`, `*.mjs`, `*.cjs`, `*.jsx`, `*.ts`, `*.tsx`, `*.html`, `*.htm` and
`*.py` route to the audit when translations or prompts are the concern, and,
per the generalisation above, when such a file was just written. A request
to *build* an interface routes to the references, not to a command.
