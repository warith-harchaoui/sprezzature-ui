# Triggers

When to reach for this package, and what to call.

This file is written for an agent: a Claude Code or OpenCode skill, an MCP
host, anything choosing a tool on someone's behalf. Humans are welcome, but
the routing rules below are the point.

---

## The generalisation, stated once

> **Somebody wants an interface built, and has not asked for a framework.**
> They say "build me a settings page", "make a dashboard for this", "I need
> a form with validation", "scaffold a landing", « fais-moi une page de
> connexion ». What is bounded is not how they phrase it: it is that the
> output is HTML a browser runs directly, with Tailwind utilities and plain
> ES modules, and no React, no build step, no framework runtime.

The second trigger is the one that gets missed: **a string was just
hardcoded.** A label in a JavaScript object, a prompt in a Python constant.
The audit catches those, and it is cheap enough to run every time.

---

## Two halves, and only one of them is a command

This is the distinction to get right before routing anything here.

| The half | Who does it | How |
|---|---|---|
| **Writing the interface** | the model | read `SKILL.md` and the files in `references/`, then write the HTML |
| **Finding hardcoded strings** | this package | `sprezzature-ui-i18n-audit`, or the `audit_i18n` MCP tool |

No HTTP route can carry "make this dashboard legible". Asking for a tool
that does it will find nothing, because nothing here claims to. The prose
in `references/` is the larger half of the package, and reading it is how
the skill is used.

---

## Which neighbour, for the question after this one

Four different questions get asked about the same page. They do not
substitute for one another, and this package answers only the first.

| The question | Package | Tool |
|---|---|---|
| **How should it be built?** stack, tokens, typography, layout | sprezzature-ui | the references, plus `audit_i18n` |
| **Is it accessible?** missing alt, unlabelled inputs, heading order | sprezzature-accessibility | `lint_html` |
| **Is it legible?** contrast, colour-blind safety | sprezzature-colors | `check_contrast`, `simulate_color_blindness` |
| **Is it usable?** too many choices, targets too small, no feedback | sprezzature-ux-laws | `audit_interface` |

A page can pass any one and fail the others. When someone asks a broad
"review my UI", run the other three and say which found what; this one has
nothing mechanical to add to that review beyond the strings.

---

## What to call, on every surface

| Job | CLI | MCP tool |
|---|---|---|
| Find hardcoded strings | `sprezzature-ui-i18n-audit` | `audit_i18n` |
| Move them to the catalogue | `sprezzature-ui-i18n-audit --fix` | none, it writes files |
| Scaffold and compile the catalogue | `sprezzature-ui-i18n-make` | none, it writes files |

The audit is the only tool that crosses a network boundary cleanly: source
in, findings out. The other two write files into a project, so they stay
commands. Call them with Bash.

Either front door works: `make-ui <tool>` reads its flags with argparse,
`sprezzature-ui <tool>` with click, and both resolve against one table.

---

## What this cannot see, and say so when you report

The audit reads source. It finds a translation dictionary sitting in
JavaScript and a prompt sitting in Python, and it says where. It cannot
tell whether the translations are any good, whether a string is
user-facing at all, or whether the interface around them works.

Two findings exist, `I18N001` and `I18N002`, out of a field that is mostly
judgement. Report them as evidence, never as a verdict. "Nothing fired"
means exactly that, not "this interface is ready to ship".

---

## File patterns

`*.js`, `*.mjs`, `*.ts`, `*.html` and `*.py` route to the audit when
translations or prompts are the concern, and, per the generalisation
above, when such a file was just written. A request to *build* an
interface routes to the references, not to a command.
