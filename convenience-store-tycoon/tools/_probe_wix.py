# 临时工具（非交付物）：探测 cache-redirector 的 WiX 镜像可达性（禁系统代理）。
import pathlib
import urllib.request

url = ("https://cache-redirector.jetbrains.com/github.com/wixtoolset/wix3/"
       "releases/download/wix3112rtm/wix311-binaries.zip")
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
try:
    req = urllib.request.Request(url, method="HEAD")
    r = opener.open(req, timeout=25)
    print("OK", r.status, r.headers.get("Content-Length"), r.headers.get("Content-Type"))
except Exception as e:
    print("FAIL", type(e).__name__, str(e)[:100])
