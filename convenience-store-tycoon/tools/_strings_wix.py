# 临时工具（非交付物）：导出 WixToolsetKt.class 的全部可读字符串。
import pathlib
import re
import zipfile

home = pathlib.Path.home()
target = None
for jar in (home / ".gradle/caches/modules-2/files-2.1").rglob(
        "compose-gradle-plugin-1.7.3.jar"):
    target = jar
    break
print("jar:", target)
with zipfile.ZipFile(target) as z:
    data = z.read("org/jetbrains/compose/desktop/application/internal/WixToolsetKt.class")
strings = re.findall(rb"[\x20-\x7e]{5,}", data)
for s in strings:
    print(s.decode())
