# 临时工具（非交付物）：静默安装 MSI 并验证文件与快捷方式，然后交付归档。
import pathlib
import subprocess
import shutil

root = pathlib.Path("F:/Administrator/Documents/代码/convenience-store-tycoon-kmp")
msi = root / "dist-delivery/_msi/便利店大亨-1.0.0.msi"
delivery = root / "dist-delivery"

# 1) 静默安装（per-user，无需管理员）
r = subprocess.run(["msiexec", "/i", str(msi), "/qn", "/norestart"],
                   capture_output=True, text=False, timeout=600)
print("install rc:", r.returncode)

installed = pathlib.Path(os_local := str(pathlib.Path.home()
                                          / "AppData/Local/Programs/ConvenienceTycoon"))
p_installed = pathlib.Path(os_local)
print("installed dir exists:", p_installed.exists())
print("jar:", (p_installed / "ConvenienceTycoon.jar").exists())
print("javaw:", (p_installed / "runtime/bin/javaw.exe").exists())
sm = (pathlib.Path.home() / "AppData/Roaming/Microsoft/Windows/Start Menu/Programs/便利店大亨")
print("start menu dir:", sm.exists())
dt = (pathlib.Path.home() / "Desktop/便利店大亨.lnk")
print("desktop lnk:", dt.exists())

# 2) 交付归档：移除免安装版，放入安装版
pc_zip = delivery / "便利店大亨-PC免安装.zip"
if pc_zip.exists():
    pc_zip.unlink()
shutil.copy2(msi, delivery / "便利店大亨-1.0.0.msi")
# dist-pc 仅作为 MSI 构建中间产物保留在本地，不再作为交付物
print("---- dist-delivery ----")
for p in sorted(delivery.iterdir()):
    if p.is_file():
        print(p.name, f"{p.stat().st_size / 1e6:.1f} MB")
