# 临时工具（非交付物）：验证 legacy PNG 图标是否真实存在于源目录。
import pathlib

res = pathlib.Path(
    "F:/Administrator/Documents/代码/convenience-store-tycoon-kmp/"
    "composeApp/src/androidMain/res")
print("res exists:", res.exists())
for p in sorted(res.rglob("*")):
    if p.is_file():
        print(" ", p.relative_to(res), p.stat().st_size)
