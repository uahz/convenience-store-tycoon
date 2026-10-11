# 临时工具（非交付物）：验证“已安装”的 PC 版：从安装目录启动 → PrintWindow 截图 → 查卸载注册表 → 结束。
import ctypes
import pathlib
import subprocess
import time
from ctypes import wintypes

from PIL import Image, ImageGrab

user32 = ctypes.windll.user32
TITLE = "便利店大亨 · Convenience Tycoon"
INST = pathlib.Path.home() / "AppData/Local/Programs/ConvenienceTycoon"
OUT = pathlib.Path(
    "F:/Administrator/Documents/代码/convenience-store-tycoon/design/ui-shots")

# 1) 卸载器注册表（jpackage/MSI 写入）
r = subprocess.run(
    ["reg", "query",
     r"HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall",
     "/s", "/f", "便利店大亨"],
    capture_output=True, text=False, timeout=30)
reg_out = r.stdout.decode("gbk", errors="replace")
print("uninstall reg found:", "便利店大亨" in reg_out)

# 2) 从安装目录启动
javaw = INST / "runtime/bin/javaw.exe"
proc = subprocess.Popen([str(javaw), "-jar", "ConvenienceTycoon.jar"],
                        cwd=str(INST))
print("launched pid:", proc.pid)


def find_window():
    result = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def cb(h, _):
        buf = ctypes.create_unicode_buffer(256)
        user32.GetWindowTextW(h, buf, 256)
        if TITLE in buf.value:
            result.append(h)
        return True
    user32.EnumWindows(cb, 0)
    return result[0] if result else None


hwnd = None
for _ in range(45):
    time.sleep(1)
    hwnd = find_window()
    if hwnd:
        break
print("hwnd:", hwnd)
if hwnd:
    time.sleep(3.5)
    # PrintWindow：不抢焦点，可截被遮挡窗口
    gdi32 = ctypes.windll.gdi32

    class BIH(ctypes.Structure):
        _fields_ = [("biSize", wintypes.DWORD), ("biWidth", wintypes.LONG),
                    ("biHeight", wintypes.LONG), ("biPlanes", wintypes.WORD),
                    ("biBitCount", wintypes.WORD),
                    ("biCompression", wintypes.DWORD),
                    ("biSizeImage", wintypes.DWORD),
                    ("biXPelsPerMeter", wintypes.LONG),
                    ("biYPelsPerMeter", wintypes.LONG),
                    ("biClrUsed", wintypes.DWORD),
                    ("biClrImportant", wintypes.DWORD)]

    class BMI(ctypes.Structure):
        _fields_ = [("bmiHeader", BIH), ("bmiColors", wintypes.DWORD * 3)]

    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    w, h = rect.right - rect.left, rect.bottom - rect.top
    hdc_window = user32.GetWindowDC(hwnd)
    hdc_mem = gdi32.CreateCompatibleDC(hdc_window)
    bmp = gdi32.CreateCompatibleBitmap(hdc_window, w, h)
    gdi32.SelectObject(hdc_mem, bmp)
    user32.PrintWindow(hwnd, hdc_mem, 2)
    bmi = BMI()
    bmi.bmiHeader.biSize = ctypes.sizeof(BIH)
    bmi.bmiHeader.biWidth = w
    bmi.bmiHeader.biHeight = -h
    bmi.bmiHeader.biPlanes = 1
    bmi.bmiHeader.biBitCount = 32
    buf = ctypes.create_string_buffer(w * h * 4)
    gdi32.GetDIBits(hdc_mem, bmp, 0, h, buf, ctypes.byref(bmi), 0)
    img = Image.frombuffer("RGBA", (w, h), buf.raw, "raw", "BGRA", 0, 1)
    img.convert("RGB").save(OUT / "pc_installed_menu.png")
    print("captured menu", img.size)
    # 自动开一局：模拟按键不可靠，改为验证窗口存活 5 秒即可（界面已在 menu）
    time.sleep(5)
    if find_window():
        print("window still alive after 5s: OK")
else:
    print("WINDOW NOT FOUND")
proc.kill()
print("done")
