# 临时工具（非交付物）：生成窗口版 GUI 的静态设计图（HTML），供截图评审。
# 设计与后续 Tkinter 实现保持同一套主题（浅色商务风、绿色主色）。
import pathlib

OUT = pathlib.Path(__file__).resolve().parent / "design" / "mockups"
OUT.mkdir(parents=True, exist_ok=True)

CSS = """
* { margin:0; padding:0; box-sizing:border-box; font-family:"Microsoft YaHei UI","PingFang SC",sans-serif; }
body { background:#aab4c0; padding:20px; }
.win { width:1040px; border-radius:12px; overflow:hidden; border:1px solid #b9c3ce;
       box-shadow:0 18px 50px rgba(20,35,50,.35); background:#eef1f5; }
.titlebar { height:38px; background:#ffffff; border-bottom:1px solid #e2e7ee;
            display:flex; align-items:center; padding:0 14px; gap:10px; }
.logo { width:22px; height:22px; border-radius:6px; background:#1f7a5a; color:#fff;
        font-size:12px; font-weight:700; display:flex; align-items:center; justify-content:center; }
.titlebar .t { font-size:12.5px; color:#4a5a6a; font-weight:600; }
.titlebar .btns { margin-left:auto; display:flex; gap:6px; }
.titlebar .btns span { width:12px; height:12px; border-radius:50%; background:#d6dde5; }
.titlebar .btns span.x { background:#e57373; }
.statusbar { display:flex; align-items:center; gap:12px; padding:10px 18px;
             background:#ffffff; border-bottom:1px solid #e2e7ee; }
.chip { display:inline-flex; align-items:center; gap:6px; padding:6px 12px; border-radius:8px;
        background:#f2f5f8; border:1px solid #e0e6ec; font-size:13px; color:#22303c; }
.chip b { font-weight:700; }
.chip .star { color:#8a6d1a; letter-spacing:1px; }
.body { padding:18px 20px; position:relative; }
h1.screen-title { font-size:20px; color:#22303c; }
.sub { font-size:12.5px; color:#68788a; margin-top:4px; }
.card { background:#fff; border:1px solid #e0e6ec; border-radius:10px; }
.btn { display:inline-flex; align-items:center; justify-content:center; gap:6px;
       padding:10px 18px; border-radius:9px; font-size:13.5px; font-weight:600;
       background:#fff; color:#22303c; border:1px solid #d0d8e0; cursor:default; }
.btn.primary { background:#1f7a5a; border-color:#1f7a5a; color:#fff; }
.btn.big { padding:14px 22px; font-size:15px; }
.btn.danger-soft { color:#c0392b; border-color:#ecc8c4; background:#fdf3f2; }
.tag { display:inline-block; padding:2px 8px; border-radius:6px; font-size:11.5px; font-weight:600; }
.tag.warn { background:#fdf3e0; color:#b7791f; }
.tag.bad  { background:#fdeceb; color:#c0392b; }
.tag.ok   { background:#e2f1ea; color:#1f7a5a; }
.tag.gold { background:#f7efd8; color:#8a6d1a; }
table.grid { width:100%; border-collapse:collapse; font-size:12.5px; background:#fff; }
table.grid th { text-align:left; font-size:12px; color:#4a5a6a; background:#f0f3f7;
                padding:8px 10px; border-bottom:1px solid #e0e6ec; white-space:nowrap; }
table.grid td { padding:7px 10px; border-bottom:1px solid #eef1f5; color:#22303c; white-space:nowrap; }
table.grid tr:last-child td { border-bottom:none; }
.num { text-align:right; font-variant-numeric:tabular-nums; }
.pbar { height:8px; border-radius:5px; background:#e6ebf1; overflow:hidden; }
.pbar i { display:block; height:100%; background:#1f7a5a; border-radius:5px; }
.overlay { position:absolute; inset:0; background:rgba(24,36,48,.45); display:flex;
           align-items:center; justify-content:center; }
.modal { width:460px; background:#fff; border-radius:12px; padding:20px 22px;
         box-shadow:0 16px 44px rgba(10,25,40,.35); }
.modal h2 { font-size:16px; margin-bottom:4px; }
.modal .m-sub { font-size:12px; color:#68788a; margin-bottom:14px; }
.footerbar { display:flex; align-items:center; gap:10px; padding:14px 0 2px; }
.spacer { flex:1; }
"""

