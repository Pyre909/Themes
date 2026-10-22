"""Generate the Pyre Daylight / Pyre Night Notepad++ themes.

Colours are defined in OKLCH (perceptually uniform lightness / chroma / hue),
gamut-mapped to sRGB, then checked with WCAG 2 contrast and APCA Lc.
Every WordsStyle of stylers.model.xml gets a semantic role, from its name
first and its default colour otherwise, so all 93 lexers are covered.
"""
import math, re, sys, pathlib, itertools

# ---------------------------------------------------------------- colour math
def oklab_to_srgb_lin(L, a, b):
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    return (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)

def enc(c):
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055

def dec(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def oklch(L, C, h):
    """OKLCH -> hex, reducing chroma until the colour is inside sRGB."""
    def lin(c):
        return oklab_to_srgb_lin(L, c * math.cos(math.radians(h)), c * math.sin(math.radians(h)))
    inside = lambda c: all(-1e-6 <= x <= 1 + 1e-6 for x in lin(c))
    if not inside(C):
        lo, hi = 0.0, C
        for _ in range(40):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if inside(mid) else (lo, mid)
        C = lo
    rgb = [min(1, max(0, x)) for x in lin(C)]
    return '%02X%02X%02X' % tuple(round(enc(x) * 255) for x in rgb)

def rgb(hexs):
    return [int(hexs[i:i + 2], 16) / 255 for i in (0, 2, 4)]

def rel_lum(hexs):
    r, g, b = (dec(x) for x in rgb(hexs))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def wcag(fg, bg, glare=0.0):
    a, b = rel_lum(fg) + glare, rel_lum(bg) + glare
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)

def apca(fg, bg):
    def y(h):
        r, g, b = (x ** 2.4 for x in rgb(h))
        v = 0.2126729 * r + 0.7151522 * g + 0.0721750 * b
        return v + (0.022 - v) ** 1.414 if v < 0.022 else v
    yt, yb = y(fg), y(bg)
    if abs(yb - yt) < 0.0005:
        return 0.0
    if yb > yt:
        s = (yb ** 0.56 - yt ** 0.57) * 1.14
        return 0.0 if s < 0.1 else (s - 0.027) * 100
    s = (yb ** 0.65 - yt ** 0.62) * 1.14
    return 0.0 if s > -0.1 else (s + 0.027) * 100

def to_oklab(hexs):
    r, g, b = (dec(x) for x in rgb(hexs))
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l, m, s = (math.copysign(abs(x) ** (1 / 3), x) for x in (l, m, s))
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)

def delta_e(h1, h2):
    return math.dist(to_oklab(h1), to_oklab(h2))

