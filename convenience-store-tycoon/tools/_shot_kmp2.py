# 临时工具（非交付物）：启动新版 PC 包 → PrintWindow 截图 → 结束该实例。
import ctypes
import pathlib
import subprocess
import time
from ctypes import wintypes

from PIL import Image, ImageGrab

user32 = ctypes.windll.user32
TITLE = "便利店大亨 · Convenience Tycoon"
OUT = pathlib.Path(
    "F:/Administrator/Documents/代码/convenience-store-tycoon/design/ui-shots")
BAT = pathlib.Path(
    "F:/Administrator/Documents/代码/convenience-store-tycoon-kmp/dist-pc/ConvenienceTycoon/启动游戏.bat")


def find_windows():
    result = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def cb(hwnd, _):
        buf = ctypes.create_unicode_buffer(256)
        user32.GetWindowTextW(hwnd, buf, 256)
        if TITLE in buf.value:
            result.append(hwnd)
        return True
    user32.EnumWindows(cb, 0)
    return result


def capture(hwnd, path):
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    w, h = rect.right - rect.left, rect.bottom - rect.top
    hdc_window = user32.GetWindowDC(hwnd)
    hdc_mem = gdi32_CreateCompatibleDC()
    bmp = gdi32_CreateCompatibleBitmap(hdc_window, w, h)
    gdi32_SelectObject(hdc_mem, bmp)
    user32.PrintWindow(hwnd, hdc_mem, 2)
    bmi = BITMAPINFO()
    bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bmi.bmiHeader.biWidth = w
    bmi.bmiHeader.biHeight = -h
    bmi.bmiHeader.biPlanes = 1
    bmi.bmiHeader.biBitCount = 32
    buf = ctypes.create_string_buffer(w * h * 4)
    gdi32_GetDIBits(hdc_mem, bmp, 0, h, buf, ctypes.byref(bmi), 0)
    img = Image.frombuffer("RGBA", (w, h), buf.raw, "raw", "BGRA", 0, 1)
    img.convert("RGB").save(path)


# gdi 简写
gdi32 = ctypes.windll.gdi32
gdi32_CreateCompatibleDC = gdi32.CreateCompatibleDC
gdi32_CreateCompatibleBitmap = gdi32.CreateCompatibleBitmap
gdi32_SelectObject = gdi32.SelectObject
gdi32_GetDIBits = gdi32.GetDIBits


class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [("biSize", wintypes.DWORD), ("biWidth", wintypes.LONG),
                ("biHeight", wintypes.LONG), ("biPlanes", wintypes.WORD),
                ("biBitCount", wintypes.WORD), ("biCompression", wintypes.DWORD),
                ("biSizeImage", wintypes.DWORD), ("biXPelsPerMeter", wintypes.LONG),
                ("biYPelsPerMeter", wintypes.LONG), ("biClrUsed", wintypes.DWORD),
                ("biClrImportant", wintypes.DWORD)]


class BITMAPINFO(ctypes.Structure):
    _fields_ = [("bmiHeader", BITMAPINFOHEADER), ("bmiColors", wintypes.DWORD * 3)]


before = set(find_windows())
proc = subprocess.Popen(["cmd", "/c", str(BAT)], cwd=str(BAT.parent))
hwnd = None
for _ in range(60):
    time.sleep(1.0)
    news = [w for w in find_windows() if w not in before]
    if news:
        hwnd = news[0]
        break
print("new hwnd:", hwnd)
if hwnd:
    time.sleep(4.0)
    # 短暂置顶抓屏（约 2 秒），随后还原并最小化，减少干扰
    HWND_TOPMOST, HWND_NOTOPMOST = -1, -2
    SWP_NOMOVE, SWP_NOSIZE = 0x0002, 0x0001
    user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                        SWP_NOMOVE | SWP_NOSIZE)
    time.sleep(0.8)
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    img = ImageGrab.grab(bbox=(rect.left, rect.top, rect.right, rect.bottom))
    img.save(OUT / "kmp_real_1_menu.png")
    user32.SetWindowPos(hwnd, HWND_NOTOPMOST, 0, 0, 0, 0,
                        SWP_NOMOVE | SWP_NOSIZE)
    user32.ShowWindow(hwnd, 6)   # SW_MINIMIZE
    print("captured", img.size)
    # 结束这个实例（不碰用户其他窗口）
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    subprocess.run(["taskkill", "/PID", str(pid.value), "/F"],
                   capture_output=True)
    print("killed pid", pid.value)
else:
    proc.kill()
    print("WINDOW NOT FOUND")
