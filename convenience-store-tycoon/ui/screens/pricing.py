"""定价与促销界面。"""

from core import catalog, inventory, pricing
from ui import console, theme


def run(game) -> None:
    state = game.state
    while True:
        console.clear()
        print(console.hr())
        print(theme.strong(" 定价管理"))
        print(theme.dim(" 售价远高于参考价会显著降低购买率；黄金位可支撑更高定价"))
        print(console.hr())
        rows = []
        for i, item in enumerate(catalog.all_items(), start=1):
            price = state.prices.get(item.id, item.ref_price)
            margin = pricing.margin_rate(state, item.id)
            ratio = price / item.ref_price if item.ref_price else 0
            tag = ""
            if ratio >= 1.25:
                tag = "⚠ 远高于参考价"
            elif ratio >= 1.1:
                tag = "偏高"
            elif ratio <= 0.8:
                tag = "引流价"
            on_shelf = inventory.item_on_shelf_qty(state, item.id)
            rows.append([
                str(i), item.name, f"{item.unit_cost:.1f}",
                f"{price:.2f}", f"{item.ref_price:.1f}",
                f"{margin * 100:.0f}%", str(on_shelf), tag,
            ])
        console.table(
            ["序", "商品", "进价", "现售价", "参考价", "毛利率", "在架", "提示"],
            rows, right={2, 3, 4, 5, 6})
        print()
        raw = console.ask_line(
            "[编号 新售价] 修改定价 · [p] 促销设置 · 回车返回: ").strip()
        if not raw:
            return
        if raw.lower() == "p":
            _promo_mode(game)
            continue
        parts = raw.split()
        if len(parts) != 2:
            print(theme.warn("格式: 编号 新售价（如 1 2.2）"))
            console.pause()
            continue
        try:
            idx = int(parts[0]) - 1
            price = float(parts[1])
        except ValueError:
            print(theme.warn("输入不合法"))
            console.pause()
            continue
        if not (0 <= idx < len(catalog.all_items())):
            print(theme.warn("编号不存在"))
            console.pause()
            continue
        err = game.set_price(catalog.all_items()[idx].id, price)
        if err:
            print(theme.bad(err))
        else:
            print(theme.good("✓ 已更新售价"))
        console.pause()


def _promo_mode(game) -> None:
    state = game.state
    while True:
        console.clear()
        print(console.hr())
        print(theme.strong(" 促销设置（折扣持续 3 天，0 = 取消）"))
        print(console.hr())
        rows = []
        for i, item in enumerate(catalog.all_items(), start=1):
            promo = state.promos.get(item.id)
            on_shelf = inventory.item_on_shelf_qty(state, item.id)
            eff = pricing.effective_price(state, item.id)
            rows.append([
                str(i), item.name, f"{state.prices.get(item.id, item.ref_price):.2f}",
                f"-{promo.discount * 100:.0f}%" if promo else "-",
                f"{eff:.2f}",
                f"{promo.days_left}天" if promo else "-",
                str(on_shelf),
            ])
        console.table(
            ["序", "商品", "售价", "促销", "生效价", "剩余", "在架"],
            rows, right={2, 3, 4, 5, 6})
        print()
        raw = console.ask_line(
            "[编号 折扣%] 设置（如 2 20）· 回车返回: ").strip()
        if not raw:
            return
        parts = raw.split()
        if len(parts) != 2:
            print(theme.warn("格式: 编号 折扣%（如 2 20，取消填 0）"))
            console.pause()
            continue
        try:
            idx = int(parts[0]) - 1
            pct_value = float(parts[1])
        except ValueError:
            print(theme.warn("输入不合法"))
            console.pause()
            continue
        if not (0 <= idx < len(catalog.all_items())):
            print(theme.warn("编号不存在"))
            console.pause()
            continue
        err = game.set_promo(catalog.all_items()[idx].id, pct_value)
        if err:
            print(theme.bad(err))
        else:
            print(theme.good("✓ 促销已更新"))
        console.pause()
