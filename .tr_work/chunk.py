import json, re, pathlib
order = json.load(open('unique.json'))
def auto_keep(s):
    if re.fullmatch(r';[^;]*;{5}\d+;;', s): return True
    if 'Lorem ipsum' in s or 'consectetur adipiscing' in s: return True
    if re.fullmatch(r'\d{1,2}/\d{1,2}/\d{2,4}.*', s): return True
    return False
todo = [s for s in order if not auto_keep(s)]
MAXC, MAXL = 11000, 220
chunks, cur, curc = [], [], 0
for s in todo:
    if cur and (curc + len(s) > MAXC or len(cur) >= MAXL):
        chunks.append(cur); cur, curc = [], 0
    cur.append(s); curc += len(s)
if cur: chunks.append(cur)
d = pathlib.Path('chunks'); d.mkdir(exist_ok=True)
idx = 0
for n, ch in enumerate(chunks, 1):
    lines = []
    for s in ch:
        idx += 1; lines.append(f'{idx}\t{s}')
    (d/f'in_{n:03d}.tsv').write_text('\n'.join(lines)+'\n', encoding='utf-8')
json.dump(todo, open('todo.json','w'), ensure_ascii=False)
json.dump(len(chunks), open('nchunks.json','w'))
print('на перевод:', len(todo), 'чанков:', len(chunks))
