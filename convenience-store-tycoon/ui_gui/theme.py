"""GUI 主题：浅色商务风。颜色/字体集中于此。"""

import tkinter as tk
from tkinter import ttk

COL = {
    "bg": "#eef1f5",          # 窗口底
    "panel": "#ffffff",       # 卡片/面板
    "border": "#d5dbe3",
    "text": "#22303c",
    "sub": "#68788a",
    "accent": "#1f7a5a",      # 主色（绿）
    "accent_dark": "#155c44",
    "accent_soft": "#e2f1ea",
    "good": "#1e8e5a",
    "bad": "#c0392b",
    "warn": "#b7791f",
    "gold": "#8a6d1a",
    "select": "#d8ece3",
}

FONT = ("Microsoft YaHei UI", 10)
FONT_B = ("Microsoft YaHei UI", 10, "bold")
FONT_TITLE = ("Microsoft YaHei UI", 18, "bold")
FONT_SUB = ("Microsoft YaHei UI", 12, "bold")
FONT_SMALL = ("Microsoft YaHei UI", 9)
FONT_MONO = ("Consolas", 10)


def apply_style(root: tk.Tk) -> None:
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure(".", background=COL["bg"], foreground=COL["text"], font=FONT)
    style.configure("TFrame", background=COL["bg"])
    style.configure("Panel.TFrame", background=COL["panel"])
    style.configure("TLabel", background=COL["bg"], foreground=COL["text"])
    style.configure("Panel.TLabel", background=COL["panel"])
    style.configure("Sub.TLabel", foreground=COL["sub"], font=FONT_SMALL)
    style.configure("Title.TLabel", font=FONT_TITLE)
    style.configure("Head.TLabel", font=FONT_SUB)
    style.configure("TButton", padding=(12, 6))
    style.configure("Accent.TButton", font=FONT_B, foreground="#ffffff",
                    background=COL["accent"], padding=(16, 8))
    style.map("Accent.TButton",
              background=[("active", COL["accent_dark"]),
                          ("disabled", "#9dbfb4")])
    style.configure("Treeview", rowheight=26, font=FONT,
                    background=COL["panel"], fieldbackground=COL["panel"],
                    bordercolor=COL["border"])
    style.configure("Treeview.Heading", font=FONT_B,
                    background="#e6eaef", foreground=COL["text"])
    style.map("Treeview", background=[("selected", COL["select"])])
    style.configure("TNotebook", background=COL["bg"], borderwidth=0)
    style.configure("TNotebook.Tab", padding=(14, 6), font=FONT)
    style.configure("TProgressbar", troughcolor="#dfe5ec",
                    background=COL["accent"], borderwidth=0)
    style.configure("TLabelframe", background=COL["bg"])
    style.configure("TLabelframe.Label", font=FONT_B, foreground=COL["text"])
