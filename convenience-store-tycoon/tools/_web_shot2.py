# 临时工具（非交付物）：headless Edge 截网页版（绕系统代理 + 真实超时等待）。
import pathlib
import subprocess

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
out = pathlib.Path(
    "F:/Administrator/Documents/代码/convenience-store-tycoon/design/ui-shots/web_real_1.png")
if out.exists():
    out.unlink()
r = subprocess.run(
    [EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars",
     "--no-proxy-server", "--window-size=1200,740", "--timeout=25000",
     r"--user-data-dir=F:\Administrator\Documents\代码\convenience-store-tycoon\tools\_webprof3",
     "--screenshot=" + str(out), "http://127.0.0.1:8089/"],
    capture_output=True, timeout=200)
print("rc", r.returncode)
print("exists", out.exists(), out.stat().st_size if out.exists() else 0)
