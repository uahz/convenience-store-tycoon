# 临时工具（非交付物）：一键完成 dist-pc → MSI → 静默安装 → 归档。
import pathlib
import shutil
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
for script in ("_package_pc.py", "_build_msi.py",
               "_install_and_collect.py", "_find_shortcuts.py"):
    r = subprocess.run(["python", str(HERE / script)], capture_output=True,
                       text=False, timeout=900)
    out = r.stdout.decode("gbk", errors="replace")
    print(f"===== {script} rc={r.returncode} =====")
    print("\n".join(out.splitlines()[-8:]))
    if r.returncode != 0:
        print(r.stderr.decode("gbk", errors="replace")[-800:])
        raise SystemExit(1)
