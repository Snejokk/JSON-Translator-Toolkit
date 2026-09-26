"""Одинаковый выбор реплик при выгрузке и сборке JSON."""
from common import ROOT

ignore = set()
ignore_file = ROOT / "ignore_list.txt"
if ignore_file.exists():
    ignore = set(ignore_file.read_text(encoding="utf-8-sig").splitlines())
    ignore = {line.strip() for line in ignore if line.strip()}


def text_fields(data):
    fields = []
    if isinstance(data, dict):
        for key, value in data.items():
            if key in ignore or isinstance(value, str) and value in ignore:
                continue
            if isinstance(value, str) and value.strip() and key.endswith("text"):
                fields.append((data, key))
            else:
                fields.extend(text_fields(value))
    elif isinstance(data, list):
        for value in data:
            fields.extend(text_fields(value))
    return fields
