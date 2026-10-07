# 临时工具（非交付物）：查看 yarn tgz 内部结构。
import tarfile
import pathlib

tools = pathlib.Path(__file__).resolve().parent
with tarfile.open(tools / "cache_yarn.tgz") as t:
    names = t.getnames()
print("entries:", len(names))
for n in names[:8]:
    print(" ", n)
