"""每日结算单。"""

from config import balance as B
from core import catalog
from ui import console, theme


def run(game, report) -> None:
    console.clear()
    width = 74
    print(console.hr(width))
    print(theme.strong(f" 第 {report.day} 天 [{report.weekday}] 结算单"))
    print(console.hr(width))
    print(" 营业流水")
    print(f"   营收            {console.signed_money(report.revenue):>14}"
          f"    ({report.conversions} 单 / 进店 {report.traffic} 人)")
    print(f"   售出成本        {console.signed_money(-report.cogs):>14}"
          f"    毛利率 {_gross_margin(report):>5}")
    if report.spoilage > 0:
        detail = "、".join(f"{_name(i)}×{q}" for i, q in report.spoilage_items)
        print(theme.bad(
            f"   报废损失        {console.signed_money(-report.spoilage):>14}"
            f"    ({detail})"))
    print(" 固定费用")
    print(f"   房租            {console.signed_money(-report.rent):>14}"
          f"    水电 {console.signed_money(-report.utilities)}")
    print(console.hr(width))
    net_color = theme.good if report.net >= 0 else theme.bad
    print(" " + net_color(
        f" 今日净利        {console.signed_money(report.net):>14}"
        f"    {_streak_text(game)}"))
    print(f" 现金余额        {console.money(report.closing_cash):>14}"
          f"    净资产 {console.money(report.net_worth)}")
    print(" KPI: "
          f"转化率 {console.pct(report.conversion_rate)} · "
          f"客单价 {console.money(report.aov)} · "
          f"周转 {report.turnover:.2f} · "
          f"缺货率 {console.pct(report.oos_rate)} · "
          f"报废率 {console.pct(report.waste_rate)}")
    sat_text = f"{report.sat_avg:.0f}" if report.sat_avg else "—"
    print(f" 满意度 {sat_text} · 声望 {report.rep_before:.0f} → "
          f"{report.rep_after:.0f} {console.stars(report.rep_after)}")
    if (report.abandon_rate > B.QUEUE_PENALTY_RATE
            or report.lost_at_close):
        print(theme.warn(
            f" ⚠ 排队流失 {report.abandons} 人，打烊滞留 "
            f"{report.lost_at_close} 人 → 考虑减少高峰缺货与提升收银效率"))
    print(console.hr(width))

    preset = B.DIFFICULTIES[game.state.difficulty]
    progress = min(100.0, report.net_worth / preset.victory_net_worth * 100)
    print(f" 胜利目标: 净资产 {console.money(preset.victory_net_worth)}"
          f"（当前达成 {progress:.1f}%）")

    if report.victory:
        print()
        _banner("★ 达成目标！你的便利店帝国起步了！", theme.good)
    if report.bankrupt:
        print()
        _banner("× 现金枯竭，门店破产清算……", theme.bad)
    console.pause()


def _banner(text: str, color) -> None:
    bar = "═" * (console.dw(text) + 4)
    print(color(f"  ╔{bar}╗"))
    print(color(f"  ║  {text}  ║"))
    print(color(f"  ╚{bar}╝"))


def _streak_text(game) -> str:
    streak = 0
    for entry in reversed(game.state.ledger):
        if entry["net"] > 0:
            streak += 1
        else:
            break
    return f"[连续盈利 {streak} 天]" if streak >= 2 else ""


def _gross_margin(report) -> str:
    if report.revenue <= 0:
        return "—"
    rate = (report.revenue - report.cogs) / report.revenue * 100
    return f"{rate:.1f}%"


def _name(item_id: str) -> str:
    return catalog.get(item_id).name
