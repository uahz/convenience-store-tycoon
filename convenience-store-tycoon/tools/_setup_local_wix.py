# 临时工具（非交付物）：解压本地 WiX 并配置 downloadWix=false。
import pathlib
import zipfile

tools = pathlib.Path("F:/Administrator/Documents/代码/convenience-store-tycoon/tools")
wix_zip = tools / "wix-local" / "wix311-binaries.zip"
wix_root = tools / "wix-local"
if not (wix_root / "wix311" / "light.exe").exists():
    with zipfile.ZipFile(wix_zip) as z:
        z.extractall(wix_root)
print("light.exe:", (wix_root / "wix311" / "light.exe").exists())

prop_file = tools.parent.parent / "convenience-store-tycoon-kmp" / "gradle.properties"
text = prop_file.read_text(encoding="utf-8")
if "compose.desktop.application.downloadWix" not in text:
    text = text.rstrip("\n") + "\ncompose.desktop.application.downloadWix=false\n"
    prop_file.write_text(text, encoding="utf-8")
print("property set")

# 同时更新 _gradle.py 注入 WIX_PATH 环境变量
runner = tools / "_gradle.py"
runner_text = runner.read_text(encoding="utf-8")
needle = 'env["PATH"] = str(jdk_dir / "bin") + os.pathsep + env.get("PATH", "")'
if "WIX_PATH" not in runner_text:
    runner_text = runner_text.replace(
        needle,
        needle + '\nenv["WIX_PATH"] = str(tools / "wix-local" / "wix311")')
    runner.write_text(runner_text, encoding="utf-8")
print("runner patched")
