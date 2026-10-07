# 临时工具（非交付物）：从 512 主图标生成安卓 legacy PNG 图标（方+圆，全密度）。
from PIL import Image, ImageDraw, ImageOps

art = pathlib = None
import pathlib

src = pathlib.Path(
    "F:/Administrator/Documents/代码/convenience-store-tycoon-kmp/art/renders/icon_main_512.png")
res = pathlib.Path(
    "F:/Administrator/Documents/代码/convenience-store-tycoon-kmp/"
    "composeApp/src/androidMain/res")

img = Image.open(src).convert("RGBA")

def rounded(im, size):
    im2 = im.resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=int(size * 0.22),
                        fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(im2, (0, 0), mask)
    return out

def circle(im, size):
    im2 = im.resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse([0, 0, size - 1, size - 1], fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(im2, (0, 0), mask)
    return out

densities = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
for dpi, size in densities.items():
    folder = res / f"mipmap-{dpi}"
    folder.mkdir(parents=True, exist_ok=True)
    rounded(img, size).save(folder / "ic_launcher.png")
    circle(img, size).save(folder / "ic_launcher_round.png")
    print(dpi, size, "ok")
