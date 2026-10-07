"""每日结算（纯函数式：状态 + DayLog → DayReport + 新状态）与 KPI 账本。"""

from dataclasses import dataclass, field
from typing import Dict, List

from config import balance as B
from core import catalog, economy, inventory
from core.simulation import DayLog
from core.state import GameState


@dataclass
class DayReport:
    day: int
    weekday: str
    revenue: float = 0.0
    cogs: float = 0.0
    spoilage: float = 0.0
    spoilage_items: List = field(default_factory=list)   # [(item_id, qty)]
    rent: float = 0.0
    utilities: float = 0.0
    net: float = 0.0
    opening_cash: float = 0.0
    closing_cash: float = 0.0
    net_worth: float = 0.0
    traffic: int = 0
    conversions: int = 0
    conversion_rate: float = 0.0
    aov: float = 0.0
    oos_rate: float = 0.0
    turnover: float = 0.0
    waste_rate: float = 0.0
    abandon_rate: float = 0.0
    abandons: int = 0
    lost_at_close: int = 0
    sat_avg: float = 0.0
    rep_before: float = 0.0
    rep_after: float = 0.0
    items_sold: Dict[str, int] = field(default_factory=dict)
    victory: bool = False
    bankrupt: bool = False


def settle(state: GameState, daylog: DayLog, inv_value_start: float,
           spoilage_cost: float, spoilage_items: List) -> DayReport:
    preset = B.DIFFICULTIES[state.difficulty]
    report = DayReport(day=state.day, weekday=B.DAY_NAMES[(state.day - 1) % 7])
    report.revenue = daylog.revenue
    report.cogs = daylog.cogs
    report.spoilage = spoilage_cost
    report.spoilage_items = list(spoilage_items)
    report.rent = B.RENT_PER_DAY * preset.rent_mult
    report.utilities = B.UTILITY_BASE + B.UTILITY_RATE * daylog.revenue

    fixed = report.rent + report.utilities
    report.net = daylog.revenue - daylog.cogs - spoilage_cost - fixed

    # ---- 现金：营收入账，固定费用支出（采购支出已在下单时扣除）----
    report.opening_cash = state.cash
    state.cash += daylog.revenue - fixed
    report.closing_cash = state.cash
    report.net_worth = economy.net_worth(state)

    # ---- KPI ----
    report.traffic = daylog.arrivals
    report.conversions = daylog.conversions
    report.conversion_rate = (daylog.conversions / daylog.arrivals
                              if daylog.arrivals else 0.0)
    report.aov = (daylog.revenue / daylog.conversions
                  if daylog.conversions else 0.0)
    report.oos_rate = (daylog.oos_needs / daylog.total_needs
                       if daylog.total_needs else 0.0)
    report.abandon_rate = (daylog.abandons / daylog.arrivals
                           if daylog.arrivals else 0.0)
    report.abandons = daylog.abandons
    report.lost_at_close = daylog.lost_at_close
    inv_value_end = inventory.inventory_value(state)
    avg_inv = (inv_value_start + inv_value_end) / 2.0
    report.turnover = daylog.cogs / avg_inv if avg_inv > 0 else 0.0
    purchases_total = sum(state.purchases_7d)
    report.waste_rate = (spoilage_cost / purchases_total
                         if purchases_total > 0 else 0.0)
    report.items_sold = dict(daylog.items_sold)

    # ---- 满意度 → 声望 / 忠诚度 ----
    report.rep_before = state.reputation
    if daylog.sat_samples:
        sat_avg = max(0.0, min(100.0, daylog.sat_avg))
        if report.abandon_rate > B.QUEUE_PENALTY_RATE:
            sat_avg -= min(B.SAT_QUEUE_PENALTY_MAX,
                           (report.abandon_rate - B.QUEUE_PENALTY_RATE)
                           * B.SAT_QUEUE_PENALTY_SLOPE)
        report.sat_avg = sat_avg
        rep_delta = max(-B.REP_DAILY_LIMIT, min(B.REP_DAILY_LIMIT,
                        B.REP_GAIN_COEF * (sat_avg - B.SAT_BASELINE)))
        state.reputation = max(0.0, min(100.0, state.reputation + rep_delta))
        loyalty_delta = max(-B.LOYALTY_DAILY_LIMIT, min(B.LOYALTY_DAILY_LIMIT,
                            B.LOYALTY_DAILY_GAIN
                            * (sat_avg - B.SAT_BASELINE) / B.SAT_BASELINE))
        for arch_id in state.archetype_loyalty:
            state.archetype_loyalty[arch_id] = max(
                0.0, min(1.0, state.archetype_loyalty[arch_id] + loyalty_delta))
    else:
        report.sat_avg = 0.0
        if report.abandon_rate > B.REP_ABANDON_RATE:
            state.reputation = max(0.0, state.reputation - min(
                B.REP_ABANDON_PENALTY_MAX,
                (daylog.abandon_rate - B.REP_ABANDON_RATE) * B.REP_ABANDON_SLOPE))
    report.rep_after = state.reputation

    # ---- 历史档案 ----
    for item in catalog.all_items():
        hist = state.sales_history.setdefault(item.id, [])
        hist.append(daylog.items_sold.get(item.id, 0))
        del hist[:-B.SALES_HISTORY_DAYS]
    state.purchases_7d.append(state.procurement_today)
    del state.purchases_7d[:-B.WASTE_RATE_WINDOW_DAYS]
    state.procurement_today = 0.0

    state.ledger.append({
        "day": state.day, "revenue": round(report.revenue, 2),
        "cogs": round(report.cogs, 2), "spoilage": round(report.spoilage, 2),
        "fixed": round(fixed, 2), "net": round(report.net, 2),
        "traffic": report.traffic, "conversions": report.conversions,
        "conv_rate": round(report.conversion_rate, 4),
        "aov": round(report.aov, 2), "oos_rate": round(report.oos_rate, 4),
        "turnover": round(report.turnover, 4),
        "waste_rate": round(report.waste_rate, 4),
        "sat": round(report.sat_avg, 1), "rep": round(state.reputation, 1),
        "cash": round(state.cash, 2), "net_worth": round(report.net_worth, 2),
    })
    del state.ledger[:-B.LEDGER_KEEP_DAYS]

    report.bankrupt = state.cash < B.BANKRUPTCY_CASH
    report.victory = (not report.bankrupt
                      and report.net_worth >= preset.victory_net_worth)
    return report
