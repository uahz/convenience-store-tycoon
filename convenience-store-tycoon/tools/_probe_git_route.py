# 临时工具（非交付物）：探测到 GitHub 各入口的 TCP 可达性 + 代理环境。
import os
import socket

print("proxy env:", {k: v for k, v in os.environ.items()
                     if "proxy" in k.lower()})

targets = [
    ("github.com:443", "github.com", 443),
    ("api.github.com:443", "api.github.com", 443),
    ("ssh.github.com:443", "ssh.github.com", 443),
    ("140.82.121.3:443", "140.82.121.3", 443),
    ("140.82.112.3:443", "140.82.112.3", 443),
]
for name, host, port in targets:
    try:
        s = socket.create_connection((host, port), timeout=8)
        s.close()
        print("OK  ", name)
    except Exception as e:
        print("FAIL", name, type(e).__name__, str(e)[:50])
