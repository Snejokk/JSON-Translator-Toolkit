import json
import os
import shutil

# Папка с оригиналами
input_dir = './TxtFolder'
# Папка с вашими переводами
trans_dir = './TxtFolderTranslated'
# НОВАЯ ПАПКА для готовых файлов
output_dir = './TxtFolderReady'

# Создаем новую папку, если ее нет
os.makedirs(output_dir, exist_ok=True)

print(f"Начинаем сборку! Готовые файлы будут сохранены в: {output_dir}\n")

for filename in os.listdir(input_dir):
    if filename.endswith('.txt'):
        input_filepath = os.path.join(input_dir, filename)
        trans_filepath = os.path.join(trans_dir, filename)
        output_filepath = os.path.join(output_dir, filename)

        try:
            # Читаем оригинальный JSON
            with open(input_filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Если есть перевод — вставляем его
            if os.path.exists(trans_filepath):
                with open(trans_filepath, 'r', encoding='utf-8') as f:
                    translated_lines = [line.strip() for line in f if line.strip()]

                idx = [0]
                def inject(d):
                    for k, v in d.items():
                        if isinstance(v, str) and v.strip():
                            if idx[0] < len(translated_lines):
                                d[k] = translated_lines[idx[0]]
                                idx[0] += 1
                        elif isinstance(v, dict):
                            inject(v)

                inject(data)
                print(f"[ПЕРЕВЕДЕН] {filename}")

            # Сохраняем результат в НОВУЮ папку
            with open(output_filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

        except json.decoder.JSONDecodeError:
            # Если файл не JSON (какие-то системные тексты), просто копируем его как есть
            shutil.copy(input_filepath, output_filepath)
        except Exception as e:
            print(f"Ошибка с файлом {filename}: {e}")

print("\nГотово! Все 106 файлов собраны в папке TxtFolderReady.")
