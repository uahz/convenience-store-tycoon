# 临时工具（非交付物）：把本地 WiX 目录写入 gradle.properties 的 baseUrl（URL 编码中文）。
import pathlib
import urllib.parse

tools = pathlib.Path("F:/Administrator/Documents/代码/convenience-store-tycoon/tools")
wix_dir = tools / "wix-local"
base = "file:///" + urllib.parse.quote(wix_dir.as_posix(), safe="/:")
print("baseUrl =", base)

prop_file = tools.parent.parent / "convenience-store-tycoon-kmp" / "gradle.properties"
text = prop_file.read_text(encoding="utf-8")
line = f"compose.desktop.wix.download.baseUrl={base}"
if "compose.desktop.wix.download.baseUrl" not in text:
    text = text.rstrip("\n") + "\n" + line + "\n"
else:
    import re
    text = re.sub(r"compose\.desktop\.wix\.download\.baseUrl=.*", line, text)
prop_file.write_text(text, encoding="utf-8")
print("gradle.properties updated")
