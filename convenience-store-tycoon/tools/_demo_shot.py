# 临时工具（非交付物）：以演示模式启动 PC 包 → 等自截 demo_open.png → 移动到 ui-shots。
import os
import pathlib
import shutil
import subprocess
import time

pkg = pathlib.Path(
    "F:/Administrator/Documents/代码/convenience-store-tycoon-kmp/dist-pc/ConvenienceTycoon")
tools = pathlib.Path("F:/Administrator/Documents/代码/convenience-store-tycoon/tools")
jdk = next(p for p in tools.iterdir()
           if p.is_dir() and p.name.startswith("jdk-"))
out_dir = pathlib.Path(
    "F:/Administrator/Documents/代码/convenience-store-tycoon/design/ui-shots")
demo_png = pkg / "demo_open.png"
if demo_png.exists():
    demo_png.unlink()

env = dict(os.environ)
env["CTYCOON_DEMO"] = "1"
javaw = jdk / "bin" / "javaw.exe"
proc = subprocess.Popen([str(javaw), "-jar", "ConvenienceTycoon.jar"],
                        cwd=str(pkg), env=env)
print("launched pid", proc.pid)
deadline = time.time() + 60
while time.time() < deadline:
    time.sleep(2)
    if demo_png.exists():
        break
    if proc.poll() is not None:
        break
if demo_png.exists():
    shutil.move(str(demo_png), str(out_dir / "kmp_real_2_open.png"))
    print("captured ->", out_dir / "kmp_real_2_open.png")
else:
    print("NO SCREENSHOT (timeout or exit)", proc.poll())
proc.kill()
