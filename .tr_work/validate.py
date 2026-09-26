import re, sys, pathlib
BASE = pathlib.Path('/home/ssdm2/Проекты/JSON-Translator-Toolkit/Files')
PAIRS = [('OriginalStringOnly','ModifiedStringOnly'),
         ('LevelOriginalStringOnly','LevelModifiedStringOnly'),
         ('TTOriginalStringOnly','TTModifiedStringOnly')]
def read_lines(p):
    t = p.read_text(encoding='utf-8-sig')
    return [] if not t else t.removesuffix('\n').split('\n')
def unescape(text):
    esc = {'n':'\n','r':'\r','\\':'\\'}; res, i = '', 0
    while i < len(text):
        c = text[i]
        if c == '\\':
            i += 1
            if i == len(text) or text[i] not in esc: raise ValueError
            c = esc[text[i]]
        res += c; i += 1
    return res
total = 0
for src_dir, dst_dir in PAIRS:
    errors = []
    for p in sorted((BASE/src_dir).rglob('*.txt')):
        name = p.relative_to(BASE/src_dir); src = read_lines(p)
        if not src: continue
        q = BASE/dst_dir/name
        if not q.exists(): errors.append(f'{name}: нет перевода'); continue
        dst = read_lines(q)
        if len(src) != len(dst):
            errors.append(f'{name}: строк {len(src)} -> {len(dst)}'); continue
        for n, (o, t) in enumerate(zip(src, dst), 1):
            try: o2, t2 = unescape(o), unescape(t)
            except ValueError: errors.append(f'{name}:{n}: неверное экранирование'); continue
            bad = ''
            if o2.strip() and not t2.strip(): bad = 'пустой перевод'
            elif not any(c.isalpha() for c in o2) and o2 != t2: bad = 'изменена служебная строка'
            elif o2.count('\n') != t2.count('\n') or o2.count('\r') != t2.count('\r'): bad = 'изменилось число переносов'
            for pat in (r'<[^<>]+>', r'\{[^{}]+\}', r'\[[^\[\]]+\]'):
                if sorted(re.findall(pat, o2)) != sorted(re.findall(pat, t2)): bad = 'изменены теги/плейсхолдеры'
            if bad: errors.append(f'{name}:{n}: {bad}')
    print(f'--- {dst_dir}: ошибок {len(errors)}')
    for e in errors[:25]: print('   ', e)
    if len(errors) > 25: print(f'    ... ещё {len(errors)-25}')
    total += len(errors)
print('ИТОГО ошибок:', total)
sys.exit(1 if total else 0)
