# 临时工具（非交付物）：ASCII 临时路径下的 aapt badging。
import pathlib
import shutil
import subprocess
import tempfile

tools = pathlib.Path("F:/Administrator/Documents/代码/convenience-store-tycoon/tools")
aapt = tools / "android-sdk/build-tools/34.0.0/aapt.exe"
apk_src = pathlib.Path(
    "F:/Administrator/Documents/代码/convenience-store-tycoon-kmp/"
    "composeApp/build/outputs/apk/debug/composeApp-debug.apk")
tmp = pathlib.Path(tempfile.gettempdir()) / "apkcheck"
tmp.mkdir(exist_ok=True)
apk = tmp / "app.apk"
shutil.copy2(apk_src, apk)
print("apk at:", apk)

r = subprocess.run([str(aapt), "dump", "badging", str(apk)],
                   capture_output=True, text=False, timeout=60)
out = r.stdout.decode("gbk", errors="replace")
keep = ("package:", "application-label", "launchable", "sdkVersion",
        "targetSdk", "uses-permission", "application-icon", "densities")
shown = 0
for line in out.splitlines():
    if any(line.startswith(k) for k in keep):
        print(line[:170])
        shown += 1
if shown == 0:
    print("RAW:", out[:300], "ERR:", r.stderr.decode("gbk", errors="replace")[:300])
