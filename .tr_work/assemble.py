import json, re, sys, pathlib
BASE = pathlib.Path('/home/ssdm2/Проекты/JSON-Translator-Toolkit/Files')
HERE = pathlib.Path(__file__).resolve().parent
PAIRS = [('OriginalStringOnly','ModifiedStringOnly'),
         ('LevelOriginalStringOnly','LevelModifiedStringOnly'),
         ('TTOriginalStringOnly','TTModifiedStringOnly')]
def is_service(s): return not any(c.isalpha() for c in s)
def is_ru(s): return bool(re.search(r'[А-Яа-яЁё]', s))
todo = json.load(open(HERE/'todo.json'))
n_chunks = json.load(open(HERE/'nchunks.json'))
tr, missing = {}, []
for n in range(1, n_chunks+1):
    p = HERE/'chunks'/f'out_{n:03d}.tsv'
    if not p.exists(): missing.append(n); continue
    for raw in p.read_text(encoding='utf-8').split('\n'):
        if not raw: continue
        idx, _, txt = raw.partition('\t')
        tr[int(idx)] = txt
if missing: sys.exit(f'нет переводов для чанков: {missing}')
mapping = {}
for i, src in enumerate(todo, 1):
    if i not in tr: sys.exit(f'в выводе нет строки {i}')
    mapping[src] = tr[i]
for src_dir, dst_dir in PAIRS:
    nf = nt = nk = 0
    for p in sorted((BASE/src_dir).rglob('*.txt')):
        text = p.read_text(encoding='utf-8')
        lines = text.split('\n')
        trailing = lines.pop() if lines and lines[-1] == '' else None
        out = []
        for line in lines:
            if not line.strip() or is_service(line) or is_ru(line) or line not in mapping:
                out.append(line); nk += 1
            else:
                out.append(mapping[line]); nt += 1
        dst = BASE/dst_dir/p.relative_to(BASE/src_dir)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text('\n'.join(out) + ('\n' if trailing is not None else ''), encoding='utf-8')
        nf += 1
    print(f'{dst_dir}: файлов={nf} переведено={nt} без изменений={nk}')