# ---------------------------------------------------------------- palettes
# Hue plan, shared by both themes so the mental map survives day <-> night:
#   keyword 55 (ember)  string 145 (green)  type 195 (teal)
#   function 255 (blue) number 305 (violet) preproc 355 (rose)
#   error 25 (red: reserved, only for errors and removals)
# Night: tokens at one lightness (~0.80), plain text brighter (0.87).
# Daylight: tokens at ~0.47 for >= 7:1, plain text 0.24.
NIGHT = dict(
    name='Pyre Night', dark=True,
    bg=(0.205, 0.012, 265), margin=(0.185, 0.010, 265), line=(0.250, 0.016, 265),
    region=(0.225, 0.020, 300), select=(0.345, 0.055, 255), guide=(0.30, 0.012, 265),
    text=(0.875, 0.018, 85), operator=(0.74, 0.025, 260), variable=(0.86, 0.045, 225),
    comment=(0.670, 0.026, 250), comment_doc=(0.685, 0.040, 215), doc_kw=(0.76, 0.075, 215),
    keyword=(0.805, 0.115, 62), type=(0.815, 0.090, 198), function=(0.790, 0.100, 258),
    string=(0.790, 0.115, 140), escape=(0.820, 0.110, 335), number=(0.830, 0.100, 318),
    preproc=(0.770, 0.100, 0), attribute=(0.815, 0.090, 198), tag=(0.790, 0.100, 258),
    hit_bg=(0.36, 0.070, 70), header_bg=(0.27, 0.035, 260), file_bg=(0.26, 0.035, 145),
    error=(0.72, 0.160, 25), error_bg=(0.27, 0.050, 25),
    added=(0.80, 0.120, 145), removed=(0.72, 0.150, 25), changed=(0.80, 0.115, 75),
    caret=(0.84, 0.140, 62), linenum=(0.52, 0.020, 265), linenum_active=(0.80, 0.060, 62),
    keyword_bold=False,
)
DAY = dict(
    name='Pyre Daylight', dark=False,
    bg=(0.990, 0.004, 95), margin=(0.962, 0.006, 95), line=(0.955, 0.014, 250),
    region=(0.970, 0.016, 300), select=(0.865, 0.060, 250), guide=(0.86, 0.010, 265),
    text=(0.235, 0.020, 265), operator=(0.40, 0.030, 265), variable=(0.31, 0.060, 230),
    comment=(0.530, 0.022, 255), comment_doc=(0.505, 0.040, 220), doc_kw=(0.44, 0.085, 220),
    keyword=(0.480, 0.150, 50), type=(0.470, 0.090, 200), function=(0.450, 0.160, 262),
    string=(0.480, 0.135, 142), escape=(0.470, 0.170, 335), number=(0.460, 0.170, 312),
    preproc=(0.470, 0.150, 2), attribute=(0.470, 0.090, 200), tag=(0.450, 0.160, 262),
    hit_bg=(0.93, 0.090, 90), header_bg=(0.91, 0.035, 262), file_bg=(0.93, 0.040, 145),
    error=(0.50, 0.190, 25), error_bg=(0.94, 0.035, 25),
    added=(0.48, 0.140, 145), removed=(0.50, 0.190, 25), changed=(0.52, 0.130, 70),
    caret=(0.52, 0.190, 45), linenum=(0.60, 0.020, 265), linenum_active=(0.40, 0.100, 48),
    keyword_bold=True,
)

BOLD, ITALIC, UNDERLINE = 1, 2, 4

def build(p):
    c = {k: oklch(*v) for k, v in p.items() if isinstance(v, tuple)}
    d = p['dark']
    # ANSI colours (errorlist / terminal output) remapped onto the palette
    c['ansi'] = {
        'BLACK': oklch(0.25, 0.01, 265) if d else oklch(0.25, 0.01, 265),
        'RED': c['error'], 'GREEN': c['string'], 'YELLOW': c['changed'],
        'BLUE': c['function'], 'MAGENTA': c['number'], 'CYAN': c['type'],
        'WHITE': oklch(0.92, 0.01, 85), 'GRAY': c['comment'], 'DARK GRAY': c['operator'],
        'BROWN': c['keyword'], 'BRIGHT RED': oklch(0.78 if d else 0.58, 0.16, 25),
        'BRIGHT GREEN': oklch(0.86 if d else 0.56, 0.14, 142),
        'BRIGHT BLUE': oklch(0.86 if d else 0.55, 0.12, 252),
        'BRIGHT MAGENTA': oklch(0.86 if d else 0.56, 0.13, 308),
        'BRIGHT CYAN': oklch(0.88 if d else 0.56, 0.10, 190),
        'DEFAULT': None,
    }
    return c

# role -> (colour key, font style)
def roles(p):
    kb = BOLD if p['keyword_bold'] else 0
    return {
        'default': ('text', 0), 'operator': ('operator', 0), 'variable': ('variable', 0),
        'comment': ('comment', ITALIC), 'comment_doc': ('comment_doc', ITALIC),
        'doc_kw': ('doc_kw', ITALIC | BOLD),
        'keyword': ('keyword', kb), 'type': ('type', 0), 'function': ('function', 0),
        'string': ('string', 0), 'escape': ('escape', 0), 'number': ('number', 0),
        'preproc': ('preproc', 0), 'regex': ('preproc', 0), 'label': ('preproc', BOLD),
        'attribute': ('attribute', 0), 'tag': ('tag', 0),
        'heading': ('keyword', BOLD), 'strong': ('text', BOLD), 'emph': ('text', ITALIC),
        'link': ('function', UNDERLINE), 'code': ('string', 0), 'quote': ('comment', ITALIC),
        'error': ('error', 0), 'added': ('added', 0), 'removed': ('removed', 0),
        'changed': ('changed', 0), 'strike': ('comment', 0),
    }

