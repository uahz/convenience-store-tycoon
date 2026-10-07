"""GUI 弹窗：结算单、难度选择、改价、促销、玩法说明。"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable

from config import balance as B
from ui import console as fmt
from ui_gui.theme import COL, FONT, FONT_B, FONT_SUB, FONT_TITLE

AUTO = None   # 由 app 注入：True 时所有弹窗自动关闭（自检模式）


def _center(win, parent):
    win.update_idletasks()
    pw = parent.winfo_rootx() + parent.winfo_width() // 2
    ph = parent.winfo_rooty() + parent.winfo_height() // 2
    win.geometry(f"+{pw - win.winfo_reqwidth() // 2}+{ph - win.winfo_reqheight() // 2}")


# ---------- 结算单 ----------

class SettlementDialog(tk.Toplevel):

    def __init__(self, parent, app, report, on_done: Callable[[], None]):
        super().__init__(parent)
        self.app = app
        self.report = report
        self.on_done = on_done
        self.title(f"每日结算 · 第 {report.day} 天")
        self.configure(bg=COL["bg"])
        self.resizable(False, False)
        try:
            self.grab_set()
        except tk.TclError:
            pass    # 自检等未映射窗口场景
        self.transient(parent)
        self._build()
        _center(self, parent)
        if AUTO:
            self._on_next()      # 自检模式：同步关闭，避免定时器竞态
            return

    def _pl(self, grid, row, label, value, color=None, big=False, bold=False):
        font = FONT_B if (big or bold) else FONT
        size = 15 if big else 10
        font = (font[0], size) + tuple(font[2:])
        ttk.Label(grid, text=label, style="Panel.TLabel",
                  foreground=COL["sub"] if not bold else COL["text"],
                  font=font).grid(row=row, column=0, sticky="w", pady=3)
        ttk.Label(grid, text=value, style="Panel.TLabel", foreground=color or COL["text"],
                  font=font).grid(row=row, column=1, sticky="e", pady=3)

    def _build(self):
        r = self.report
        box = ttk.Frame(self, style="Panel.TFrame", padding=18)
        box.pack(fill="both", expand=True)
        head = ttk.Frame(box, style="Panel.TFrame")
        head.pack(fill="x")
        ttk.Label(head, text=f"每日结算 · 第 {r.day} 天 [{r.weekday}]",
                  style="Panel.TLabel", font=FONT_SUB).pack(side="left")
        if r.net > 0:
            ttk.Label(head, text="盈利", style="Panel.TLabel",
                      foreground=COL["good"]).pack(side="right")
        elif r.net < 0:
            ttk.Label(head, text="亏损", style="Panel.TLabel",
                      foreground=COL["bad"]).pack(side="right")
        grid = ttk.Frame(box, style="Panel.TFrame")
        grid.pack(fill="x", pady=8)
        grid.columnconfigure(1, weight=1)
        row = 0
        self._pl(grid, row, f"营收（{r.conversions} 单 / 进店 {r.traffic} 人）",
                 fmt.signed_money(r.revenue), bold=True); row += 1
        self._pl(grid, row, "售出成本", fmt.signed_money(-r.cogs)); row += 1
        if r.spoilage > 0:
            names = "、".join(f"{_n(i)}×{q}" for i, q in r.spoilage_items)
            self._pl(grid, row, f"报废损失（{names}）",
                     fmt.signed_money(-r.spoilage), COL["bad"]); row += 1
        self._pl(grid, row, "房租", fmt.signed_money(-r.rent)); row += 1
        self._pl(grid, row, "水电", fmt.signed_money(-r.utilities)); row += 1
        self._pl(grid, row, "今日净利", fmt.signed_money(r.net),
                 COL["good"] if r.net >= 0 else COL["bad"], big=True); row += 1

        chips = ttk.Frame(box, style="Panel.TFrame")
        chips.pack(fill="x", pady=4)
        for text in (f"转化率 {fmt.pct(r.conversion_rate)}",
                     f"客单价 {fmt.money(r.aov)}",
                     f"缺货率 {fmt.pct(r.oos_rate)}",
                     f"周转 {r.turnover:.2f}",
                     f"报废率 {fmt.pct(r.waste_rate)}"):
            ttk.Label(chips, text=text, style="Panel.TLabel",
                      background=COL["select"], padding=(8, 3)).pack(side="left",
                                                                     padx=3)
        sat = f"{r.sat_avg:.0f}" if r.sat_avg else "—"
        ttk.Label(box, text=f"满意度 {sat} · 声望 {r.rep_before:.0f} → "
                            f"{r.rep_after:.0f} {fmt.stars(r.rep_after)}",
                  style="Panel.TLabel").pack(anchor="w", pady=6)
        if r.abandon_rate > B.QUEUE_PENALTY_RATE or r.lost_at_close:
            ttk.Label(box, text=f"⚠ 排队流失 {r.abandons} 人，打烊滞留 "
                                f"{r.lost_at_close} 人 → 优化高峰备货",
                      style="Panel.TLabel", foreground=COL["warn"]).pack(anchor="w")
        if r.victory:
            ttk.Label(box, text="🏆 达成胜利目标！",
                      style="Panel.TLabel", font=FONT_SUB,
                      foreground=COL["good"]).pack(anchor="w", pady=4)
        if r.bankrupt:
            ttk.Label(box, text="✖ 现金枯竭，门店破产清算……",
                      style="Panel.TLabel", font=FONT_SUB,
                      foreground=COL["bad"]).pack(anchor="w", pady=4)

        btn_row = ttk.Frame(box, style="Panel.TFrame")
        btn_row.pack(fill="x", pady=(10, 0))
        if r.victory or r.bankrupt:
            text = "返回主菜单"
            cmd = self._on_next
        else:
            text = f"开始第 {r.day + 1} 天 →"
            cmd = self._on_next
        ttk.Button(btn_row, text=text, style="Accent.TButton",
                   command=cmd).pack(side="right")

    def _on_next(self):
        self.grab_release()
        self.destroy()
        self.on_done()


def _n(item_id):
    from core import catalog
    return catalog.get(item_id).name


# ---------- 难度选择 ----------

class DifficultyDialog(tk.Toplevel):

    def __init__(self, parent, on_pick: Callable[[str], None]):
        super().__init__(parent)
        self.title("选择难度")
        self.configure(bg=COL["bg"])
        self.resizable(False, False)
        self.grab_set()
        ttk.Label(self, text="选择难度", style="TLabel",
                  font=FONT_SUB, padding=(20, 14, 20, 4)).pack()
        ttk.Label(self, text="三种开局强度，胜利线与经营压力不同",
                  style="TLabel", foreground=COL["sub"],
                  padding=(20, 0, 20, 8)).pack()
        for key, preset in B.DIFFICULTIES.items():
            row = ttk.Frame(self, padding=(20, 5))
            row.pack(fill="x")
            ttk.Label(row, text=preset.label, style="TLabel",
                      font=FONT_B, width=6).pack(side="left")
            ttk.Label(row, text=(f"初始资金 {fmt.money(preset.cash)} · "
                                 f"客流 ×{preset.traffic_mult:.2f} · "
                                 f"房租 ×{preset.rent_mult:.2f}"),
                      style="TLabel", foreground=COL["sub"]).pack(side="left",
                                                                  padx=10)
            ttk.Label(row, text=f"胜利线 {fmt.money(preset.victory_net_worth)}",
                      style="TLabel").pack(side="left", padx=10)
            ttk.Button(row, text="选择", style="Accent.TButton",
                       command=lambda k=key: self._pick(k, on_pick)).pack(
                side="right")
        ttk.Button(self, text="返回", command=self.destroy).pack(pady=10)
        self.transient(parent)
        _center(self, parent)

    def _pick(self, key, on_pick):
        self.destroy()
        on_pick(key)


# ---------- 改价 / 促销 ----------

class PriceDialog(tk.Toplevel):

    def __init__(self, parent, game, item_id, on_done: Callable[[], None]):
        super().__init__(parent)
        from core import catalog
        self.game, self.item_id, self.on_done = game, item_id, on_done
        self.title("修改售价")
        self.configure(bg=COL["bg"])
        self.resizable(False, False)
        item = catalog.get(item_id)
        cur = game.state.prices.get(item_id, item.ref_price)
        ttk.Label(self, text=f"{item.name} · 进价 ¥{item.unit_cost:.2f} · "
                             f"参考价 ¥{item.ref_price:.2f}",
                  style="TLabel", padding=(18, 12, 18, 2)).pack()
        self.var = tk.StringVar(value=f"{cur:.2f}")
        entry = ttk.Entry(self, textvariable=self.var, width=14,
                          font=FONT_B)
        entry.pack(pady=6)
        entry.select_range(0, "end")
        entry.focus_set()
        row = ttk.Frame(self, padding=(18, 4, 18, 14))
        row.pack()
        ttk.Button(row, text="取消", command=self.destroy).pack(side="left",
                                                               padx=4)
        ttk.Button(row, text="确定", style="Accent.TButton",
                   command=self._ok).pack(side="left", padx=4)
        self.bind("<Return>", lambda e: self._ok())
        self.transient(parent)
        _center(self, parent)

    def _ok(self):
        try:
            price = float(self.var.get())
        except ValueError:
            messagebox.showwarning("无效输入", "请输入数字", parent=self)
            return
        err = self.game.set_price(self.item_id, price)
        if err:
            messagebox.showwarning("无法设置", err, parent=self)
            return
        self.destroy()
        self.on_done()


class PromoDialog(tk.Toplevel):

    def __init__(self, parent, game, item_id, on_done: Callable[[], None]):
        super().__init__(parent)
        from core import catalog, pricing
        self.game, self.item_id, self.on_done = game, item_id, on_done
        self.title("促销设置")
        self.configure(bg=COL["bg"])
        self.resizable(False, False)
        item = catalog.get(item_id)
        promo = game.state.promos.get(item_id)
        cur_pct = int(promo.discount * 100) if promo else 0
        ttk.Label(self, text=f"{item.name} 促销折扣（0 = 取消，持续 "
                             f"{B.PROMO_DEFAULT_DAYS} 天）",
                  style="TLabel", padding=(18, 12, 18, 4)).pack()
        self.var = tk.IntVar(value=cur_pct)
        ttk.Scale(self, from_=0, to=B.PROMO_MAX_PCT, variable=self.var,
                  length=240).pack(padx=18)
        lbl = ttk.Label(self, text="", style="TLabel", font=FONT_B)
        lbl.pack(pady=4)

        def refresh_label(*_):
            p = self.var.get()
            eff = item.ref_price * (1 - p / 100.0)
            lbl.config(text=f"折扣 {p}% · 生效价 ¥{eff:.2f}")
        self.var.trace_add("write", refresh_label)
        refresh_label()
        row = ttk.Frame(self, padding=(18, 4, 18, 14))
        row.pack()
        ttk.Button(row, text="取消", command=self.destroy).pack(side="left",
                                                               padx=4)
        ttk.Button(row, text="确定", style="Accent.TButton",
                   command=self._ok).pack(side="left", padx=4)
        self.transient(parent)
        _center(self, parent)

    def _ok(self):
        err = self.game.set_promo(self.item_id, float(self.var.get()))
        if err:
            messagebox.showwarning("无法设置", err, parent=self)
            return
        self.destroy()
        self.on_done()


# ---------- 玩法说明 ----------

HELP_TEXT = """目标：滚动经营，净资产达到难度胜利线即胜利；结算后现金为负即破产。

