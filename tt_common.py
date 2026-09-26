"""Чтение полей MonoBehaviour по схемам из DummyDll."""
import re
import struct
from collections import Counter

import UnityPy
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator
from common import ROOT, read_game_dir

generator = None
include = []
exclude = set()
for line in (ROOT / "tt_fields.txt").read_text(encoding="utf-8-sig").splitlines():
    if line.startswith("+"):
        include.append(line[1:].strip().lower())
    elif line.startswith("-"):
        exclude.add(line[1:].strip())


def data_dir(game):
    for path in sorted(game.glob("*_Data")):
        if path.is_dir():
            return path
    raise SystemExit(f"В {game} нет папки *_Data")


def load_level(path):
    global generator
    game = read_game_dir()
    env = UnityPy.load(str(path))
    env.path = str(data_dir(game))
    dll_dir = ROOT / "Dumps" / game.name / "DummyDll"
    if not dll_dir.is_dir():
        raise SystemExit("Сначала запусти collect_dumps.py")
    if generator is None:
        version = next(iter(env.files.values())).unity_version
        generator = TypeTreeGenerator(version)
        generator.load_local_dll_folder(str(dll_dir))
    env.typetree_generator = generator
    return env


def pick_field(name, value):
    if name in exclude or not any(word in name.lower() for word in include):
        return False
    value = value.strip()
    if not value or len(value) > 20000:
        return False
    if re.fullmatch(r"[0-9a-f]{16,}", value) or "/" in value and " " not in value:
        return False
    if re.fullmatch(r"[\w.<>+]+, [\w.]+", value):
        return False
    return any(char.isalpha() for char in value)


def text_fields(node, name=""):
    fields = []
    if isinstance(node, dict):
        items = node.items()
    elif isinstance(node, list):
        items = enumerate(node)
    else:
        return fields
    for key, value in items:
        field_name = key if isinstance(node, dict) else name
        if isinstance(value, str) and pick_field(field_name, value):
            fields.append((node, key))
        else:
            fields.extend(text_fields(value, field_name))
    return fields


def raw_strings(data):
    """Find ordinary Unity strings without knowing the class schema."""
    fields = []
    for start in range(0, len(data) - 4, 4):
        size = struct.unpack_from("<I", data, start)[0]
        if not 2 <= size <= min(20000, len(data) - start - 4):
            continue
        end = start + 4 + size
        try:
            value = data[start + 4:end].decode("utf-8")
        except UnicodeDecodeError:
            continue
        padding = (-size) % 4
        if data[end:end + padding] != b"\0" * padding:
            continue
        if any(char.isalpha() for char in value) and all(
            char in "\t\r\n" or char.isprintable() for char in value
        ):
            fields.append((start, end + padding, value))
    return fields


def class_name(obj):
    try:
        script = obj.parse_monobehaviour_head().m_Script.deref_parse_as_object()
        return script.m_ClassName
    except Exception:
        return "неизвестный класс"


def fallback_fields(obj, name):
    """Recover known user-facing strings when the generated schema is wrong."""
    fields = raw_strings(obj.get_raw_data())
    if name == "ItemInfo":
        return fields[:2]  # ItemName and itemflavor
    if name == "EnemyController":
        return [field for field in fields if field[0] <= 40]  # CharacterName
    if name == "PlayerHealth":
        return fields
    return []


def replace_raw_strings(data, fields, translations):
    result = bytearray(data)
    for (start, end, old), text in reversed(list(zip(fields, translations))):
        raw = text.encode("utf-8")
        result[start:end] = struct.pack("<I", len(raw)) + raw + b"\0" * ((-len(raw)) % 4)
    return bytes(result)


def read_objects(env):
    objects = []
    skipped = Counter()
    recovered = Counter()
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        try:
            tree = obj.read_typetree()
        except Exception:
            name = class_name(obj)
            fields = fallback_fields(obj, name)
            if fields:
                objects.append((obj, None, fields))
                recovered[name] += len(fields)
            else:
                skipped[name] += 1
            continue
        fields = text_fields(tree)
        if fields:
            objects.append((obj, tree, fields))
    if recovered:
        details = ", ".join(f"{name}: {count}" for name, count in recovered.items())
        print(f"Восстановлено без схемы: {details}")
    if skipped:
        details = ", ".join(f"{name}: {count}" for name, count in skipped.items())
        print(f"Без переводимого текста или без схемы: {details}")
    return objects
