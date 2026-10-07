"""实时地板视图：30FPS 重绘的俯视店铺画布。

呈现内容：货架（商品/价格/库存刻度/黄金位）、顾客小人（按原型着色，
带状态气泡）、收银台与队列、门、游戏时钟。动画为纯呈现层——经济真值
始终由 core 引擎在每个"游戏小时"节拍上计算。
"""

import math
import random
import tkinter as tk
from typing import Dict, List, Tuple

from config import balance as B
from core import catalog, pricing
from ui_gui.theme import COL, FONT, FONT_B, FONT_SMALL

W, H = 660, 560
SHELF_POS = [(28, 46), (216, 46), (404, 46),
             (28, 152), (216, 152), (404, 152)]
SHELF_W, SHELF_H = 166, 60
DOOR = (10, 430)
COUNTER = (452, 468)
FRAME_MS = 33
BASE_WALK = 150.0        # 像素/秒（1× 基准）

ARCH_COLORS = {"office": "#3a7bd5", "student": "#e67e22", "senior": "#8e6cc9"}


class Agent:
    __slots__ = ("x", "y", "wps", "wi", "color", "bubble", "r")

    def __init__(self, x, y, wps, color, bubble=""):
        self.x, self.y = x, y
        self.wps = wps
        self.wi = 0
        self.color = color
        self.bubble = bubble
        self.r = 7


