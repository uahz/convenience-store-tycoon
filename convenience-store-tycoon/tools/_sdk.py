# 临时工具（非交付物）：安装 Android SDK（cmdline-tools → platforms/build-tools）。
import os
import pathlib
import shutil
import subprocess
import zipfile

tools = pathlib.Path("F:/Administrator/Documents/代码/convenience-store-tycoon/tools")
sdk = tools / "android-sdk"
zip_path = pathlib.Path(
    "F:/Administrator/Documents/convenience-store-tycoon-kmp-tools-cmdtools.zip")
jdk_dir = next(p for p in tools.iterdir()
               if p.is_dir() and p.name.startswith("jdk-"))

if not sdk.exists():
    sdk.mkdir(parents=True)
cmdtools_root = sdk / "cmdline-tools"
latest = cmdtools_root / "latest"
if not latest.exists():
    tmp = sdk / "_cmdtools"
    if tmp.exists():
        shutil.rmtree(tmp)
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(tmp)          # 解出 tmp/cmdline-tools/*
    latest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(tmp / "cmdline-tools"), str(latest))
    tmp.rmdir()
print("cmdline-tools ready:", latest.exists())

sdkmanager = latest / "bin" / "sdkmanager.bat"
env = dict(os.environ)
env["JAVA_HOME"] = str(jdk_dir)
env["PATH"] = str(jdk_dir / "bin") + os.pathsep + env.get("PATH", "")

what = sys_arg = None
import sys
what = sys.argv[1] if len(sys.argv) > 1 else "list"

if what == "licenses":
    r = subprocess.run([str(sdkmanager), "--sdk_root=" + str(sdk), "--licenses"],
                       input="y\n" * 20, capture_output=True, text=False,
                       timeout=600, env=env)
    print(r.stdout.decode("gbk", errors="replace")[-1200:])
    print("rc:", r.returncode)
elif what == "install":
    r = subprocess.run(
        [str(sdkmanager), "--sdk_root=" + str(sdk),
         "platform-tools", "platforms;android-34", "build-tools;34.0.0"],
        input="y\n" * 20, capture_output=True, text=False, timeout=3500, env=env)
    print(r.stdout.decode("gbk", errors="replace")[-1200:])
    print("rc:", r.returncode)
else:
    r = subprocess.run([str(sdkmanager), "--sdk_root=" + str(sdk), "--list"],
                       capture_output=True, text=False, timeout=600, env=env)
    out = r.stdout.decode("gbk", errors="replace")
    print(out[:600])
    print("rc:", r.returncode)