def page(body: str, with_status: bool = True) -> str:
    status = """
  <div class="statusbar">
    <span class="chip">📅 第 12 天 [周三]</span>
    <span class="chip">💵 现金 <b>¥19,746.80</b></span>
    <span class="chip">声望 <span class="star">★★★★☆</span> <b>68</b></span>
    <span class="chip">净资产 <b>¥26,415</b></span>
    <span class="spacer"></span>
    <span class="chip" style="color:#68788a">目标 ¥200,000</span>
  </div>""" if with_status else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head>
<body><div class="win">
  <div class="titlebar"><span class="logo">便</span>
    <span class="t">便利店大亨 · Demo v0.1.0</span>
    <span class="btns"><span></span><span></span><span class="x"></span></span></div>
  {status}
  <div class="body">{body}</div>
</div></body></html>"""

def table(headers, rows, num_cols=()):
    ths = "".join(f'<th class="{"num" if i in num_cols else ""}">{h}</th>'
                  for i, h in enumerate(headers))
    trs = []
    for r in rows:
        tds = "".join(f'<td class="{"num" if i in num_cols else ""}">{c}</td>'
                      for i, c in enumerate(r))
        trs.append(f"<tr>{tds}</tr>")
    return f'<table class="grid"><thead><tr>{ths}</tr></thead><tbody>{"".join(trs)}</tbody></table>'

# ---------------- s01 主菜单 ----------------
s01 = page(with_status=False, body="""
 <div style="text-align:center; padding:56px 0 10px">
   <div style="font-size:46px">🏪</div>
   <h1 class="screen-title" style="font-size:30px; letter-spacing:6px; margin-top:8px">便 利 店 大 亨</h1>
   <div class="sub" style="font-size:13px; letter-spacing:2px; margin-top:6px">街角生意 · 日进斗金 —— 单人经营模拟</div>
 </div>
 <div style="width:420px; margin:26px auto 8px; display:flex; flex-direction:column; gap:10px">
   <span class="btn primary big">▶ 开始新游戏</span>
   <span class="btn big">📂 继续游戏（读取自动存档）</span>
   <span class="btn big">📖 玩法说明</span>
   <span class="btn big">⚙ 设置</span>
   <span class="btn danger-soft big">✕ 退出</span>
 </div>
 <div class="sub" style="text-align:center; padding:14px 0 30px">Demo v0.1.0 · 窗口版 · 存档位于程序同目录 saves/ 下</div>
""")

# ---------------- s02 难度选择 ----------------
s02 = page(with_status=False, body="""
 <div style="text-align:center; padding:40px 0 10px">
   <h1 class="screen-title">选择难度</h1>
   <div class="sub">三种开局强度，胜利线与经营压力不同</div>
 </div>
 <div style="width:760px; margin:18px auto; display:flex; flex-direction:column; gap:12px">
   <div class="card" style="padding:16px 18px; display:flex; align-items:center; gap:16px">
     <div style="width:86px"><span class="tag ok">轻松</span></div>
     <div style="flex:1; font-size:13px; color:#4a5a6a">初始资金 ¥25,000 · 客流 ×1.30 · 房租 ×0.85</div>
     <div style="font-size:12.5px; color:#68788a">胜利线 ¥150,000</div><span class="btn">选择</span>
   </div>
   <div class="card" style="padding:16px 18px; display:flex; align-items:center; gap:16px; border:2px solid #1f7a5a">
     <div style="width:86px"><span class="tag gold">普通</span></div>
     <div style="flex:1; font-size:13px; color:#4a5a6a">初始资金 ¥20,000 · 客流 ×1.00 · 房租 ×1.00</div>
     <div style="font-size:12.5px; color:#68788a">胜利线 ¥200,000</div><span class="btn primary">选择</span>
   </div>
   <div class="card" style="padding:16px 18px; display:flex; align-items:center; gap:16px">
     <div style="width:86px"><span class="tag bad">硬核</span></div>
     <div style="flex:1; font-size:13px; color:#4a5a6a">初始资金 ¥15,000 · 客流 ×0.85 · 房租 ×1.25</div>
     <div style="font-size:12.5px; color:#68788a">胜利线 ¥260,000</div><span class="btn">选择</span>
   </div>
   <div style="text-align:center; padding-top:8px"><span class="btn" style="padding:8px 26px">返回</span></div>
 </div>
