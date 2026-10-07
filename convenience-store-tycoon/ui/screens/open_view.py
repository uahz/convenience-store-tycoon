"""营业实录：渲染 DayLog 的逐小时流水。"""

from ui import console, theme


def run(game, report) -> None:
    daylog = game.last_daylog
    console.clear()
    print(console.hr())
    print(theme.strong(
        f" 第 {report.day} 天 [{report.weekday}] 营业实录"))
    print(console.hr())
    print(theme.dim("  时刻     到达  服务  营收        备注"))
    for hlog in daylog.hour_logs:
        notes = "；".join(hlog.notes) if hlog.notes else ""
        line = (f"  {hlog.hour:02d}:00   {hlog.arrivals:4d}  {hlog.served:4d}  "
                f"{console.money(hlog.revenue):>10}")
        if hlog.abandons:
            line = theme.warn(line)
        print(line + (theme.dim("   " + notes) if notes else ""))
    print(console.hr())
    print(f"  全日: 到达 {daylog.arrivals} · 服务 {daylog.served} · "
          f"成交 {daylog.conversions} 单 · 排队放弃 {daylog.abandons} · "
          f"打烊滞留 {daylog.lost_at_close}")
    print(f"  营收 {console.money(daylog.revenue)} · "
          f"售出成本 {console.money(daylog.cogs)} · "
          f"商品售出 {sum(daylog.items_sold.values())} 件")
    console.pause()
