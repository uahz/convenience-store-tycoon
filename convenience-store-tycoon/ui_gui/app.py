"""主窗口：顶栏 + 实时地板 + 常驻侧栏；日流程状态机与小时节拍驱动。

状态机：menu → prep(备货,暂停) → open(营业,时间流动) → settle(结算弹窗)
        → night(打烊夜) → prep(次日)……  game over/victory → menu
"""

import time
import tkinter as tk
from tkinter import ttk

import save.savegame as savegame
from config import APP_VERSION, balance as B
from core import economy
from core.game import Game
from core.simulation import DayLog
from ui import console as fmt
from ui_gui import dialogs
from ui_gui.floorview import FloorView
from ui_gui.sidebar import Sidebar
from ui_gui.theme import COL, FONT, FONT_B, FONT_SUB, FONT_TITLE, apply_style

SPEED_MS = {"1x": 4000, "2x": 2000, "4x": 1000}


class TycoonApp(tk.Tk):

    def __init__(self, game: Game):
        super().__init__()
        from ui import theme
        theme.init(False)        # 声望★等格式化符号复用终端主题的字符表（幂等）
        self.game = game
        self.title(f"便利店大亨 · Demo v{APP_VERSION}")
        self.geometry("1200x740")
        self.minsize(1080, 660)
        apply_style(self)
        style = ttk.Style(self)
        style.configure("SpeedOn.TButton", background=COL["accent"],
                        foreground="#ffffff", font=FONT_B)
        style.map("SpeedOn.TButton",
                  background=[("active", COL["accent_dark"])])

        self.phase = "menu"          # menu/prep/open/settle/night
        self.speed = "1x"
        self.auto_dialogs = False
        self._gen = None
        self._hour_job = None
        self._hour_t0 = 0.0
        self._current_hour = B.DAY_START_HOUR
        self._daylog_running = DayLog()

        self._build_topbar()
        body = ttk.Frame(self, style="TFrame", padding=(10, 8))
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)
        self.floor = FloorView(body, self)
        self.floor.grid(row=0, column=0, sticky="nsw")
        self.sidebar = Sidebar(body, self)
        self.sidebar.grid(row=0, column=1, sticky="nse", padx=(10, 0))
        self._build_menu_overlay(body)
        self.refresh_topbar()
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    # ---------- 顶栏 ----------
    def _build_topbar(self):
        bar = ttk.Frame(self, style="TFrame", padding=(12, 8))
        bar.pack(fill="x")
        self.lbl_day = ttk.Label(bar, text="主菜单", font=FONT_SUB)
        self.lbl_day.pack(side="left")
        self.speed_btns = {}
        for key, label in (("pause", "⏸ 暂停"), ("1x", "▶ 1×"),
                           ("2x", "2×"), ("4x", "4×")):
            btn = ttk.Button(bar, text=label, width=7,
                             command=lambda k=key: self.set_speed(k))
            btn.pack(side="left", padx=(10 if key == "pause" else 3, 0))
            self.speed_btns[key] = btn
        self.lbl_cash = ttk.Label(bar, text="", font=FONT_B)
        self.lbl_cash.pack(side="left", padx=16)
        self.lbl_rep = ttk.Label(bar, text="", font=FONT_B)
        self.lbl_rep.pack(side="left")
        self.lbl_net = ttk.Label(bar, text="", font=FONT_B)
        self.lbl_net.pack(side="right")
        ttk.Label(bar, text="净资产", style="Sub.TLabel").pack(
            side="right", padx=(0, 4))

    def refresh_topbar(self):
        state = self.game.state
        for key, btn in self.speed_btns.items():
            on = (key == self.speed and self.phase == "open")
            btn.configure(style="SpeedOn.TButton" if on else "TButton")
        if state is None:
            self.lbl_day.config(text="主菜单")
            self.lbl_cash.config(text="")
            self.lbl_rep.config(text="")
            self.lbl_net.config(text="")
            return
        self.lbl_day.config(text=f"第 {state.day} 天 "
                                 f"[{B.DAY_NAMES[(state.day - 1) % 7]}]")
        self.lbl_cash.config(text=f"现金 {fmt.money(state.cash)}")
        self.lbl_rep.config(text=f"声望 {fmt.stars(state.reputation)} "
                                 f"{state.reputation:.0f}")
        self.lbl_net.config(text=f"{fmt.money(economy.net_worth(state))}")

    # ---------- 菜单层 ----------
    def _build_menu_overlay(self, body):
        self.menu = ttk.Frame(body, style="TFrame")
        self.menu.grid(row=0, column=0, columnspan=2, sticky="nsew")
        inner = ttk.Frame(self.menu, style="TFrame")
        inner.place(relx=0.5, rely=0.5, anchor="center")
        ttk.Label(inner, text="便 利 店 大 亨", style="Title.TLabel").pack(
            pady=(0, 4))
        ttk.Label(inner, text="街角生意 · 日进斗金 —— 实时经营模拟",
                  style="Sub.TLabel").pack(pady=(0, 22))
        ttk.Button(inner, text="▶ 开始新游戏", style="Accent.TButton",
                   width=24, command=self._new_game).pack(pady=5)
        self.btn_continue = ttk.Button(inner, text="📂 继续游戏（自动存档）",
                                       width=24, command=self._continue)
        self.btn_continue.pack(pady=5)
        ttk.Button(inner, text="📖 玩法说明", width=24,
                   command=lambda: dialogs.show_help(self)).pack(pady=5)
        ttk.Button(inner, text="✕ 退出", width=24,
                   command=self.destroy).pack(pady=5)
        ttk.Label(inner, text=f"Demo v{APP_VERSION} · 存档位于程序目录 saves/ 下",
                  style="Sub.TLabel").pack(pady=(18, 0))

    def _refresh_menu(self):
        self.btn_continue.config(
            state="normal" if savegame.has_save() else "disabled")

    def _show_menu(self):
        self.phase = "menu"
        self._cancel_hour_job()
        self._refresh_menu()
        self.menu.lift()
        self.refresh_topbar()

    def back_to_menu(self):
        self._show_menu()

    def _new_game(self):
        dialogs.DifficultyDialog(self, self.start_new_game)

    def start_new_game(self, difficulty_key: str):
        self.game.new_game(difficulty_key)
        self.phase = "prep"
        self.menu.lower()
        self.floor.reset_day()
        self._daylog_running = DayLog()
        self.sidebar.refresh_all()
        self.sidebar.append_log("开业第一天！先在侧栏进货、定价、陈列，然后开门营业。",
                                "good")
        self.refresh_topbar()

    def _continue(self):
        try:
            meta = savegame.load(self.game, "autosave")
        except savegame.SaveError as exc:
            from tkinter import messagebox
            messagebox.showwarning("读取失败", str(exc), parent=self)
            return
        self.phase = "night"
        self.menu.lower()
        self.floor.reset_day()
        self.sidebar.refresh_all()
        self.sidebar.append_log(f"已读取存档：第 {meta['day']} 天结算后。"
                                "点「结束今天」开始下一天。", "good")
        self.refresh_topbar()

    # ---------- 日流程 ----------
    def open_store(self):
        state = self.game.state
        info = self.game.morning_info()
        if info["on_shelf"] == 0 and not self.auto_dialogs:
            from tkinter import messagebox
            if not messagebox.askyesno(
                    "确认", "货架上没有任何商品，开门将不会产生生意。仍要开门吗？",
                    parent=self):
                return
        self._gen = self.game.begin_day()
        self._daylog_running = DayLog()
        self.phase = "open"
        self.floor.reset_day()
        self.sidebar.refresh_today()
        self.sidebar.append_log("开门营业！", "good")
        self.refresh_topbar()
        self._schedule_hour()

    def _schedule_hour(self):
        self._cancel_hour_job()
        if self.phase != "open" or self.speed == "pause":
            return
        self._hour_t0 = time.monotonic()
        self._hour_job = self.after(SPEED_MS[self.speed], self._hour_tick)

    def _cancel_hour_job(self):
        if self._hour_job is not None:
            self.after_cancel(self._hour_job)
            self._hour_job = None

    def set_speed(self, key: str):
        self.speed = key
        self._schedule_hour()
        self.refresh_topbar()

    def clock_state(self):
        if self.phase != "open":
            return B.DAY_START_HOUR, 0.0
        interval = SPEED_MS.get(self.speed, 4000)
        progress = min(1.0, (time.monotonic() - self._hour_t0) / interval)
        return self._current_hour, progress

    def _hour_tick(self):
        if self.phase != "open":
            return
        try:
            hour, hlog = next(self._gen)
        except StopIteration as exc:
            self._finish_day(exc.value)
            return
        self._current_hour = hour
        dl = self._daylog_running
        dl.revenue += hlog.revenue
        dl.conversions += hlog.conversions
        dl.arrivals += hlog.arrivals
        dl.abandons += hlog.abandons
        if hlog.served and hlog.sat_hour:
            dl.sat_samples.append(hlog.sat_hour)
        self.floor.spawn_hour(hour, hlog)
        for note in hlog.notes:
            self.sidebar.append_log(f"{hour:02d}:00  {note}",
                                    "bad" if "缺货" in note or "放弃" in note
                                    else "dim")
        if hlog.served:
            self.sidebar.append_log(
                f"{hour:02d}:00  到达 {hlog.arrivals} · 成交 {hlog.conversions} 单"
                f" · 营收 {fmt.signed_money(hlog.revenue)}", "good")
        self.sidebar.refresh_today()
        self.refresh_topbar()
        self._schedule_hour()

    def _finish_day(self, daylog):
        self._cancel_hour_job()
        report = self.game.finish_day(daylog)
        try:
            savegame.save(self.game, "autosave")
        except OSError:
            pass
        self.phase = "settle"
        self.sidebar.append_log(
            f"打烊 · 今日净利 {fmt.signed_money(report.net)}", "good")
        self.refresh_topbar()
        self.sidebar.refresh_all()
        dialogs.SettlementDialog(self, self, report, self._after_settlement)

    def _after_settlement(self):
        report = self.game.last_report
        if report is not None and (report.victory or report.bankrupt):
            if report.bankrupt:
                savegame.delete_save("autosave")
            self._show_menu()
            return
        self.phase = "night"
        self.floor.reset_day()
        self.sidebar.refresh_all()
        self.refresh_topbar()

    def next_day(self):
        if self.phase != "night":
            return
        self.game.start_new_day()
        self.phase = "prep"
        self.floor.reset_day()
        self._daylog_running = DayLog()
        self.sidebar.refresh_all()
        self.sidebar.append_log(f"—— 第 {self.game.state.day} 天开始 ——", "dim")
        self.refresh_topbar()


