# 临时工具（非交付物）：对打包后的窗口版 exe 运行 --selftest 并读取结果文件。
import pathlib
import subprocess
import sys
import time

EXE = pathlib.Path(sys.argv[1] if len(sys.argv) > 1
                   else r"dist\ConvenienceTycoon.exe")
result_file = EXE.resolve().parent / "selftest_result.txt"
if result_file.exists():
    result_file.unlink()

proc = subprocess.run([str(EXE.resolve()), "--selftest"],
                      timeout=180, capture_output=True)
time.sleep(0.5)
content = result_file.read_text(encoding="utf-8").strip() if result_file.exists() \
    else "(no result file)"
print("returncode:", proc.returncode)
print("selftest_result.txt:", content.splitlines()[0])
