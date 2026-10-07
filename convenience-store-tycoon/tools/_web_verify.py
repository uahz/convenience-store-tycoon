# 临时工具（非交付物）：单进程内起服务器 + Edge 打开网页版 + PrintWindow 截图。
import ctypes
import functools
import pathlib
import shutil
import subprocess
import threading
import time
import urllib.request
from ctypes import wintypes
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

from PIL import Image

DIST = (r"F:\Administrator\Documents\代码"
        r"\convenience-store-tycoon-kmp\composeApp\build\dist\wasmJs"
        r"\developmentExecutable")
PORT = 8089
OUT = pathlib.Path(
    "F:/Administrator/Documents/代码/convenience-store-tycoon/design/ui-shots")

handler = functools.partial(SimpleHTTPRequestHandler, directory=DIST)
server = ThreadingHTTPServer(("127.0.0.1", PORT), handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
print("server on", PORT)

# 本机请求不走系统代理
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
prof = r"F:\Administrator\Documents\代码\convenience-store-tycoon\tools\_webprof2"
proc = subprocess.Popen([EDGE, "--new-window", "--no-proxy-server",
                         "--user-data-dir=" + prof,
                         "--window-size=1200,740",
                         f"http://127.0.0.1:{PORT}/"])
time.sleep(22)

user32 = ctypes.windll.user32
TITLE_KEYS = ("便利店大亨", "Convenience Tycoon", "127.0.0.1")
hwnd = None
for _ in range(20):
    result = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def cb(h, _):
        buf = ctypes.create_unicode_buffer(256)
        user32.GetWindowTextW(h, buf, 256)
        if any(k in buf.value for k in TITLE_KEYS) and "Edge" not in buf.value:
            result.append(h)
        return True
    user32.EnumWindows(cb, 0)
    if result:
        hwnd = result[0]
        break
    time.sleep(1.5)
print("hwnd:", hwnd)

if hwnd:
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
    img.convert("RGB").save(OUT / "web_real_1.png")
    print("saved", OUT / "web_real_1.png")
proc.kill()
server.shutdown()

# 用户长期使用：生成一键启动脚本
bat_dir = pathlib.Path(
    r"F:\Administrator\Documents\代码\convenience-store-tycoon-kmp\dist-web")
bat_dir.mkdir(parents=True, exist_ok=True)
bat = bat_dir / "启动网页版.bat"
bat.write_text(
    "@echo off\r\n"
    "cd /d \"%~dp0\"\r\n"
    "start \"\" http://127.0.0.1:8090/\r\n"
    "python -m http.server 8090 --bind 127.0.0.1 --directory \"%~dp0web\"\r\n",
    encoding="gbk")
web_dir = bat_dir / "web"
if web_dir.exists():
    shutil.rmtree(web_dir)
import shutil as _sh
_sh.copytree(DIST, web_dir)
(web_dir / "index.html").write_text((DIST and pathlib.Path(DIST, "index.html")
                                     .read_text(encoding="utf-8")).replace(
    "8089", "8090"), encoding="utf-8")
print("web package at", bat_dir)