""")

# ---------------- s03 晨间准备 ----------------
s03 = page(body="""
 <div style="display:flex; align-items:baseline; gap:14px">
   <h1 class="screen-title">第 12 天 [周三] · 晨间准备</h1>
   <span class="sub">开门前把货备齐、价定好、架摆满</span>
 </div>
 <div style="display:flex; gap:10px; margin-top:12px">
   <span class="tag bad">今晨报废：城市晚报 ×10，损失 ¥8.00</span>
   <span class="tag warn">⚠ 临期：全麦面包 ×12（剩 2 天）→ 建议促销</span>
   <span class="tag warn">⚠ 滞销：抽纸（周转超标 1.8 倍）</span>
 </div>
 <div style="display:flex; gap:12px; margin-top:14px">
   <div class="card" style="flex:1; padding:14px 16px">
     <div class="sub">仓库容量</div>
     <div style="font-size:22px; font-weight:700; margin:4px 0 8px">142<span style="font-size:13px; color:#68788a"> / 300 件</span></div>
     <div class="pbar"><i style="width:47%"></i></div>
   </div>
   <div class="card" style="flex:1; padding:14px 16px">
     <div class="sub">货架在售</div>
     <div style="font-size:22px; font-weight:700; margin:4px 0 8px">5<span style="font-size:13px; color:#68788a"> / 6 槽（86 件）</span></div>
     <div class="pbar"><i style="width:83%"></i></div>
   </div>
   <div class="card" style="flex:1; padding:14px 16px">
     <div class="sub">进行中促销</div>
     <div style="font-size:22px; font-weight:700; margin:4px 0 8px">2<span style="font-size:13px; color:#68788a"> 个（可乐 −20% 等）</span></div>
     <div class="pbar"><i style="width:33%; background:#b7791f"></i></div>
   </div>
 </div>
 <div style="display:flex; gap:18px; margin-top:14px; align-items:stretch">
   <div class="card" style="flex:1.35; padding:14px 16px">
     <div style="font-weight:700; font-size:13.5px; margin-bottom:10px">经营操作</div>
     <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px">
       <span class="btn">📦 进货订货</span><span class="btn">🏷 定价与促销</span>
       <span class="btn">🗂 货架陈列</span><span class="btn">📊 报表中心</span>
       <span class="btn">📖 玩法说明</span><span class="btn danger-soft">⌂ 退出到主菜单</span>
     </div>
   </div>
   <div class="card" style="flex:1; padding:14px 16px; display:flex; flex-direction:column; gap:10px">
     <div style="font-weight:700; font-size:13.5px">今日提示</div>
     <div class="sub" style="line-height:1.7">· 面包保质期 3 天，别一次订太多<br>· 黄金位（1、4 号槽）曝光更高，放高周转商品<br>· 售价远高于参考价会明显赶客</div>
     <div class="spacer"></div>
     <span class="btn primary big" style="justify-content:center">▶ 开门营业</span>
   </div>
 </div>
