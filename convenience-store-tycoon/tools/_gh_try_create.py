# 临时工具（非交付物）：尝试 REST 建仓 + 检查凭据管理器可用登录。
import os
import subprocess

r = subprocess.run(
    ["gh", "api", "/user/repos", "-f", "name=convenience-store-tycoon",
     "-f", "private=false",
     "-f", "description=便利店大亨 · 实时便利店经营模拟（Kotlin 三端：PC / 网页 / 安卓）"],
    capture_output=True, text=True, timeout=60)
print("gh api rc:", r.returncode)
out = (r.stdout or "") + (r.stderr or "")
print(out[:300])

cred = subprocess.run(["git", "credential", "fill"], input="protocol=https\nhost=github.com\n\n",
                      capture_output=True, text=True, timeout=30)
for line in (cred.stdout or "").splitlines():
    if line.startswith(("username=", "password=")):
        k, v = line.split("=", 1)
        print(k, "=", (v[:6] + "...") if k == "password" and len(v) > 6 else v)
