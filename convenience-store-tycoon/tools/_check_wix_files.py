# 临时工具（非交付物）：验证 WiX 工具与安装源文件数量。
import pathlib

wix = pathlib.Path(
    "F:/Administrator/Documents/代码/convenience-store-tycoon/tools/wix-local")
for n in ("candle.exe", "light.exe", "heat.exe"):
    print(n, (wix / n).exists())

src = pathlib.Path(
    "F:/Administrator/Documents/代码/convenience-store-tycoon-kmp/dist-pc/ConvenienceTycoon")
files = [p for p in src.rglob("*") if p.is_file()]
print("install source files:", len(files))
print("jar:", (src / "ConvenienceTycoon.jar").stat().st_size)
