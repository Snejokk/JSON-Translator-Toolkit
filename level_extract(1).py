"""Выгрузить реплики перед ExtraData из Level_Original."""
import UnityPy
from common import ROOT, write_lines
from level_common import find_lines, level_files

input_dir = ROOT / "Level_Original"
output_dir = ROOT / "Files/LevelOriginalStringOnly"
if not input_dir.is_dir():
    raise SystemExit(f"Положи level-файлы в {input_dir}")

for path in level_files(input_dir):
    env = UnityPy.load(str(path))
    lines = []
    for obj in env.objects:
        if obj.type.name == "MonoBehaviour":
            for start, end, text in find_lines(obj.get_raw_data()):
                lines.append(text)
    output = output_dir / path.relative_to(input_dir).with_suffix(".txt")
    write_lines(output, lines)
    print(f"{path.name}: {len(lines)} реплик")
