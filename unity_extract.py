"""Выгрузить TextAsset из Unity-файлов."""
import UnityPy
from common import ROOT

input_dir = ROOT / "Unity_Original"
output_dir = ROOT / "Files/Original"
output_dir.mkdir(parents=True, exist_ok=True)

for path in sorted(input_dir.rglob("*")):
    if not path.is_file() or path.name.startswith("."):
        continue
    env = UnityPy.load(str(path))
    for obj in env.objects:
        if obj.type.name != "TextAsset":
            continue
        asset = obj.read()
        output = output_dir / (asset.m_Name + ".txt")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(asset.m_Script.encode("utf-8", "surrogateescape"))
        print(f"Извлечён: {output.name}")
