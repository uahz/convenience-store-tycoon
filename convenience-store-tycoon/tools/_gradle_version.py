# 临时工具（非交付物）：以二进制模式运行 gradle --version（兼容 GBK 输出）。
import os
import pathlib
import subprocess

tools = pathlib.Path(__file__).resolve().parent
jdk_dir = next(p for p in tools.iterdir()
               if p.is_dir() and p.name.startswith("jdk-"))
gradle_bat = tools / "gradle-8.10.2" / "bin" / "gradle.bat"
env = dict(os.environ)
env["JAVA_HOME"] = str(jdk_dir)
env["PATH"] = str(jdk_dir / "bin") + os.pathsep + env.get("PATH", "")
r = subprocess.run([str(gradle_bat), "--version"], capture_output=True,
                   timeout=300, env=env, cwd=str(tools))
out = r.stdout.decode("gbk", errors="replace")
print(out)
