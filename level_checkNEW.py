"""Проверить перевод перед сборкой."""
from common import ROOT
from check_common import check_folder

raise SystemExit(check_folder(
    ROOT / "Files/LevelOriginalStringOnly",
    ROOT / "Files/LevelModifiedStringOnly",
    ROOT / "check_report.txt",
))
