import os
import UnityPy

# --- ПУТИ ---
unity_input_dir = './Unity_Original' # Папка, куда нужно положить оригинальные файлы Unity (bundles, .assets)
txt_output_dir = './Files/TxtFolder' # Сюда выгрузятся файлы .txt (для твоих скриптов)

os.makedirs(unity_input_dir, exist_ok=True)
os.makedirs(txt_output_dir, exist_ok=True)

print(f"Поиск Unity-файлов в папке: {unity_input_dir}")

files_extracted = 0

# Проходим по всем файлам в папке с Unity-ресурсами
for root, dirs, files in os.walk(unity_input_dir):
    for filename in files:
        file_path = os.path.join(root, filename)

        try:
            # Загружаем Unity-файл (архив, бандл или .assets)
            env = UnityPy.load(file_path)

            # Проходим по всем объектам внутри
            for obj in env.objects:
                if obj.type.name == "TextAsset":
                    data = obj.read()

                    # Имя файла из ассета + .txt
                    asset_name = f"{data.name}.txt"
                    out_filepath = os.path.join(txt_output_dir, asset_name)

                    # Сохраняем "сырые" байты, чтобы не сломать кодировку JSON
                    with open(out_filepath, "wb") as f:
                        f.write(bytes(data.script))

                    print(f"Экспортирован TextAsset: {asset_name} (из {filename})")
                    files_extracted += 1

        except Exception as e:
            print(f"Пропущен файл {filename} (Не является файлом Unity или ошибка: {e})")

print(f"\nВыгрузка из Unity завершена! Извлечено файлов: {files_extracted}")
print(f"Теперь можно запускать твой export.py")