def run_gui(seed=None) -> int:
    from ui import theme
    theme.init(False)            # 声望★等格式化符号复用终端主题的字符表
    app = TycoonApp(Game(seed=seed))
    app.mainloop()
    return 0


def run_selftest(seed=None) -> bool:
    """无头驱动完整一日流程，验证 GUI 状态机与核心链路。"""
    from ui import theme
    theme.init(False)
    dialogs.AUTO = True
    game = Game(seed=seed if seed is not None else 7)
    app = TycoonApp(game)
    app.withdraw()
    app.auto_dialogs = True
    ok = True
    try:
        app.update()
        app.start_new_game("normal")
        app.update()
        buy = app.sidebar.buy
        buy.add_to_cart("water", 2)
        buy.add_to_cart("cola", 2)
        buy.add_to_cart("bread", 2)
        buy.add_to_cart("noodles", 2)
        buy.confirm_order()
        app.game.shelve(0, "water", None)
        app.game.shelve(3, "cola", None)
        app.game.shelve(2, "noodles", None)
        app.game.shelve(4, "bread", None)
        app.update()
        app.open_store()
        guard = 0
        while app.phase == "open" and guard < 30:
            app._hour_tick()
            app.update()
            guard += 1
        if app.phase != "night" or len(app.game.state.ledger) != 1:
            ok = False
        app.next_day()
        if app.phase != "prep" or app.game.state.day != 2:
            ok = False
        app.update()
    except Exception:
        import traceback
        traceback.print_exc()
        ok = False
    finally:
        result = "OK" if ok else "FAILED"
        try:
            app.destroy()
        except Exception:
            pass
    from save.savegame import _app_dir
    (_app_dir() / "selftest_result.txt").write_text(
        result + "\n", encoding="utf-8")
    print("SELFTEST", result)
    return ok
