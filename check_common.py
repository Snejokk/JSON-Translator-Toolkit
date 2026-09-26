"""Основные проверки перевода: строки, экранирование, теги."""
import re
from common import read_lines, unescape_line


def check_folder(original_dir, translation_dir, report_path):
    if not original_dir.is_dir():
        raise SystemExit(f"Нет папки оригиналов: {original_dir}")
    errors = []
    for original in sorted(original_dir.rglob("*.txt")):
        name = original.relative_to(original_dir)
        source = read_lines(original)
        if not source:
            continue
        translation = translation_dir / name
        if not translation.exists():
            errors.append(f"{name}: нет перевода")
            continue
        target = read_lines(translation)
        if len(source) != len(target):
            errors.append(f"{name}: нужно {len(source)} строк, получено {len(target)}")
            continue
        for number, (old, new) in enumerate(zip(source, target), 1):
            problem = ""
            try:
                old = unescape_line(old)
                new = unescape_line(new)
            except ValueError:
                errors.append(f"{name}:{number}: неверное экранирование")
                continue
            if old.strip() and not new.strip():
                problem = "пустой перевод"
            elif not any(char.isalpha() for char in old) and old != new:
                problem = "изменена служебная строка"
            elif old.count("\n") != new.count("\n") or old.count("\r") != new.count("\r"):
                problem = "изменилось число переносов внутри реплики"
            for pattern in (r"<[^<>]+>", r"\{[^{}]+\}", r"\[[^\[\]]+\]"):
                if sorted(re.findall(pattern, old)) != sorted(re.findall(pattern, new)):
                    problem = "изменены теги или плейсхолдеры"
            if problem:
                errors.append(f"{name}:{number}: {problem}")
    report_path.write_text("\n".join(errors), encoding="utf-8")
    for error in errors:
        print(error)
    print(f"Ошибок: {len(errors)}. Отчёт: {report_path.name}")
    return 1 if errors else 0
