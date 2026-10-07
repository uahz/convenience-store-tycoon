# 临时工具（非交付物）：ASCII 路径下 aapt badging。
import pathlib
import shutil
import subprocess

tools = pathlib.Path("F:/Administrator/Documents/代码/convenience-store-tycoon/tools")
aapt = tools / "android-sdk/build-tools/34.0.0/aapt.exe"
apk_src = pathlib.Path(
    "F:/Administrator/Documents/代码/convenience-store-tycoon-kmp/"
    "composeApp/build/outputs/apk/debug/composeApp-debug.apk")
apk = tools / "_apk" / "app.apk"
apk.parent.mkdir(exist_ok=True)
shutil.copy2(apk_src, apk)

r = subprocess.run([str(aapt), "dump", "badging", str(apk)],
                   capture_output=True, text=False, timeout=60,
                   cwd=str(apk.parent))
out = r.stdout.decode("gbk", errors="replace")
err = r.stderr.decode("gbk", errors="replace")
print("rc:", r.returncode)
keep = ("package:", "application-label", "launchable", "sdkVersion",
        "targetSdk", "uses-permission", "application-icon",
        "application:", "densities")
shown = 0
for line in out.splitlines():
    if any(line.startswith(k) for k in keep):
        print(line[:170])
        shown += 1
if shown == 0:
    print("RAW head:", out[:400])
    print("ERR:", err[:400])
