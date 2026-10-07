"""右侧常驻侧栏：今日 / 进货 / 定价 / 陈列 / 报表 五个页签。

所有经营操作都在侧栏完成（营业中随时可用，暂停时从容操作）；
操作直接调用 core Game 公共方法，侧栏不做任何规则判断。
"""

import math
import tkinter as tk
from tkinter import ttk
from typing import Dict

from config import balance as B
from core import catalog, inventory, pricing
from ui import console as fmt
from ui_gui import dialogs
from ui_gui.theme import COL, FONT, FONT_B, FONT_SMALL
from ui_gui.widgets import BarChart, fill_tree, make_tree


class Sidebar(ttk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)
        self.tab_today = TodayTab(nb, app)
        self.buy = BuyTab(nb, app)
        self.pricing = PricingTab(nb, app)
        self.display = DisplayTab(nb, app)
        self.reports = ReportsTab(nb, app)
        for tab, label in ((self.tab_today, "今日"), (self.buy, "进货"),
                           (self.pricing, "定价"), (self.display, "陈列"),
                           (self.reports, "报表")):
            nb.add(tab, text=label)
        self.nb = nb

    def refresh_all(self):
        for tab in (self.tab_today, self.buy, self.pricing, self.display,
                    self.reports):
            tab.refresh()

    def refresh_today(self):
        self.tab_today.refresh()

    def append_log(self, text: str, kind: str = "info"):
        self.tab_today.append_log(text, kind)


# ================= 今日 =================

