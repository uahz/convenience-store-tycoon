# 临时工具（非交付物）：检查 mergeDebugResources 中间产物里的 mipmap。
import pathlib

inter = pathlib.Path(
    "F:/Administrator/Documents/代码/convenience-store-tycoon-kmp/"
    "composeApp/build/intermediates")
hits = []
for p in inter.rglob("*mipmap*"):
    hits.append(p)
print("mipmap intermediates:", len(hits))
for p in hits[:15]:
    print(" ", p.relative_to(inter))
# 也看 merged_res 顶层
merged = inter / "merged_res"
if merged.exists():
    for p in sorted(merged.iterdir())[:10]:
        print("merged:", p.name)
else:
    print("no merged_res dir")
