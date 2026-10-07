# 临时测试驱动（非交付物）：以子进程运行打包后的 exe，喂入按键序列并检查关键画面。
import subprocess
import sys

EXE = sys.argv[1]
SCRIPT = """1
2
1
1 2
2 2
3 2
4 2
5 2
y


3
1 1

2 2

3 4

4 5

5 7


6


3

0
0
0
"""

proc = subprocess.run([EXE, "--ascii"], input=SCRIPT, encoding="utf-8",
                      errors="replace", capture_output=True, timeout=120)
out = proc.stdout or ""
err = proc.stderr or ""
print("returncode:", proc.returncode)
markers = ["晨间准备", "进货订货", "货架陈列", "营业实录", "结算单", "今日净利",
           "夜间运营", "已保存", "第 2 天", "全日:"]
ok = True
for m in markers:
    hit = m in out
    ok = ok and hit
    print(f"  [{'OK' if hit else 'MISS'}] {m}")
print("---- stdout tail ----")
print("\n".join(out.splitlines()[-28:]))
if err.strip():
    print("---- stderr ----")
    print(err[-800:])
sys.exit(0 if ok and proc.returncode == 0 else 1)