class TodayTab(ttk.Frame):

    def __init__(self, nb, app):
        super().__init__(nb, style="TFrame", padding=10)
        self.app = app
        top = ttk.Frame(self, style="TFrame")
        top.pack(fill="x")
        self.stats = {}
        for i, name in enumerate(("今日营收", "成交", "客流", "满意度")):
            cell = ttk.Frame(top, style="TFrame")
            cell.grid(row=0, column=i, padx=(0, 14), sticky="w")
            ttk.Label(cell, text=name, style="Sub.TLabel").pack(anchor="w")
            v = ttk.Label(cell, text="—", font=FONT_B)
            v.pack(anchor="w")
            self.stats[name] = v
        self.alerts = tk.Text(self, height=4, bd=0, bg=COL["bg"],
                              fg=COL["text"], font=FONT_SMALL, wrap="word",
                              highlightthickness=0)
        self.alerts.pack(fill="x", pady=(8, 2))
        self.alerts.tag_configure("bad", foreground=COL["bad"])
        self.alerts.tag_configure("warn", foreground=COL["warn"])
        self.alerts.tag_configure("ok", foreground=COL["good"])
        self.alerts.configure(state="disabled")

        logbox = ttk.Labelframe(self, text="最近动态", padding=6)
        logbox.pack(fill="both", expand=True, pady=(6, 6))
        self.log = tk.Text(logbox, height=14, bd=0, bg=COL["panel"],
                           fg=COL["text"], font=FONT_SMALL, wrap="word",
                           highlightthickness=0)
        self.log.pack(fill="both", expand=True)
        self.log.tag_configure("good", foreground=COL["good"])
        self.log.tag_configure("bad", foreground=COL["bad"])
        self.log.tag_configure("dim", foreground=COL["sub"])
        self.log.configure(state="disabled")

        self.actions = ttk.Frame(self, style="TFrame")
        self.actions.pack(fill="x")
        self.main_btn = ttk.Button(self.actions, text="开门营业",
                                   style="Accent.TButton", command=self._main)
        self.main_btn.pack(fill="x", pady=(0, 6))
        row = ttk.Frame(self.actions, style="TFrame")
        row.pack(fill="x")
        ttk.Button(row, text="💾 保存进度",
                   command=self._save).pack(side="left", padx=(0, 6))
        ttk.Button(row, text="⌂ 主菜单",
                   command=self._menu).pack(side="left")
        self._log_count = 0

    # ---- 行为 ----
    def _main(self):
        app = self.app
        if app.phase == "prep":
            info = app.game.morning_info()
            if info["on_shelf"] == 0 and not messagebox_askyesno(
                    "货架上没有任何商品，开门将不会产生生意。仍要开门吗？"):
                return
            app.open_store()
        elif app.phase == "night":
            app.next_day()

    def _save(self):
        import save.savegame as savegame
        try:
            savegame.save(self.app.game, "autosave")
            self.append_log("✓ 已保存进度", "good")
        except OSError as exc:
            self.append_log(f"保存失败：{exc}", "bad")

    def _menu(self):
        self.app.back_to_menu()

    def append_log(self, text: str, kind: str = "info"):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n", kind)
        self._log_count += 1
        if self._log_count > 120:
            self.log.delete("1.0", "20.0")
            self._log_count -= 20
        self.log.see("end")
        self.log.configure(state="disabled")

    # ---- 刷新 ----
    def refresh(self):
        app = self.app
        state = app.game.state
        if state is None:
            return
        ledger = state.ledger
        today = ledger[-1] if ledger else None
        if app.phase == "open":
            # 营业中：显示当日实时累计（小时节拍聚合值）
            dl = app._daylog_running
            rev, conv = dl.revenue, dl.conversions
            traf, sat = dl.arrivals, (f"{dl.sat_avg:.0f}" if dl.sat_samples else "—")
        elif today:
            rev, conv = today["revenue"], today["conversions"]
            traf, sat = today["traffic"], today["sat"]
        else:
            rev, conv, traf, sat = 0, 0, 0, "—"
        self.stats["今日营收"].config(text=fmt.money(rev))
        self.stats["成交"].config(text=f"{conv} 单")
        self.stats["客流"].config(text=str(traf))
        self.stats["满意度"].config(text=str(sat))
        # 提醒
        info = app.game.morning_info()
        msgs = []
        for item_id, qty, days in info["expiry_warns"]:
            msgs.append(("warn", f"⚠ 临期：{_n(item_id)} ×{qty}（剩 {days} 天）"
                                 "→ 建议促销"))
        for item_id, ratio in info["stagnants"]:
            msgs.append(("warn", f"⚠ 滞销：{_n(item_id)} → 降价/促销"))
        if app.phase == "open":
            dl = app._daylog_running
            if dl and dl.oos_needs:
                msgs.append(("bad", f"⚠ 今日缺货 {dl.oos_needs} 次未满足"))
            if dl and dl.abandons:
                msgs.append(("bad", f"⚠ 排队流失 {dl.abandons} 人"))
        if app.phase == "night" and today:
            msgs.append(("ok", f"昨日净利 {fmt.signed_money(today['net'])}，"
                               f"声望 {today['rep']}"))
        self.alerts.configure(state="normal")
        self.alerts.delete("1.0", "end")
        for kind, text in msgs[:6]:
            self.alerts.insert("end", text + "\n", kind)
        self.alerts.configure(state="disabled")
        # 主按钮文案
        if app.phase == "prep":
            self.main_btn.config(text=f"▶ 开门营业（第 {state.day} 天）")
        elif app.phase == "night":
            self.main_btn.config(text=f"🌙 结束今天 → 第 {state.day + 1} 天")
        elif app.phase == "open":
            self.main_btn.config(text="营业中……（侧栏可随时操作）")
        else:
            self.main_btn.config(text="—")


def messagebox_askyesno(msg):
    from tkinter import messagebox
    return messagebox.askyesno("确认", msg)


def _n(item_id):
    return catalog.get(item_id).name


# ================= 进货 =================