# ---------------------------------------------------------------- classification
RULES = [
    (r'^(TAG UNKNOWN|USER TAGS)', 'tag'),
    (r'^ATTRIBUTE UNKNOWN|^USER ATTRIBUTES', 'attribute'),
    (r'COMMENT.*(KEYWORD|KEY\b|TAG)|DOC KEYWORD|DOCUMENTATION (MACRO|HELPER)', 'doc_kw'),
    (r'ERROR|ILLEGAL|GARBAGE|_WRONG|NOT CLOSED|TOO MANY|BAD STRING|STRING EOL|EOL OPEN|EOL NC|LEXICAL', 'error'),
    (r'^DIFF ADDITION$|^ADDED', 'added'),
    (r'^DIFF DELETION$|^DELETED$|^REMOVED', 'removed'),
    (r'^DIFF CHANGED$|^CHANGED$', 'changed'),
    (r'DOC COMMENT|COMMENT DOC|LINE DOC|BLOCK DOC|COMMENT LINE DOC|^POD|#IFDEF DOC|FUNCTION COMMENT|MODULE COMMENT|DSC COMMENT', 'comment_doc'),
    (r'COMMENT|^REM\b|INACTIVE', 'comment'),
    (r'ESCAPE|SPECIAL CHAR|FORMAT IDENTIFIER|GUID IN', 'escape'),
    (r'VAR IN |STRING VAR|INTERPOL|SUBSTITUTION|SERVER-GLOBAL|CLASS VAR|INSTANCE VAR', 'variable'),
    (r'REGEX|REGULAR EXP', 'regex'),
    (r'STRING|CHARACTER|\bCHAR\b|VERBATIM|HEREDOC|HERE (Q|DELIM|STRING|CHARACTER)|QUOTE|TRIPLE|CDATA|BACKTICK|LITERAL STRING|TEMPLATE LIT|^F (TRIPLE|STRING|CHARACTER)', 'string'),
    (r'NUMBER|NUMERIC|\bHEX|BINARY|\bDATE|^TIME|MONEY|CONSTANT|\bBOOL|^NIL$|^ATOM|^SYMBOL$|^PAIR|^TUPLE|^ISSUE|LIFETIME', 'number'),
    (r'PREPROC|MACRO|DIRECTIVE|PRAGMA|DEFINE|IFDEF|DECORATOR|ANNOTATION|^IMPORT|ASP SYMBOL|^ASM$|XML START|XML END|SGML|^PLUGIN$', 'preproc'),
    (r'\bTAG|NODE NAME|^ELEMENT', 'tag'),
    (r'ATTRIBUTE|PROPERTY NAME|^KEY\b|^PARAM|^OPTION|QUALIFIER|OBJECT PROPERTY|VALUE NAME|^COL NAME|^PSEUDO|^EXTENDED_PSEUDO|^LEGACY PSEUDO|^UNKNOWN PSEUDO|^ID$|^CLASS$|^IMPORTANT', 'attribute'),
    (r'TYPE|CLASS|STRUCT|INTERFACE|STD PACKAGE|MODULE NAME|^SELF$|^SUPER$|^INSTANCE$|NAMESPACE|^TABLE|SYSTEM TABLE', 'type'),
    (r'FUNC|METHOD|CMDLET|^COMMAND|^TK COMMAND|SHORT COMMAND|BUILT-?IN|BUILTINS|CALLABLE|PROCEDURE|STORED PROC|DLL FUNCTIONS|CORE API|PLUGIN|DEF NAME|PROTOTYPE|^FILTER$', 'function'),
    (r'^LABEL|REFERENCE \(TO A LABEL|^TARGET$', 'label'),
    (r'^H[1-6]$|^HEADER$|HEADING|^SECTION|SUB ?SECTION|MAIN SECTIONS|^TITLE|^PREFACE$|^FILE HEADER|SEARCH HEADER', 'heading'),
    (r'^EM1|ITALIC|^EMPHASIS', 'emph'),
    (r'^STRONG|^EM2', 'strong'),
    (r'STRIKEOUT', 'strike'),
    (r'^LINK$|^URL|^URI$|^EMAIL|^COMPACT IRI', 'link'),
    (r'^BLOCKQUOTE$', 'quote'),
    (r'^CODE|^CODEBLOCK', 'code'),
    (r'^(USER KEYWORDS?|USER|KEYWORD USER|USER DEFINED|USER DEFINE|USER SCALAR)\s*\d*$', 'user'),
    (r'(KEYWORDS?|WORD|INSTRUCTION|INSTRE)\s*[2-9]$', 'secondary'),
    (r'KEYWORD|INSTRUCTION|^INSTR\b|\bWORD\b|WORDS$|RESERVED|STATEMENT|OPCODE|^CONTROL$|^RETURN$|MODIFIER|MODIFICATORS|DECLARATION|LANGUAGE NATIVE|DEFWORDS|BASE WORD|PREWORD|^ADVERB|^SENT|^GRAMMAR|^MU$|^ALIAS|WHILEDEF|FOREACHDEF|^ENUM', 'keyword'),
    (r'OPERATOR|DELIMITER|PUNCT|BRACE|^SYMBOLS$|^ASSIGN|DIVIS|QUESTION MARK|^ASTERISK|^HRULE|CONTINUATION|^PAREN', 'operator'),
    (r'VARIABLE|^VAR$|SCALAR|^ARRAY|^HASH$|IDENTIFIER[23]|^GLOBAL|INSTANCE VAR|CLASS VAR|ENVIRONMENT|-RATE VARIABLE|^REGISTER|PREDEFINED|^POSITIONAL|^PARAMETER', 'variable'),
    (r'^ULIST|^OLIST', 'keyword'),
    (r'DEFAULT|IDENTIFIER|TEXT|WHITE ?SPACE|^NAME$|^DATA', 'default'),
]
RULES = [(re.compile(r, re.I), role) for r, role in RULES]

