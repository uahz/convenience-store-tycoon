# 临时工具（非交付物）：SSH 通道推送（临时密钥：生成→注册→推送→注销→删除）。
import json
import os
import pathlib
import subprocess

tools = pathlib.Path("F:/Administrator/Documents/代码/convenience-store-tycoon/tools")
root = tools.parent.parent
key = tools / "_upload_key"
token_file = pathlib.Path.home() / "AppData/Local/Temp/gh_upload_token.txt"
token = token_file.read_text(encoding="utf-8").strip()
REPO_SSH = "ssh://git@ssh.github.com:443/uahz/convenience-store-tycoon.git"

env = dict(os.environ)
env["GH_TOKEN"] = token

# 1) 生成临时密钥
if not key.exists():
    subprocess.run(["ssh-keygen", "-t", "ed25519", "-N", "", "-f", str(key),
                    "-C", "ctycoon-upload-temp"],
                   capture_output=True, timeout=60)
pub = (key.with_suffix(".pub")).read_text(encoding="utf-8").strip()
print("key ready:", key.exists())

# 2) 注册公钥到账号（用后删除）
r = subprocess.run(["gh", "api", "/user/keys", "-f", "title=ctycoon-upload-temp",
                    "-f", "key=" + pub],
                   env=env, capture_output=True, text=True, timeout=60)
import json
key_id = None
try:
    key_id = json.loads(r.stdout)["id"]
except Exception:
    pass
print("key registered:", key_id is not None, r.stdout[:120] if key_id is None else "")

# 3) SSH 推送（443 端口）
ssh_cmd = f'ssh -i "{key}" -o StrictHostKeyChecking=accept-new'
push = subprocess.run(["git", "push", "-u", REPO_SSH, "main"],
                      cwd=str(root), env={**env, "GIT_SSH_COMMAND": ssh_cmd},
                      capture_output=True, text=True, timeout=550)
print("push rc:", push.returncode)
print((push.stdout or "")[-500:], (push.stderr or "")[-500:])

# 4) 注销并删除临时密钥
if key_id:
    subprocess.run(["gh", "api", "-X", "DELETE", f"/user/keys/{key_id}"],
                   env=env, capture_output=True, timeout=60)
    print("temp key revoked:", key_id)
for p in (key, key.with_suffix(".pub")):
    if p.exists():
        p.unlink()
print("local key removed")

# 5) remote 换成不带令牌的 https 地址（如果之前带 token）
subprocess.run(["git", "remote", "set-url", "origin",
                "https://github.com/uahz/convenience-store-tycoon.git"],
               cwd=str(root), capture_output=True)
print("origin URL scrubbed")
