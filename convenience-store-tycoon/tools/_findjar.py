# 临时工具（非交付物）：在构建目录里找产物 jar。
import pathlib

root = pathlib.Path("F:/Administrator/Documents/代码/convenience-store-tycoon-kmp/composeApp/build")
for p in sorted(root.rglob("*.jar")):
    print(p.relative_to(root), p.stat().st_size)
