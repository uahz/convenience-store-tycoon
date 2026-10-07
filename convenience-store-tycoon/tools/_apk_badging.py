# 临时工具（非交付物）：aapt badging（GBK 兼容）。
import pathlib
import subprocess

tools = pathlib.Path("F:/Administrator/Documents/代码/convenience-store-tycoon/tools")
aapt = tools / "android-sdk/build-tools/34.0.0/aapt.exe"
apk = pathlib.Path(
    "F:/Administrator/Documents/代码/convenience-store-tycoon-kmp/"
    "composeApp/build/outputs/apk/debug/composeApp-debug.apk")

r = subprocess.run([str(aapt), "dump", "badging", str(apk)],
                   capture_output=True, text=False, timeout=60)
out = r.stdout.decode("gbk", errors="replace")
keep = ("package:", "application-label", "launchable", "sdkVersion",
        "targetSdk", "uses-permission", "application-icon",
        "application:")
for line in out.splitlines():
    if any(line.startswith(k) for k in keep):
        print(line[:170])