""")

# ---------------- s04 进货 ----------------
_rows = [
    ("1", "矿泉水", "1.0", "2.0", "180天", "24", "48", "30", "22.5", "2"),
    ("2", "可乐", "1.8", "3.5", "180天", "24", "24", "36", "18.2", "1"),
    ("3", "鲜榨果汁1L", "3.0", "6.0", "7天", "6", "12", "18", "9.8", "1"),
    ("4", "红烧牛肉面", "2.2", "4.0", "180天", "12", "24", "24", "14.0", "1"),
    ("5", "全麦面包", "2.5", "4.5", "3天", "6", "12", "18", "11.5", "2"),
    ("6", "金枪鱼三明治", "4.5", "9.0", "2天", "6", "0", "12", "8.2", "2"),
    ("7", "曲奇饼干", "2.8", "5.5", "120天", "10", "10", "10", "6.4", "-"),
    ("8", "薄荷口香糖", "1.2", "3.0", "365天", "20", "20", "10", "5.1", "-"),
    ("9", "城市晚报", "0.8", "2.0", "1天", "10", "0", "0", "7.0", "1"),
    ("10", "抽纸", "2.0", "4.5", "999天", "20", "40", "0", "4.6", "-"),
]
s04_rows = []
for _r in _rows:
    row = list(_r)
    if row[0] in ("5", "6", "9"):
        row[1] += " ⚠"     # 短保质期商品标注
    s04_rows.append(tuple(row))

s04 = page(body="""
 <div style="display:flex; align-items:baseline; gap:14px">
   <h1 class="screen-title">进货订货</h1>
   <span class="sub">标准供货 · 当日早到货 · 按整箱进货 · 现金 ¥19,746.80</span>
 </div>
 <div style="display:flex; gap:14px; margin-top:12px">
   <div class="card" style="flex:1.7; overflow:hidden">"""
         + table(["序", "商品", "进价", "参考价", "保质期", "箱规", "仓库", "货架", "7日均销", "建议(箱)"],
                 s04_rows, num_cols={2, 3, 6, 7, 8, 9}) + """
   </div>
   <div style="flex:1; display:flex; flex-direction:column; gap:12px">
     <div class="card" style="padding:14px 16px">
       <div style="font-weight:700; font-size:13.5px; margin-bottom:8px">加入订单</div>
       <div class="sub">选中左侧商品行，设置箱数后加入</div>
       <div style="display:flex; gap:8px; margin-top:10px; align-items:center">
         <span style="font-size:12.5px; color:#68788a">箱数</span>
         <span style="border:1px solid #d0d8e0; border-radius:8px; padding:7px 12px; font-size:13px">2 ▾</span>
         <span class="btn">＋ 加入订单</span>
       </div>
     </div>
     <div class="card" style="padding:14px 16px; flex:1">
       <div style="font-weight:700; font-size:13.5px; margin-bottom:8px">订单车</div>
       <table class="grid">
         <tr><td>矿泉水 ×2箱</td><td class="num">¥96.00</td></tr>
         <tr><td>可乐 ×1箱</td><td class="num">¥86.40</td></tr>
         <tr><td>全麦面包 ×2箱</td><td class="num">¥60.00</td></tr>
         <tr><td>金枪鱼三明治 ×2箱</td><td class="num">¥108.00</td></tr>
         <tr><td>城市晚报 ×1箱</td><td class="num">¥16.00</td></tr>
       </table>
       <div style="margin-top:10px; font-size:12.5px; color:#4a5a6a">
         合计 <b style="font-size:15px">¥366.40</b> · 共 60 件
         <span style="color:#68788a">（仓库剩余 158 件）</span></div>
       <div style="display:flex; gap:8px; margin-top:10px"><span class="btn">✕ 删除选中</span><span class="btn">清空</span></div>
     </div>
     <span class="btn primary big" style="justify-content:center">✓ 确认下单（当日到仓）</span>
     <span class="btn" style="justify-content:center">← 返回晨间准备</span>
   </div>
 </div>
