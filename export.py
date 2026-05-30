import json
import os

input_dir = './Files/Original'
output_dir = './Files/OriginalStringOnly'
os.makedirs(output_dir, exist_ok=True)

# Загружаем игнор-лист
ignore_list = set()
if os.path.exists('ignore_list.txt'):
    with open('ignore_list.txt', 'r', encoding='utf-8') as f:
        ignore_list = {line.strip() for line in f if line.strip()}

def extract(d, f):
    if isinstance(d, dict):
        for k, v in d.items():
            # Пропускаем если ключ в игнор-листе
            if k in ignore_list:
                continue
            # Пропускаем если значение - строка и она в игнор-листе
            if isinstance(v, str) and v in ignore_list:
                continue
            if isinstance(v, str) and v.strip():
                f.write(f"{v}\n")
            elif isinstance(v, (dict, list)):
                extract(v, f)
    elif isinstance(d, list):
        for item in d:
            if isinstance(item, str) and item in ignore_list:
                continue
            if isinstance(item, (dict, list)):
                extract(item, f)

for filename in os.listdir(input_dir):
    if filename.endswith('.txt'):
        with open(os.path.join(input_dir, filename), 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
        with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
            extract(data, f)

print("Экспорт завершен. Технический мусор пропущен.")
