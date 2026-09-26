"""Проверить перевод перед сборкой."""
from common import ROOT
from check_common import check_folder

raise SystemExit(check_folder(
    ROOT / "Files/OriginalStringOnly",
    ROOT / "Files/ModifiedStringOnly",
    ROOT / "assets_check_report.txt",
))
