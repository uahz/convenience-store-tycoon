# 临时工具（非交付物）：探测 Inno Setup 与 WiX 的可达下载源。
import urllib.request

opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

candidates = [
    ("inno-6.4.3", "https://files.jrsoftware.org/is/6/innosetup-6.4.3.exe"),
    ("inno-6.4.1", "https://files.jrsoftware.org/is/6/innosetup-6.4.1.exe"),
    ("inno-6.3.3", "https://files.jrsoftware.org/is/6/innosetup-6.3.3.exe"),
    ("inno-6.2.1", "https://files.jrsoftware.org/is/6/innosetup-6.2.1.exe"),
    ("wix-ghfast", "https://ghfast.top/https://github.com/wixtoolset/wix3/releases/download/wix3112rtm/wix311-binaries.zip"),
    ("wix-ghproxy-net", "https://ghproxy.net/https://github.com/wixtoolset/wix3/releases/download/wix3112rtm/wix311-binaries.zip"),
    ("wix-mirror-ghproxy", "https://mirror.ghproxy.com/https://github.com/wixtoolset/wix3/releases/download/wix3112rtm/wix311-binaries.zip"),
]

for name, url in candidates:
    try:
        req = urllib.request.Request(url, method="HEAD")
        r = opener.open(req, timeout=15)
        print("OK  ", name, r.status, r.headers.get("Content-Length"))
    except Exception as e:
        print("FAIL", name, type(e).__name__, str(e)[:60])