""")

# ---------------- s05 定价与促销（含弹窗） ----------------
price_rows = [
    ("1", "矿泉水", "1.0", "2.20", "2.0", "45%", "30", "-", "偏高"),
    ("2", "可乐", "1.8", "3.50", "3.5", "49%", "36", "-20% · 剩2天", "促销中"),
    ("3", "鲜榨果汁1L", "3.0", "6.00", "6.0", "50%", "18", "-", "✓"),
    ("4", "红烧牛肉面", "2.2", "4.00", "4.0", "45%", "24", "-", "✓"),
    ("5", "全麦面包", "2.5", "4.50", "4.5", "44%", "18", "-30% · 剩3天", "临期促销"),
    ("6", "金枪鱼三明治", "4.5", "9.00", "9.0", "50%", "12", "-", "✓"),
]
s05 = page(body="""
 <div style="display:flex; align-items:baseline; gap:14px">
   <h1 class="screen-title">定价与促销</h1>
   <span class="sub">售价贴近参考价好卖；远高于参考价会显著赶客（毛利率不含促销）</span>
 </div>
 <div class="card" style="margin-top:12px; overflow:hidden">"""
         + table(["序", "商品", "进价", "现售价", "参考价", "毛利率", "在架", "促销", "提示"],
                 price_rows, num_cols={2, 3, 4, 5, 6}) + """
 </div>
 <div class="footerbar">
   <span class="btn">✎ 修改选中售价</span>
   <span class="btn primary">🏷 促销设置</span>
   <span class="spacer"></span>
   <span class="btn">← 返回晨间准备</span>
 </div>
 <div class="overlay">
   <div class="modal">
     <h2>促销设置 — 可乐</h2>
     <div class="m-sub">促销立即生效，持续 3 天；折扣同时提升门店吸引力（0 = 取消促销）</div>
     <div style="display:flex; align-items:center; gap:12px">
       <span style="font-size:12.5px; color:#68788a; width:56px">折扣</span>
       <div style="flex:1; height:6px; border-radius:4px; background:#e6ebf1; position:relative">
         <div style="width:40%; height:100%; background:#1f7a5a; border-radius:4px"></div>
         <div style="position:absolute; left:40%; top:-5px; width:16px; height:16px; border-radius:50%; background:#fff; border:2px solid #1f7a5a"></div>
       </div>
       <b style="width:44px; text-align:right">20%</b>
     </div>
     <div style="display:flex; justify-content:space-between; margin-top:14px; font-size:13px">
       <span style="color:#68788a">现售价 ¥3.50 → 生效价 <b style="color:#1f7a5a">¥2.80</b></span>
       <span style="color:#68788a">持续 3 天</span>
     </div>
     <div style="display:flex; gap:10px; margin-top:18px; justify-content:flex-end">
       <span class="btn">取消</span><span class="btn primary">确定</span>
     </div>
   </div>
 </div>
""")

# ---------------- s06 货架陈列 ----------------
def slot_card(idx, star, name, qty, cap):
    star_tag = '<span class="tag gold">★ 黄金位</span>' if star else '<span class="tag">普通位</span>'
    fill = int(qty / cap * 100)
    return f"""
   <div class="card" style="padding:12px 14px">
     <div style="display:flex; align-items:center; gap:8px">
       <b style="font-size:13px">槽 {idx}</b>{star_tag}
       <span class="spacer"></span><span class="sub">{qty}/{cap} 件</span>
     </div>
     <div style="font-size:15px; font-weight:700; margin:6px 0">{name}</div>
     <div class="pbar"><i style="width:{fill}%"></i></div>
     <div style="display:flex; gap:8px; margin-top:10px">
       <span class="btn" style="padding:6px 12px; font-size:12px">上架</span>
       <span class="btn" style="padding:6px 12px; font-size:12px">取下</span>
     </div>
   </div>"""

s06 = page(body="""
 <div style="display:flex; align-items:baseline; gap:14px">
   <h1 class="screen-title">货架陈列</h1>
   <span class="sub">选中右侧仓库商品 → 点槽位上的「上架」；只有上架商品才会被顾客看到</span>
 </div>
 <div style="display:flex; gap:14px; margin-top:12px">
   <div style="flex:1.5; display:grid; grid-template-columns:1fr 1fr; gap:10px">"""
         + slot_card(1, True, "矿泉水", 30, 36) + slot_card(2, False, "可乐", 36, 36)
         + slot_card(3, False, "红烧牛肉面", 24, 36) + slot_card(4, True, "金枪鱼三明治", 12, 36)
         + slot_card(5, False, "全麦面包", 18, 36) + slot_card(6, False, "（空槽位）", 0, 36) + """
   </div>
   <div style="flex:1; display:flex; flex-direction:column; gap:12px">
     <div class="card" style="padding:14px 16px; flex:1">
       <div style="font-weight:700; font-size:13.5px; margin-bottom:8px">仓库（未上架）</div>
       <table class="grid">
         <tr><th>商品</th><th class="num">件数</th><th>最早到期</th></tr>
         <tr><td>可乐</td><td class="num">12</td><td><span class="tag ok">180天</span></td></tr>
         <tr><td>全麦面包</td><td class="num">12</td><td><span class="tag warn">剩2天</span></td></tr>
         <tr><td>曲奇饼干</td><td class="num">10</td><td><span class="tag ok">120天</span></td></tr>
         <tr><td>薄荷口香糖</td><td class="num">20</td><td><span class="tag ok">365天</span></td></tr>
         <tr><td>抽纸</td><td class="num">40</td><td><span class="tag ok">长期</span></td></tr>
       </table>
       <div class="sub" style="margin-top:10px">剩余仓库容量 158 件 · 单槽容量 36 件</div>
     </div>
     <span class="btn" style="justify-content:center">← 返回晨间准备</span>
   </div>
 </div>
