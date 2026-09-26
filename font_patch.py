"""Кириллица для TMP-шрифтов Peripeteia.

ZLK (меню): дорисовать глифы из Russo One в атлас 1024x2048.
LiberationSans SDF - Fallback: включить мульти-атлас, чтобы не кончалось место.
Результат: Font_Modded/, копируется в *_Data игры вручную.
"""
import math

import freetype
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt

from common import ROOT, read_game_dir
from tt_common import data_dir, load_level

FONT = ROOT / "Tools/Fonts/RussoOne-Regular.ttf"
OUT = ROOT / "Font_Modded"
PIXEL_SIZE = 134          # высота заглавных ~95, как у ZLK на 125pt
SUPER = 8                 # суперсэмплинг для расчёта дистанции
GAP = 1                   # зазор между ячейками атласа

ZLK_FONTS = ["ZLK", "ZLK_____ SDF", "ZLKmorevisible", "ZLKwite"]
ZLK_TEXTURES = ["ZLK_____ SDF Atlas", "ZLKmorevisible Atlas", "ZLKselected Atlas"]
FALLBACK = "LiberationSans SDF - Fallback"

UPPER = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
EXTRA = "«»—–…№“”„’"


def font_tree(obj, names):
    """Дерево TMP_FontAsset с нужным именем или None."""
    if obj.type.name != "MonoBehaviour" or obj.peek_name() not in names:
        return None
    try:
        tree = obj.read_typetree()
    except Exception:
        return None
    return tree if "m_GlyphTable" in tree else None


