# Color Psychology: tokens and selection rules

Source: [deraison.ai/colors](https://deraison.ai/colors) (in English:
[deraison.ai/en/colors](https://deraison.ai/en/colors)). It is the single
source of truth for every colour in the sprezzature suite. Read the values
there rather than copying them by hand.

The site publishes three palettes with the same eleven names: Red, Orange,
Yellow, Green, Turquoise, Blue, Purple, Pink, Brown, Black, Gray. Each name
carries a hex code and a light tint.

| Palette | What it is | When to use it |
|---|---|---|
| corporate | Apple's system colours, light mode, values of June 9, 2025 | The default for interfaces generated here |
| academic | OKABE and ITO (2002), readable with colour blindness, completed from the CUD (Colour Universal Design) recommended set | Charts and figures that must survive colour blindness |
| print | Checked for offset printing on coated paper | Anything that will be printed |

`sprezzature-colors` ships the site's three files as they are:
`references/palette-corporate.csv`, `palette-academic.csv` and
`palette-print.csv` (CSV: comma-separated values, a table saved as plain
text). Its `references/palette.csv` is the corporate one in a compact
layout. To regenerate the Tailwind `theme.extend.colors` block run:

```bash
sprezzature-colors-palette-to-tailwind --emit theme
sprezzature-colors-palette-to-tailwind --emit theme --theme print
```

The hex codes below are the corporate palette, kept because generated code
needs them. If one drifts from the site, the **site wins** and this file is
updated to match. White is not a palette colour since 2026-11-13. It stays
the page surface (`surface-primary`), as in `ui-guidelines/foundations/color.md`.

**Curated default: user colors win.** When the user has supplied their
own palette, use it. The curated set below is the default for fresh
generation when no palette is in play. See rule 7 in
`sprezzature-ui/SKILL.md` for the full carve-out.

Every colour decision maps back to a row in one of these tables. The
UI guidelines define *how* colour is applied (contrast, dark mode,
semantics); this file defines *which* hue is chosen and *why*.

## Base palette (corporate)

Each hue ships with a light tint for backgrounds, hover, selection. The
first eight are the saturated brand hues; Brown, Black and Gray complete
the eleven names.

| Name | Hex | Light variant | Hex |
|---|---|---|---|
| Red | `#FF383C` | Light Red | `#FFD7D8` |
| Orange | `#FF8D28` | Light Orange | `#FFE8D4` |
| Yellow | `#FFCC00` | Light Yellow | `#FFF5CC` |
| Green | `#34C759` | Light Green | `#D6F4DE` |
| Turquoise | `#00C3D0` | Light Turquoise | `#CCF3F6` |
| Blue | `#0088FF` | Light Blue | `#CCE7FF` |
| Purple | `#CB30E0` | Light Purple | `#F5D6F9` |
| Pink | `#FF2D55` | Light Pink | `#FFC0CC` |
| Brown | `#AC7F5E` | Light Brown | `#EEE5DF` |
| Black | `#000000` | Light Black | `#CCCCCC` |
| Gray | `#8E8E93` | Light Gray | `#E8E8E9` |

## Emotion → hue

The hue is a name; its hex is in the base palette above, or on the site
for the academic and print palettes.

| Emotion | Hue |
|---|---|
| Silence | Black |
| Neutral | Gray |
| Anger | Red |
| Surprise | Orange |
| Joy | Yellow |
| Disgust | Green |
| Happiness | Turquoise |
| Sadness | Blue |
| Fear | Purple |
| Love | Pink |
| Comfort | Brown |

## Concept → hue

| Concept | Hue |
|---|---|
| Balance, Neutral, Calm | Gray |
| Excitement, Youthful, Bold | Red |
| Friendly, Cheerful, Confidence | Orange |
| Optimism, Clarity, Warmth | Yellow |
| Peaceful, Growth, Health | Green |
| Refreshing, Clear, Calm | Turquoise |
| Trust, Dependable, Reliable, Strength | Blue |
| Creative, Imaginative, Wise | Purple |
| Playful, Romantic, Compassionate | Pink |
| Earthy, Natural, Dependable | Brown |
| Sophisticated, Powerful, Mysterious | Black |

## Positive vs negative associations

Always check the negative column before locking a colour. A hue that fits the positive list for one brand can project a negative trait you did not intend.

| Color | Positive | Negative |
|---|---|---|
| Red | Power, Passion, Energy, Strength | Anger, Danger, Warning, Aggression |
| Orange | Courage, Confidence, Warmth, Innovation | Deprivation, Frustration, Frivolity, Immaturity |
| Yellow | Optimism, Happiness, Creativity, Intellect | Irrationality, Caution, Anxiety, Cowardice |
| Green | Health, Hope, Freshness, Growth | Boredom, Envy, Blandness, Sickness |
| Turquoise | Communication, Clarity, Calmness, Healing | Boastfulness, Secrecy, Unreliability, Aloofness |
| Blue | Trust, Loyalty, Logic, Serenity | Coldness, Emotionless, Uncaring |
| Purple | Wisdom, Luxury, Spirituality, Sophistication | Decadence, Inferiority, Moodiness |
| Pink | Imaginative, Passion, Creative, Innovation | Outrageousness, Flippancy, Impulsiveness |
| Brown | Seriousness, Warmth, Reliability, Authenticity | Humorlessness, Heaviness, Sadness |
| Black | Sophistication, Power, Elegance, Authority | Oppression, Menace, Heaviness, Mourning |
| Gray | Timelessness, Neutrality, Reliability, Balance | Unconfident, Depression, Lack of energy |

## Selection rules

1. Start from intent (emotion, concept, or system semantic), not aesthetics.
2. Read the negative column. If a negative trait clashes with brand voice, pick a neighbour.
3. Pair with the light variant for backgrounds, hover, selection. Do **not** reuse the base hue at low opacity for surfaces.
4. Always emit a Tailwind token (`bg-brand-blue`), never a hex literal (`bg-[#0088FF]`); see `stack-tailwind.md`.
5. Red is reserved for destructive / critical states. Never primary CTA.

## Semantic defaults

| Role | Default | Reason |
|---|---|---|
| Primary action / link | Blue `#0088FF` | Trust |
| Destructive | Red `#FF383C` | Universal danger signal |
| Success | Green `#34C759` | Growth |
| Warning | Yellow `#FFCC00` | Attention without alarm |
| Info | Turquoise `#00C3D0` | Calm, communicative |
| Premium / accent | Purple `#CB30E0` | Luxury, sparingly |
| Brand emotion (joy) | Orange `#FF8D28` or Pink `#FF2D55` | Friendly, energetic |
| Neutral surfaces | Gray `#8E8E93`, Black `#000000`, on the white page surface | Layout backbone |
