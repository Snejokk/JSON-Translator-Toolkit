import json
import os

input_dir = './TxtFolder'
output_dir = './TranslationFiles'
os.makedirs(output_dir, exist_ok=True)

for filename in os.listdir(input_dir):
    if filename.endswith('.txt'):
        filepath = os.path.join(input_dir, filename)
        try:
            # encoding='utf-8-sig' автоматически убирает BOM (тот самый "мусор" в начале)
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                content = f.read().strip()
                if not content: # Пропускаем пустые файлы
                    continue
                data = json.loads(content)

            with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
                def extract(d):
                    if isinstance(d, dict):
                        for k, v in d.items():
                            if isinstance(v, str) and v.strip():
                                f.write(f"{v}\n")
                            elif isinstance(v, (dict, list)):
                                extract(v)
                    elif isinstance(d, list):
                        for item in d:
                            extract(item)
                extract(data)
        except Exception as e:
            print(f"!!! ОШИБКА в файле {filename}: {e}")

print("Готово! Проверьте папку TranslationFiles.")