# Scintilla / Notepad++ default colours of stylers.model.xml -> role
COLOR_ROLE = {
    '000000': 'default', '0000FF': 'keyword', '808080': 'string', '008000': 'comment',
    'FF0000': 'preproc', '008080': 'type', 'FF8000': 'number', '8000FF': 'type',
    '000080': 'operator', '00007F': 'keyword', '804000': 'preproc', '7F007F': 'string',
    '007F7F': 'number', '007F00': 'comment', '800000': 'preproc', '0080FF': 'function',
    '0080C0': 'function', '007FFF': 'function', '8080FF': 'function', '7F0000': 'keyword',
    'FF8040': 'number', '7F7F00': 'preproc', '808000': 'preproc', '8080C0': 'variable',
}

def hue_role(hexs):
    r, g, b = rgb(hexs)
    mx, mn = max(r, g, b), min(r, g, b)
    if mx - mn < 0.12:
        return 'default' if mx < 0.6 else 'comment'
    if mx == r:
        h = (60 * ((g - b) / (mx - mn))) % 360
    elif mx == g:
        h = 60 * ((b - r) / (mx - mn)) + 120
    else:
        h = 60 * ((r - g) / (mx - mn)) + 240
    for lim, role in ((15, 'preproc'), (50, 'number'), (75, 'preproc'), (165, 'comment'),
                      (200, 'type'), (250, 'keyword'), (290, 'type'), (345, 'string'), (361, 'preproc')):
        if h < lim:
            return role

USER_CYCLE = ['keyword', 'type', 'function', 'number', 'preproc', 'string', 'variable', 'attribute']
SECONDARY = {2: 'type', 3: 'function', 4: 'preproc', 5: 'number', 6: 'variable', 7: 'attribute',
             8: 'string', 9: 'escape'}

