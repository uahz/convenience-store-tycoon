# 临时工具（非交付物）：Edge 无头渲染图标 SVG → PNG（主图标多尺寸 + 小图标集展示）。
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent   # convenience-store-tycoon-kmp
ART = ROOT / "art"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
OUT = ART / "renders"
OUT.mkdir(parents=True, exist_ok=True)

svg_path = ART / "icons.html"
url = "file:///" + str(svg_path).replace("\\", "/")

# 1) 主图标：截 512 区域（页面左上角即为 512×512 的主图标）
r1 = subprocess.run(
    [EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars",
     "--window-size=512,512", "--no-first-run",
     f"--user-data-dir={OUT / '_prof'}",
     f"--screenshot={OUT / 'icon_main_512.png'}", url + "#icon-main"],
    capture_output=True, timeout=120)
print("icon_main:", r1.returncode)

# 2) 小图标集：单独页面（隐藏主图标，只显示 sheet）
sheet_html = svg_path.read_text(encoding="utf-8").replace(
    'id="icon-main"', 'id="icon-main" style="display:none"')
tmp = ART / "_sheet.html"
tmp.write_text(sheet_html, encoding="utf-8")
url2 = "file:///" + str(tmp).replace("\\", "/")
r2 = subprocess.run(
    [EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars",
     "--window-size=1500,260", "--no-first-run",
     f"--user-data-dir={OUT / '_prof'}",
     f"--screenshot={OUT / 'icons_sheet.png'}", url2],
    capture_output=True, timeout=120)
print("icons_sheet:", r2.returncode)

# 3) 生成 Windows .ico（多尺寸）
from PIL import Image
img = Image.open(OUT / "icon_main_512.png").convert("RGBA")
img.save(ROOT / "composeApp" / "icons" / "game.ico",
         sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
for size in (512, 192, 96):
    img.resize((size, size), Image.LANCZOS).save(OUT / f"icon_main_{size}.png")
print("ico + png done")
