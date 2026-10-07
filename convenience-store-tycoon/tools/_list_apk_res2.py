# 临时工具（非交付物）：重新检查最新 APK 的 mipmap 条目与时间戳。
import pathlib
import zipfile

apk = pathlib.Path(
    "F:/Administrator/Documents/代码/convenience-store-tycoon-kmp/"
    "composeApp/build/outputs/apk/debug/composeApp-debug.apk")
print("apk mtime:", apk.stat().st_mtime)
with zipfile.ZipFile(apk) as z:
    mm = [n for n in z.namelist() if "mipmap" in n]
    print("mipmap entries:", mm)
    infos = z.infolist()
    print("total:", len(infos))
    # 找出排除了什么：对比 merged_res flat 文件数