SPECIAL = {
    ('searchResult', 'Search Header'): ('function', 'header_bg', BOLD),
    ('searchResult', 'File Header'): ('string', 'file_bg', BOLD),
    ('searchResult', 'Line Number'): ('linenum', 'bg', 0),
    ('searchResult', 'Hit Word'): ('text', 'hit_bg', BOLD),
    ('searchResult', 'Current line background colour'): (None, 'line', None),
}

# Per-language corrections, from reading every lexer's mapping: keys look alike across
# JSON / YAML / TOML / INI / CSS, headers alike across INI / TOML, and a few names the
# generic rules read the wrong way.
OVERRIDE = {
    ('python', 'ATTRIBUTE'): 'default',          # obj.attr: plain, not the type colour
    ('css', 'IDENTIFIER'): 'attribute',          # property names, like JSON keys
    ('css', 'UNKNOWN IDENTIFIER'): 'attribute',
    ('css', 'CLASS'): 'keyword',                 # selectors stand apart from properties
    ('css', 'ID'): 'keyword',
    ('css', 'PSEUDOCLASS'): 'preproc',
    ('css', 'UNKNOWN PSEUDOCLASS'): 'preproc',
    ('css', 'PSEUDOELEMENT'): 'preproc',
    ('css', 'LEGACY PSEUDOELEMENT'): 'preproc',
    ('css', 'MEDIA'): 'preproc',
    ('yaml', 'IDENTIFIER'): 'attribute',         # keys
    ('toml', 'TABLE'): 'heading',                # [table], like an INI [section]
    ('html', 'VALUE'): 'string',                 # unquoted attribute values
    ('perl', 'REGEX SUBSTITUTION'): 'regex',     # s/// and tr///
    ('perl', 'TRANSLATION'): 'regex',
    ('bash', 'PARAM'): 'variable',               # ${...}
    ('batch', 'HIDE SYMBOL'): 'operator',        # the @ of @echo
    ('powershell', 'ALIAS'): 'function',         # ls, cd: commands
    ('php', 'QUESTION MARK'): 'preproc',         # <?php ?>
    ('go', 'PREDECLARED IDENTIFIERS'): 'function',  # len, make, append
    ('gdscript', 'NODEPATH'): 'variable',        # $Node/Path
    ('haskell', 'CAPITAL'): 'type',              # types and constructors
    ('haskell', 'CLASS'): 'type',
    ('haskell', 'MODULE'): 'type',
    ('haskell', 'DATA'): 'type',
    ('txt2tags', 'BLOCKQUOTE'): 'quote',
    ('errorlist', 'GCC Excerpt Error'): 'default',   # quoted source, not an error
    ('errorlist', 'GCC Included-From Error'): 'comment',
    ('registry', 'ADDED KEY'): 'heading',        # an ordinary [HKEY_...] key, like an INI section
    ('nim', 'DECORATORS'): 'comment_doc',        # the Nim lexer styles ## doc comments with it
    ('visualprolog', 'MAJOR'): 'keyword',        # implement, class, clauses
    ('visualprolog', 'MINOR'): 'type',
}
# compiler / tool output lines (file:line: message): blue like a link to jump to, not red,
# since warnings and notes get the same style as errors
ERRORLIST_LOCATION = re.compile(r' Error$|^JAVA Stack Error$')

# styles a lexer draws but stylers.model.xml leaves out, so every theme shows them as plain
# text: added here (FreeBASIC block and doc comments: SCE_B_COMMENTBLOCK .. SCE_B_DOCKEYWORD)
EXTRA_STYLES = {
    'freebasic': [('COMMENT BLOCK', 19, 'comment'), ('DOC LINE', 20, 'comment_doc'),
                  ('DOC BLOCK', 21, 'comment_doc'), ('DOC KEYWORD', 22, 'doc_kw')],
}

