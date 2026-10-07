# 临时工具（非交付物）：统一 Gradle 构建驱动（设置 JAVA_HOME、GBK 兼容输出）。
import os
import pathlib
import subprocess
import sys

tools = pathlib.Path(__file__).resolve().parent
root = tools.parent.parent
proj = root / "convenience-store-tycoon-kmp"
jdk_dir = next(p for p in tools.iterdir()
               if p.is_dir() and p.name.startswith("jdk-"))
gradle_bat = tools / "gradle-8.10.2" / "bin" / "gradle.bat"

env = dict(os.environ)
env["JAVA_HOME"] = str(jdk_dir)
env["PATH"] = str(jdk_dir / "bin") + os.pathsep + env.get("PATH", "")
env["WIX_PATH"] = str(tools / "wix-local")

args = sys.argv[1:] or ["--version"]
r = subprocess.run([str(gradle_bat), *args], cwd=str(proj), env=env,
                   capture_output=True, timeout=3500)
out = r.stdout.decode("gbk", errors="replace")
err = r.stderr.decode("gbk", errors="replace")
print(out[-6000:])
if r.returncode != 0:
    print("=== STDERR ===")
    print(err[-3000:])
print("EXIT:", r.returncode)
sys.exit(r.returncode)
