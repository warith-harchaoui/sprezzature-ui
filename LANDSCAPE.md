# Landscape

`sprezzature-ui` is the interface brick of the [sprezzature](https://sprezzature.ai/) suite, ten Python packages for building publication-quality web content. It has two storeys, and an honest comparison has to name both. The Python half is deterministic: it walks a source tree, finds the sentences hardcoded in JavaScript, in HTML attributes and in Python prompt templates, and returns a verdict with an exit code; then it scaffolds a single locales file, compiles it to JSON and emits the loader that reads it. The other half, writing the interface in semantic HTML with Tailwind utilities and plain ES modules, no framework runtime, with dark-mode peers, focus rings and a reduced-motion guard, is the model's work, guided by `SKILL.md` and the 64 reference files beside it. No HTTP route can carry "make this dashboard legible", and the package says so in its own README.

So the table below holds two families at once: internationalisation (i18n) toolchains, and ways of producing an interface. That is not a trick of presentation. It is where this package actually sits, and a comparison against only one of the two would flatter it.

## How it fits in the ecosystem

```
sprezzature suite
├── sprezzature-ui             ← this package (the i18n pair, and the design prose)
├── sprezzature-accessibility  (static HTML lint, and the alt text it says is missing)
├── sprezzature-colors         (whether a colour passes, and what to use instead)
├── sprezzature-ux-laws        (whether the page feels right, by the named heuristics)
├── sprezzature-cli-gui        (the same stack, when a command line is behind the screen)
├── sprezzature-figures        (the charts a dashboard tile needs)
├── sprezzature-maps           (the same numbers attached to real places)
├── sprezzature-publish        (Markdown to a findable site, narration included)
├── sprezzature-audio          (speech to text, text to speech)
└── sprezzature-video          (what a film about a project claims, checked)
```

What comes before: a screen somebody asked for, and a source tree that already has strings in it. What comes after: three sibling auditors that read the HTML this one produced. `sprezzature-accessibility` asks whether it is usable, `sprezzature-colors` whether a colour passes, `sprezzature-ux-laws` how it feels. The sister brick doing the neighbouring job is `sprezzature-cli-gui`: same stack rules, same tokens, but it starts from an existing argument parser rather than from a blank screen.

Inside the package the two storeys meet in one file. `locales/i18n.yaml` holds interface labels under `gui:` and model prompts under `prompts:`, because a screen and a prompt that disagree about a language is a bug nobody reports.

## When to choose it

- You are about to add a second language to a project that never planned for one, and the first question is how much is buried in the code. `sprezzature-ui-i18n-audit src/` answers it in one pass over JavaScript, HTML and Python, with a path and a line per finding, and `--fix` moves what it can read into the catalogue and prints the call to paste for each string it moved.
- Your Python assembles prompts for a model and your JavaScript renders labels, and both are language. One catalogue serves both, and the prompt half carries a rule the GUI half does not need: every `prompts:` entry declares the one locale it was engineered and tested in, so a missing translation resolves to that text rather than to the first declared locale or, worse, to the message id.
- You want a pre-commit hook rather than a migration. The audit is standard library only, which is what makes it cheap enough to run on every commit. A hardcoded sentence costs nothing the day it is written and a week the day somebody needs a second language.
- You are writing an interface and have not chosen a framework, and you want output a browser runs directly: semantic HTML, Tailwind utilities, plain ES modules, a `dark:` peer on every styled element, a visible focus ring, and no translate or scale under `prefers-reduced-motion`. That half is prose read by a model, not a command.

## When to pick something else

- **You want every hardcoded string found, not a subset.** [`eslint-plugin-i18next`](https://github.com/edvardchen/eslint-plugin-i18next)'s `no-literal-string` flags every literal that reaches a user, and [`i18next-cli lint`](https://github.com/i18next/i18next-cli) does the same across JavaScript and TypeScript with an SWC parser behind it. This package detects two specific shapes, a locale-keyed table living in code and a prompt constant in Python, and will not see `el.textContent = "Save"`. On that criterion it loses, and the table says so.
- **You have translators.** Weblate, Crowdin, Lokalise and Tolgee are editors, translation memories, machine translation, screenshot context and review queues. This package has a YAML file. If somebody who is not the author is going to touch your strings, start there and keep the audit alongside: it finds strings that are in no catalogue at all, including theirs.
- **Your messages need gender, dates, currencies or nested selection.** [FormatJS](https://formatjs.github.io/) and [LinguiJS](https://lingui.dev/) implement ICU MessageFormat, and [Project Fluent](https://projectfluent.org/) goes further with asymmetric localisation, where a target language may add grammatical complexity the source does not have. This package does CLDR plural categories through `Intl.PluralRules` and named `{placeholder}` interpolation, and stops there.
- **You already have a framework.** React, Vue and Svelte teams should take [shadcn/ui](https://ui.shadcn.com/) or [Radix UI](https://www.radix-ui.com/), which ship behaviour this package asks a model to write by hand: focus trapping, scroll locking, return focus on close, and the keyboard patterns of the ARIA Authoring Practices Guide. Radix does them correctly out of the box; prose asking for a `<dialog>` plus an `Escape` handler does not carry the same guarantee.
- **You need a component library today.** [Preline UI](https://preline.co/) ships over 300 components, [Flowbite](https://flowbite.com/) and [DaisyUI](https://daisyui.com/) a few hundred between them, all with dark mode, and [Bootstrap](https://getbootstrap.com/) has honoured `prefers-reduced-motion` in its own CSS for years. This package has seven component shapes and eight law-keyed snippets. It does not compete on breadth and will not.
- **You want a working application from a sentence.** [v0](https://v0.dev/), [Lovable](https://lovable.dev/) and [bolt.new](https://bolt.new/) take a prompt and give back a deployed application, with authentication and a database wired in. They are not reproducible, they need an account, and their output carries a framework runtime. All three are deliberate trades, and for a weekend prototype they are the right ones.

## Ideas worth stealing

Twenty-five tools were read for this document. Studying a competitor and bringing nothing back is wasted reading, so here is what is worth taking, best value first. Two entries are refusals, with the reason.

**[Weblate](https://weblate.org/): the placeholder check.** Weblate runs a catalogue of quality checks over every translation, and one of them compares the placeholders of the translation against those of the source string: a French line that drops the `{count}` the English one has is a hole that only appears at runtime. Here it is a sibling to a function that already exists. `check_prompts()` in `scripts/i18n_make.py` blocks the compile on a prompt with no `validated:` locale; `check_placeholders()` would block it on any locale whose `{name}` set differs from the source locale's, called from `compile_json()` so it fails at build time with the same severity. Cost: about thirty lines and one test. Half of this is already built, because the emitted `interpolate()` deliberately leaves an unmatched placeholder visible on screen rather than blanking it. Only the compile-time half is missing, which is why it is the best ratio on the list.

**[i18next-cli](https://github.com/i18next/i18next-cli): the lint baseline.** `i18next-cli lint --update-baseline` records today's findings to a file so the gate fails only on new ones. That is what makes a rule adoptable in a codebase that already has four hundred violations: without it the first run is a wall, and the hook gets removed the same afternoon. Here: a `--baseline .i18n-baseline.json` flag in `scripts/audit_i18n.py`, subtracting known findings before the exit code is computed. Cost: an afternoon, standard library only, no new dependency. The one hard part is the fingerprint, because a line number moves on the next edit, so the key has to be the rule plus the path plus a hash of the snippet, never the line.

**[i18next-cli](https://github.com/i18next/i18next-cli): `status --unused`.** The audit looks one way only, from the code to the catalogue, so it never notices a message id nobody calls any more. `i18next-cli status` reports both directions, unused keys included. Here: a third rule, I18N003, or a `--unused` flag on the make half, reading `locales/i18n.yaml` and searching the tree for `t("id")` and `prompt("id")`. Cost: half a day. It has to report rather than block, because `t(key)` with a computed id is legitimate and no static pass can resolve it. A rule that cannot be sure is a rule that warns.

**[i18next-cli](https://github.com/i18next/i18next-cli): the `types` command.** It generates TypeScript definitions from the catalogue, so a typo in a message id fails the build instead of rendering the id on screen. Here: an `--emit-types` step on `sprezzature-ui-i18n-make`, writing `locales/i18n.d.ts` with `type MessageId = "app.title" | "action.save" | ...` beside the emitted `i18n.js`, and a `Literal` alias in `i18n_prompts.py`. Cost: half a day, and take the Python half first because it is nearly free: the loader is already generated from the same data. The honest caveat is that this package's output is vanilla JavaScript with no build step, so the `.d.ts` pays off in an editor and not in continuous integration.

**[GNU gettext](https://www.gnu.org/software/gettext/): the fuzzy flag.** When a source string changes, `msgmerge` marks every translation of it fuzzy instead of keeping it silently, and the runtime then treats it as missing. [i18n-ally](https://i18nally.org/) rebuilt the same idea as stale-translation detection inside the editor. Here: store a short hash of the source-locale text with each entry, and have `compile_json()` report any locale written against a different hash. Cost: an afternoon for the code, plus a change to the catalogue format, which is the real price. A format change needs a migration path and a test proving an old catalogue still compiles.

**[shadcn/ui](https://ui.shadcn.com/): the distribution model.** shadcn/ui is not a dependency; a command copies the component source into your repository, where you own it and edit it. That matches this package exactly: `assets/components/*.html` and `assets/snippets/*.html` are fifteen files meant to be copied and adapted, and no command places them. A `sprezzature-ui components add modal` would be a file copy and nothing more. Cost: a day. The argument against is that it widens a package whose README promises to stay small, and "adding routes for the sake of the count would be mistaking breadth for value" is that README's own sentence.

**Refused: [i18next-cli](https://github.com/i18next/i18next-cli)'s `instrument`.** It rewrites the call sites, turning `"Save"` into `t('save')` across the tree, with `--dry-run` and `--interactive` to make that bearable. This package's `--fix` deliberately stops short, for the reason `pybabel extract` stops there too: only the author knows which id the call should use, and whether the surrounding code wants a plural form or a placeholder. Taking it would mean owning a codemod for every JavaScript dialect and for Python, which is most of what SWC is. What is worth taking from the same command is its `--dry-run`, because today `--fix` writes on the first run with no preview.

**Refused: MessageFormat 2.0 as the catalogue syntax.** The Unicode standard reached Final Candidate in March 2025 and is stable in CLDR through the LDML 47 and 48 releases, and it is the right long-term target for a message format. Not in 2026: as of May 2026 the i18next MessageFormat 2 plugin had single-digit weekly npm downloads against roughly 340 000 for the underlying `messageformat` library, and the TC39 process wants about a dozen organisations running it in production before it advances. Shipping a parser for a syntax nobody writes yet, inside a runtime that is 80 lines, is cost with no reader. Revisit the day `Intl.MessageFormat` lands in browsers, because that is when the runtime cost drops to zero.

## How the field divides

**Finding strings, moving them, translating them.** Three jobs, and most tools do one. A linter finds (`eslint-plugin-i18next`, `i18next-cli lint`); a catalogue toolchain moves and compiles (GNU gettext plus Babel, FormatJS, LinguiJS, the make half here); a platform translates and reviews (Weblate, Crowdin, Lokalise, Tolgee). The tools that span two of the three are the ones worth comparing, and `i18next-cli` is the clearest example in the field: one binary that extracts, lints, types, syncs, and since June 2026 chains the lot into a single `localize` command. This package spans the first two over a narrower slice of input, and does not attempt the third at all.

**Static against runtime, on the production side.** A component library ships behaviour: Radix traps focus and locks scroll, Flowbite and Preline ship a JavaScript layer, shadcn/ui hands you React source. At the other end are the ones that ship only markup or only CSS. HyperUI is copy-and-paste Tailwind, DaisyUI is CSS with no JavaScript runtime at all, Pico CSS styles semantic elements without a single class, htmx is fourteen kilobytes of attribute handling with no opinion about looks. `sprezzature-ui` belongs at that end by rule rather than by circumstance: its first hard rule is that the output never contains `react`, `vue`, `svelte`, `next` or `angular`, and it is told to refuse and offer the vanilla equivalent when asked.

**Prose against product.** The newest division is between a tool you run and a document a model reads. v0, Lovable and bolt.new are products: a prompt goes in, an application comes out, and the price is an account, a subscription, and a result nobody can reproduce twice. The design half of this package is the opposite shape: 4 772 lines across 64 reference files, read by whatever model is in front of them, with the output checked afterwards by three deterministic sibling auditors. Neither shape is better in general. They answer different questions about who is accountable for the result.

## How it compares

Every alternative is rated 1 to 5 on each criterion, higher is better (⭐ weak to ⭐⭐⭐⭐⭐ strongest). The scores are an argued judgement, not a benchmark, and each axis is oriented so that more stars mean stronger on that trait: for cost, more stars mean cheaper or more open. A single star means "it does not really do this", never "unknown". The machine-readable source is [`assets/landscape.csv`](assets/landscape.csv): 25 tools across 16 criteria.

| i18n or UI tool | Hardcoded string detection | Source languages covered | Catalogue scaffolding and compilation | Runtime loader shipped | CI verdict with an exit code | No framework runtime in the output | Accessibility out of the box | Dark mode out of the box | Reduced motion guard | Customisation and theming | Deterministic and reproducible | Local and offline (no account) | Free or open source | Maturity and ecosystem | Component library breadth | Translator workflow |
| --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| sprezzature-ui | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐ |
| i18next + i18next-cli | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐ |
| eslint-plugin-i18next | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐ |
| i18n-ally | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐ |
| FormatJS / react-intl | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐ |
| LinguiJS | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐ |
| GNU gettext + Babel | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐ |
| Project Fluent | ⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐⭐ |
| Weblate | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ |
| Crowdin | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ |
| Lokalise | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ |
| Tolgee | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ |
| shadcn/ui | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ |
| Tailwind Plus | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ |
| DaisyUI | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ |
| Flowbite | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ |
| Preline UI | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ |
| HyperUI | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ |
| Radix UI | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ |
| Bootstrap | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ |
| Pico CSS | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐ |
| htmx | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐ |
| v0 (Vercel) | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ |
| Lovable | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| bolt.new | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ |


![sprezzature-ui against 24 other i18n and interface tools, on two axes derived from a principal component analysis. The package sits alone in the top right corner, by construction. At the same height but far to its left is a tight cluster of i18n toolchains: i18next with i18next-cli, GNU gettext with Babel, LinguiJS, eslint-plugin-i18next, FormatJS, Project Fluent and i18n-ally, with Tolgee and Weblate just below them. Lokalise and Crowdin sit at the far left of the horizontal axis. The bottom right holds the component libraries in a diagonal band: Pico CSS, HyperUI, DaisyUI, Bootstrap, Preline UI, Flowbite, Radix UI, shadcn/ui and Tailwind Plus. At the bottom centre, apart from everything else, are Lovable, bolt.new and v0. The horizontal axis opposes a toolchain you run yourself and own the output of against a hosted platform other people log into; the vertical axis opposes a deterministic catalogue toolchain that returns a verdict against a broad library of ready-made components.](assets/landscape.svg)

The source is [`assets/landscape.csv`](assets/landscape.csv), the star table above and nothing added, and the map is regenerated with:

```sh
python ~/sprezzature/scripts/landscape_to_csv.py ~/sprezzature-ui/LANDSCAPE.md
standpoint assets/landscape.csv --outdir assets --stem landscape --check
```

The geometry is ordinary correlation principal component analysis (PCA) and is **deterministic**: the same table gives the same map every run, whatever model named the poles. The four words at the edges come from a local model through Ollama, and they are vaguer than the loadings behind them, so the loadings are the control. Here is what the two axes are made of.

**Horizontal, 41.9 % of the variance.** Deterministic and reproducible (+0.35), local and offline (+0.34), dark mode out of the box (+0.32) and customisation and theming (+0.31) pull right; translator workflow (−0.36) and source languages covered (−0.29) pull left. It is the axis of a tool you run and own the output of against a platform other people log into, and `sprezzature-ui` sits at its far right by construction: it is the reference row, and `standpoint` anchors the reference top right. The model named the poles Capable on the left and Adaptable on the right.

**Vertical, 22.1 % of the variance.** Free or open source (+0.35), local and offline (+0.34), deterministic and reproducible (+0.33), catalogue scaffolding and compilation (+0.32) and a CI verdict with an exit code (+0.30) load at the top; component library breadth (−0.33) and accessibility out of the box (−0.24) load at the bottom. That is the i18n toolchain against the component library, which is exactly the two families the table was built to hold, and the map found the split on its own. The model named the poles Reliable at the top and Inclusive at the bottom.

**Two axes carry 64.1 % of the table.** More than a third of what those 16 criteria say is not on this page. The clearest thing missing from the map is the one the first paragraph of this file insists on: the axes see a package that is free, offline, deterministic and framework-free, and they do not see that its detection rule covers two shapes rather than the whole class, which is the two-star cell in the first column. `standpoint` also writes a prose interpretation beside the figure; it is not reproduced here, because a model reading back ratings somebody wrote is not a finding.

`--check` reports `leader_top_right: True` and `axis_labels_visible: True`, and `readable: False`: with 25 points, five pairs of labels risk overlapping (i18n-ally with FormatJS, FormatJS with Project Fluent, Crowdin with Lokalise, Flowbite with Preline UI, HyperUI with Pico CSS). The SVG is interactive, so the names resolve on hover; the PNG is the one to read at a distance.

## Sources

- [i18next-cli](https://github.com/i18next/i18next-cli), the official i18next toolchain; `i18next-parser` is deprecated in its favour
- [eslint-plugin-i18next](https://github.com/edvardchen/eslint-plugin-i18next) and the `no-literal-string` rule
- [i18n Ally](https://i18nally.org/), now carried by community forks
- [LinguiJS against i18next](https://lingui.dev/misc/i18next), written by LinguiJS
- [MessageFormat 2 in i18next: state of the migration, May 2026](https://www.locize.com/blog/messageformat-2-i18next)
- [Fluent against gettext](https://github.com/projectfluent/fluent/wiki/Fluent-vs-gettext), written by Project Fluent
- [Localisation platforms compared, 2026](https://alconost.com/en/blog/localization-platforms-comparison)
- [Radix, Headless UI and Ark UI compared, 2026](https://codecudos.com/blog/radix-ui-vs-headless-ui-vs-ark-ui-2026)
- [Tailwind component libraries ranked, 2026](https://designrevision.com/blog/best-tailwind-component-libraries)
- [Lovable, Bolt and v0 compared, 2026](https://superframeworks.com/compare/lovable-vs-bolt-vs-v0)
