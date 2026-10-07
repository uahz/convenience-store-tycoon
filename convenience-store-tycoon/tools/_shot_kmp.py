# 临时工具（非交付物）：启动/复用 PC 端窗口，置顶后截图。
import ctypes
import pathlib
import subprocess
import time
from ctypes import wintypes

from PIL import ImageGrab

OUT = pathlib.Path("F:/Administrator/Documents/代码/convenience-store-tycoon/design/ui-shots")
BAT = pathlib.Path(
    "F:/Administrator/Documents/代码/convenience-store-tycoon-kmp/dist-pc/ConvenienceTycoon/启动游戏.bat")
TITLE = "便利店大亨 · Convenience Tycoon"
user32 = ctypes.windll.user32


def find_window():
    result = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def cb(hwnd, _):
        buf = ctypes.create_unicode_buffer(256)
        user32.GetWindowTextW(hwnd, buf, 256)
        if TITLE in buf.value:
            result.append(hwnd)
        return True
    user32.EnumWindows(cb, 0)
    return result[0] if result else None


hwnd = find_window()
proc = None
if not hwnd:
    proc = subprocess.Popen(["cmd", "/c", str(BAT)], cwd=str(BAT.parent))
    for _ in range(60):
        time.sleep(1.0)
        hwnd = find_window()
        if hwnd:
            break
print("hwnd:", hwnd)
if hwnd:
    user32.ShowWindow(hwnd, 9)      # SW_RESTORE
    user32.SetForegroundWindow(hwnd)
    time.sleep(2.5)                  # 等置顶与首帧渲染
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    img = ImageGrab.grab(bbox=(rect.left, rect.top, rect.right, rect.bottom))
    img.save(OUT / "kmp_real_1_menu.png")
    print("saved menu shot", img.size, "pid:", proc.pid if proc else "existing")
else:
    print("WINDOW NOT FOUND")
