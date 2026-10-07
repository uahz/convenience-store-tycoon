# 临时工具（非交付物）：检查暂存清单（数量、大文件、排除项是否生效）。
import pathlib

lines = pathlib.Path(
    "F:/Administrator/Documents/代码/convenience-store-tycoon/tools/_gitstatus.txt"
).read_text(encoding="utf-8", errors="replace").splitlines()
print("staged entries:", len(lines))

bad = [l for l in lines if any(
    k in l for k in (".jar", ".msi", ".exe", "jdk-", "gradle-8",
                     "android-sdk", "wix-local", "dist-pc", "dist-web",
                     "_msi/", "local.properties"))]
print("suspicious big/artifact entries:", len(bad))
for l in bad[:10]:
    print("  ", l[:120])

big = []
for l in lines:
    if l.startswith("A  ") or l.startswith("M  "):
        p = pathlib.Path("F:/Administrator/Documents/代码") / l[3:].strip('"')
        try:
            if p.is_file() and p.stat().st_size > 50_000_000:
                big.append((l[:100], p.stat().st_size / 1e6))
        except OSError:
            pass
print("files >50MB staged:", len(big))
for l, mb in big:
    print(f"  {l} {mb:.0f}MB")
