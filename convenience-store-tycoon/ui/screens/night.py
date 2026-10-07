"""夜间运营菜单：报表 / 统计 / 保存 / 结束今天。"""

import save.savegame as savegame
from ui import console, theme


def run(game) -> str:
    """返回 "next" | "menu"。"""
    while True:
        console.clear()
        state = game.state
        print(console.hr())
        print(theme.strong(
            f" 第 {state.day} 天 [夜间运营]     "
            f"现金 {console.money(state.cash)} · "
            f"净资产 {console.money(game_net_worth(game))}"))
        print(console.hr())
        key = console.menu("", [
            ("1", "库存与经营报表"),
            ("2", "生涯统计"),
            ("3", "保存进度"),
            ("0", "结束今天（进入下一天）"),
        ])
        if key == "1":
            from ui.screens import reports
            reports.run(game)
        elif key == "2":
            _career(game)
        elif key == "3":
            try:
                path = savegame.save(game, "autosave")
                print(theme.good(f"✓ 已保存到 {path.name}"))
            except OSError as exc:
                print(theme.bad(f"保存失败：{exc}"))
            console.pause()
        elif key == "0":
            return "next"


def game_net_worth(game) -> float:
    from core import economy
    return economy.net_worth(game.state)


def _career(game) -> None:
    console.clear()
    ledger = game.state.ledger
    print(console.hr())
    print(theme.strong(" 生涯统计"))
    print(console.hr())
    if not ledger:
        print(" （暂无经营数据）")
        console.pause()
        return
    days = len(ledger)
    total_rev = sum(e["revenue"] for e in ledger)
    total_net = sum(e["net"] for e in ledger)
    best = max(ledger, key=lambda e: e["net"])
    total_traffic = sum(e["traffic"] for e in ledger)
    total_orders = sum(e["conversions"] for e in ledger)
    print(f" 经营天数     {days} 天")
    print(f" 累计营收     {console.money(total_rev)}")
    print(f" 累计净利     {console.signed_money(total_net)}")
    print(f" 最好一天     第 {best['day']} 天（净利 "
          f"{console.signed_money(best['net'])}）")
    print(f" 累计客流     {total_traffic} 人 · 成交 {total_orders} 单")
    print(f" 当前声望     {console.stars(game.state.reputation)} "
          f"({game.state.reputation:.0f})")
    print(console.hr())
    console.pause()