class FloorView(tk.Canvas):

    def __init__(self, parent, app):
        super().__init__(parent, width=W, height=H, bg="#e8e2d8",
                         highlightthickness=0)
        self.app = app
        self.agents: List[Agent] = []
        self._last_ms = 0
        self._draw_static()
        self.after(FRAME_MS, self._frame)

    # ---------- 静态层（一次性） ----------
    def _draw_static(self):
        self.create_rectangle(0, 0, W, 16, fill="#7d6b58", outline="")
        self.create_rectangle(W - 16, 0, W, H, fill="#8a7864", outline="")
        step = 36
        for gy in range(16, H - step, step):
            for gx in range((gy // step % 2) * 18, W - 16 - step, step * 2):
                self.create_rectangle(gx, gy, gx + 18, gy + 18,
                                      fill="#efe9de", outline="")
        self.create_rectangle(DOOR[0], DOOR[1], DOOR[0] + 14, DOOR[1] + 56,
                              fill="#ffffff", outline=COL["accent"], width=2)
        self.create_text(DOOR[0] + 7, DOOR[1] + 28, text="入",
                         font=FONT_SMALL, fill=COL["accent"])
        cx, cy = COUNTER
        self.create_rectangle(cx, cy, cx + 150, cy + 30,
                              fill="#5c4a38", outline="#4a3b2c")
        self.create_text(cx + 75, cy + 15, text="🧾 收银台",
                         font=FONT_SMALL, fill="#ffffff")

    # ---------- 帧循环 ----------
    def _frame(self):
        now = self.tk.call("clock", "milliseconds")
        dt = min(0.1, (now - self._last_ms) / 1000.0) if self._last_ms else 0.016
        self._last_ms = now
        if self.app.phase == "open" and self.app.speed != "pause":
            mult = {"1x": 1.0, "2x": 2.0, "4x": 4.0}[self.app.speed]
            self._advance(dt * mult)
        self._draw_dynamic()
        self.after(FRAME_MS, self._frame)

    def _advance(self, dist_px: float):
        for a in self.agents:
            if a.wi >= len(a.wps):
                continue
            tx, ty = a.wps[a.wi]
            dx, dy = tx - a.x, ty - a.y
            d = math.hypot(dx, dy)
            if d <= dist_px:
                a.x, a.y = tx, ty
                a.wi += 1
            else:
                a.x += dx / d * dist_px
                a.y += dy / d * dist_px
        self.agents = [a for a in self.agents if a.wi < len(a.wps)][-40:]

    # ---------- 动态层 ----------
    def _draw_dynamic(self):
        self.delete("dyn")
        state = self.app.game.state
        # 货架
        if state:
            for i, slot in enumerate(state.slots):
                self._draw_shelf(i, slot)
        # 顾客（结账队列中的点排到收银台前）
        for a in self.agents:
            self.create_oval(a.x - a.r, a.y - a.r, a.x + a.r, a.y + a.r,
                             fill=a.color, outline="#8090a0", tags="dyn")
            if a.bubble:
                bx, by = a.x, a.y - 20
                tw = max(28, len(a.bubble) * 7 + 10)
                self.create_rectangle(bx - tw / 2, by - 9, bx + tw / 2, by + 9,
                                      fill="#ffffff", outline="#d0d8e0",
                                      tags="dyn")
                self.create_text(bx, by, text=a.bubble, font=FONT_SMALL,
                                 fill=COL["text"], tags="dyn")
        self._draw_clock()

    def _draw_shelf(self, i, slot):
        x, y = SHELF_POS[i]
        premium = slot.premium
        if slot.item_id:
            item = catalog.get(slot.item_id)
            name = item.name
            price = pricing.effective_price(self.app.game.state, item.id)
            promo = self.app.game.state.promos.get(item.id)
            price_txt = f"¥{price:.2f}" + (f" (−{promo.discount * 100:.0f}%)" if promo else "")
            ratio = min(1.0, slot.qty / B.SLOT_CAPACITY)
        else:
            name, price_txt, ratio = "（空槽位）", "从侧栏「陈列」上架", 0.0
        fill = COL["accent"] if slot.item_id else "#b9c3ce"
        outline = "#e8b45a" if premium else "#155c44"
        self.create_rectangle(x, y, x + SHELF_W, y + SHELF_H, fill=fill,
                              outline=outline, width=2, tags="dyn")
        if premium:
            self.create_rectangle(x + SHELF_W - 52, y - 8, x + SHELF_W, y + 6,
                                  fill="#f7efd8", outline="#e0cf96", tags="dyn")
            self.create_text(x + SHELF_W - 26, y - 1, text="★ 黄金位",
                             font=("Microsoft YaHei UI", 7, "bold"),
                             fill="#8a6d1a", tags="dyn")
        if slot.item_id and len(name) > 7:
            name = name[:7] + "…"
        name_color = "#ffffff" if slot.item_id else "#5b6a79"
        self.create_text(x + 8, y + 8, text=name, anchor="w", font=FONT_B,
                         fill=name_color, tags="dyn")
        self.create_text(x + SHELF_W - 8, y + 9, text=f"{slot.qty}/{B.SLOT_CAPACITY}",
                         anchor="e", font=FONT_SMALL, fill="#f2f2f2",
                         tags="dyn")
        self.create_text(x + 8, y + 24, text=price_txt, anchor="w",
                         font=FONT_SMALL, fill="#f0f0f0", tags="dyn")
        # 库存刻度条
        bar_w = SHELF_W - 16
        self.create_rectangle(x + 8, y + SHELF_H - 12, x + 8 + bar_w,
                              y + SHELF_H - 6, fill="#123c2e", outline="",
                              tags="dyn")
        fw = max(0, int(bar_w * ratio))
        bar_color = "#8fe3c0" if ratio > 0.33 else "#e8b45a"
        if fw:
            self.create_rectangle(x + 8, y + SHELF_H - 12, x + 8 + fw,
                                  y + SHELF_H - 6, fill=bar_color, outline="",
                                  tags="dyn")

    def _draw_clock(self):
        self.create_rectangle(W - 96, 24, W - 26, 48, fill="#ffffff",
                              outline="#e0e6ec", tags="dyn")
        phase = self.app.phase
        if phase == "open":
            hour, prog = self.app.clock_state()
            minute = int(prog * 60)
            txt = f"{hour:02d}:{minute:02d}"
        elif phase in ("prep",):
            txt = "备货中"
        elif phase == "night":
            txt = "已打烊"
        else:
            txt = "--:--"
        self.create_text(W - 61, 36, text=txt, font=FONT_B, fill=COL["text"],
                         tags="dyn")
        if phase != "open":
            self.create_text(W / 2, H / 2, text="休业中",
                             font=("Microsoft YaHei UI", 22, "bold"),
                             fill="#c9c2b4", tags="dyn")

    # ---------- 小时事件 → 顾客动画 ----------
    def spawn_hour(self, hour: int, hlog) -> None:
        """把刚结束的一个游戏小时呈现为顾客动画。"""
        state = self.app.game.state
        if state is None or self.app.speed == "pause":
            return
        rng = random.Random(hour * 31 + state.day)
        arch_ids = [a["id"] for a in _archetypes()]
        shelf_targets = [SHELF_POS[s.index][:2] for s in state.slots
                         if s.item_id] or [(200, 200)]
        served = min(hlog.served, 14)
        for k in range(served):
            arch = arch_ids[k % len(arch_ids)]
            color = ARCH_COLORS[arch]
            sx, sy = rng.choice(shelf_targets)
            mid = (sx + SHELF_W / 2, sy + SHELF_H + 26 + (k % 3) * 14)
            qx = COUNTER[0] - 40 - (k % 5) * 26
            qy = COUNTER[1] - 8 + (k % 4) * 10
            bubble = "结账" if k % 3 == 0 else ""
            self.agents.append(Agent(DOOR[0] + 10, DOOR[1] + 30,
                                     [(mid[0], mid[1]), (qx, qy),
                                      (DOOR[0] + 10, DOOR[1] + 30)],
                                     color, bubble))
        for k in range(min(hlog.abandons, 8)):
            mx = rng.uniform(120, 420)
            my = rng.uniform(220, 400)
            self.agents.append(Agent(DOOR[0] + 10, DOOR[1] + 30,
                                     [(mx, my), (DOOR[0] + 10, DOOR[1] + 30)],
                                     "#c0392b", "缺货走了…" if "缺货" in " ".join(hlog.notes) else "排队走了…"))

    def reset_day(self) -> None:
        self.agents = []


def _archetypes():
    from config import customers as customers_cfg
    return customers_cfg.ARCHETYPES
