"""Старый вариант: заменить все непустые строки в словарях JSON."""
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
input_dir = root / "TxtFolder"
translation_dir = root / "TxtFolderTranslated"
output_dir = root / "TxtFolderReady"
output_dir.mkdir(parents=True, exist_ok=True)


def text_fields(data):
    fields = []
    for key, value in data.items():
        if isinstance(value, str) and value.strip():
            fields.append((data, key))
        elif isinstance(value, dict):
            fields.extend(text_fields(value))
    return fields


for path in sorted(input_dir.glob("*.txt")):
    output = output_dir / path.name
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (ValueError, UnicodeError):
        output.write_bytes(path.read_bytes())
        continue
    translation = translation_dir / path.name
    if translation.exists():
        fields = text_fields(data)
        lines = translation.read_text(encoding="utf-8-sig").splitlines()
        if len(fields) != len(lines):
            raise ValueError(f"{path.name}: число строк перевода не совпадает")
        for (container, key), text in zip(fields, lines):
            container[key] = text
    output.write_text(json.dumps(data, ensure_ascii=False, indent=4), encoding="utf-8")
    print(f"Собран: {path.name}")