""")

# ---------------- s07 营业进行中 ----------------
def log_line(t, a, s, rev, note="", cls=""):
    n = f'<span class="tag {cls}" style="margin-left:10px">{note}</span>' if note else ""
    return (f'<div style="display:flex; gap:18px; padding:6px 12px; font-size:12.5px;'
            f'font-variant-numeric:tabular-nums; {"background:#f7faf8;" if cls=="" else ""}">'
            f'<b style="width:44px">{t}</b><span style="width:70px">到达 {a}</span>'
            f'<span style="width:70px">服务 {s}</span>'
            f'<span style="width:110px; color:#1f7a5a">营收 +¥{rev}</span>{n}</div>')

s07 = page(body="""
 <div style="display:flex; align-items:center; gap:14px">
   <h1 class="screen-title">第 12 天 · 营业中</h1>
   <div style="flex:1; max-width:320px"><div class="pbar" style="height:10px"><i style="width:62%"></i></div></div>
   <span class="sub">14:00 / 24:00</span>
   <span class="spacer"></span>
   <span class="btn" style="padding:7px 14px; font-size:12px">⏩ 加速</span>
   <span class="btn danger-soft" style="padding:7px 14px; font-size:12px">⏹ 立即打烊</span>
 </div>
 <div style="display:flex; gap:14px; margin-top:12px">
   <div class="card" style="flex:1.9; padding:10px 6px">"""
         + log_line("08:00", 14, 12, "96.0") + log_line("09:00", 12, 11, "88.5")
         + log_line("10:00", 6, 6, "41.0") + log_line("12:00", 13, 11, "102.5", "缺货：三明治 ×3", "warn")
         + log_line("13:00", 8, 7, "58.0") + log_line("15:00", 9, 8, "66.5")
         + log_line("17:00", 11, 9, "81.0", "排队放弃 2 人", "bad")
         + log_line("18:00", 12, 10, "93.5") + log_line("21:00", 7, 6, "49.0") + """
   </div>
   <div style="flex:1; display:flex; flex-direction:column; gap:12px">
     <div class="card" style="padding:14px 16px">
       <div style="font-weight:700; font-size:13.5px; margin-bottom:10px">实时战况</div>
       <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; font-size:13px">
         <div><div class="sub">到达</div><b style="font-size:19px">96</b></div>
         <div><div class="sub">成交</div><b style="font-size:19px">71 单</b></div>
         <div><div class="sub">营收</div><b style="font-size:19px; color:#1f7a5a">¥1,132</b></div>
         <div><div class="sub">排队放弃</div><b style="font-size:19px; color:#c0392b">5 人</b></div>
       </div>
     </div>
     <div class="card" style="padding:14px 16px; flex:1">
       <div style="font-weight:700; font-size:13.5px; margin-bottom:8px">今日热卖</div>
       <table class="grid">
         <tr><td>1. 可乐</td><td class="num">28 件</td></tr>
         <tr><td>2. 金枪鱼三明治</td><td class="num">19 件</td></tr>
         <tr><td>3. 矿泉水</td><td class="num">17 件</td></tr>
       </table>
       <div class="sub" style="margin-top:8px">打烊后自动进入结算单</div>
     </div>
   </div>
 </div>
