"""Выгрузить текстовые поля уровней через схемы типов."""
from common import ROOT, read_game_dir, write_lines
from level_common import level_files
from tt_common import data_dir, load_level, read_objects

input_dir = data_dir(read_game_dir())
output_dir = ROOT / "Files/TTOriginalStringOnly"

for path in level_files(input_dir):
    env = load_level(path)
    lines = []
    for obj, tree, fields in read_objects(env):
        if tree is None:
            lines.extend(text for start, end, text in fields)
        else:
            lines.extend(container[key] for container, key in fields)
    output = output_dir / path.relative_to(input_dir).with_suffix(".txt")
    write_lines(output, lines)
    print(f"{path.name}: {len(lines)} строк")
