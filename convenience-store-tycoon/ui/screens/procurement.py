"""进货界面：目录 + 订单车。"""

import math

from config import balance as B
from core import catalog, inventory
from ui import console, theme


def run(game) -> None:
    state = game.state
    cart: dict = {}
    while True:
        console.clear()
        capacity = B.WAREHOUSE_CAPACITY
        print(console.hr())
        print(theme.strong(
            f" 进货订货   现金 {console.money(state.cash)}   "
            f"仓库 {inventory.warehouse_units(state)}/{capacity} 件"))
        print(theme.dim(" 供应商: 标准供货（当日早到货）· 按整箱进货"))
        print(console.hr())

        rows = []
        for i, item in enumerate(catalog.all_items(), start=1):
            wh = inventory.item_warehouse_qty(state, item.id)
            shelf = inventory.item_on_shelf_qty(state, item.id)
            avg = inventory.avg_daily_sales(state, item.id)
            suggest_units = inventory.suggested_order_units(state, item.id)
            suggest_cases = math.ceil(suggest_units / item.case_size)
            rows.append([
                str(i), item.name, f"{item.unit_cost:.1f}",
                f"{item.ref_price:.1f}", f"{item.shelf_life_days}天",
                f"{item.case_size}", str(wh), str(shelf),
                f"{avg:.1f}", str(suggest_cases) if suggest_cases else "-",
            ])
        console.table(
            ["序", "商品", "进价", "参考价", "保质", "箱规",
             "仓库", "货架", "7日均销", "建议(箱)"],
            rows, right={2, 3, 5, 6, 7, 8, 9})

        if cart:
            print()
            total_cost = 0
            total_units = 0
            for iid, cases in cart.items():
                item = catalog.get(iid)
                total_cost += item.unit_cost * item.case_size * cases
                total_units += item.case_size * cases
            names = "  ".join(
                f"{catalog.get(iid).name}×{cases}箱"
                for iid, cases in sorted(cart.items(),
                                         key=lambda kv: catalog.all_items().index(
                                             catalog.get(kv[0]))))
            print(f" 订单车: {names}")
            free = inventory.warehouse_free(state)
            units_text = theme.warn(f"{total_units} 件 > 剩余 {free} 件 ⚠") \
                if total_units > free else f"{total_units} 件"
            print(f" 合计 {console.money(total_cost)} · 共 {units_text}"
                  f"（仓库剩余 {free} 件）")
        print()
        raw = console.ask_line(
            "[编号 箱数] 加购 · [d编号] 删除 · [y] 确认下单 · 回车返回: ").strip()
        if not raw:
            return
        low = raw.lower()
        if low == "y":
            err = game.confirm_order(cart)
            if err:
                print(theme.bad(f"下单失败：{err}"))
            else:
                cart = {}
                print(theme.good("✓ 订单已确认，货已到仓。"))
            console.pause()
            continue
        if low.startswith("d"):
            try:
                idx = int(low[1:]) - 1
                item = catalog.all_items()[idx]
                cart.pop(item.id, None)
            except (ValueError, IndexError):
                print(theme.warn("格式: d编号（如 d3）"))
                console.pause()
            continue
        parts = raw.split()
        if len(parts) != 2:
            print(theme.warn("格式: 编号 箱数（如 3 2）"))
            console.pause()
            continue
        try:
            idx = int(parts[0]) - 1
            cases = int(parts[1])
        except ValueError:
            print(theme.warn("编号与箱数必须是整数"))
            console.pause()
            continue
        if not (0 <= idx < len(catalog.all_items())) or cases <= 0:
            print(theme.warn("编号或箱数不合法"))
            console.pause()
            continue
        item = catalog.all_items()[idx]
        cart[item.id] = cart.get(item.id, 0) + cases
