# 临时工具（非交付物）：发布 Release v1.0.0 并附三端安装包。
import os
import pathlib
import subprocess

tools = pathlib.Path("F:/Administrator/Documents/代码/convenience-store-tycoon/tools")
token_file = pathlib.Path.home() / "AppData/Local/Temp/gh_upload_token.txt"
token = token_file.read_text(encoding="utf-8").strip()
delivery = (tools.parent.parent /
            "convenience-store-tycoon-kmp/dist-delivery")
env = dict(os.environ)
env["GH_TOKEN"] = token

assets = [
    delivery / "便利店大亨-1.0.0.msi",
    delivery / "便利店大亨-安卓-1.0.2.apk",
    delivery / "便利店大亨-网页版.zip",
]
notes = (
    "## 便利店大亨 v1.0.0（三端 Demo）\n\n"
    "### 下载\n"
    "| 平台 | 文件 | 说明 |\n|---|---|---|\n"
    "| Windows | 便利店大亨-1.0.0.msi | 安装版（含运行时，无需 Java） |\n"
    "| Android 12+ | 便利店大亨-安卓-1.0.2.apk | 直接安装（横屏） |\n"
    "| 网页 | 便利店大亨-网页版.zip | 解压后运行「启动网页版.bat」 |\n\n"
    "### 说明\n"
    "- 实时经营：时钟流动 + 顾客 AI 进店选购排队，随时暂停/加速\n"
    "- 本轮修复：安卓启动闪退（Manifest Activity 类名）、仅适配 Android 12+\n"
    "- 源码与设计文档见仓库主页\n"
)

r = subprocess.run(
    ["gh", "release", "create", "v1.0.0", "--repo",
     "uahz/convenience-store-tycoon",
     "--title", "便利店大亨 v1.0.0（三端 Demo）",
     "--notes", notes,
     *[str(a) for a in assets]],
    env=env, capture_output=True, text=True, timeout=1700)
print("release rc:", r.returncode)
print((r.stdout or "")[-300:], (r.stderr or "")[-300:])
