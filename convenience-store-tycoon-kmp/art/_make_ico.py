# 临时工具（非交付物）：生成多尺寸 .ico。
from PIL import Image
import pathlib

art = pathlib.Path(__file__).resolve().parent
img = Image.open(art / "renders" / "icon_main_512.png").convert("RGBA")
icons_dir = art.parent / "composeApp" / "icons"
icons_dir.mkdir(exist_ok=True)
img.save(icons_dir / "game.ico",
         sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
print("ico saved:", icons_dir / "game.ico")
