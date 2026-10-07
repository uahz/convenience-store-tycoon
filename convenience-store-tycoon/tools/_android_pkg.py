# 临时工具（非交付物）：Android SDK 组件获取（licenses / packages / list）。
import os
import pathlib
import subprocess
import sys

tools = pathlib.Path(__file__).resolve().parent
sdk = tools / "android-sdk"
jdk_dir = next(p for p in tools.iterdir()
               if p.is_dir() and p.name.startswith("jdk-"))

latest = sdk / "cmdline-tools" / "latest"
sdkmanager = latest / "bin" / "sdkmanager.bat"
env = dict(os.environ)
env["JAVA_HOME"] = str(jdk_dir)
env["PATH"] = str(jdk_dir / "bin") + os.pathsep + env.get("PATH", "")

mode = sys.argv[1] if len(sys.argv) > 1 else "list"

if mode == "licenses":
    r = subprocess.run([str(sdkmanager), "--sdk_root=" + str(sdk), "--licenses"],
                       input="y\n" * 20, capture_output=True, text=False,
                       timeout=600, env=env)
elif mode == "packages":
    r = subprocess.run(
        [str(sdkmanager), "--sdk_root=" + str(sdk),
         "platform-tools", "platforms;android-34", "build-tools;34.0.0"],
        input="y\n" * 20, capture_output=True, text=False, timeout=3500, env=env)
else:
    r = subprocess.run([str(sdkmanager), "--sdk_root=" + str(sdk), "--list"],
                       capture_output=True, text=False, timeout=600, env=env)

print(r.stdout.decode("gbk", errors="replace")[-1500:])
print("rc:", r.returncode)