一天循环：
  1. 备货（暂停状态）：进货订货 → 定价/促销 → 货架陈列
  2. 开门营业：时间开始流动，顾客实时进店选购、排队结账
  3. 随时切侧栏补货/改价/促销（想从容操作就先暂停）
  4. 24:00 打烊 → 结算单 → 开始下一天

关键规则：
  · 售价贴近参考价好卖；远高于参考价（>1.25×）顾客明显流失
  · 保质期：到期批次晨间自动报废（报纸 1 天、面包 3 天！）
  · 缺货：顾客买不到会不满离开，拉低声望 → 次日客流下降
  · 黄金位（1、4 号槽）曝光更高，适合放高周转商品
  · 排队过长顾客会放弃购买 → 高峰期前把畅销品备足
"""


def show_help(parent):
    win = tk.Toplevel(parent)
    win.title("玩法说明")
    win.configure(bg=COL["bg"])
    txt = tk.Text(win, width=64, height=20, wrap="word", bd=0,
                  bg=COL["panel"], fg=COL["text"], font=FONT,
                  padx=18, pady=14)
    txt.insert("1.0", HELP_TEXT)
    txt.configure(state="disabled")
    txt.pack(fill="both", expand=True)
    ttk.Button(win, text="知道了", command=win.destroy).pack(pady=10)
    win.transient(parent)
    _center(win, parent)
