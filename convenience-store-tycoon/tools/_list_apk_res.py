# 临时工具（非交付物）：列出 APK 内 mipmap 相关资源。
import pathlib
import zipfile

apk = pathlib.Path(
    "F:/Administrator/Documents/代码/convenience-store-tycoon-kmp/"
    "composeApp/build/outputs/apk/debug/composeApp-debug.apk")
with zipfile.ZipFile(apk) as z:
    names = [n for n in z.namelist() if "mipmap" in n or n.startswith("res/")]
    for n in names[:40]:
        print(n)
    print("total res entries:", len(names))