class BuyTab(ttk.Frame):

    def __init__(self, nb, app):
        super().__init__(nb, style="TFrame", padding=8)
        self.app = app
        self.cart: Dict[str, int] = {}
        self.cat_tree = make_tree(self, [
            ("name", "商品", 92, "w"), ("cost", "进价", 46, "e"),
            ("ref", "参考价", 52, "e"), ("life", "保质", 46, "e"),
            ("case", "箱规", 40, "e"), ("have", "仓库+架", 60, "e"),
            ("avg", "7日均销", 56, "e"), ("sug", "建议(箱)", 58, "e"),
        ], height=8)
        self.cat_tree.pack(fill="x")
        addrow = ttk.Frame(self, style="TFrame")
        addrow.pack(fill="x", pady=5)
        ttk.Label(addrow, text="箱数", style="Sub.TLabel").pack(side="left")
        self.qty = tk.IntVar(value=1)
        ttk.Spinbox(addrow, from_=1, to=99, textvariable=self.qty,
                    width=5).pack(side="left", padx=6)
        ttk.Button(addrow, text="＋ 加入订单",
                   command=self._add_selected).pack(side="left")
        self.cart_tree = make_tree(self, [
            ("name", "订单车", 150, "w"), ("cases", "箱数", 60, "e"),
            ("amount", "金额", 80, "e")], height=4)
        self.cart_tree.pack(fill="x")
        self.total_lbl = ttk.Label(self, text="订单为空", style="Sub.TLabel")
        self.total_lbl.pack(anchor="w", pady=4)
        row = ttk.Frame(self, style="TFrame")
        row.pack(fill="x", pady=(2, 0))
        ttk.Button(row, text="✕ 删除选中",
                   command=self._remove_selected).pack(side="left", padx=(0, 6))
        ttk.Button(row, text="确认下单（当日到仓）", style="Accent.TButton",
                   command=self.confirm_order).pack(side="left", fill="x",
                                                    expand=True)
        self.refresh()

    def _add_selected(self):
        sel = self.cat_tree.selection()
        if not sel:
            return
        self.add_to_cart(sel[0], max(1, self.qty.get()))

    def add_to_cart(self, item_id: str, cases: int):
        self.cart[item_id] = self.cart.get(item_id, 0) + cases
        self._render_cart()

    def _remove_selected(self):
        sel = self.cart_tree.selection()
        if sel:
            self.cart.pop(sel[0], None)
            self._render_cart()

    def _render_cart(self):
        state = self.app.game.state
        total_cost = total_units = 0
        rows = []
        for iid, cases in self.cart.items():
            item = catalog.get(iid)
            cost = item.unit_cost * item.case_size * cases
            total_cost += cost
            total_units += item.case_size * cases
            rows.append((item.name, f"{cases}箱", fmt.money(cost)))
        fill_tree(self.cart_tree, rows)
        free = inventory.warehouse_free(state) if state else 0
        warn = " ⚠ 超容量" if total_units > free else ""
        self.total_lbl.config(text=(f"合计 {fmt.money(total_cost)} · 共 "
                                    f"{total_units} 件{warn}"
                                    f"（仓库剩余 {free} 件）"))

    def confirm_order(self):
        err = self.app.game.confirm_order(self.cart)
        if err:
            from tkinter import messagebox
            messagebox.showwarning("下单失败", err)
            return
        self.cart = {}
        self._render_cart()
        self.refresh()
        self.app.sidebar.append_log("✓ 订单已确认，货已到仓", "good")

    def refresh(self):
        state = self.app.game.state
        if state is None:
            return
        rows = []
        for item in catalog.all_items():
            have = (inventory.item_warehouse_qty(state, item.id)
                    + inventory.item_on_shelf_qty(state, item.id))
            avg = inventory.avg_daily_sales(state, item.id)
            sug = inventory.suggested_order_units(state, item.id)
            sug_cases = math.ceil(sug / item.case_size) if sug else 0
            rows.append((item.id, item.name, f"{item.unit_cost:.1f}",
                         f"{item.ref_price:.1f}", f"{item.shelf_life_days}天",
                         f"{item.case_size}", str(have), f"{avg:.1f}",
                         str(sug_cases) if sug_cases else "-"))
        fill_tree(self.cat_tree, rows)
        self._render_cart()


# ================= 定价 =================

class PricingTab(ttk.Frame):

    def __init__(self, nb, app):
        super().__init__(nb, style="TFrame", padding=8)
        self.app = app
        self.tree = make_tree(self, [
            ("name", "商品", 92, "w"), ("cost", "进价", 44, "e"),
            ("price", "现售价", 56, "e"), ("ref", "参考价", 52, "e"),
            ("margin", "毛利率", 52, "e"), ("onshelf", "在架", 40, "e"),
            ("promo", "促销", 74, "w"), ("eff", "生效价", 56, "e"),
        ], height=12)
        self.tree.pack(fill="both", expand=True)
        row = ttk.Frame(self, style="TFrame")
        row.pack(fill="x", pady=6)
        ttk.Button(row, text="✎ 修改售价",
                   command=self._edit_price).pack(side="left", padx=(0, 6))
        ttk.Button(row, text="🏷 促销设置",
                   command=self._edit_promo).pack(side="left")
        self.refresh()

    def _selected(self):
        sel = self.tree.selection()
        return sel[0] if sel else None

    def _edit_price(self):
        item_id = self._selected()
        if item_id:
            dialogs.PriceDialog(self, self.app.game, item_id,
                                self.refresh)

    def _edit_promo(self):
        item_id = self._selected()
        if item_id:
            dialogs.PromoDialog(self, self.app.game, item_id,
                                self.refresh)

    def refresh(self):
        state = self.app.game.state
        if state is None:
            return
        rows = []
        for item in catalog.all_items():
            price = state.prices.get(item.id, item.ref_price)
            margin = pricing.margin_rate(state, item.id)
            promo = state.promos.get(item.id)
            eff = pricing.effective_price(state, item.id)
            rows.append((item.id, item.name, f"{item.unit_cost:.1f}",
                         f"{price:.2f}", f"{item.ref_price:.1f}",
                         f"{margin * 100:.0f}%",
                         str(inventory.item_on_shelf_qty(state, item.id)),
                         f"−{promo.discount * 100:.0f}%·剩{promo.days_left}天"
                         if promo else "-", f"{eff:.2f}"))
        fill_tree(self.tree, rows)


