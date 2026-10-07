# 临时工具（非交付物）：读取 jpackage 参数文件（tmp 根目录）。
import pathlib

base = pathlib.Path(
    "F:/Administrator/Documents/代码/convenience-store-tycoon-kmp/composeApp/build/compose")
args_file = base / "tmp/createRuntimeImage.args.txt"
print("== jpackage args ==")
print(args_file.read_text(encoding="utf-8", errors="replace"))
