"""结局画面（胜利 / 破产）。"""

import save.savegame as savegame
from ui import console, theme


def victory(game, report) -> None:
    console.clear()
    print()
    print(theme.strong(theme.good(
        " ╔══════════════════════════════════════════════════╗")))
    print(theme.strong(theme.good(
        " ║        ★ 胜 利 —— 社 区 便 利 店 之 王 ★        ║")))
    print(theme.strong(theme.good(
        " ╚══════════════════════════════════════════════════╝")))
    print()
    _stats(game, report)
    console.pause()


def bankrupt(game, report) -> None:
    console.clear()
    print()
    print(theme.strong(theme.bad(
        " ╔══════════════════════════════════════════════════╗")))
    print(theme.strong(theme.bad(
        " ║        × 破 产 —— 现金枯竭，门店清算              ║")))
    print(theme.strong(theme.bad(
        " ╚══════════════════════════════════════════════════╝")))
    print()
    _stats(game, report)
    savegame.delete_save("autosave")
    print(theme.dim(" （自动存档已清除）"))
    console.pause()


def _stats(game, report) -> None:
    ledger = game.state.ledger
    days = len(ledger)
    total_rev = sum(e["revenue"] for e in ledger)
    total_net = sum(e["net"] for e in ledger)
    print(f" 经营天数   {days} 天")
    print(f" 累计营收   {console.money(total_rev)}")
    print(f" 累计净利   {console.signed_money(total_net)}")
    print(f" 最终声望   {console.stars(game.state.reputation)} "
          f"({game.state.reputation:.0f})")
    print(f" 结算日     第 {report.day} 天 · 净资产 "
          f"{console.money(report.net_worth)}")
