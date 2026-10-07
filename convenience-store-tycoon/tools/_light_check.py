# 临时工具（非交付物）：检查 MSI 是否生成 + 导出 light 完整输出。
import pathlib
import subprocess

wix = pathlib.Path(
    "F:/Administrator/Documents/代码/convenience-store-tycoon/tools/wix-local")
work = pathlib.Path(
    "F:/Administrator/Documents/代码/convenience-store-tycoon-kmp/dist-delivery/_msi")
msi = work / "便利店大亨-1.0.0.msi"
print("msi exists:", msi.exists(), msi.stat().st_size if msi.exists() else 0)

r = subprocess.run([
    str(wix / "light.exe"),
    str(work / "Product.wixobj"), str(work / "AppFiles.wixobj"),
    "-out", str(msi),
], capture_output=True, text=False)
out = r.stdout.decode("gbk", errors="replace")
err = r.stderr.decode("gbk", errors="replace")
all_text = out + "\n=== STDERR ===\n" + err
lines = [l for l in all_text.splitlines()
         if "LGHT1076" not in l and l.strip()]
(pathlib.Path(__file__).resolve().parent / "_light_out.txt").write_text(
    "\n".join(lines[-40:]), encoding="utf-8")
print("rc:", r.returncode)
print("non-warning lines:", len(lines))
