import json, re, pathlib
BASE = pathlib.Path('/home/ssdm2/Проекты/JSON-Translator-Toolkit/Files')
SRC = [('assets','OriginalStringOnly'), ('level','LevelOriginalStringOnly'), ('tt','TTOriginalStringOnly')]
def is_service(s): return not any(c.isalpha() for c in s)
def is_ru(s): return bool(re.search(r'[А-Яа-яЁё]', s))
seen, order = set(), []
for tag, d in SRC:
    for p in sorted((BASE/d).rglob('*.txt')):
        for line in p.read_text(encoding='utf-8').split('\n'):
            if not line.strip() or is_service(line) or is_ru(line) or line in seen: continue
            seen.add(line); order.append(line)
json.dump(order, open('unique.json','w'), ensure_ascii=False)
print('уникальных к переводу:', len(order))
