# 临时工具（非交付物）：生成"WASD 可操控 + 自由镜头"版设计图。
# 关键变化：店长角色可走动（WASD）、镜头跟随/缩放/旋转（滚轮 + Q/E）、走近货架按 E 互动。
import pathlib

OUT = pathlib.Path(__file__).resolve().parent / "design" / "mockups"
OUT.mkdir(parents=True, exist_ok=True)

CSS = """
* { margin:0; padding:0; box-sizing:border-box; font-family:"Microsoft YaHei UI","PingFang SC",sans-serif; }
body { background:#aab4c0; padding:20px; }
.win { width:1060px; border-radius:12px; overflow:hidden; border:1px solid #b9c3ce;
       box-shadow:0 18px 50px rgba(20,35,50,.35); background:#eef1f5; }
.titlebar { height:36px; background:#fff; border-bottom:1px solid #e2e7ee;
            display:flex; align-items:center; padding:0 12px; gap:9px; }
.logo { width:22px; height:22px; border-radius:6px; background:#1f7a5a; color:#fff;
        font-size:12px; font-weight:700; display:flex; align-items:center; justify-content:center; }
.titlebar .t { font-size:12.5px; color:#4a5a6a; font-weight:600; }
.titlebar .btns { margin-left:auto; display:flex; gap:6px; }
.titlebar .btns span { width:12px; height:12px; border-radius:50%; background:#d6dde5; }
.titlebar .btns span.x { background:#e57373; }
.topbar { display:flex; align-items:center; gap:10px; padding:8px 14px; background:#fff;
          border-bottom:1px solid #e2e7ee; }
.chip { display:inline-flex; align-items:center; gap:6px; padding:5px 11px; border-radius:8px;
        background:#f2f5f8; border:1px solid #e0e6ec; font-size:12.5px; color:#22303c; }
.chip b { font-weight:700; }
.chip .star { color:#8a6d1a; letter-spacing:1px; }
.speed { display:flex; border:1px solid #d0d8e0; border-radius:8px; overflow:hidden; }
.speed span { padding:5px 12px; font-size:12.5px; color:#4a5a6a; border-right:1px solid #e0e6ec; }
.speed span.on { background:#1f7a5a; color:#fff; font-weight:700; }
.main { display:flex; gap:12px; padding:12px; }
/* ---------- 世界视口（镜头内容） ---------- */
.viewport { position:relative; flex:1.6; height:540px; border-radius:10px; overflow:hidden;
            border:1px solid #d0d8e0; background:#5e564a; }
.world { position:absolute; inset:-80px; transform-origin:center center; }
.floor { position:absolute; left:80px; top:80px; width:760px; height:520px; background:#e8e2d8;
         border:10px solid #7d6b58;
         background-image:linear-gradient(45deg,#efe9de 25%,transparent 25%),
           linear-gradient(-45deg,#efe9de 25%,transparent 25%),
           linear-gradient(45deg,transparent 75%,#efe9de 75%),
           linear-gradient(-45deg,transparent 75%,#efe9de 75%);
         background-size:36px 36px; background-position:0 0,0 18px,18px -18px,-18px 0; }
.door { position:absolute; left:-10px; bottom:60px; width:12px; height:56px; background:#fff;
        border:2px solid #1f7a5a; border-left:none; border-radius:0 8px 8px 0; }
.shelf { position:absolute; width:150px; height:48px; border-radius:7px; background:#1f7a5a;
         border:2px solid #155c44; padding:5px 8px; color:#fff; box-shadow:0 3px 6px rgba(0,0,0,.18); }
.shelf .nm { font-size:11.5px; font-weight:700; display:flex; gap:6px; }
.shelf .pr { font-size:10px; opacity:.85; margin-top:1px; }
.pips { display:flex; gap:2px; margin-top:4px; }
.pips i { width:8px; height:5px; border-radius:2px; background:rgba(255,255,255,.92); }
.pips i.low { background:#e8b45a; }
.shelf.premium { border-color:#e8b45a; }
.shelf.empty { background:#b9c3ce; border-color:#9aa7b4; }
.counter { position:absolute; width:130px; height:26px; background:#5c4a38; border-radius:6px;
           color:#fff; font-size:10.5px; display:flex; align-items:center; justify-content:center;
           font-weight:700; }
.cust { position:absolute; width:13px; height:13px; border-radius:50%;
        box-shadow:0 2px 4px rgba(0,0,0,.25); }
.cust.office { background:#3a7bd5; } .cust.student { background:#e67e22; }
.cust.senior { background:#8e6cc9; } .cust.gone { background:#c0392b; }
.player { position:absolute; width:18px; height:18px; border-radius:50%; background:#14532d;
          border:3px solid #ffffff; box-shadow:0 0 0 3px rgba(31,122,90,.45), 0 3px 8px rgba(0,0,0,.35); }
.player .ptag { position:absolute; top:-24px; left:50%; transform:translateX(-50%);
        background:#14532d; color:#fff; border-radius:8px; font-size:10px; padding:2px 8px;
        white-space:nowrap; font-weight:700; }
.hint { position:absolute; background:#fff; border:1px solid #1f7a5a; color:#1f7a5a;
        border-radius:8px; font-size:10.5px; padding:3px 9px; font-weight:700;
        box-shadow:0 6px 18px rgba(10,25,40,.25); }
/* HUD 覆盖层（属于视口，不随镜头转） */
.hud-bl { position:absolute; left:10px; bottom:10px; background:rgba(255,255,255,.95);
          border:1px solid #e0e6ec; border-radius:10px; padding:8px 12px; font-size:11px;
          color:#4a5a6a; display:grid; grid-template-columns:1fr 1fr; gap:4px 14px; }
.hud-bl b { color:#22303c; font-size:11px; }
kbd { background:#f0f3f7; border:1px solid #d0d8e0; border-bottom-width:2px; border-radius:5px;
      padding:0 6px; font-size:10.5px; font-family:Consolas,monospace; color:#22303c; }
.minimap { position:absolute; right:10px; top:10px; background:rgba(255,255,255,.95);
           border:1px solid #e0e6ec; border-radius:10px; padding:7px; }
.minimap .map { width:150px; height:104px; background:#e8e2d8; border:2px solid #7d6b58;
                position:relative; border-radius:3px; }
.mm-shelf { position:absolute; width:22px; height:9px; background:#1f7a5a; border-radius:2px; }
.mm-view { position:absolute; border:2px solid #c0392b; border-radius:3px; background:rgba(192,57,43,.08); }
.mm-me { position:absolute; width:7px; height:7px; background:#14532d; border:1.5px solid #fff;
         border-radius:50%; }
.zoomchip { position:absolute; right:10px; bottom:10px; background:rgba(255,255,255,.94);
            border:1px solid #e0e6ec; border-radius:8px; padding:4px 10px; font-size:11px;
            font-weight:700; color:#4a5a6a; }
/* 弹卡 */
.pop { position:absolute; width:240px; background:#fff; border:1px solid #d0d8e0;
       border-radius:11px; padding:12px 14px; box-shadow:0 14px 38px rgba(10,25,40,.30); }
.pop .nm { font-size:13px; font-weight:700; display:flex; gap:7px; align-items:center; }
.pop .sub { font-size:11px; color:#68788a; margin-top:3px; }
.pbar { height:7px; border-radius:4px; background:#e6ebf1; overflow:hidden; }
.pbar i { display:block; height:100%; background:#1f7a5a; border-radius:4px; }
.btnrow { display:grid; grid-template-columns:1fr 1fr 1fr; gap:6px; margin-top:10px; }
.btn { display:inline-flex; align-items:center; justify-content:center;
       padding:6px 10px; border-radius:8px; font-size:11.5px; font-weight:600;
       background:#fff; color:#22303c; border:1px solid #d0d8e0; }
.btn.primary { background:#1f7a5a; border-color:#1f7a5a; color:#fff; }
/* ---------- 右侧栏 ---------- */
.side { flex:1; display:flex; flex-direction:column; gap:10px; height:540px; }
.tabs { display:flex; background:#fff; border:1px solid #e0e6ec; border-radius:9px; overflow:hidden; }
.tabs span { flex:1; text-align:center; padding:8px 0; font-size:12.5px; color:#68788a; }
.tabs span.on { color:#1f7a5a; font-weight:700; background:#e2f1ea; }
.card { background:#fff; border:1px solid #e0e6ec; border-radius:10px; padding:12px 14px; }
.sub { font-size:11.5px; color:#68788a; }
.stat { display:flex; flex-direction:column; }
.stat b { font-size:19px; } .stat b.green { color:#1f7a5a; } .stat b.red { color:#c0392b; }
.tag { display:inline-block; padding:2px 8px; border-radius:6px; font-size:11px; font-weight:600; }
.tag.warn { background:#fdf3e0; color:#b7791f; } .tag.bad { background:#fdeceb; color:#c0392b; }
.tag.ok { background:#e2f1ea; color:#1f7a5a; }
.logline { display:flex; gap:10px; font-size:11.5px; padding:4px 0; border-bottom:1px dashed #eef1f5;
           font-variant-numeric:tabular-nums; }
"""

