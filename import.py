"""Вставить переведённые реплики обратно в JSON."""
import json
from common import ROOT, decode_asset, encode_asset, read_translation
from json_common import text_fields

input_dir = ROOT / "Files/Original"
translation_dir = ROOT / "Files/ModifiedStringOnly"
output_dir = ROOT / "Files/Output/Ready"
output_dir.mkdir(parents=True, exist_ok=True)

for path in sorted(input_dir.glob("*.txt")):
    output = output_dir / path.name
    # Старый результат не должен попасть в сборку, если новый перевод ошибочен.
    output.unlink(missing_ok=True)
    raw = path.read_bytes()
    text, encoding = decode_asset(raw)
    try:
        data = json.loads(text)
    except ValueError:
        translation = translation_dir / path.name
        if not translation.exists():
            output.write_bytes(raw)
            continue
        original = text.replace("\r\n", "\n").replace("\r", "\n")
        lines = read_translation(translation, len(original.splitlines()))
        newline = "\r\n" if "\r\n" in text else "\r" if "\r" in text else "\n"
        rebuilt = newline.join(lines)
        if text.endswith(("\n", "\r")):
            rebuilt += newline
        output.write_bytes(encode_asset(rebuilt, encoding))
        print(f"Собран обычный текст: {path.name}")
        continue
    translation = translation_dir / path.name
    if translation.exists():
        fields = text_fields(data)
        lines = read_translation(translation, len(fields))
        for (container, key), text in zip(fields, lines):
            container[key] = text
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Собран: {path.name}")
