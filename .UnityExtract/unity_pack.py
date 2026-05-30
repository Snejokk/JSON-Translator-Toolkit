import os
import UnityPy

# --- ПУТИ ---
unity_input_dir = './Unity_Original'     # Откуда берем оригиналы Unity
unity_output_dir = './Unity_Modded'      # Куда сохраняем запакованные файлы с русификатором
base_folder = './Files'
base_output_name = 'TxtFolderReady'

os.makedirs(unity_output_dir, exist_ok=True)

# Автоматически находим последнюю папку TxtFolderReady_X, которую создал твой import.py
existing_folders = [d for d in os.listdir(base_folder) if d.startswith(base_output_name)]
if not existing_folders:
    print(f"ОШИБКА: Не найдено ни одной папки {base_output_name} в {base_folder}!")
    exit(1)

# Сортируем папки по номеру на конце, чтобы взять самую свежую
existing_folders.sort(key=lambda x: int(x.split('_')[-1]) if '_' in x else 0)
latest_txt_dir = os.path.join(base_folder, existing_folders[-1])

print(f"Берем готовые переведенные тексты из: {latest_txt_dir}")
print("Начинаю запаковку в Unity...\n")

files_modified = 0

# Проходим по оригинальным Unity файлам
for root, dirs, files in os.walk(unity_input_dir):
    for filename in files:
        input_filepath = os.path.join(root, filename)
        output_filepath = os.path.join(unity_output_dir, filename)

        try:
            env = UnityPy.load(input_filepath)
            is_modified_bundle = False

            for obj in env.objects:
                if obj.type.name == "TextAsset":
                    data = obj.read()

                    # Ищем соответствующий .txt файл в твоей последней папке
                    target_txt_name = f"{data.name}.txt"
                    target_txt_path = os.path.join(latest_txt_dir, target_txt_name)

                    if os.path.exists(target_txt_path):
                        # Читаем новый переведенный файл как байты
                        with open(target_txt_path, "rb") as f:
                            new_script_bytes = f.read()

                        # Заменяем содержимое ассета
                        data.script = new_script_bytes
                        data.save()

                        print(f"Заменен TextAsset: {data.name} (в {filename})")
                        is_modified_bundle = True
                        files_modified += 1

            # Если хотя бы один текстовый файл внутри бандла был заменен, пересобираем Unity-файл
            if is_modified_bundle:
                with open(output_filepath, "wb") as f:
                    f.write(env.file.save())
                print(f"-> Файл Unity сохранен: {output_filepath}\n")

        except Exception as e:
            print(f"Ошибка при обработке {filename}: {e}")

print(f"Готово! Заменено TextAsset'ов: {files_modified}.")
print(f"Модифицированные файлы игры лежат в папке {unity_output_dir}")
