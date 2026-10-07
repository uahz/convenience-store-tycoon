# 临时工具（非交付物）：交付 1.0.2 修复版 APK 并归档移除旧版。
import pathlib
import shutil

root = pathlib.Path("F:/Administrator/Documents/代码/convenience-store-tycoon-kmp")
apk = root / "composeApp/build/outputs/apk/debug/composeApp-debug.apk"
delivery = root / "dist-delivery"
for old in delivery.glob("便利店大亨-安卓*.apk"):
    old.unlink()
shutil.copy2(apk, delivery / "便利店大亨-安卓-1.0.2.apk")
print("delivered 1.0.2:", f"{apk.stat().st_size / 1e6:.1f} MB")
for p in sorted(delivery.iterdir()):
    if p.is_file():
        print(p.name, f"{p.stat().st_size / 1e6:.1f} MB")
