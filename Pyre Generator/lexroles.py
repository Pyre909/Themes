import re, sys, pathlib
sys.path.insert(0, '.')
import make_themes as m
model = pathlib.Path(sys.argv[1]).read_text(encoding='utf-8')
lexer = None
ab = {'default': '-', 'operator': 'op', 'comment': 'cm', 'comment_doc': 'cd', 'doc_kw': 'dk', 'keyword': 'KW',
      'type': 'TY', 'function': 'FN', 'string': 'st', 'escape': 'esc', 'number': 'num', 'preproc': 'PP',
      'regex': 're', 'label': 'lbl', 'attribute': 'attr', 'tag': 'tag', 'heading': 'HEAD', 'variable': 'var',
      'error': 'ERR', 'added': 'add', 'removed': 'rem', 'changed': 'chg'}
out = {}
for line in model.splitlines():
    g = re.search(r'<LexerType name="([^"]*)"', line)
    if g: lexer = g.group(1)
    if '<WordsStyle ' in line and lexer:
        name = re.search(r'name="([^"]*)"', line).group(1).replace('&apos;', "'").replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        fg = (re.search(r'fgColor="([^"]*)"', line) or [0, '000000'])[1] if re.search(r'fgColor="([^"]*)"', line) else '000000'
        if m.ANSI_RE.match(name) or m.ANSI2_RE.match(name.upper()) or (lexer, name) in m.SPECIAL:
            continue
        r = m.classify(lexer, name, fg)
        out.setdefault(lexer, []).append(f'{name}={ab.get(r, r)}')
for lx in out:
    print(f'[{lx}] ' + ' | '.join(out[lx]))
