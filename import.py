import json
import os

input_dir = './Files/TxtFolder'
trans_dir = './Files/TxtFolderTranslated'
output_dir = './Files/TxtFolderReady'
os.makedirs(output_dir, exist_ok=True)

# Загружаем игнор-лист
ignore_list = set()
if os.path.exists('ignore_list.txt'):
    with open('ignore_list.txt', 'r', encoding='utf-8') as f:
        ignore_list = {line.strip() for line in f if line.strip()}

for filename in os.listdir(input_dir):
    if filename.endswith('.txt'):
        with open(os.path.join(input_dir, filename), 'r', encoding='utf-8') as f:
            data = json.load(f)

        trans_filepath = os.path.join(trans_dir, filename)
        if os.path.exists(trans_filepath):
            with open(trans_filepath, 'r', encoding='utf-8') as f:
                translated_lines = [line.strip() for line in f if line.strip()]

            idx = [0]
            def inject(d):
                if isinstance(d, dict):
                    for k, v in d.items():
                        # Пропускаем по той же логике, что и при экспорте
                        if k in ignore_list or v in ignore_list:
                            continue
                        if isinstance(v, str) and v.strip():
                            if idx[0] < len(translated_lines):
                                d[k] = translated_lines[idx[0]]
                                idx[0] += 1
                        elif isinstance(v, (dict, list)):
                            inject(v)
                elif isinstance(d, list):
                    for item in d:
                        inject(item)

            inject(data)
            with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
                print(f"[ОБРАБОТАН] {filename}")
