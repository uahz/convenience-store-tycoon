# 临时工具（非交付物）：重命名交付资产为 ASCII 并替换 Release 资产（标注端别）。
import json
import os
import pathlib
import shutil
import subprocess

root = pathlib.Path("F:/Administrator/Documents/代码")
delivery = root / "convenience-store-tycoon-kmp/dist-delivery"
token_file = pathlib.Path.home() / "AppData/Local/Temp/gh_upload_token.txt"
token = token_file.read_text(encoding="utf-8").strip()
env = dict(os.environ)
env["GH_TOKEN"] = token
REPO = "uahz/convenience-store-tycoon"


def gh(args, timeout=900):
    r = subprocess.run(["gh", *args], env=env, capture_output=True,
                       text=True, timeout=timeout)
    return r


# 1) 现有资产清单
r = gh(["api", f"/repos/{REPO}/releases"])
rel = json.loads(r.stdout)[0]
print("release:", rel["tag_name"], rel["id"])
old_assets = {a["name"]: a["id"] for a in rel["assets"]}
print("old assets:", list(old_assets))

# 2) 本地重命名为 ASCII（平台+版本清晰标注）
renames = {
    "便利店大亨-1.0.0.msi": "ConvenienceTycoon-Windows-Setup-v1.0.0.msi",
    "便利店大亨-安卓-1.0.2.apk": "ConvenienceTycoon-Android-v1.0.2.apk",
    "便利店大亨-网页版.zip": "ConvenienceTycoon-Web-v1.0.0.zip",
}
local_new = {}
for old_cn, new_name in renames.items():
    src = delivery / old_cn
    dst = delivery / new_name
    if src.exists():
        shutil.move(str(src), str(dst))
    local_new[new_name] = dst
    print("renamed:", dst.name, f"{dst.stat().st_size / 1e6:.1f} MB")

# 3) 删除旧资产
for name, aid in old_assets.items():
    r = gh(["api", "-X", "DELETE", f"/repos/{REPO}/releases/assets/{aid}"])
    print("deleted asset:", name, r.returncode)

# 4) 上传新资产
r = gh(["release", "upload", "v1.0.0",
        *[str(p) for p in local_new.values()], "--clobber"], timeout=1700)
print("upload rc:", r.returncode)

# 5) 更新 Release 说明中的文件名表格
notes = (
    "## 便利店大亨 v1.0.0（三端 Demo）\n\n"
    "### 下载（文件名即平台标注）\n"
    "| 平台 | 文件 | 说明 |\n|---|---|---|\n"
    "| **Windows PC** | ConvenienceTycoon-Windows-Setup-v1.0.0.msi | "
    "安装版（含运行时，无需 Java，开始菜单+桌面快捷方式） |\n"
    "| **Android 12+** | ConvenienceTycoon-Android-v1.0.2.apk | "
    "直接安装（横屏，支持 Android 12 及以上） |\n"
    "| **网页** | ConvenienceTycoon-Web-v1.0.0.zip | "
    "解压后运行「启动网页版.bat」，浏览器即玩 |\n\n"
    "### 更新\n"
    "- 修复安卓启动闪退（Manifest Activity 类名指向错误）\n"
    "- 仅适配 Android 12+（minSdk 31）\n"
    "- 全新 UI 体系与实时经营玩法，详见仓库主页\n"
)
r = gh(["release", "edit", "v1.0.0", "--repo", REPO, "--notes", notes])
print("notes update rc:", r.returncode)

# 6) 最终资产校验
r = gh(["api", f"/repos/{REPO}/releases"])
rel = json.loads(r.stdout)[0]
for a in rel["assets"]:
    print("asset:", a["name"], f"{a['size'] / 1e6:.1f} MB")