# ================= 陈列 =================

class DisplayTab(ttk.Frame):

    def __init__(self, nb, app):
        super().__init__(nb, style="TFrame", padding=8)
        self.app = app
        ttk.Label(self, text="货架槽位（选中一个槽）", style="Sub.TLabel").pack(
            anchor="w")
        self.slot_tree = make_tree(self, [
            ("slot", "槽", 36, "w"), ("kind", "类型", 60, "w"),
            ("name", "商品", 110, "w"), ("qty", "数量", 70, "e")], height=6)
        self.slot_tree.pack(fill="x")
        ttk.Label(self, text="仓库（未上架）—— 选中商品后点「上架」",
                  style="Sub.TLabel").pack(anchor="w", pady=(8, 0))
        self.wh_tree = make_tree(self, [
            ("name", "商品", 110, "w"), ("qty", "仓库件数", 70, "e"),
            ("expire", "最早到期", 80, "w")], height=6)
        self.wh_tree.pack(fill="x")
        row = ttk.Frame(self, style="TFrame")
        row.pack(fill="x", pady=8)
        ttk.Label(row, text="数量(空=尽量多)", style="Sub.TLabel").pack(side="left")
        self.qty = tk.StringVar(value="")
        ttk.Spinbox(row, from_=1, to=999, textvariable=self.qty,
                    width=6).pack(side="left", padx=6)
        ttk.Button(row, text="⬆ 上架", style="Accent.TButton",
                   command=self._shelve).pack(side="left", padx=(0, 6))
        ttk.Button(row, text="⬇ 取下", command=self._unshelve).pack(
            side="left", padx=(0, 6))
        ttk.Button(row, text="一键补满所有槽", command=self._fill_all).pack(
            side="left")
        self.refresh()

    def _selected_slot(self):
        sel = self.slot_tree.selection()
        return int(sel[0]) if sel else None

    def _selected_item(self):
        sel = self.wh_tree.selection()
        return sel[0] if sel else None

    def _parse_qty(self):
        v = self.qty.get().strip()
        return int(v) if v.isdigit() and int(v) > 0 else None

    def _shelve(self):
        slot_idx = self._selected_slot()
        item_id = self._selected_item()
        if slot_idx is None or item_id is None:
            return
        err = self.app.game.shelve(slot_idx, item_id, self._parse_qty())
        if err:
            from tkinter import messagebox
            messagebox.showwarning("无法上架", err)
        self.refresh()
        self.app.sidebar.refresh_today()

    def _unshelve(self):
        slot_idx = self._selected_slot()
        if slot_idx is None:
            return
        err = self.app.game.unshelve(slot_idx, self._parse_qty())
        if err:
            from tkinter import messagebox
            messagebox.showwarning("无法取下", err)
        self.refresh()

    def _fill_all(self):
        state = self.app.game.state
        for slot in state.slots:
            if slot.item_id:
                self.app.game.shelve(slot.index, slot.item_id, None)
        self.refresh()
        self.app.sidebar.refresh_today()

    def refresh(self):
        state = self.app.game.state
        if state is None:
            return
        slot_rows = []
        for slot in state.slots:
            name = catalog.get(slot.item_id).name if slot.item_id else "（空）"
            slot_rows.append((str(slot.index),
                              "★ 黄金位" if slot.premium else "普通位",
                              name, f"{slot.qty}/{B.SLOT_CAPACITY}"))
        fill_tree(self.slot_tree, slot_rows)
        wh_rows = []
        for item in catalog.all_items():
            qty = inventory.item_warehouse_qty(state, item.id)
            if qty <= 0:
                continue
            batches = [b for b in state.warehouse if b.item_id == item.id]
            soonest = min((b.expire_day - state.day for b in batches),
                          default=None)
            wh_rows.append((item.id, item.name, str(qty),
                            f"剩{soonest}天" if soonest is not None else "长期"))
        fill_tree(self.wh_tree, wh_rows)


