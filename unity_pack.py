"""Вставить готовые TextAsset из Files/Output/Ready в Unity-файлы."""
import UnityPy
from common import ROOT

input_dir = ROOT / "Unity_Original"
text_dir = ROOT / "Files/Output/Ready"
output_dir = ROOT / "Unity_Modded"
if not text_dir.is_dir():
    raise SystemExit("Сначала запусти import.py")

for path in sorted(input_dir.rglob("*")):
    if not path.is_file() or path.name.startswith("."):
        continue
    env = UnityPy.load(str(path))
    changed = False
    for obj in env.objects:
        if obj.type.name != "TextAsset":
            continue
        asset = obj.read()
        translation = text_dir / (asset.m_Name + ".txt")
        if translation.is_file():
            asset.m_Script = translation.read_bytes().decode("utf-8", "surrogateescape")
            asset.save()
            changed = True
    if changed:
        output = output_dir / path.relative_to(input_dir)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(env.file.save())
        print(f"Собран: {output}")