""")

# ---------------- s08 每日结算 ----------------
def pl_row(label, value, cls="", strong=False, big=False):
    w = "font-weight:700;" if strong else ""
    size = "font-size:19px;" if big else "font-size:13.5px;"
    return (f'<div style="display:flex; justify-content:space-between; padding:9px 4px;'
            f'border-bottom:1px solid #eef1f5; {w}">'
            f'<span style="font-size:13.5px; color:{"" if strong else "#4a5a6a"}">{label}</span>'
            f'<span style="{size}{w}color:{cls or "#22303c"}">{value}</span></div>')

s08 = page(body="""
 <div style="display:flex; gap:18px; align-items:flex-start; justify-content:center">
   <div class="card" style="width:560px; padding:18px 22px">
     <div style="display:flex; align-items:baseline; gap:10px; margin-bottom:8px">
       <h1 class="screen-title" style="font-size:17px">每日结算 · 第 12 天 [周三]</h1>
       <span class="tag ok">连续盈利 4 天</span>
     </div>"""
         + pl_row("营收（75 单 / 进店 96 人）", "+¥1,845.00", strong=True)
         + pl_row("售出成本", "−¥1,254.60") + pl_row("报废损失（城市晚报 ×10 等）", "−¥27.00", "c0392b")
         + pl_row("房租", "−¥250.00") + pl_row("水电（30 + 营收×1.5%）", "−¥57.68")
         + pl_row("今日净利", "+¥255.72", "#1e8e5a", strong=True, big=True)
         + f"""
     <div style="display:flex; gap:8px; margin:14px 0 4px; flex-wrap:wrap">
       <span class="chip">转化率 <b>78%</b></span><span class="chip">客单价 <b>¥24.6</b></span>
       <span class="chip">缺货率 <b style="color:#b7791f">9.4%</b></span>
       <span class="chip">周转 <b>0.31</b></span><span class="chip">报废率 <b>2.1%</b></span>
     </div>
     <div style="padding:10px 4px; font-size:13px; color:#4a5a6a">
       满意度 77 · 声望 67 → <b style="color:#1e8e5a">68</b>
       <span style="color:#8a6d1a; letter-spacing:1px">★★★★☆</span></div>
     <div class="footerbar"><span class="spacer"></span>
       <span class="btn primary big">进入夜间运营 →</span></div>
   </div>
   <div class="card" style="width:280px; padding:16px 18px">
     <div style="font-weight:700; font-size:13.5px; margin-bottom:10px">资金概览</div>
     <div class="sub">现金余额</div><div style="font-size:21px; font-weight:700">¥19,802.68</div>
     <div class="sub" style="margin-top:10px">净资产</div><div style="font-size:21px; font-weight:700">¥26,415</div>
     <div class="sub" style="margin-top:12px">胜利进度（¥200,000）</div>
     <div class="pbar" style="margin-top:6px"><i style="width:13%"></i></div>
     <div class="sub" style="margin-top:4px">已达成 13.2%</div>
   </div>
 </div>
