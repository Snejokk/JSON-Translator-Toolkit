"""Выгрузить JSON-реплики и обычный текст для перевода."""
import json
from common import ROOT, decode_asset, write_lines
from json_common import text_fields

input_dir = ROOT / "Files/Original"
output_dir = ROOT / "Files/OriginalStringOnly"

for path in sorted(input_dir.glob("*.txt")):
    output = output_dir / path.name
    output.unlink(missing_ok=True)
    raw = path.read_bytes()
    text, encoding = decode_asset(raw)
    try:
        data = json.loads(text)
    except ValueError:
        lines = text.replace("\r\n", "\n").replace("\r", "\n").splitlines()
        write_lines(output, lines)
        print(f"{path.name}: {len(lines)} строк обычного текста")
        continue
    lines = [container[key] for container, key in text_fields(data)]
    write_lines(output, lines)
    print(f"{path.name}: {len(lines)} реплик")