def classify(lexer, name, fg):
    up = name.upper()
    if (lexer, name) in OVERRIDE:
        return OVERRIDE[(lexer, name)]
    if lexer == 'errorlist' and ERRORLIST_LOCATION.search(name):
        return 'function'
    if up == 'ENTITY':
        return 'escape'    # &amp; and friends, like escapes in strings
    if lexer == 'diff':
        for pat, role in ((r'ADDED', 'added'), (r'DELETED|REMOVED', 'removed'), (r'CHANGED', 'changed'),
                          (r'HEADER', 'heading'), (r'POSITION', 'number'), (r'COMMAND', 'keyword'),
                          (r'COMMENT', 'comment')):
            if re.search(pat, up):
                return role
    for pat, role in RULES:
        if pat.search(up):
            if role == 'user':
                n = re.search(r'(\d+)', up)
                return USER_CYCLE[(int(n.group(1)) - 1) % len(USER_CYCLE)] if n else 'keyword'
            if role == 'secondary':
                n = int(re.search(r'(\d)\s*$', up).group(1))
                cr = COLOR_ROLE.get(fg.upper()) or hue_role(fg)
                return cr if cr not in ('default', 'keyword', 'comment', 'string') else SECONDARY[n]
            return role
    return COLOR_ROLE.get(fg.upper()) or hue_role(fg)

ANSI_RE = re.compile(r'^(BOLD )?(BLACK|RED|GREEN|YELLOW|BLUE|MAGENTA|CYAN|WHITE|DEFAULT) on (BLACK|RED|GREEN|YELLOW|BLUE|MAGENTA|CYAN|WHITE|DEFAULT)$')
ANSI2_RE = re.compile(r'^ANSI COLOR (.+)$')

# ---------------------------------------------------------------- global styles
def global_styles(p, c):
    d = p['dark']
    # indicator fills (Notepad++ blends them over the text background, so on a light theme they need
    # more colour than their hex suggests: Mark Style 4 at 0.80 nearly vanished in Daylight)
    hi = lambda h, Ld=0.62, Ll=0.76, C=0.13: oklch(Ld if d else Ll, C, h)
    tab = lambda h: oklch(0.38, 0.060, h) if True else None
    g = {
        'Default Style': dict(fg=c['text'], bg=c['bg']),
        'Indent guideline style': dict(fg=c['guide'], bg=c['bg']),
        'Brace highlight style': dict(fg=c['caret'], bg=c['select'], fontStyle=BOLD),
        'Bad brace colour': dict(fg=c['error'], bg=c['error_bg'], fontStyle=BOLD),
        'Current line background colour': dict(bg=c['line']),
        'Selected text colour': dict(bg=c['select'], fg=c['text']),
        'Multi-selected text color': dict(bg=c['select']),
        'Caret colour': dict(fg=c['caret']),
        'Multi-edit carets color': dict(fg=c['function']),
        'Edge colour': dict(fg=c['guide']),
        'Line number margin': dict(fg=c['linenum'], bg=c['margin']),
        'Bookmark margin': dict(bg=c['margin']),
        'Change History margin': dict(bg=c['margin']),
        'Change History modified': dict(fg=c['changed'], bg=c['changed']),
        'Change History revert modified': dict(fg=c['type'], bg=c['type']),
        'Change History revert origin': dict(fg=c['function'], bg=c['function']),
        'Change History saved': dict(fg=c['added'], bg=c['added']),
        'Fold': dict(fg=c['linenum'], bg=c['margin']),
        'Fold active': dict(fg=c['caret']),
        'Fold margin': dict(fg=c['margin'], bg=c['margin']),
        'White space symbol': dict(fg=c['guide']),
        # same word as the selection: a quiet blue, like the selection itself, so it can't be taken
        # for Mark Style 5 (green)
        'Smart Highlighting': dict(bg=hi(255, 0.50, 0.80, 0.08)),
        'Find Mark Style': dict(bg=hi(25, 0.60, 0.78, 0.15)),
        'Find status: Not found': dict(fg=c['error']),
        'Find status: Message': dict(fg=c['function']),
        'Find status: Search end reached': dict(fg=c['added']),
        'Mark Style 1': dict(bg=hi(205)),
        'Mark Style 2': dict(bg=hi(55)),
        'Mark Style 3': dict(bg=hi(95, 0.70, 0.88, 0.14)),
        'Mark Style 4': dict(bg=hi(305, 0.62, 0.72, 0.15)),
        'Mark Style 5': dict(bg=hi(135, 0.55, 0.76, 0.14)),
        'Incremental highlight all': dict(bg=hi(235)),
        'Tags match highlighting': dict(bg=hi(305, 0.50, 0.82, 0.10)),
        'Tags attribute': dict(bg=hi(95, 0.55, 0.88, 0.10)),
        'Active tab focused indicator': dict(fg=c['caret']),
        'Active tab unfocused indicator': dict(fg=oklch(0.55, 0.06, 62) if d else oklch(0.80, 0.06, 55)),
        'Active tab text': dict(fg=c['text']),
        'Inactive tabs': dict(fg=c['linenum'], bg=c['margin']),
        'Tab color 1': dict(bg=oklch(0.93, 0.05, 95)),
        'Tab color 2': dict(bg=oklch(0.93, 0.05, 145)),
        'Tab color 3': dict(bg=oklch(0.92, 0.04, 255)),
        'Tab color 4': dict(bg=oklch(0.92, 0.05, 45)),
        'Tab color 5': dict(bg=oklch(0.92, 0.05, 320)),
        'Tab color dark mode 1': dict(bg=tab(95)),
        'Tab color dark mode 2': dict(bg=tab(145)),
        'Tab color dark mode 3': dict(bg=tab(255)),
        'Tab color dark mode 4': dict(bg=tab(35)),
        'Tab color dark mode 5': dict(bg=tab(320)),
        'URL hovered': dict(fg=c['function']),
        'Document map': dict(fg=c['caret'], bg=c['bg']),
        'EOL custom color': dict(fg=c['guide']),
        'Non-printing characters custom color': dict(fg=c['changed']),
        'Global override': dict(fg=c['text'], bg=c['bg']),
    }
    return g

