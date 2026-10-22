"""Draw the Pyre palette swatches (SVG) and print the colour table (Markdown) from make_themes.

python make_palette.py "Pyre Palette.svg"
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import make_themes as m

ROWS = [  # (palette key, label, used for)
    ('bg', 'Background', 'Editor background'),
    ('text', 'Text', 'Identifiers, plain text'),
    ('operator', 'Operators', 'Operators, punctuation'),
    ('comment', 'Comments', 'Comments'),
    ('comment_doc', 'Doc comments', 'Documentation comments'),
    ('keyword', 'Keywords', 'Keywords, headings, INI/TOML sections'),
    ('type', 'Types', 'Types, classes, keys, attributes'),
    ('function', 'Functions', 'Functions, built-ins, tags, links'),
    ('string', 'Strings', 'Strings, characters'),
    ('number', 'Numbers', 'Numbers, constants, symbols'),
    ('preproc', 'Preprocessor', 'Directives, macros, decorators, regex'),
    ('escape', 'Escapes', 'Escape sequences, entities'),
    ('error', 'Errors', 'Errors, removed lines'),
    ('linenum', 'Line numbers', 'Line-number margin'),
    ('select', 'Selection', 'Selected text background'),
    ('line', 'Current line', 'Current-line background'),
    ('caret', 'Caret', 'Caret, active fold, matching brace'),
]
BACKGROUNDS = {'bg', 'select', 'line'}
MONO = "Consolas, 'Cascadia Mono', Menlo, monospace"


def panel(x, p, c):
    w, h = 460, 64 + 30 * len(ROWS) + 14
    out = [f'  <rect x="{x}" y="0" width="{w}" height="{h}" rx="12" fill="#{c["bg"]}" '
           f'stroke="#{c["linenum"]}" stroke-opacity="0.35"/>',
           f'  <text x="{x + 24}" y="40" font-size="20" font-weight="600" fill="#{c["text"]}">{p["name"]}</text>']
    for i, (key, label, _) in enumerate(ROWS):
        y = 64 + 30 * i
        out.append(f'  <rect x="{x + 24}" y="{y}" width="22" height="22" rx="4" fill="#{c[key]}" '
                   f'stroke="#{c["linenum"]}" stroke-opacity="0.6"/>')
        out.append(f'  <text x="{x + 60}" y="{y + 16}" font-size="14" fill="#{c["text"]}">{label}</text>')
        out.append(f'  <text x="{x + 436}" y="{y + 16}" font-size="14" text-anchor="end" '
                   f'font-family="{MONO}" fill="#{c["comment"]}">#{c[key]}</text>')
    return out, h


def main():
    day, night = m.build(m.DAY), m.build(m.NIGHT)
    left, h = panel(0, m.DAY, day)
    right, _ = panel(480, m.NIGHT, night)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="940" height="{h}" viewBox="0 0 940 {h}" '
           "font-family=\"'Segoe UI', -apple-system, Helvetica, Arial, sans-serif\">", *left, *right, '</svg>', '']
    pathlib.Path(sys.argv[1]).write_text('\n'.join(svg), encoding='utf-8', newline='\n')

    print('| Role | Used for | Pyre Daylight | Contrast | Pyre Night | Contrast |')
    print('|---|---|---|---|---|---|')
    for key, label, used in ROWS:
        cell = lambda c: '' if key in BACKGROUNDS else f'{m.wcag(c[key], c["bg"]):.1f}:1'
        print(f'| {label} | {used} | `#{day[key]}` | {cell(day)} | `#{night[key]}` | {cell(night)} |')


if __name__ == '__main__':
    main()
