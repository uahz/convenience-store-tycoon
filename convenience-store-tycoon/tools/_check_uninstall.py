# 临时工具（非交付物）：PowerShell 确认卸载注册表项。
import subprocess

r = subprocess.run(
    ["powershell", "-NoProfile", "-Command",
     "Get-ItemProperty 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*',"
     "'HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*',"
     "'HKLM:\\Software\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*' "
     "-ErrorAction SilentlyContinue | "
     "Where-Object { $_.DisplayName -like '*便利店*' -or $_.DisplayName -like '*Tycoon*' } | "
     "Select-Object DisplayName, DisplayVersion, InstallLocation | Format-List"],
    capture_output=True, text=False, timeout=60)
out = r.stdout.decode("gbk", errors="replace")
print(out if out.strip() else "(no uninstall entry found)")
