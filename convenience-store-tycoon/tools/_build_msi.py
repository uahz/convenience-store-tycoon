# 临时工具（非交付物）：用 WiX 打 MSI 安装程序（per-user，含快捷方式与卸载）。
import pathlib
import subprocess
import uuid

wix = pathlib.Path(
    "F:/Administrator/Documents/代码/convenience-store-tycoon/tools/wix-local")
src = pathlib.Path(
    "F:/Administrator/Documents/代码/convenience-store-tycoon-kmp/dist-pc/ConvenienceTycoon")
work = pathlib.Path(
    "F:/Administrator/Documents/代码/convenience-store-tycoon-kmp/dist-delivery/_msi")
work.mkdir(parents=True, exist_ok=True)
upgrade_code = "8C4E7F52-1B3D-4E9A-9F7E-2C6D5A1B0F3A"
guid_a = str(uuid.uuid4()).upper()
guid_b = str(uuid.uuid4()).upper()
icon_abs = (r"F:\Administrator\Documents\代码\convenience-store-tycoon-kmp"
            r"\composeApp\icons\game.ico")

# 1) heat 收集文件
files_wxs = work / "AppFiles.wxs"
r1 = subprocess.run([
    str(wix / "heat.exe"), "dir", str(src),
    "-gg", "-g1", "-srd", "-sreg", "-sfrag",
    "-cg", "AppFiles", "-dr", "INSTALLFOLDER",
    "-var", "var.SourceRoot", "-out", str(files_wxs),
], capture_output=True, text=False)
print("heat rc:", r1.returncode,
      r1.stderr.decode("gbk", errors="replace")[-300:])
assert r1.returncode == 0 and files_wxs.exists()

# 2) Product.wxs（per-user，中文，快捷方式）
product_wxs = f'''<?xml version="1.0" encoding="utf-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
  <Product Id="*" Name="便利店大亨" Language="2052" Codepage="936"
           Version="1.0.0" Manufacturer="Convenience Tycoon"
           UpgradeCode="{upgrade_code}">
    <Package InstallerVersion="200" Compressed="yes"
             InstallScope="perUser" Description="便利店大亨安装程序"
             Comments="实时便利店经营模拟" />
    <MajorUpgrade AllowSameVersionUpgrades="yes"
                  DowngradeErrorMessage="已安装更高版本。" />
    <MediaTemplate EmbedCab="yes" />
    <Icon Id="AppIcon" SourceFile="{icon_abs}" />
    <Property Id="ARPPRODUCTICON" Value="AppIcon" />
    <Property Id="ARPHELPLINK" Value="https://github.com/uahz" />

    <Directory Id="TARGETDIR" Name="SourceDir">
      <Directory Id="ProgramMenuFolder">
        <Directory Id="AppMenuDir" Name="便利店大亨">
          <Component Id="ShortcutStartMenu" Guid="{guid_a}" Win64="yes">
            <RegistryValue Root="HKCU" Key="Software\\ConvenienceTycoon"
                           Name="sm" Type="integer" Value="1" KeyPath="yes" />
            <Shortcut Id="StartMenuShortcut" Name="便利店大亨"
                      Description="实时便利店经营模拟"
                      Target="[INSTALLFOLDER]runtime\\bin\\javaw.exe"
                      Arguments='-jar "[INSTALLFOLDER]ConvenienceTycoon.jar"'
                      WorkingDirectory="INSTALLFOLDER" />
            <RemoveFolder Id="RemoveAppMenuDir" On="uninstall" />
          </Component>
        </Directory>
      </Directory>
      <Directory Id="DesktopFolder">
        <Component Id="ShortcutDesktop" Guid="{guid_b}" Win64="yes">
          <RegistryValue Root="HKCU" Key="Software\\ConvenienceTycoon"
                         Name="dt" Type="integer" Value="1" KeyPath="yes" />
          <Shortcut Id="DesktopShortcut" Name="便利店大亨"
                    Description="实时便利店经营模拟"
                    Target="[INSTALLFOLDER]runtime\\bin\\javaw.exe"
                    Arguments='-jar "[INSTALLFOLDER]ConvenienceTycoon.jar"'
                    WorkingDirectory="INSTALLFOLDER" />
        </Component>
      </Directory>
      <Directory Id="LocalAppDataFolder">
        <Directory Id="ProgramsDir" Name="Programs">
          <Directory Id="INSTALLFOLDER" Name="ConvenienceTycoon" />
        </Directory>
      </Directory>
    </Directory>

    <Feature Id="Main" Title="便利店大亨" Level="1">
      <ComponentGroupRef Id="AppFiles" />
      <ComponentRef Id="ShortcutStartMenu" />
      <ComponentRef Id="ShortcutDesktop" />
    </Feature>
  </Product>
</Wix>
'''
product_file = work / "Product.wxs"
product_file.write_text(product_wxs, encoding="utf-8")

# 3) candle
for wxs in (product_file, files_wxs):
    r = subprocess.run([
        str(wix / "candle.exe"), "-arch", "x64",
        f"-dSourceRoot={src}", "-out", str(wxs.with_suffix(".wixobj")),
        str(wxs),
    ], capture_output=True, text=False, cwd=str(work))
    print("candle", wxs.name, "rc:", r.returncode)
    print(r.stdout.decode("gbk", errors="replace")[-1500:])
    print(r.stderr.decode("gbk", errors="replace")[-500:])
    if r.returncode != 0:
        raise SystemExit(1)

# 4) light
msi = work / "便利店大亨-1.0.0.msi"
r = subprocess.run([
    str(wix / "light.exe"),
    str(work / "Product.wixobj"), str(work / "AppFiles.wixobj"),
    "-out", str(msi),
], capture_output=True, text=False)
print("light rc:", r.returncode)
print(r.stdout.decode("gbk", errors="replace")[-2500:])
if r.returncode == 0:
    print("MSI:", msi, f"{msi.stat().st_size / 1e6:.1f} MB")
