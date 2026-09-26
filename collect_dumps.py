"""Скопировать файлы IL2CPP и получить DummyDll через Il2CppDumper."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
from common import ROOT, read_game_dir

if len(sys.argv) > 1:
    game = Path(os.path.expandvars(sys.argv[1])).expanduser().resolve()
else:
    game = read_game_dir()
if not game.is_dir():
    raise SystemExit(f"Нет папки игры: {game}")
output = ROOT / "Dumps" / game.name
output.mkdir(parents=True, exist_ok=True)

for name in ("GameAssembly.dll", "global-metadata.dat"):
    target = output / name
    if target.exists():
        continue
    source = next(game.rglob(name), None)
    if source is None:
        raise SystemExit(f"В папке игры не найден {name}")
    shutil.copy2(source, target)
    print(f"Скопирован: {name}")

if not (output / "DummyDll").is_dir():
    dumper = ROOT / "Tools/Il2CppDumper/Il2CppDumper.dll"
    if not dumper.is_file():
        raise SystemExit(f"Установи Il2CppDumper в {dumper.parent}")
    env = os.environ.copy()
    env["DOTNET_ROLL_FORWARD"] = "LatestMajor"
    subprocess.run([
        "dotnet", str(dumper), str(output / "GameAssembly.dll"),
        str(output / "global-metadata.dat"), str(output),
    ], env=env, stdin=subprocess.DEVNULL)
    # Dumper может упасть на ожидании клавиши уже после успешной работы.
    if not (output / "DummyDll").is_dir():
        raise SystemExit("Il2CppDumper не создал DummyDll")
print(f"Готово: {output / 'DummyDll'}")
