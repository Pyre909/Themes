# Fovea palette

![Fovea palette](Fovea%20Palette.svg)

Fovea Light and Fovea Dark are Notepad++ themes whose syntax colours were chosen by a constrained optimisation over vision-science data rather than by eye:

- **As little colour as possible.** Visual discomfort rises with the chromaticity difference between neighbouring colours (Haigh et al. 2013, 2018), and colour adds nothing to legibility once luminance contrast is present (Legge et al. 1990).
- **Nothing glows.** A colour starts to look self-luminous as its luminance approaches the brightest a real surface of that colour could be (Speigle & Brainard 1996; Duay & Nagai 2026). Every colour stays inside the range measured for calm themes such as One Dark.
- **Every token type identifiable at a glance.** Letter-sized marks need 2-3x larger colour differences than large swatches (Szafir 2018); every pair of syntax colours clears the threshold at which 80% of people tell them apart, on hue alone.
- **Legible at code sizes.** Letters at about 0.2 degrees are below the size where reading tolerates reduced contrast (Legge et al. 1987); syntax colours are at least 5.5:1 (light) and 6:1 (dark).

Hue roles follow Atom One Dark/Light: keywords purple, functions blue, strings green, numbers orange, types cyan, tags red.

## Colours

| Role | Used for | Fovea Light | Contrast | Fovea Dark | Contrast |
|---|---|---|---|---|---|
| Background | Editor background | `#F8F7F2` |  | `#1F232A` |  |
| Text | Identifiers, plain text | `#3B3E45` | 10.0:1 | `#C5C9D0` | 9.5:1 |
| Operators | Operators, punctuation | `#4C5057` | 7.6:1 | `#B5B9BF` | 8.0:1 |
| Comments | Comments | `#64707D` | 4.7:1 | `#818B9A` | 4.6:1 |
| Keywords | Keywords, preprocessor, decorators | `#924389` | 5.8:1 | `#D98CCE` | 6.5:1 |
| Functions | Function and method names | `#37619B` | 5.9:1 | `#7EA2E0` | 6.1:1 |
| Strings | Strings, characters | `#3E5C2E` | 7.1:1 | `#8BAB6B` | 6.1:1 |
| Numbers | Numbers, constants, booleans, attributes | `#995011` | 5.6:1 | `#C89F70` | 6.5:1 |
| Types | Types, classes, built-ins, escapes, regex | `#006F6F` | 5.6:1 | `#6ECBD8` | 8.4:1 |
| Tags | HTML/XML tags, JSON/YAML/INI keys, errors | `#A34558` | 5.5:1 | `#F6B2BB` | 9.0:1 |
| Line numbers | Line-number margin | `#9A9FA6` | 2.5:1 | `#696D72` | 3.0:1 |
| Selection | Selected text background | `#CCE2FE` |  | `#34425D` |  |
| Current line | Current-line background | `#ECF0F5` |  | `#262A32` |  |
| Caret | Caret, active fold, hovered link | `#004388` | 9.1:1 | `#9BC6FF` | 8.9:1 |

Contrast is the WCAG luminance ratio against the theme background.

## Measured against well-known themes

| Theme | Glow (avg / max) | Chromatic load (avg Δu′v′) | Worst token separation |
|---|---|---|---|
| One Light | 0.47 / 0.80 | 0.127 | 1.12 |
| **Fovea Light** | 0.21 / 0.30 | 0.097 | 1.00 |
| One Dark | 0.58 / 0.80 | 0.076 | 0.99 |
| **Fovea Dark** | 0.58 / 0.69 | 0.058 | 1.00 |

Glow: luminance over the optimal-colour limit (calm themes measure about 0.4-0.6 on average, vivid ones like Dracula about 0.8). Chromatic load: lower is less discomfort. Separation: 1.00 or more means 80% of people tell the closest two token colours apart at letter size.

## Install

1. Copy `Fovea Light.xml` and `Fovea Dark.xml` to `%AppData%\Notepad++\themes\` (for a portable Notepad++, the `themes` folder next to `notepad++.exe`).
2. Restart Notepad++ and pick the theme in **Settings → Style Configurator → Select theme**.
3. With Fovea Dark, also turn on **Settings → Preferences → Dark Mode** so the toolbar and tabs match.

The themes set Consolas 12 pt, which puts the x-height at the 0.2 degree critical print size at a 60 cm viewing distance (Legge & Bigelow 2011).

## Sources

- Duay & Nagai (2026), *PLOS One* 21(3): e0343984
- Haigh et al. (2013), *Vision Research* 89: 47-53; Haigh, Cooper & Wilkins (2018), *Neuropsychologia*
- Legge, Rubin & Luebker (1987), *Vision Research* 27(7); Legge, Parish, Luebker & Wurm (1990), *JOSA A* 7(10)
- Legge & Bigelow (2011), *Journal of Vision* 11(5): 8
- Speigle & Brainard (1996), *JOSA A* 13(3): 436
- Szafir (2018), *IEEE TVCG* 24(1); data at https://cmci.colorado.edu/visualab/VisColors/
