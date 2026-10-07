# 临时工具（非交付物）：更新 APK 交付（1.0.1 修复版）。
import pathlib
import shutil

root = pathlib.Path("F:/Administrator/Documents/代码/convenience-store-tycoon-kmp")
apk = root / "composeApp/build/outputs/apk/debug/composeApp-debug.apk"
delivery = root / "dist-delivery"
old = delivery / "便利店大亨-安卓.apk"
if old.exists():
    old.unlink()
shutil.copy2(apk, delivery / "便利店大亨-安卓-1.0.1修复版.apk")
print("delivered:", delivery / "便利店大亨-安卓-1.0.1修复版.apk",
      f"{apk.stat().st_size / 1e6:.1f} MB")
