# 临时工具（非交付物）：写 local.properties 并检查 SDK 组件目录。
import pathlib

tools = pathlib.Path(__file__).resolve().parent
sdk = tools / "android-sdk"
proj = tools.parent.parent / "convenience-store-tycoon-kmp"

lp = proj / "local.properties"
lp.write_text(f"sdk.dir={sdk.as_posix()}\n", encoding="utf-8")
print("local.properties:", lp.read_text(encoding="utf-8"))

for d in ("platform-tools", "platforms/android-34", "build-tools/34.0.0"):
    p = sdk / d
    print(("OK " if p.exists() else "MISS ") + d)