def page(body: str) -> str:
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head>
<body><div class="win">
  <div class="titlebar"><span class="logo">便</span>
    <span class="t">便利店大亨 · Demo v0.3 可操控版（WASD + 自由镜头）</span>
    <span class="btns"><span></span><span></span><span class="x"></span></span></div>
  {body}
</div></body></html>"""

TOPBAR = """
  <div class="topbar">
    <span class="chip"><b>第 12 天</b> [周三] 14:23</span>
    <div class="speed"><span class="on">▶ 1×</span><span>2×</span><span>4×</span><span>⏸ 空格</span></div>
    <span class="chip">💵 <b>¥19,746.80</b></span>
    <span class="chip">声望 <span class="star">★★★★☆</span> <b>68</b></span>
    <span style="flex:1"></span>
    <span class="chip">净资产 <b>¥26,415</b></span>
  </div>"""

def world(transform, shelves, custs, player_pos, pop=""):
    return (f'<div class="viewport"><div class="world" style="{transform}">'
            f'<div class="floor">'
            + shelves + custs
            + f'<div class="counter" style="left:560px; top:430px">🧾 收银台</div>'
            + f'<div class="door" style="left:-10px; bottom:60px"></div>'
            + f'<div class="player" style="left:{player_pos[0]}px; top:{player_pos[1]}px">'
            f'<span class="ptag">店长（你）</span></div>'
            + pop +
            '</div></div>'
            + HUD_BL + MINIMAP + '</div>')

SHELVES = """
  <div class="shelf premium" style="left:30px; top:24px"><div class="nm">矿泉水</div>
    <div class="pr">30/36 · ¥2.20</div><div class="pips">""" + "<i></i>" * 22 + '<i class="low"></i>' * 6 + """</div></div>
  <div class="shelf" style="left:196px; top:24px"><div class="nm">红烧牛肉面</div>
    <div class="pr">24/36 · ¥4.00</div><div class="pips">""" + "<i></i>" * 18 + '<i class="low"></i>' * 4 + """</div></div>
  <div class="shelf" style="left:362px; top:24px"><div class="nm">全麦面包</div>
    <div class="pr">18/36 · ¥4.50 ⚠</div><div class="pips">""" + "<i></i>" * 13 + '<i class="low"></i>' * 4 + """</div></div>
  <div class="shelf premium" style="left:30px; top:104px"><div class="nm">可乐</div>
    <div class="pr">36/36 · ¥3.50 −20%</div><div class="pips">""" + "<i></i>" * 30 + """</div></div>
  <div class="shelf" style="left:196px; top:104px"><div class="nm">金枪鱼三明治</div>
    <div class="pr">12/36 · ¥9.00 ⚠</div><div class="pips">""" + "<i></i>" * 9 + '<i class="low"></i>' * 3 + """</div></div>
  <div class="shelf empty" style="left:362px; top:104px"><div class="nm" style="color:#5b6a79">（空）</div>
    <div class="pr" style="color:#8a97a4">走近按 E 上货</div></div>"""

CUSTS = """
  <div class="cust office" style="left:150px; top:190px"></div>
  <div class="cust office" style="left:430px; top:88px"></div>
  <div class="cust student" style="left:250px; top:150px"></div>
  <div class="cust student" style="left:330px; top:255px"></div>
  <div class="cust senior" style="left:110px; top:300px"></div>
  <div class="cust senior" style="left:520px; top:330px"></div>
  <div class="cust office" style="left:545px; top:400px"></div>
  <div class="cust student" style="left:515px; top:425px"></div>
  <div class="cust gone" style="left:70px; top:430px"></div>"""

HUD_BL = """
  <div class="hud-bl">
    <span><kbd>W</kbd><kbd>A</kbd><kbd>S</kbd><kbd>D</kbd> <b>移动店长</b></span>
    <span><kbd>滚轮</kbd> <b>缩放镜头</b></span>
    <span><kbd>Q</kbd>/<kbd>E</kbd> <b>旋转镜头</b></span>
    <span><kbd>F</kbd> <b>互动（对准货架/收银台）</b></span>
    <span><kbd>Space</kbd> 暂停 · <kbd>Tab</kbd> 侧栏</span>
    <span><kbd>1×</kbd><kbd>2×</kbd><kbd>4×</kbd> 时间流速</span>
  </div>"""

MINIMAP = ("""<div class="minimap"><div class="map">"""
           + '<div class="mm-shelf" style="left:8px; top:10px"></div>'
           + '<div class="mm-shelf" style="left:36px; top:10px"></div>'
           + '<div class="mm-shelf" style="left:64px; top:10px"></div>'
           + '<div class="mm-shelf" style="left:8px; top:26px"></div>'
           + '<div class="mm-shelf" style="left:36px; top:26px"></div>'
           + '<div class="mm-shelf" style="left:64px; top:26px; background:#b9c3ce"></div>'
           + '<div class="mm-shelf" style="left:110px; top:88px; background:#5c4a38"></div>'
           + '<div class="mm-view" style="left:VIEWX; top:VIEWY; width:VIEWW; height:VIEWH"></div>'
           + '<div class="mm-me" style="left:MEX; top:MEY"></div>'
           + """</div><div class="sub" style="margin-top:5px; text-align:center">小地图</div></div>""")

def minimap(vx, vy, vw, vh, mx, my):
    return (MINIMAP.replace("VIEWX", str(vx)).replace("VIEWY", str(vy))
            .replace("VIEWW", str(vw)).replace("VIEWH", str(vh))
            .replace("MEX", str(mx)).replace("MEY", str(my)))

SIDE_TODAY = """
  <div class="side">
    <div class="tabs"><span class="on">今日</span><span>进货</span><span>定价</span><span>陈列</span><span>报表</span></div>
    <div class="card">
      <div style="display:flex; gap:16px">
        <div class="stat"><span class="sub">今日营收</span><b class="green">¥1,132</b></div>
        <div class="stat"><span class="sub">成交</span><b>71 单</b></div>
        <div class="stat"><span class="sub">客流</span><b>96</b></div>
        <div class="stat"><span class="sub">满意度</span><b>77</b></div>
      </div>
    </div>
    <div class="card">
      <div style="font-weight:700; font-size:12.5px; margin-bottom:6px">实时提醒</div>
      <span class="tag bad">⚠ 缺货：城市晚报（需求 6 次未满足）</span><br><br>
      <span class="tag warn">⚠ 三明治剩 1 天 → 走过去按 F 促销</span>
    </div>
    <div class="card" style="flex:1">
      <div style="font-weight:700; font-size:12.5px; margin-bottom:6px">最近动态</div>
      <div class="logline"><b>14:20</b><span>上班族 购买 可乐×1 三明治×1</span><span style="margin-left:auto; color:#1f7a5a">+¥11.8</span></div>
      <div class="logline"><b>14:22</b><span>学生 购买 可乐×2</span><span style="margin-left:auto; color:#1f7a5a">+¥5.6</span></div>
      <div class="logline"><b>14:23</b><span style="color:#c0392b">银发族 想买晚报 — 缺货离开</span></div>
      <div class="logline"><b>14:23</b><span>银发族 购买 抽纸×1</span><span style="margin-left:auto; color:#1f7a5a">+¥4.5</span></div>
    </div>
  </div>"""

# ---- u01：全景（镜头缩放 70%，轻微旋转 -6°，店长站在卖场中间） ----
u01 = page(TOPBAR + '<div class="main">'
           + world("transform: rotate(-6deg) scale(.86);",
                   SHELVES, CUSTS, (365, 280))
           + SIDE_TODAY + "</div>")

# ---- u02：走近三明治货架按 F 互动（镜头拉近 190% 并旋转 8°，弹出操作卡） ----
POP = ("""<div class="pop" style="left:196px; top:168px">
  <div class="nm">金枪鱼三明治 <span class="tag warn">剩1天</span></div>
  <div class="sub">售价 ¥9.00（参考 ¥9.00）· 今日 8 件 · 库存 12/36</div>
  <div class="pbar" style="margin-top:6px"><i style="width:33%; background:#b7791f"></i></div>
  <div class="btnrow"><span class="btn">✎ 改价</span><span class="btn">🏷 促销</span>
  <span class="btn primary">＋ 补货</span></div>
  <div class="sub" style="margin-top:8px"><kbd>F</kbd> 打开 · <kbd>Esc</kbd> 关闭 · 操作立即生效</div>
</div>
<div class="hint" style="left:330px; top:120px">按 F 互动</div>""")
u02 = page(TOPBAR + '<div class="main">'
           + world("transform: rotate(8deg) scale(1.55);",
                   SHELVES, CUSTS, (300, 176), POP)
           + SIDE_TODAY + "</div>")

SCREENS = {"u01_wasd_camera": u01, "u02_interact_popover": u02}
for name, html in SCREENS.items():
    (OUT / f"{name}.html").write_text(html, encoding="utf-8")
print("written:", len(SCREENS), "->", OUT)
