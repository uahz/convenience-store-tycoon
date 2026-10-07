# 临时工具（非交付物）：查看 wix zip 内部结构与实际解压结果。
import pathlib
import zipfile

tools = pathlib.Path("F:/Administrator/Documents/代码/convenience-store-tycoon/tools")
with zipfile.ZipFile(tools / "wix-local" / "wix311-binaries.zip") as z:
    names = z.namelist()
print("entries:", len(names))
for n in names[:15]:
    print(" ", n)
print("...")
for p in sorted((tools / "wix-local").rglob("*"))[:20]:
    print(("D " if p.is_dir() else "F "), p.relative_to(tools / "wix-local"))
