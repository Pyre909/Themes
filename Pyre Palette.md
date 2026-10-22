# Pyre palette

![Pyre palette](Pyre%20Palette.svg)

Pyre Daylight and Pyre Night are a pair of Notepad++ themes: Daylight for a bright room, sunlight on the
screen included, and Night for long sessions in the dark. Notepad++ keeps one theme for Dark Mode and one
for light mode, so with Pyre Night as the first and Pyre Daylight as the second, turning Dark Mode on or
off switches between them.

The colours are set in OKLCH, a colour space where equal steps look equally different (Ottosson 2020),
then checked for contrast rather than picked by eye:

- **Brightness contrast first, hue second.** Reading depends on luminance contrast; colour differences
  alone do little for legibility (Legge et al. 1990). Every syntax colour clears 6:1 against its
  background, and hue only tells token types apart.
- **Daylight is dark text on a light page.** Positive polarity reads faster and more accurately, whatever
  the room lighting (Buchner & Baumgartner 2007; Piepenbrock et al. 2013). Syntax colours are deep, not
  pastel, and still clear 4.2:1 with a 10% veiling glare added to both text and background (sunlight on
  the screen). Keywords are bold, since letter weight survives glare that washes colour out.
- **Night has no pure white on pure black.** Text is a warm off-white at 12.3:1 on a blue-charcoal
  background: clear, without the halo very bright text gets on black. Its "blue" is a light periwinkle,
  as the centre of the fovea has almost no blue-sensitive cones (Wald 1967), so fine detail in saturated
  blue looks soft. Keywords are not bold: bright bold text glows more at night.
- **Calm by default.** In Night all syntax colours sit at the same perceived lightness, with plain
  identifiers (the part you actually read) the brightest; comments step back (cooler, italic) but stay at
  5:1 or more.
- **One hue map, day and night.** Keywords ember (55°), strings green (145°), types teal (195°), functions
  blue (255°), numbers violet (305°), preprocessor rose (0°): six families about 60° apart. Red is kept
  for errors and removed lines. Blues, teals and greens are among the most liked colours and dark yellow /
  olive among the least (Palmer & Schloss 2010); there is no olive here.

## Colours

| Role | Used for | Pyre Daylight | Contrast | Pyre Night | Contrast |
|---|---|---|---|---|---|
| Background | Editor background | `#FCFCF9` |  | `#14171D` |  |
| Text | Identifiers, plain text | `#191E28` | 16.2:1 | `#DBD5C9` | 12.3:1 |
| Operators | Operators, punctuation | `#404858` | 8.9:1 | `#A2ABBB` | 7.8:1 |
| Comments | Comments | `#636D79` | 5.1:1 | `#8A97A5` | 6.0:1 |
| Doc comments | Documentation comments | `#4B6A75` | 5.6:1 | `#7EA1A9` | 6.5:1 |
| Keywords | Keywords, headings, INI/TOML sections | `#944300` | 6.7:1 | `#F5AE6F` | 9.5:1 |
| Types | Types, classes, keys, attributes | `#00686C` | 6.4:1 | `#76D5D7` | 10.5:1 |
| Functions | Functions, built-ins, tags, links | `#1E4EAC` | 7.5:1 | `#92BDFB` | 9.3:1 |
| Strings | Strings, characters | `#266F20` | 6.1:1 | `#92CD86` | 9.7:1 |
| Numbers | Numbers, constants, symbols | `#77319B` | 7.6:1 | `#E3B3F2` | 10.3:1 |
| Preprocessor | Directives, macros, decorators, regex | `#992A54` | 7.3:1 | `#E999B1` | 8.3:1 |
| Escapes | Escape sequences, entities | `#902880` | 7.3:1 | `#F1A9E0` | 9.8:1 |
| Errors | Errors, removed lines | `#B71824` | 6.4:1 | `#F97770` | 6.8:1 |
| Line numbers | Line-number margin | `#7A808D` | 3.9:1 | `#636975` | 3.3:1 |
| Selection | Selected text background | `#B5D6F9` |  | `#253A55` |  |
| Current line | Current-line background | `#E9F1F9` |  | `#1E222A` |  |
| Caret | Caret, active fold, matching brace | `#AB4500` | 5.7:1 | `#FFBA7D` | 10.7:1 |

Contrast is the WCAG luminance ratio against the theme background.

The highlights get their own colours too: the five Mark styles (cyan, amber, yellow, lilac, green), Smart
Highlighting in a quiet blue close to the selection, search results, bookmarks and change history.

## Coverage

Every language Notepad++ has a highlighter for was opened in Notepad++ with both themes and checked on
screen. Keys look the same in JSON, YAML, TOML, INI and CSS (teal); section headers the same in INI,
TOML and registry files (bold amber). FreeBASIC block and doc comments, which Notepad++'s own style list
leaves out (so other themes show them as plain text), are included.

## Install

1. Copy `Pyre Daylight.xml` and `Pyre Night.xml` to `%AppData%\Notepad++\themes\` (for a portable
   Notepad++, the `themes` folder next to `notepad++.exe`).
2. Restart Notepad++. Turn **Settings → Preferences → Dark Mode** on and pick **Pyre Night** in
   **Settings → Style Configurator → Select theme**.
3. Turn Dark Mode off and pick **Pyre Daylight**. From then on, the Dark Mode switch changes the theme.

The themes set Consolas 10 pt. For long sessions 11-12 pt and a little extra line spacing are easier on the
eyes. When Windows' output gets rescaled (a VM window, a remote desktop), grayscale antialiasing avoids
the colour fringes ClearType leaves on the letters (the Pyre909 build of Notepad++ has it under
Preferences → Editing 1 → Text Rendering).

The themes are generated: see [Pyre Generator](Pyre%20Generator/README.md) to change a colour and rebuild them.

## Sources

- Buchner & Baumgartner (2007), *Ergonomics* 50(7): 1036-1063
- Legge, Parish, Luebker & Wurm (1990), *JOSA A* 7(10): 2002-2010
- Ottosson (2020), *A perceptual color space for image processing* (OKLab), https://bottosson.github.io/posts/oklab/
- Palmer & Schloss (2010), *PNAS* 107(19): 8877-8882
- Piepenbrock, Mayr, Mund & Buchner (2013), *Ergonomics* 56(7): 1116-1124
- Wald (1967), *JOSA* 57(11): 1289-1301
