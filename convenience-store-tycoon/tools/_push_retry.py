# 临时工具（非交付物）：重试 git push 直到成功，然后清除 remote 中的令牌。
import os
import pathlib
import subprocess
import time

root = pathlib.Path("F:/Administrator/Documents/代码")
env = dict(os.environ)
ok = False
for i in range(1, 7):
    r = subprocess.run(["git", "push", "-u", "origin", "main"],
                       cwd=str(root), env=env, capture_output=True,
                       text=True, timeout=550)
    out = (r.stdout or "") + (r.stderr or "")
    print(f"attempt {i}: rc={r.returncode}")
    print(out[-400:])
    if r.returncode == 0:
        ok = True
        break
    time.sleep(3)
if ok:
    # 清除 remote URL 中的令牌（改为不含凭证的地址）
    subprocess.run(["git", "remote", "set-url", "origin",
                    "https://github.com/uahz/convenience-store-tycoon.git"],
                   cwd=str(root))
    print("remote token scrubbed")
else:
    print("PUSH FAILED after retries")
