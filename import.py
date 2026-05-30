import json
import os

# --- ПУТИ ---
input_dir = './Files/Original'
trans_dir = './Files/ModifiedStringOnly'
base_output_folder = './Files/Output'
base_output_name = 'ModifiedStringOnly'

# Логика создания папок: TxtFolderReady_1, _2 и т.д.
existing_folders = [FolderName for FolderName in os.listdir(base_output_folder) if FolderName.startswith(base_output_name)]
new_folder_index = len(existing_folders) + 1
output_dir = os.path.join(base_output_folder, f"{base_output_name}_{new_folder_index}")
os.makedirs(output_dir, exist_ok=True)
print(f"Результат будет сохранен в: {output_dir}")

# --- ЗАГРУЗКА ИГНОР-ЛИСТА ---
ignore_list = set()
if os.path.exists('ignore_list.txt'):
    with open('ignore_list.txt', 'r', encoding='utf-8') as File:
        ignore_list = {line.strip() for line in File if line.strip()}

# --- ОСНОВНОЙ ЦИКЛ ---
files = [File for File in os.listdir(input_dir) if File.endswith('.txt')]

for i, filename in enumerate(files, 1):
    input_filepath = os.path.join(input_dir, filename)
    trans_filepath = os.path.join(trans_dir, filename)
    output_filepath = os.path.join(output_dir, filename)

    print(f"[{i}/{len(files)}] Обработка: {filename}")

    try:
        with open(input_filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                continue
            data = json.loads(content)

        if os.path.exists(trans_filepath):
            with open(trans_filepath, 'r', encoding='utf-8') as f:
                translated_lines = [line.strip() for line in f if line.strip()]

            idx = [0]

            def inject(d):
                if isinstance(d, dict):
                    for k, v in d.items():
                        # Пропускаем если ключ в игнор-листе
                        if k in ignore_list:
                            continue
                        # Пропускаем если значение - строка и она в игнор-листе
                        # Счётчик НЕ двигаем — экспорт тоже её пропустил
                        if isinstance(v, str) and v in ignore_list:
                            continue
                        # Подставляем перевод
                        if isinstance(v, str) and v.strip():
                            if idx[0] < len(translated_lines):
                                d[k] = translated_lines[idx[0]]
                                idx[0] += 1
                        # Рекурсия для вложенных объектов
                        elif isinstance(v, (dict, list)):
                            inject(v)
                elif isinstance(d, list):
                    for item in d:
                        if isinstance(item, str) and item in ignore_list:
                            continue
                        if isinstance(item, (dict, list)):
                            inject(item)

            inject(data)

        with open(output_filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

    except Exception as e:
        print(f"!!! ОШИБКА в файле {filename}: {e}")

print("\nГотово! Все файлы собраны.")