""")

# ---------------- s09 夜间运营 ----------------
s09 = page(body="""
 <div style="display:flex; align-items:baseline; gap:14px">
   <h1 class="screen-title">第 12 天 · 夜间运营</h1>
   <span class="sub">看看账本，然后结束今天 —— 升级与贷款将在后续版本加入</span>
 </div>
 <div style="display:flex; gap:18px; margin-top:14px">
   <div style="width:300px; display:flex; flex-direction:column; gap:10px">
     <span class="btn big">📊 报表中心</span>
     <span class="btn big">🏆 生涯统计</span>
     <span class="btn big">💾 保存进度</span>
     <span class="btn primary big">🌙 结束今天 → 第 13 天</span>
     <span class="btn danger-soft big">⌂ 退出到主菜单</span>
   </div>
   <div class="card" style="flex:1; padding:16px 18px">
     <div style="font-weight:700; font-size:13.5px; margin-bottom:12px">生涯统计（近 30 日）</div>
     <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:14px">
       <div><div class="sub">经营天数</div><b style="font-size:20px">12 天</b></div>
       <div><div class="sub">累计营收</div><b style="font-size:20px">¥15,860</b></div>
       <div><div class="sub">累计净利</div><b style="font-size:20px; color:#1e8e5a">+¥1,902</b></div>
       <div><div class="sub">最好一天</div><b style="font-size:15px">D11 · +¥318</b></div>
       <div><div class="sub">累计客流</div><b style="font-size:20px">1,286 人</b></div>
       <div><div class="sub">当前声望</div><b style="font-size:20px">★★★★☆</b></div>
     </div>
     <div class="sub" style="margin-top:14px">存档：每日结算后自动保存 · 夜间可手动覆盖</div>
   </div>
 </div>
""")

# ---------------- s10 报表中心 ----------------
bars = [("D1", 610), ("D2", 640), ("D3", 590), ("D4", 720), ("D5", 830), ("D6", 940),
        ("D7", 910), ("D8", 700), ("D9", 690), ("D10", 950), ("D11", 880), ("D12", 1845)]
max_v = max(v for _, v in bars)
bar_html = "".join(
    f'<div style="display:flex; flex-direction:column; align-items:center; gap:4px">'
    f'<span class="sub" style="font-size:10px">{v}</span>'
    f'<div style="width:26px; height:{int(v/max_v*120)}px; background:#1f7a5a; border-radius:4px 4px 0 0"></div>'
    f'<span class="sub" style="font-size:10px">{d}</span></div>'
    for d, v in bars)

s10 = page(body="""
 <div style="display:flex; align-items:baseline; gap:14px">
   <h1 class="screen-title">报表中心</h1>
   <span class="sub">库存 / KPI 趋势 / 销售排行</span>
 </div>
 <div style="display:flex; gap:0; margin-top:12px; border-bottom:2px solid #e0e6ec">
   <span style="padding:9px 18px; font-size:13.5px; color:#68788a">库存明细</span>
   <span style="padding:9px 18px; font-size:13.5px; font-weight:700; color:#1f7a5a;
                border-bottom:3px solid #1f7a5a; margin-bottom:-2px">KPI 趋势</span>
   <span style="padding:9px 18px; font-size:13.5px; color:#68788a">销售排行</span>
 </div>
 <div class="card" style="margin-top:12px; padding:14px 16px">
   <div style="font-weight:700; font-size:13px; margin-bottom:10px">近 12 日营收（元）</div>
   <div style="display:flex; align-items:flex-end; gap:10px; height:158px; padding:0 6px">{BARS}</div>
 </div>
 <div class="card" style="margin-top:12px; overflow:hidden">"""
         + table(["指标", "今日", "7日均值", "健康区间"],
                 [("营收", "¥1,845", "¥1,020", "—"),
                  ("净利", "+¥255.7", "+¥118.4", "> 0 且逐月抬升"),
                  ("转化率", "78%", "81%", "≥ 72%"),
                  ("客单价", "¥24.6", "¥21.8", "¥14~20"),
                  ("缺货率", "9.4% ⚠", "14.1%", "< 8%"),
                  ("报废率", "2.1%", "3.0%", "< 4%"),
                  ("满意度", "77", "76", "65~85")], num_cols={1, 2}) + """
 </div>
 <div class="footerbar"><span class="spacer"></span><span class="btn">← 返回</span></div>
""").replace("{BARS}", bar_html)

SCREENS = {
    "s01_main_menu": s01, "s02_difficulty": s02, "s03_prep": s03,
    "s04_procurement": s04, "s05_pricing": s05, "s06_shelving": s06,
    "s07_day_run": s07, "s08_settlement": s08, "s09_night": s09,
    "s10_reports": s10,
}

for name, html in SCREENS.items():
    (OUT / f"{name}.html").write_text(html, encoding="utf-8")
print("written:", len(SCREENS), "->", OUT)
