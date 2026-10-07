# 临时工具（非交付物）：验证 JDK/Gradle 可用。
import pathlib
import subprocess

tools = pathlib.Path(".")
jdk_dir = next(
    (p for p in tools.iterdir()
     if p.is_dir() and p.name.startswith(("jdk", "jdk-microsoft"))),
    None,
)
print("jdk_dir:", jdk_dir)
gradle_bat = tools / "gradle-8.10.2" / "bin" / "gradle.bat"
print("gradle_bat exists:", gradle_bat.exists())
if jdk_dir and gradle_bat.exists():
    import os
    env = dict(os.environ)
    env["JAVA_HOME"] = str(jdk_dir)
    env["PATH"] = str(jdk_dir / "bin") + os.pathsep + env.get("PATH", "")
    r = subprocess.run([str(gradle_bat), "--version"], capture_output=True,
                       text=True, timeout=300, env=env, cwd=".")
    print(r.stdout[-600:])
    print(r.stderr[-300:])
