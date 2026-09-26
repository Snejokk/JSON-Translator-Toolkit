"""Пути проекта и формат TXT: одна реплика на строку."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def decode_asset(raw):
    """Decode normal UTF-8 TextAsset and two old Windows-1252 text files."""
    try:
        encoding = "utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8"
        return raw.decode(encoding), encoding
    except UnicodeDecodeError:
        return raw.decode("cp1252"), "cp1252"


def encode_asset(text, encoding):
    try:
        return text.encode(encoding)
    except UnicodeEncodeError:
        # A Russian translation cannot be represented in Windows-1252.
        return text.encode("utf-8")


def escape_line(text):
    return text.replace("\\", "\\\\").replace("\r", "\\r").replace("\n", "\\n")


def unescape_line(text):
    # Читаем пары символов слева направо: \\n и \\\\n имеют разный смысл.
    escapes = {"n": "\n", "r": "\r", "\\": "\\"}
    result = ""
    index = 0
    while index < len(text):
        char = text[index]
        if char == "\\":
            index += 1
            if index == len(text) or text[index] not in escapes:
                raise ValueError("Допустимы только \\n, \\r и \\\\")
            char = escapes[text[index]]
        result += char
        index += 1
    return result


def read_lines(path):
    text = path.read_text(encoding="utf-8-sig")
    if not text:
        return []
    # Убираем только последний перенос. Пустые реплики сохраняем.
    return text.removesuffix("\n").split("\n")


def read_translation(path, count):
    lines = read_lines(path)
    if len(lines) != count:
        raise ValueError(f"{path}: нужно {count} строк, получено {len(lines)}")
    return [unescape_line(line) for line in lines]


def write_lines(path, lines):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(escape_line(line) + "\n" for line in lines)
    path.write_text(text, encoding="utf-8")


def read_game_dir():
    for line in (ROOT / "GameDir.txt").read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            path = Path(os.path.expandvars(line)).expanduser()
            if path.is_dir():
                return path
            raise SystemExit(f"Папка игры не найдена: {path}")
    raise SystemExit("Впиши путь к игре в GameDir.txt")
