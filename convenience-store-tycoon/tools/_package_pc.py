# 临时工具（非交付物）：组装免安装 PC 包（jar + 内置 JRE + 启动脚本）。
import pathlib
import shutil

kmp = pathlib.Path("F:/Administrator/Documents/代码/convenience-store-tycoon-kmp")
tools = pathlib.Path("F:/Administrator/Documents/代码/convenience-store-tycoon/tools")
jar = kmp / "composeApp/build/compose/jars/ConvenienceTycoon-windows-x64-1.0.0.jar"
jdk = next(p for p in tools.iterdir()
           if p.is_dir() and p.name.startswith("jdk-"))

out = kmp / "dist-pc" / "ConvenienceTycoon"
out.mkdir(parents=True, exist_ok=True)
shutil.copy2(jar, out / "ConvenienceTycoon.jar")
runtime = out / "runtime"
if not runtime.exists():
    shutil.copytree(jdk, runtime,
                    ignore=shutil.ignore_patterns("*.zip", "demo", "jmods"))
bat = out / "启动游戏.bat"
bat.write_text(
    "@echo off\r\n"
    "start \"\" \"%~dp0runtime\\bin\\javaw.exe\" -jar \"%~dp0ConvenienceTycoon.jar\"\r\n",
    encoding="gbk",
)
readme = out / "说明.txt"
readme.write_text(
    "便利店大亨 · Convenience Tycoon（PC 免安装版）\r\n"
    "=============================================\r\n"
    "双击「启动游戏.bat」即可开始游戏。\r\n"
    "存档保存在本程序目录的 saves/ 文件夹中。\r\n",
    encoding="utf-8",
)
print("PC package at:", out)
print("jar:", (out / "ConvenienceTycoon.jar").stat().st_size)
