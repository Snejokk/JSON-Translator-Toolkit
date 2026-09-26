"""Вставить переводы реплик в level-файлы."""
import UnityPy
from common import ROOT, read_translation
from level_common import find_lines, level_files, replace_lines

input_dir = ROOT / "Level_Original"
translation_dir = ROOT / "Files/LevelModifiedStringOnly"
output_dir = ROOT / "Level_Modded"
if not input_dir.is_dir() or not translation_dir.is_dir():
    raise SystemExit("Нужны Level_Original и Files/LevelModifiedStringOnly")

for path in level_files(input_dir):
    relative = path.relative_to(input_dir)
    translation = translation_dir / relative.with_suffix(".txt")
    if not translation.exists():
        continue
    output = output_dir / relative
    # Сохраняем правки tt_pack, если этот файл уже собран.
    source = output if output.exists() else path
    env = UnityPy.load(str(source))
    objects = []
    count = 0
    for obj in env.objects:
        if obj.type.name == "MonoBehaviour":
            data = obj.get_raw_data()
            size = len(find_lines(data))
            if size:
                objects.append((obj, data, size))
                count += size
    lines = read_translation(translation, count)
    index = 0
    for obj, data, size in objects:
        obj.set_raw_data(replace_lines(data, lines[index:index + size]))
        index += size
    output.parent.mkdir(parents=True, exist_ok=True)
    # Сначала собираем байты, затем открываем файл для записи.
    data = env.file.save()
    output.write_bytes(data)
    print(f"Собран: {relative}, реплик: {count}")
