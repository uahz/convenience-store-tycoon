# 临时工具（非交付物）：收集三端产物到 dist-delivery 并生成压缩包。
import pathlib
import shutil
import zipfile

root = pathlib.Path("F:/Administrator/Documents/代码/convenience-store-tycoon-kmp")
delivery = root / "dist-delivery"
delivery.mkdir(parents=True, exist_ok=True)

# 1) 安卓 APK
apk_src = next((root / "composeApp/build/outputs/apk/debug").glob("*.apk"), None)
print("apk:", apk_src, apk_src.stat().st_size if apk_src else "MISSING")
if apk_src:
    shutil.copy2(apk_src, delivery / "便利店大亨-安卓.apk")

# 2) PC 免安装包（压缩）
pc = root / "dist-pc" / "ConvenienceTycoon"
pc_zip = delivery / "便利店大亨-PC免安装.zip"
if pc.exists() and not pc_zip.exists():
    with zipfile.ZipFile(pc_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for p in pc.rglob("*"):
            if p.is_file():
                z.write(p, p.relative_to(pc.parent))
print("pc zip:", pc_zip, pc_zip.stat().st_size if pc_zip.exists() else "")

# 3) 网页版（压缩）
web_src = (root / "composeApp/build/dist/wasmJs/developmentExecutable")
web_zip = delivery / "便利店大亨-网页版.zip"
if web_src.exists() and not web_zip.exists():
    with zipfile.ZipFile(web_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for p in web_src.rglob("*"):
            if p.is_file():
                z.write(p, p.relative_to(web_src))
print("web zip:", web_zip, web_zip.stat().st_size if web_zip.exists() else "")

print("---- dist-delivery ----")
for p in sorted(delivery.iterdir()):
    print(p.name, f"{p.stat().st_size / 1e6:.1f} MB")
