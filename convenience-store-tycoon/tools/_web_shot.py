# 临时工具（非交付物）：无头 Edge 截取部署中的网页版游戏画面。
import pathlib
import subprocess

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
out = pathlib.Path(
    "F:/Administrator/Documents/代码/convenience-store-tycoon/design/ui-shots/web_real_1.png")
r = subprocess.run(
    [EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars",
     "--window-size=1200,740", "--virtual-time-budget=30000",
     r"--user-data-dir=F:\Administrator\Documents\代码\convenience-store-tycoon\tools\_webprof",
     "--screenshot=" + str(out), "http://localhost:6988/"],
    capture_output=True, timeout=180)
print("rc", r.returncode)
print("exists", out.exists(), out.stat().st_size if out.exists() else 0)
