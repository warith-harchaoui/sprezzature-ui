# Foundations — Color

## When to consult this file

- Choosing a tint or accent for a screen, component, or brand
- Building a dark mode palette
- Picking semantic colors (success / warning / destructive / info)
- Auditing contrast for accessibility

## Core principles

- **Every hue should encode meaning:** state, hierarchy, mood, or system semantic. If a color does not communicate something, remove it.
- **Use the curated base palette** in `references/color-psychology.md` for all hue choices.
- **Design for both color schemes from the start.** Each color needs a light-mode value and a dark-mode value; do not just invert.
- **Don't rely on color alone.** Pair color with shape, label, or icon so color-blind users and screen-reader users can still parse state.
- **Preserve sufficient contrast.** Body text ≥ 4.5:1 against its background, large text and UI controls ≥ 3:1. Aim higher when readability matters (long-form reading, low-vision users).
- **Reserve red for destructive or critical states**, not for primary CTAs.
- **Use accent color sparingly.** A single tint should anchor a screen; secondary colors are supportive, not competing.

## Semantic color tokens (light / dark)

These are the only colors authors should reference. The light values of the hues are the corporate palette of [deraison.ai/en/colors](https://deraison.ai/en/colors), the source of truth for every colour in the suite. The dark values are the dark-mode system colours of the same platform, June 9, 2025, which the site does not publish. The site also offers an academic palette, readable with colour blindness, and a print palette, under the same names.

| Role | Light | Dark |
|---|---|---|
| Tint primary (Blue) | `#0088FF` | `#0091FF` |
| Danger (Red) | `#FF383C` | `#FF4245` |
| Success (Green) | `#34C759` | `#30D158` |
| Warning (Orange) | `#FF8D28` | `#FF9230` |
| Attention (Yellow) | `#FFCC00` | `#FFD600` |
| Accent (Purple) | `#CB30E0` | `#DB34F2` |
| Joy (Pink) | `#FF2D55` | `#FF375F` |
| Info (Turquoise) | `#00C3D0` | `#00D2E0` |
| Label primary (text) | `#000000` | `#FFFFFF` |
| Label secondary | `rgba(60,60,67,0.6)` | `rgba(235,235,245,0.6)` |
| Label tertiary | `rgba(60,60,67,0.3)` | `rgba(235,235,245,0.3)` |
| Surface primary | `#FFFFFF` | `#000000` |
| Surface secondary | `#F2F2F7` | `#1C1C1E` |
| Surface tertiary | `#FFFFFF` | `#2C2C2E` |
| Separator | `rgba(60,60,67,0.36)` | `rgba(84,84,88,0.65)` |

## Mapping to Tailwind

Authors should write semantic class names (never raw hex) so the system stays consistent.

```js
// tailwind.config.js — excerpt
colors: {
  brand: {
    blue:      { DEFAULT: '#0088FF', dark: '#0091FF', light: '#CCE7FF' },
    red:       { DEFAULT: '#FF383C', dark: '#FF4245', light: '#FFD7D8' },
    green:     { DEFAULT: '#34C759', dark: '#30D158', light: '#D6F4DE' },
    orange:    { DEFAULT: '#FF8D28', dark: '#FF9230', light: '#FFE8D4' },
    yellow:    { DEFAULT: '#FFCC00', dark: '#FFD600', light: '#FFF5CC' },
    purple:    { DEFAULT: '#CB30E0', dark: '#DB34F2', light: '#F5D6F9' },
    pink:      { DEFAULT: '#FF2D55', dark: '#FF375F', light: '#FFC0CC' },
    turquoise: { DEFAULT: '#00C3D0', dark: '#00D2E0', light: '#CCF3F6' },
  },
  label: {
    primary:   { DEFAULT: '#000000', dark: '#FFFFFF' },
    secondary: { DEFAULT: 'rgba(60,60,67,0.6)', dark: 'rgba(235,235,245,0.6)' },
    tertiary:  { DEFAULT: 'rgba(60,60,67,0.3)', dark: 'rgba(235,235,245,0.3)' },
  },
  surface: {
    primary:   { DEFAULT: '#FFFFFF', dark: '#000000' },
    secondary: { DEFAULT: '#F2F2F7', dark: '#1C1C1E' },
    tertiary:  { DEFAULT: '#FFFFFF', dark: '#2C2C2E' },
  },
  separator: 'rgba(60,60,67,0.36)',
}
```

## Checklist before shipping

- [ ] No raw hex in markup: use Tailwind tokens (`bg-brand-blue`, not `bg-[#0088FF]`).
- [ ] Both `light` and `dark:` variants set for every meaningful surface and text token.
- [ ] Body text ≥ 4.5:1, UI ≥ 3:1, verified with a contrast tool.
- [ ] Red used only for destructive/critical states.
- [ ] State (selected, disabled, error) communicated by more than color.
- [ ] Semantic intent picked using the Concept/Psychology tables in `color-psychology.md`.
