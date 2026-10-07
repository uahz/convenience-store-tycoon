# 临时工具（非交付物）：网页版 zip 改从 dist-web 打包（含 index.html）。
import pathlib
import zipfile

root = pathlib.Path("F:/Administrator/Documents/代码/convenience-store-tycoon-kmp")
web_src = root / "dist-web" / "web"
web_zip = root / "dist-delivery" / "便利店大亨-网页版.zip"
print("has index:", (web_src / "index.html").exists())
web_zip.unlink()
with zipfile.ZipFile(web_zip, "w", zipfile.ZIP_DEFLATED) as z:
    for p in web_src.rglob("*"):
        if p.is_file():
            z.write(p, p.relative_to(web_src))
print("web zip:", web_zip.stat().st_size / 1e6, "MB")
