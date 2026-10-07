"""GUI 复用组件：表格、柱状图、小工具。"""

import tkinter as tk
from tkinter import ttk
from typing import List, Sequence, Tuple

from ui_gui.theme import COL, FONT, FONT_B, FONT_SMALL


def make_tree(parent, cols: Sequence[Tuple[str, str, int, str]],
              height: int = 12) -> ttk.Treeview:
    """cols: [(key, 表头, 宽度, anchor)]。返回带滚动条的 Treeview。"""
    wrapper = ttk.Frame(parent)
    tree = ttk.Treeview(wrapper, columns=[c[0] for c in cols],
                        show="headings", height=height)
    for key, header, width, anchor in cols:
        tree.heading(key, text=header)
        tree.column(key, width=width, anchor=anchor, stretch=True)
    vsb = ttk.Scrollbar(wrapper, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    tree.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")
    tree._wrapper = wrapper
    return tree


def fill_tree(tree: ttk.Treeview, rows: Sequence[Sequence[str]],
              tags: Sequence[str] = ()) -> None:
    tree.delete(*tree.get_children())
    for row in rows:
        tree.insert("", "end", values=list(row) + [""] * (len(tree["columns"]) - len(row)),
                    tags=tags)


def row_tag(tree: ttk.Treeview, bad_keys: set, warn_keys: set) -> None:
    """按行首列值着色（bad 红 / warn 黄）。"""
    tree.tag_configure("bad", foreground=COL["bad"])
    tree.tag_configure("warn", foreground=COL["warn"])
    for item in tree.get_children():
        head = str(tree.set(item, tree["columns"][0]))
        if head in bad_keys:
            tree.item(item, tags=("bad",))
        elif head in warn_keys:
            tree.item(item, tags=("warn",))


class BarChart(tk.Canvas):
    """简单横向柱状图（近 N 日营收等）。"""

    def __init__(self, parent, height=160, **kwargs):
        super().__init__(parent, height=height, highlightthickness=0,
                         bg=COL["panel"], **kwargs)
        self.bind("<Configure>", lambda e: self.redraw())
        self._data: List[Tuple[str, float]] = []

    def set_data(self, data: List[Tuple[str, float]]) -> None:
        self._data = list(data)
        self.redraw()

    def redraw(self) -> None:
        self.delete("all")
        width = max(self.winfo_width(), 320)
        height = max(self.winfo_height(), 120)
        if not self._data:
            self.create_text(width // 2, height // 2, text="（暂无数据）",
                             font=FONT_SMALL, fill=COL["sub"])
            return
        max_v = max(abs(v) for _, v in self._data) or 1.0
        n = len(self._data)
        bar_w = max(10, min(38, (width - 40) // n - 8))
        gap = (width - 40) / max(n, 1)
        baseline = height - 28
        self.create_line(24, baseline, width - 8, baseline,
                         fill=COL["border"])
        for i, (label, v) in enumerate(self._data):
            x = 28 + i * gap
            h = abs(v) / max_v * (baseline - 24)
            color = COL["accent"] if v >= 0 else COL["bad"]
            self.create_rectangle(x, baseline - h, x + bar_w, baseline,
                                  fill=color, outline="")
            self.create_text(x + bar_w / 2, baseline + 12, text=label,
                             font=FONT_SMALL, fill=COL["sub"])
            if v:
                self.create_text(x + bar_w / 2, baseline - h - 8,
                                 text=f"{v:,.0f}", font=FONT_SMALL,
                                 fill=COL["text"])


def money_label_pair(parent, title: str) -> tuple:
    """返回 (标题label, 数值label)，供 KPI 行使用。"""
    t = ttk.Label(parent, text=title, style="Sub.TLabel")
    v = ttk.Label(parent, text="-", font=FONT_B, style="Panel.TLabel")
    return t, v
