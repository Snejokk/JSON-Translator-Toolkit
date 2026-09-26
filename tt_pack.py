"""Вставить переводы текстовых полей через схемы типов."""
from common import ROOT, read_game_dir, read_translation
from level_common import level_files
from tt_common import data_dir, load_level, read_objects, replace_raw_strings

input_dir = data_dir(read_game_dir())
translation_dir = ROOT / "Files/TTModifiedStringOnly"
output_dir = ROOT / "Level_Modded"
if not translation_dir.is_dir():
    raise SystemExit(f"Нет перевода: {translation_dir}")

for path in level_files(input_dir):
    relative = path.relative_to(input_dir)
    translation = translation_dir / relative.with_suffix(".txt")
    if not translation.exists():
        print(f"{relative}: перевода нет, пропуск")
        continue
    output = output_dir / relative
    # Сохраняем реплики, уже собранные level_pack.
    source = output if output.exists() else path
    env = load_level(source)
    objects = read_objects(env)
    count = sum(len(fields) for obj, tree, fields in objects)
    try:
        lines = read_translation(translation, count)
    except ValueError as error:
        # Один плохой файл не должен ронять весь прогон.
        print(f"!!! {error}. Пропускаю файл.")
        continue
    index = 0
    changed = False
    for obj, tree, fields in objects:
        if tree is None:
            chunk = lines[index:index + len(fields)]
            index += len(fields)
            if any(old != new for (start, end, old), new in zip(fields, chunk)):
                obj.set_raw_data(replace_raw_strings(obj.get_raw_data(), fields, chunk))
                changed = True
            continue
        edited = False
        for container, key in fields:
            if container[key] != lines[index]:
                container[key] = lines[index]
                edited = True
            index += 1
        # Пересобираем только изменённые объекты.
        if edited:
            obj.save_typetree(tree)
            changed = True
    if not changed:
        print(f"{relative}: изменений нет")
        continue
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(env.file.save())
    print(f"Собран: {relative}, строк: {count}")
