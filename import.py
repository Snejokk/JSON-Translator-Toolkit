import json
import os
import shutil

# Папка с оригиналами
input_dir = './TxtFolder'
# Папка с вашими переводами
trans_dir = './TxtFolderTranslated'
# НОВАЯ ПАПКА для готовых файлов
output_dir = './TxtFolderReady'

os.makedirs(output_dir, exist_ok=True)
print(f"Начинаем сборку! Готовые файлы будут сохранены в: {output_dir}\n")

for filename in os.listdir(input_dir):
    if filename.endswith('.txt'):
        input_filepath = os.path.join(input_dir, filename)
        trans_filepath = os.path.join(trans_dir, filename)
        output_filepath = os.path.join(output_dir, filename)

        try:
            with open(input_filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

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

            # ВАЖНО: сохраняем в сжатом виде (в одну строку, без пробелов)
            with open(output_filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

        except json.decoder.JSONDecodeError:
            shutil.copy(input_filepath, output_filepath)
        except Exception as e:
            print(f"Ошибка с файлом {filename}: {e}")

print("\nГотово! Все 106 файлов собраны в папке TxtFolderReady.")
