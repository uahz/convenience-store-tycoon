# 临时工具（非交付物）：在 Compose Gradle 插件 jar 中查找 WiX 下载相关的属性名。
import pathlib
import zipfile

home = pathlib.Path.home()
hits = []
for jar in (home / ".gradle/caches/modules-2/files-2.1").rglob("*gradle-plugin*.jar"):
    try:
        with zipfile.ZipFile(jar) as z:
            for n in z.namelist():
                if n.endswith(".class") and ("wix" in n.lower() or "Wix" in n):
                    data = z.read(n)
                    for needle in (b"baseUrl", b"wix.download", b"wix311"):
                        idx = data.find(needle)
                        if idx >= 0:
                            seg = data[max(0, idx - 60):idx + 90]
                            hits.append((jar.name, n, seg))
                            break
    except Exception:
        pass
for jar, n, seg in hits[:12]:
    print("==", jar, n)
    print("   ", seg)
print("total hits:", len(hits))
