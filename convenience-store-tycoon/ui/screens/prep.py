"""晨间营业准备（每日主界面 / Hub）。"""

from ui import console, theme


def run(game) -> str:
    """返回 "open" | "menu"。"""
    while True:
        console.clear()
        info = game.morning_info()
        state = game.state
        _header(game, info)
        _notices(info)

        key = console.menu("", [
            ("1", "进货订货"),
            ("2", "定价与促销"),
            ("3", "货架陈列"),
            ("4", "晨报详情 / 昨日小结"),
            ("5", "玩法说明"),
            ("6", "▶ 开门营业"),
            ("0", "退出到主菜单（未结算进度不保存）"),
        ])
        if key == "1":
            from ui.screens import procurement
            procurement.run(game)
        elif key == "2":
            from ui.screens import pricing
            pricing.run(game)
        elif key == "3":
            from ui.screens import shelving
            shelving.run(game)
        elif key == "4":
            _morning_report(game, info)
        elif key == "5":
            from ui.screens import help_screen
            help_screen.run()
        elif key == "6":
            if info["on_shelf"] == 0:
                print(theme.warn("⚠ 货架上没有任何商品，开门将不会产生任何生意。"))
                confirm = console.ask_line("仍要开门吗？(y/N): ").strip().lower()
                if confirm != "y":
                    continue
            return "open"
        elif key == "0":
            return "menu"


def _header(game, info) -> None:
    state = game.state
    print(console.hr())
    print(theme.strong(
        f" 第 {info['day']} 天 [{info['weekday']}] 晨间准备     "
        f"现金: {console.money(state.cash)}   "
        f"声望: {console.stars(state.reputation)} ({state.reputation:.0f})"))
    print(console.hr())
    print(theme.dim(
        f" 仓库: {info['warehouse_used']}/{info['warehouse_used'] + info['warehouse_free']} 件"
        f"   货架: {info['slots_filled']}/{len(state.slots)} 槽在售"
        f" ({info['on_shelf']} 件)   进行中促销: {info['active_promos']} 个"))
    print(console.hr())


def _notices(info) -> None:
    if info["spoilage_cost"] > 0:
        names = "、".join(
            f"{_name(i)}×{q}" for i, q in info["spoilage_items"])
        print(theme.bad(
            f" ✦ 今晨报废: {names}，损失 {console.money(info['spoilage_cost'])}"
            "（进货前先看库存！）"))
    for item_id, qty, days in info["expiry_warns"]:
        print(theme.warn(
            f" ⚠ 临期: {_name(item_id)} 还有 {qty} 件，"
            f"剩余 {days} 天保质期 → 建议促销或清仓"))
    for item_id, ratio in info["stagnants"]:
        ratio_text = "滞销(无销量)" if ratio == 9.9 else f"周转超标 {ratio:.1f} 倍"
        print(theme.warn(f" ⚠ 滞销: {_name(item_id)} — {ratio_text}"))


def _morning_report(game, info) -> None:
    console.clear()
    print(console.hr())
    print(theme.strong(f" 第 {info['day']} 天 晨报"))
    print(console.hr())
    ledger = game.state.ledger
    if ledger:
        y = ledger[-1]
        print(f" 昨日（第 {y['day']} 天）小结:")
        print(f"   营收 {console.money(y['revenue'])} · 净利 "
              f"{console.signed_money(y['net'])} · 客流 {y['traffic']} · "
              f"成交 {y['conversions']} 单")
        print(f"   声望 {y['rep']} · 满意度 {y['sat']} · "
              f"缺货率 {console.pct(y['oos_rate'])}")
    else:
        print(" 今天是开业第一天。先去进货，把货架填满！")
    print()
    if info["spoilage_items"]:
        print(" 今晨报废明细:")
        for item_id, qty in info["spoilage_items"]:
            print(f"   · {_name(item_id)} ×{qty}")
    if info["expiry_warns"]:
        print(" 临期预警（剩余保质期 ≤ 2 天）:")
        for item_id, qty, days in info["expiry_warns"]:
            print(f"   · {_name(item_id)} ×{qty}（剩 {days} 天）")
    console.pause()


def _name(item_id: str) -> str:
    from core import catalog
    return catalog.get(item_id).name