# ---------------------------------------------------------------- generation
ATTR = lambda name: re.compile(r'(\b' + name + r'=")([^"]*)(")')

def set_attr(line, name, value):
    pat = ATTR(name)
    if pat.search(line):
        return pat.sub(lambda m: m.group(1) + value + m.group(3), line, count=1)
    return line.replace(' />', f' {name}="{value}" />', 1)

def generate(model_text, p, user_font):
    c = build(p)
    R = roles(p)
    out, lexer, report = [], None, {}
    gs = global_styles(p, c)
    for line in model_text.splitlines(keepends=True):
        m = re.search(r'<LexerType name="([^"]*)"', line)
        if m:
            lexer = m.group(1)
        if '<WordsStyle ' in line:
            name = re.search(r'name="([^"]*)"', line).group(1)
            fg0 = (ATTR('fgColor').search(line) or [None, None, '000000'])[2]
            bg0 = (ATTR('bgColor').search(line) or [None, None, 'FFFFFF'])[2].upper()
            fs0 = int((ATTR('fontStyle').search(line) or [None, None, '0'])[2] or 0)
            uname = name.replace('&apos;', "'").replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
            am, am2 = ANSI_RE.match(uname), ANSI2_RE.match(uname.upper())
            if (lexer, uname) in SPECIAL:
                fk, bk, fs = SPECIAL[(lexer, uname)]
                role = 'special'
                line = set_attr(line, 'bgColor', c[bk])
                if fk:
                    line = set_attr(set_attr(line, 'fgColor', c[fk]), 'fontStyle', str(fs))
                report.setdefault(role, []).append(f'{lexer}:{uname}')
                out.append(line)
                continue
            if am:
                fg = c['ansi'][am.group(2)] or c['text']
                bg = c['ansi'][am.group(3)] or c['bg']
                fs, role = (BOLD if am.group(1) else 0), 'ansi'
            elif am2 and am2.group(1) in c['ansi']:
                fg, bg, fs, role = c['ansi'][am2.group(1)], c['bg'], 0, 'ansi'
            else:
                role = classify(lexer, uname, fg0)
                key, fs = R[role]
                fg = c[key]
                if role == 'error' and bg0 != 'FFFFFF':
                    bg = c['error_bg']
                elif role == 'error':
                    bg = c['bg'] if not re.search(r'EOL|NOT CLOSED', uname.upper()) else c['error_bg']
                else:
                    # no tinted band behind embedded PHP / ASP / script: in a plain .php file it
                    # read as a stray highlight; the syntax colours already mark the code
                    bg = c['bg']
            report.setdefault(role, []).append(f'{lexer}:{uname}')
            line = set_attr(set_attr(set_attr(line, 'fgColor', fg), 'bgColor', bg), 'fontStyle', str(fs))
        elif '<WidgetStyle ' in line:
            name = re.search(r'name="([^"]*)"', line).group(1)
            spec = gs.get(name)
            if spec is None:
                print('unmapped global style:', name, file=sys.stderr)
            else:
                if 'fg' in spec:
                    line = set_attr(line, 'fgColor', spec['fg'])
                if 'bg' in spec:
                    line = set_attr(line, 'bgColor', spec['bg'])
                if 'fontStyle' in spec:
                    line = set_attr(line, 'fontStyle', str(spec['fontStyle']))
                if name in ('Default Style', 'Global override') and user_font:
                    line = set_attr(line, 'fontName', user_font)
        elif '</LexerType>' in line and lexer in EXTRA_STYLES:
            eol = line[len(line.rstrip('\r\n')):]
            for sname, sid, role in EXTRA_STYLES[lexer]:
                key, fs = R[role]
                out.append(f'            <WordsStyle name="{sname}" styleID="{sid}" fgColor="{c[key]}" '
                           f'bgColor="{c["bg"]}" fontName="" fontStyle="{fs}" fontSize="" />{eol}')
                report.setdefault(role, []).append(f'{lexer}:{sname}')
        out.append(line)
    return ''.join(out), c, report

