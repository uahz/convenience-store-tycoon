# 临时工具（非交付物）：解压 JDK/Gradle 并打印工具链版本。
import os
import pathlib
import subprocess
import zipfile

tools = pathlib.Path(__file__).resolve().parent
for name in ("gradle.zip", "jdk17.zip"):
    src = tools / name
    if src.exists():
        print("extracting", name)
        zipfile.ZipFile(src).extractall(tools)
    else:
        print("missing", name)

jdk_dir = next((p for p in tools.iterdir()
                if p.is_dir() and p.name.startswith("jdk-")), None)
print("jdk_dir:", jdk_dir)
print("dirs:", sorted(p.name for p in tools.iterdir() if p.is_dir()))

gradle_bat = tools / "gradle-8.10.2" / "bin" / "gradle.bat"
if jdk_dir and gradle_bat.exists():
    env = dict(os.environ)
    env["JAVA_HOME"] = str(jdk_dir)
    env["PATH"] = str(jdk_dir / "bin") + os.pathsep + env.get("PATH", "")
    r = subprocess.run([str(gradle_bat), "--version"], capture_output=True,
                       text=True, timeout=300, env=env, cwd=str(tools))
    print(r.stdout[-500:])
    if r.returncode != 0:
        print(r.stderr[-500:])