# ================= 报表 =================

class ReportsTab(ttk.Frame):

    def __init__(self, nb, app):
        super().__init__(nb, style="TFrame", padding=8)
        self.app = app
        inner = ttk.Notebook(self)
        inner.pack(fill="both", expand=True)
        page_inv = ttk.Frame(inner, style="TFrame")
        self.inv_tree = make_tree(page_inv, [
            ("name", "商品", 90, "w"), ("batches", "批次", 40, "e"),
            ("qty", "数量", 46, "e"), ("expire", "最近到期", 70, "w"),
            ("status", "状态", 90, "w")], height=10)
        page_inv.pack(fill="both", expand=True)
        inner.add(page_inv, text="库存")
        page_kpi = ttk.Frame(inner, style="TFrame", padding=6)
        inner.add(page_kpi, text="KPI 趋势")
        self.chart = BarChart(page_kpi, height=150)
        self.chart.pack(fill="x")
        self.kpi_tree = make_tree(page_kpi, [
            ("kpi", "指标", 70, "w"), ("today", "今日", 80, "e"),
            ("week", "7日均值", 80, "e")], height=7)
        page_rank = ttk.Frame(inner, style="TFrame")
        self.rank_tree = make_tree(page_rank, [
            ("name", "商品", 100, "w"), ("today", "今日", 50, "e"),
            ("week", "7日合计", 60, "e"), ("stock", "当前库存", 70, "e")],
            height=12)
        page_rank.pack(fill="both", expand=True)
        inner.add(page_rank, text="销售排行")
        self.refresh()

    def refresh(self):
        state = self.app.game.state
        if state is None:
            return
        inv_rows = []
        for item in catalog.all_items():
            batches = [b for b in state.warehouse
                       if b.item_id == item.id and b.qty > 0]
            if not batches:
                continue
            total = sum(b.qty for b in batches)
            soonest = min(b.expire_day - state.day for b in batches)
            avg = inventory.avg_daily_sales(state, item.id)
            have_days = (total / avg) if avg > 0 else float("inf")
            status = []
            if soonest <= B.EXPIRY_WARN_DAYS:
                status.append("⚠临期")
            if have_days > B.TARGET_TURNOVER_DAYS * B.STAGNANT_RATIO:
                status.append("⚠滞销")
            inv_rows.append((item.name, str(len(batches)), str(total),
                             f"剩{soonest}天", " ".join(status) or "正常"))
        fill_tree(self.inv_tree, inv_rows)

        ledger = state.ledger
        recent = ledger[-14:]
        self.chart.set_data([(f"D{e['day']}", e["revenue"]) for e in recent])
        kpi_rows = []
        if ledger:
            last = ledger[-1]
            week = ledger[-7:]

            def wavg(key):
                return sum(e[key] for e in week) / len(week)
            kpi_rows = [
                ("营收", fmt.money(last["revenue"]), fmt.money(wavg("revenue"))),
                ("净利", fmt.signed_money(last["net"]),
                 fmt.signed_money(wavg("net"))),
                ("转化率", fmt.pct(last["conv_rate"]), fmt.pct(wavg("conv_rate"))),
                ("客单价", fmt.money(last["aov"]), fmt.money(wavg("aov"))),
                ("缺货率", fmt.pct(last["oos_rate"]), fmt.pct(wavg("oos_rate"))),
                ("周转", f"{last['turnover']:.2f}", f"{wavg('turnover'):.2f}"),
                ("满意度", f"{last['sat']:.0f}", f"{wavg('sat'):.0f}"),
            ]
        fill_tree(self.kpi_tree, kpi_rows)

        rank_rows = []
        for item in catalog.all_items():
            hist = state.sales_history.get(item.id, [])
            total7 = sum(hist)
            rank_rows.append((item.name, str(hist[-1] if hist else 0),
                              str(total7),
                              str(inventory.item_on_shelf_qty(state, item.id)
                                  + inventory.item_warehouse_qty(state, item.id))))
        rank_rows.sort(key=lambda r: -int(r[2]))
        fill_tree(self.rank_tree, rank_rows)
