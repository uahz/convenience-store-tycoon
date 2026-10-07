# 临时工具（非交付物）：APK 静态体检 + 检查是否有已连接的安卓设备。
import pathlib
import subprocess

tools = pathlib.Path("F:/Administrator/Documents/代码/convenience-store-tycoon/tools")
sdk = tools / "android-sdk"
aapt = sdk / "build-tools/34.0.0/aapt.exe"
adb = sdk / "platform-tools/adb.exe"
apk = pathlib.Path(
    "F:/Administrator/Documents/代码/convenience-store-tycoon-kmp/"
    "composeApp/build/outputs/apk/debug/composeApp-debug.apk")

print("== aapt badging ==")
r = subprocess.run([str(aapt), "dump", "badging", str(apk)],
                   capture_output=True, text=True, timeout=60)
for line in (r.stdout or "").splitlines():
    if line.startswith(("package:", "application-label", "launchable-activity:",
                        "sdkVersion", "targetSdkVersion", "uses-permission",
                        "application-icon:")):
        print(" ", line[:150])
print("stderr:", (r.stderr or "")[:200])

print("== adb devices ==")
r2 = subprocess.run([str(adb), "devices"], capture_output=True, text=True,
                    timeout=30)
print(r2.stdout)
