"""Реплика в level: [длина UTF-8][текст][нули до 4 байт][ExtraData]."""
import re
import struct

MARKER = b"\x09\x00\x00\x00ExtraData"
MAX_LINE_LEN = 4000


def level_files(folder):
    return sorted(path for path in folder.rglob("*")
                  if path.is_file() and re.fullmatch(r"level\d+", path.name))


def find_lines(data):
    lines = []
    for match in re.finditer(re.escape(MARKER), data):
        end = match.start()
        # Ищем самый длинный подходящий текст перед ExtraData.
        for length in reversed(range(min(MAX_LINE_LEN, end))):
            padding = (-length) % 4
            start = end - padding - length - 4
            if start < 0 or struct.unpack_from("<I", data, start)[0] != length:
                continue
            try:
                text = data[start + 4:start + 4 + length].decode("utf-8")
            except UnicodeDecodeError:
                continue
            if all(char in "\t\n\r" or ord(char) >= 32 for char in text):
                lines.append((start, end, text))
                break
    return lines


def replace_lines(data, translations):
    lines = find_lines(data)
    if len(lines) != len(translations):
        raise ValueError("Число реплик и переводов не совпадает")
    # Замены с конца не сдвигают позиции предыдущих реплик.
    result = bytearray(data)
    for (start, end, old), text in reversed(list(zip(lines, translations))):
        raw = text.encode("utf-8")
        result[start:end] = struct.pack("<I", len(raw)) + raw + b"\x00" * ((-len(raw)) % 4)
    return bytes(result)
