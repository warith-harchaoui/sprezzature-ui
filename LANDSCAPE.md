# Landscape

This package is small, and comparing it to a component library would flatter
it dishonestly. It does not ship components. The honest comparison is against
**two different families at once**, because it sits between them:

- **Component and styling systems** — Tailwind UI, shadcn/ui, Material UI,
  Bootstrap. They give you the parts. They say nothing about where your
  strings live.
- **Internationalisation toolchains** — i18next, gettext/Babel. They give you
  a catalogue and a loader. They say nothing about what the interface should
  look like.

`sprezzature-ui` claims neither territory. It claims the seam: *the strings in
your interface belong in a catalogue, and here is the audit that finds the
ones that do not.*

## The honest table

Judgements, not measurements — a 5 means "this is a strength as of October
2026", a 1 means "it does not really do this". Written down so somebody can
argue with a number rather than with a feeling.

| Approach | No framework runtime | Catalogue-driven i18n | Works as a pre-commit gate | Design rules written down | Breadth of components | Setup simplicity |
|---|---|---|---|---|---|---|
| **sprezzature-ui** | 5 | 5 | 5 | 5 | 1 | 5 |
| Tailwind UI | 5 | 1 | 1 | 3 | 5 | 3 |
| shadcn/ui | 1 | 1 | 1 | 4 | 5 | 3 |
| Material UI | 1 | 2 | 1 | 5 | 5 | 2 |
| Bootstrap | 4 | 1 | 1 | 3 | 5 | 4 |
| i18next | 3 | 5 | 2 | 1 | 1 | 3 |
| gettext / Babel | 4 | 5 | 3 | 1 | 1 | 2 |

Source: [`assets/landscape.csv`](assets/landscape.csv).

## The map

![Positioning map](assets/sprezzature_ui.png)

```sh
standpoint assets/landscape.csv --outdir assets
```

Produced with [`standpoint`](https://github.com/warith-harchaoui/standpoint).
The geometry is correlation PCA and is deterministic: the same table gives the
same map every run, whatever model named the axes. `standpoint` also writes a
prose interpretation; it is not reproduced here, because a model reading back
ratings somebody wrote is not a finding.

## What the shape actually says

**The breadth column is the one to look at, and it is a 1.** That is not a gap
to close. A component library is the model's work here, guided by the
suite's `SKILL.md` — no HTTP route can carry "make this dashboard legible",
and this package says so in its own README. Adding components to raise that
number would be taking width for value.

**The pre-commit column is nearly empty across the field.** The two i18n
toolchains score 2 and 3; everything else scores 1. That is the real argument
for this package: a hardcoded sentence costs nothing the day it is written and
a week the day somebody needs a second language, and the only tool that helps
is one cheap enough to run on every commit.

**It overlaps with i18next and gettext more than with Tailwind.** That is
worth saying plainly: if you already have a working i18n toolchain, the audit
is the only part of this package you want, and it runs alongside yours — it
finds strings that are not in *any* catalogue, including yours.

## When to pick something else

- **You need components** — Tailwind UI, shadcn/ui, Material UI. This package
  does not compete and will not.
- **You need runtime translation with plurals, interpolation and lazy
  loading** — i18next. The audit here finds what belongs in your catalogue; it
  does not replace the catalogue's runtime.
- **You have a framework already** — keep it. The audit is stdlib-only and
  does not care what renders the page.

## See also

- [`sprezzature-accessibility`](https://github.com/warith-harchaoui/sprezzature-accessibility) — whether the HTML is usable
- [`sprezzature-colors`](https://github.com/warith-harchaoui/sprezzature-colors) — whether the contrast passes
- [`sprezzature-cli-gui`](https://github.com/warith-harchaoui/sprezzature-cli-gui) — when there is a command line behind the screen
