"""库存明细 / KPI 趋势 / 销售排行。"""

from core import catalog, inventory
from ui import console, theme


def run(game) -> None:
    while True:
        console.clear()
        key = console.menu(" 报表中心", [
            ("1", "库存明细（批次级）"),
            ("2", "KPI 趋势与营收图表"),
            ("3", "商品销售排行"),
            ("0", "返回"),
        ])
        if key == "0":
            return
        if key == "1":
            _inventory_detail(game)
        elif key == "2":
            _kpi_trend(game)
        elif key == "3":
            _sales_rank(game)


def _inventory_detail(game) -> None:
    console.clear()
    state = game.state
    print(console.hr())
    print(theme.strong(" 库存明细（含在架部分）"))
    print(console.hr())
    rows = []
    for item in catalog.all_items():
        batches = [b for b in state.warehouse if b.item_id == item.id and b.qty > 0]
        if not batches:
            continue
        total = sum(b.qty for b in batches)
        soonest = min(b.expire_day - state.day for b in batches)
        avg = inventory.avg_daily_sales(state, item.id)
        have_days = (total / avg) if avg > 0 else float("inf")
        status = []
        if soonest <= 2:
            status.append("⚠临期")
        if have_days > 3 * 1.5:
            status.append("⚠滞销")
        rows.append([
            item.name, str(len(batches)), str(total),
            f"{item.unit_cost:.1f}", f"剩{soonest}天",
            "—" if avg == 0 else f"{have_days:.1f}天",
            " ".join(status) or "正常",
        ])
    if rows:
        console.table(["商品", "批次数", "数量", "进价", "最近到期",
                       "库存天数", "状态"], rows, right={1, 2, 3, 4, 5})
    else:
        print(" （库存为空）")
    stagnant = inventory.stagnant_items(state)
    if stagnant:
        names = "、".join(catalog.get(i).name for i, _ in stagnant)
        print(theme.warn(f" ⚠ 滞销清单: {names} → 降价 / 促销 / 停止进货"))
    console.pause()


def _kpi_trend(game) -> None:
    console.clear()
    ledger = game.state.ledger
    print(console.hr())
    print(theme.strong(" 近 14 日营收（元）"))
    print(console.hr())
    recent = ledger[-14:]
    if recent:
        console.bar_chart([(f"D{e['day']}", e["revenue"]) for e in recent])
    else:
        print(" （暂无数据）")
    print()
    if ledger:
        last = ledger[-1]
        week = ledger[-7:]
        def wavg(key):
            return sum(e[key] for e in week) / len(week)
        rows = [[
            "营收", console.money(last["revenue"]), console.money(wavg("revenue")),
        ], [
            "净利", console.signed_money(last["net"]),
            console.signed_money(wavg("net")),
        ], [
            "客流", str(last["traffic"]), f"{wavg('traffic'):.0f}",
        ], [
            "转化率", console.pct(last["conv_rate"]),
            console.pct(wavg("conv_rate")),
        ], [
            "客单价", console.money(last["aov"]), console.money(wavg("aov")),
        ], [
            "缺货率", console.pct(last["oos_rate"]),
            console.pct(wavg("oos_rate")),
        ], [
            "周转率", f"{last['turnover']:.2f}", f"{wavg('turnover'):.2f}",
        ], [
            "报废率", console.pct(last["waste_rate"]),
            console.pct(wavg("waste_rate")),
        ], [
            "满意度", f"{last['sat']:.0f}", f"{wavg('sat'):.0f}",
        ]]
        console.table(["指标", "今日", "7日均值"], rows, right={1, 2})
    console.pause()


def _sales_rank(game) -> None:
    console.clear()
    state = game.state
    print(console.hr())
    print(theme.strong(" 商品销售排行（近 7 日）"))
    print(console.hr())
    rows = []
    for item in catalog.all_items():
        hist = state.sales_history.get(item.id, [])
        total7 = sum(hist)
        today = hist[-1] if hist else 0
        rows.append([item.name, str(today), str(total7),
                     str(inventory.item_on_shelf_qty(state, item.id)
                         + inventory.item_warehouse_qty(state, item.id))])
    rows.sort(key=lambda r: -int(r[2]))
    console.table(["商品", "今日", "7日合计", "当前库存"], rows,
                  right={1, 2, 3})
    console.pause()