def render_sdf(face, char, padding):
    """Глиф SDFAA: 0.5 на контуре, спад 1/(2*(padding+1)) на пиксель."""
    face.set_pixel_sizes(0, PIXEL_SIZE * SUPER)
    face.load_char(char, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_NO_HINTING)
    bitmap = face.glyph.bitmap
    hi = np.array(bitmap.buffer, dtype=np.uint8).reshape(bitmap.rows, bitmap.width)

    face.set_pixel_sizes(0, PIXEL_SIZE)
    face.load_char(char, freetype.FT_LOAD_NO_HINTING)
    m = face.glyph.metrics
    metrics = {
        "m_Width": m.width / 64, "m_Height": m.height / 64,
        "m_HorizontalBearingX": m.horiBearingX / 64,
        "m_HorizontalBearingY": m.horiBearingY / 64,
        "m_HorizontalAdvance": m.horiAdvance / 64,
    }
    width = math.ceil(metrics["m_Width"])
    height = math.ceil(metrics["m_Height"])
    if not width or not height:
        return metrics, None

    # Холст в высоком разрешении: глиф + отступ, выровненный по bbox.
    pad_hi = padding * SUPER
    canvas = np.zeros(((height + 2 * padding) * SUPER, (width + 2 * padding) * SUPER), bool)
    ink = hi >= 128
    rows, cols = min(ink.shape[0], height * SUPER), min(ink.shape[1], width * SUPER)
    canvas[pad_hi:pad_hi + rows, pad_hi:pad_hi + cols] = ink[:rows, :cols]
    inside = distance_transform_edt(canvas)
    outside = distance_transform_edt(~canvas)
    signed = (inside - outside) / SUPER
    # Берём значение в центре каждого пикселя.
    centers = signed[SUPER // 2::SUPER, SUPER // 2::SUPER]
    spread = 2 * (padding + 1)
    alpha = np.clip(0.5 + centers / spread, 0, 1)
    return metrics, (alpha * 255 + 0.5).astype(np.uint8)


def pack_zlk(env, objects, face):
    trees = [(o, t) for o in objects if (t := font_tree(o, ZLK_FONTS))]
    if not trees:
        raise SystemExit("ZLK не найден")
    if any(c["m_Unicode"] == ord("Ж") for c in trees[0][1]["m_CharacterTable"]):
        print("ZLK: кириллица уже есть, пропуск")
        return False

    base = trees[0][1]
    old_w, old_h = base["m_AtlasWidth"], base["m_AtlasHeight"]
    padding = base["m_AtlasPadding"]
    new_h = old_h * 2
    atlas = np.zeros((new_h, old_w), np.uint8)  # строка 0 = низ, как в Unity

    glyphs, characters, used = [], [], []
    x, y, shelf = 0, old_h, 0
    next_index = max(g["m_Index"] for g in base["m_GlyphTable"]) + 1
    for char in UPPER + EXTRA:
        metrics, sdf = render_sdf(face, char, padding)
        rect = {"m_X": 0, "m_Y": 0, "m_Width": 0, "m_Height": 0}
        if sdf is not None:
            cell_h, cell_w = sdf.shape
            if x + cell_w > old_w:
                x, y, shelf = 0, y + shelf + GAP, 0
            if y + cell_h > new_h:
                raise SystemExit("Не хватило места в атласе")
            # sdf идёт сверху вниз, атлас снизу вверх.
            atlas[y:y + cell_h, x:x + cell_w] = sdf[::-1]
            rect = {"m_X": x + padding, "m_Y": y + padding,
                    "m_Width": cell_w - 2 * padding, "m_Height": cell_h - 2 * padding}
            used.append({"m_X": x, "m_Y": y, "m_Width": cell_w, "m_Height": cell_h})
            x += cell_w + GAP
            shelf = max(shelf, cell_h)
        glyphs.append({"m_Index": next_index, "m_Metrics": metrics, "m_GlyphRect": rect,
                       "m_Scale": 1.0, "m_AtlasIndex": 0})
        codes = {ord(char)}
        if char in UPPER:
            # ZLK — капительный шрифт: строчные рисуются теми же глифами.
            codes.add(ord(char.lower()))
        for code in sorted(codes):
            characters.append({"m_ElementType": 1, "m_Unicode": code,
                               "m_GlyphIndex": next_index, "m_Scale": 1.0})
        next_index += 1

    for obj, tree in trees:
        tree["m_GlyphTable"] += glyphs
        tree["m_CharacterTable"] += characters
        tree["m_UsedGlyphRects"] += used
        tree["m_AtlasHeight"] = new_h
        tree["m_CreationSettings"]["atlasHeight"] = new_h
        obj.save_typetree(tree)
        print(f"{tree['m_Name']}: +{len(characters)} символов")

    textures = [o for o in objects if o.type.name == "Texture2D" and o.peek_name() in ZLK_TEXTURES]
    for obj in textures:
        tex = obj.read()
        old = np.array(tex.image.getchannel("A"))[::-1]  # к порядку Unity
        full = atlas.copy()
        full[:old_h] = old
        tex.m_Height = new_h
        tex.image_data = full.tobytes()
        tex.m_CompleteImageSize = len(tex.image_data)
        tex.m_StreamData.path = ""
        tex.m_StreamData.offset = 0
        tex.m_StreamData.size = 0
        tex.save()
        print(f"{tex.m_Name}: {old_w}x{new_h}")

    for obj in objects:
        if obj.type.name != "Material":
            continue
        mat = obj.read()
        main = dict(mat.m_SavedProperties.m_TexEnvs).get("_MainTex")
        if main and main.m_Texture.path_id in {t.path_id for t in textures} and main.m_Texture.file_id == 0:
            mat.m_SavedProperties.m_Floats = [
                (k, float(new_h) if k == "_TextureHeight" else v)
                for k, v in mat.m_SavedProperties.m_Floats]
            mat.save()
    Image.fromarray(atlas[::-1]).save(OUT / "zlk_cyrillic_preview.png")
    return True


def patch_fallback(objects):
    for obj in objects:
        if tree := font_tree(obj, [FALLBACK]):
            if tree["m_IsMultiAtlasTexturesEnabled"]:
                print(f"{FALLBACK}: уже включено")
                return False
            tree["m_IsMultiAtlasTexturesEnabled"] = 1
            obj.save_typetree(tree)
            print(f"{FALLBACK}: мульти-атлас включён")
            return True
    raise SystemExit(f"{FALLBACK} не найден")


def main():
    game_data = data_dir(read_game_dir())
    OUT.mkdir(exist_ok=True)
    face = freetype.Face(str(FONT))
    for name, action in [("sharedassets0.assets", lambda objs: pack_zlk(env, objs, face)),
                         ("resources.assets", patch_fallback)]:
        env = load_level(game_data / name)
        objects = list(env.objects)
        if action(objects):
            (OUT / name).write_bytes(env.file.save())
            print(f"Собран: {OUT / name}")


if __name__ == "__main__":
    main()
