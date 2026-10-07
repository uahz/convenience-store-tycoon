"""控制台 IO 原语：菜单、输入校验、表格、柱状图、格式化。

约定：表格单元格内不使用颜色码（宽度计算会被破坏），颜色只用于整行。
"""

import unicodedata
from typing import List, Optional, Sequence, Set, Tuple

from ui import theme


# ---------- 宽度与格式化 ----------

def dw(s: str) -> int:
    """显示宽度：东亚全角字符按 2 列计。"""
    return sum(2 if unicodedata.east_asian_width(ch) in ("F", "W") else 1
               for ch in s)


def pad(s: str, width: int, align: str = "left") -> str:
    gap = max(0, width - dw(s))
    if align == "right":
        return " " * gap + s
    if align == "center":
        left = gap // 2
        return " " * left + s + " " * (gap - left)
    return s + " " * gap


def money(v: float) -> str:
    v = float(v)
    if abs(v - round(v)) < 0.005:
        return f"¥{round(v):,.0f}"
    return f"¥{v:,.2f}"


def signed_money(v: float) -> str:
    sign = "+" if v >= 0 else "-"
    return sign + money(abs(v))


def pct(v: float, digits: int = 1) -> str:
    return f"{v * 100:.{digits}f}%"


def stars(rep: float) -> str:
    filled = max(0, min(5, round(rep / 20)))
    return theme.BOX["star"] * filled + theme.BOX["hollow"] * (5 - filled)


# ---------- 屏幕原语 ----------

def clear() -> None:
    if theme.ASCII:
        print("\n" * 2)
    else:
        print("\x1b[2J\x1b[H", end="")


def hr(width: int = 76) -> str:
    return theme.dim(theme.BOX["h"] * width)


def pause(msg: str = "回车继续 ...") -> None:
    try:
        input(msg)
    except EOFError:
        raise


def menu(prompt: str, options: Sequence[Tuple[str, str]],
         tip: Optional[str] = None) -> str:
    """渲染编号菜单并循环直到输入合法选项 key（大小写不敏感）。"""
    keys = []
    for key, label in options:
        print(f"  [{key}] {label}")
        keys.append(key.lower())
    if tip:
        print(theme.dim(tip))
    while True:
        raw = input(f"{prompt}> ").strip().lower()
        if raw in keys:
            return raw
        print(theme.warn("无效选择，请重新输入"))


def ask_line(prompt: str) -> str:
    try:
        return input(prompt)
    except EOFError:
        return ""


def ask_float(prompt: str, lo: float, hi: float,
              blank_ok: bool = False) -> Optional[float]:
    while True:
        raw = input(prompt).strip()
        if blank_ok and raw == "":
            return None
        try:
            v = float(raw)
        except ValueError:
            print(theme.warn("请输入数字"))
            continue
        if lo <= v <= hi:
            return v
        print(theme.warn(f"请输入 {lo} ~ {hi} 之间的数值"))


def ask_int(prompt: str, lo: int, hi: int,
            blank_ok: bool = False) -> Optional[int]:
    while True:
        raw = input(prompt).strip()
        if blank_ok and raw == "":
            return None
        try:
            v = int(raw)
        except ValueError:
            print(theme.warn("请输入整数"))
            continue
        if lo <= v <= hi:
            return v
        print(theme.warn(f"请输入 {lo} ~ {hi} 之间的整数"))


# ---------- 表格 ----------

def table(headers: List[str], rows: List[List[str]],
          right: Set[int] = frozenset()) -> None:
    widths = [dw(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], dw(str(cell)))

    def border(left: str, mid: str, right_ch: str) -> str:
        return (left + mid.join(theme.BOX["h"] * (w + 2) for w in widths)
                + right_ch)

    def render(row: List[str]) -> str:
        cells = []
        for i, cell in enumerate(row):
            align = "right" if i in right else "left"
            cells.append(" " + pad(str(cell), widths[i], align) + " ")
        return theme.BOX["v"] + theme.BOX["v"].join(cells) + theme.BOX["v"]

    print(border(theme.BOX["tl"], theme.BOX["cross"], theme.BOX["tr"]))
    print(render(headers))
    print(border(theme.BOX["ml"], theme.BOX["cross"], theme.BOX["mr"]))
    for row in rows:
        print(render(row))
    print(border(theme.BOX["bl"], theme.BOX["cross"], theme.BOX["br"]))


def bar_chart(pairs: Sequence[Tuple[str, float]], bar_width: int = 36,
              unit: str = "") -> None:
    """横向柱状图。pairs: [(标签, 数值)]。"""
    max_v = max((abs(v) for _, v in pairs), default=0.0) or 1.0
    for label, v in pairs:
        n = int(round(abs(v) / max_v * bar_width))
        bar = theme.BOX["bar"] * n
        print(f" {pad(label, 8)}│{bar} {v:,.0f}{unit}")