def contrast_table(p, c):
    rows = []
    bg = c['bg']
    for k in ('text', 'operator', 'variable', 'comment', 'comment_doc', 'doc_kw', 'keyword', 'type',
              'function', 'string', 'escape', 'number', 'preproc', 'error', 'linenum', 'caret'):
        rows.append((k, c[k], wcag(c[k], bg), apca(c[k], bg), wcag(c[k], bg, 0.10 if not p['dark'] else 0.0),
                     wcag(c[k], c['select']), wcag(c[k], c['line'])))
    return rows

if __name__ == '__main__':
    model = pathlib.Path(sys.argv[1]).read_text(encoding='utf-8')
    outdir = pathlib.Path(sys.argv[2])
    user_font = sys.argv[3] if len(sys.argv) > 3 else ''
    for p in (DAY, NIGHT):
        text, c, report = generate(model, p, user_font)
        (outdir / f"{p['name']}.xml").write_text(text, encoding='utf-8', newline='')
        print(f"\n== {p['name']}  bg #{c['bg']}")
        print(f"{'role':12} {'hex':7} {'WCAG':>6} {'APCA':>6} {'glare10':>8} {'onSel':>6} {'onLine':>6}")
        for k, h, w, a, gl, sel, ln in contrast_table(p, c):
            print(f"{k:12} #{h} {w:6.2f} {a:6.1f} {gl:8.2f} {sel:6.2f} {ln:6.2f}")
        toks = ['keyword', 'type', 'function', 'string', 'number', 'preproc', 'text', 'comment']
        pairs = sorted(((delta_e(c[a], c[b]), a, b) for a, b in itertools.combinations(toks, 2)))[:5]
        print('closest token pairs (dE OK):', ', '.join(f'{a}/{b} {d:.3f}' for d, a, b in pairs))
        if '--roles' in sys.argv:
            for role, items in sorted(report.items()):
                print(f'  {role:12} {len(items):4}  ', '; '.join(items[:400]))
