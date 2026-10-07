# 临时工具（非交付物）：确认 dex 中存在 tycoon/MainActivity 且旧类名不存在。
import pathlib
import zipfile

apk = pathlib.Path(
    "F:/Administrator/Documents/代码/convenience-store-tycoon-kmp/"
    "composeApp/build/outputs/apk/debug/composeApp-debug.apk")
with zipfile.ZipFile(apk) as z:
    dexes = [n for n in z.namelist() if n.endswith(".dex")]
    found_main = False
    found_wrong = False
    for d in dexes:
        data = z.read(d)
        if b"tycoon/MainActivity" in data:
            found_main = True
        if b"com/convenience/tycoon/MainActivity" in data:
            found_wrong = True
    print("dex files:", dexes)
    print("tycoon/MainActivity in dex:", found_main)
    print("wrong-path class present:", found_wrong)
