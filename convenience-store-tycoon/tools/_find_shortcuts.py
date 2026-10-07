# 临时工具（非交付物）：搜索安装产生的快捷方式与实际安装目录。
import pathlib

home = pathlib.Path.home()
hits = []
for base in (home / "AppData/Roaming/Microsoft/Windows/Start Menu",
             home / "Desktop",
             home / "AppData/Local/Programs"):
    if not base.exists():
        continue
    for p in base.rglob("*"):
        if "便利店" in p.name or "tycoon" in p.name.lower():
            hits.append(str(p))
for h in hits[:20]:
    print(h)
print("hits:", len(hits))
