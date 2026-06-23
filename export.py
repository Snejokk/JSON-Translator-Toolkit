import json
import os

input_dir = './Files/Original'
output_dir = './Files/OriginalStringOnly'
os.makedirs(output_dir, exist_ok=True)

# Загружаем игнор-лист (необязателен — основная фильтрация идёт по ключу *text)
ignore_list = set()
if os.path.exists('ignore_list.txt'):
    with open('ignore_list.txt', 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                ignore_list.add(line.strip())

def extract(d, f):
    if isinstance(d, dict):
        for k, v in d.items():
            if k in ignore_list:
                continue
            if isinstance(v, str) and v in ignore_list:
                continue
            # Выгружаем только реплики: ключ оканчивается на "text"
            if isinstance(v, str) and v.strip() and k.endswith("text"):
                # Экранируем внутренние переносы, чтобы одна реплика = одна строка
                f.write(v.replace("\\", "\\\\").replace("\r", "\\r").replace("\n", "\\n") + "\n")
            elif isinstance(v, (dict, list)):
                extract(v, f)
    elif isinstance(d, list):
        # У строк в списках нет ключа — текста тут нет, только рекурсия вглубь
        for item in d:
            if isinstance(item, (dict, list)):
                extract(item, f)

ok = 0
skipped = 0
for filename in os.listdir(input_dir):
    if not filename.endswith('.txt'):
        continue
    path = os.path.join(input_dir, filename)
    try:
        with open(path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError):
        print(f"Пропущен (не JSON): {filename}")
        skipped += 1
        continue

    with open(os.path.join(output_dir, filename), 'w', encoding='utf-8', newline='') as f:
        extract(data, f)
    ok += 1

print(f"\nЭкспорт завершен. Обработано: {ok}, пропущено не-JSON: {skipped}")
