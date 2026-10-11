# 临时工具（非交付物）：用用户提供的 KEY 建仓 → 推送 → 发布 Release。
# 令牌经环境变量传入（GH_TOKEN），不落盘、不回显。
import os
import pathlib
import subprocess
import sys

TOKEN = os.environ.get("GH_UPLOAD_TOKEN")
if not TOKEN:
    print("missing GH_UPLOAD_TOKEN")
    sys.exit(1)
REPO = "uahz/convenience-store-tycoon"
ROOT = pathlib.Path("F:/Administrator/Documents/代码")
DELIVERY = ROOT / "convenience-store-tycoon-kmp/dist-delivery"

env = dict(os.environ)
env["GH_TOKEN"] = TOKEN


def run(cmd, cwd=ROOT, timeout=1800):
    r = subprocess.run(cmd, cwd=str(cwd), env=env, capture_output=True,
                       text=True, timeout=timeout)
    out = (r.stdout or "") + (r.stderr or "")
    tail = "\n".join(out.splitlines()[-6:])
    print("rc:", r.returncode, "|", " ".join(cmd[:4]), "...")
    print(tail)
    return r.returncode


mode = sys.argv[1] if len(sys.argv) > 1 else "all"

if mode in ("all", "repo"):
    # 建公开仓库（幂等：已存在则跳过）
    rc = run(["gh", "repo", "create", REPO, "--public",
              "--description",
              "便利店大亨 · 实时便利店经营模拟（Kotlin 三端：Windows / 网页 / 安卓）"])
    if rc != 0:
        print("(repo 可能已存在，继续)")
    # 配 remote + 推送
    run(["git", "remote", "remove", "origin"])
    rc = run(["git", "remote", "add", "origin",
              f"https://{TOKEN}@github.com/{REPO}.git"])
    rc = run(["git", "push", "-u", "origin", "main"], timeout=1800)

if mode in ("all", "release"):
    assets = [
        DELIVERY / "便利店大亨-1.0.0.msi",
        DELIVERY / "便利店大亨-安卓-1.0.2.apk",
        DELIVERY / "便利店大亨-网页版.zip",
    ]
    notes = (
        "## 便利店大亨 v1.0.0（Demo）\n\n"
        "### 下载\n"
        "- **Windows**：便利店大亨-1.0.0.msi（安装版，含运行时）\n"
        "- **Android 12+**：便利店大亨-安卓-1.0.2.apk\n"
        "- **网页**：便利店大亨-网页版.zip（解压后运行 启动网页版.bat）\n\n"
        "### 更新\n"
        "- 修复安卓启动闪退（Manifest Activity 类名指向错误）\n"
        "- 仅适配 Android 12+（minSdk 31）\n"
        "- 全新 UI 体系与实时经营玩法，详见 README\n"
    )
    rc = run(["gh", "release", "create", "v1.0.0", "--repo", REPO,
              "--title", "便利店大亨 v1.0.0（三端 Demo）",
              "--notes", notes,
              *[str(a) for a in assets]], timeout=1800)
