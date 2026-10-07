"""日仿真引擎：16 个小时刻度推进，产出 DayLog（逐事件流水）。

core 零 IO：本模块只做计算，输出数据结构由 UI 渲染。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from config import balance as B
from core import catalog, customer as customer_mod, inventory, pricing, traffic
from core.rng import GameRNG
from core.state import GameState


@dataclass
class HourLog:
    hour: int = 0
    arrivals: int = 0
    served: int = 0
    conversions: int = 0
    revenue: float = 0.0
    abandons: int = 0
    sat_hour: float = 0.0        # 本小时满意度均值（无成交样本则为 0）
    notes: List[str] = field(default_factory=list)


@dataclass
class DayLog:
    hour_logs: List[HourLog] = field(default_factory=list)
    revenue: float = 0.0
    cogs: float = 0.0
    arrivals: int = 0
    served: int = 0
    conversions: int = 0
    abandons: int = 0
    lost_at_close: int = 0
    oos_needs: int = 0
    total_needs: int = 0
    items_sold: Dict[str, int] = field(default_factory=dict)
    sat_samples: List[float] = field(default_factory=list)

    @property
    def sat_avg(self) -> float:
        if not self.sat_samples:
            return 0.0
        return sum(self.sat_samples) / len(self.sat_samples)


def _service_minutes(picks: List[Tuple[str, int]]) -> float:
    total_items = sum(q for _, q in picks)
    return B.QUEUE_SERVICE_MIN_BASE + B.QUEUE_PER_ITEM_MIN * total_items


def _checkout(state: GameState, basket, log: DayLog, hlog: HourLog) -> None:
    """结账：FIFO 扣库存、计营收/COGS、产生满意度样本。

    满意度为绝对值口径：SAT_NEUTRAL(70) ± 当次体验增量。
    """
    revenue = 0.0
    sat = B.SAT_NEUTRAL + B.SAT_BASE
    for item_id, qty in basket.picks:
        slot = inventory.slot_with_item(state, item_id)
        if slot is None or slot.qty < qty:
            # 理论上 shop() 已按货架余量封顶；防御性降量
            if slot is None:
                continue
            qty = slot.qty
            if qty <= 0:
                continue
        price = pricing.effective_price(state, item_id)
        revenue += price * qty
        consumed = inventory.consume(state, slot, qty)
        log.cogs += sum(q * cost for q, cost in consumed)
        log.items_sold[item_id] = log.items_sold.get(item_id, 0) + qty
        ref = catalog.get(item_id).ref_price
        unfair = max(0.0, min(1.0, price / ref - 1.0)) if ref > 0 else 1.0
        sat -= B.SAT_PRICE_UNFAIR_COEF * unfair
    sat -= B.SAT_OOS_SUB * basket.sub_count
    sat -= B.SAT_OOS_NOSUB * (basket.oos_count - basket.sub_count)
    log.revenue += revenue
    hlog.revenue += revenue
    log.sat_samples.append(sat)
    if basket.picks:
        log.conversions += 1
    log.served += 1
    hlog.served += 1


def _run_hour(state: GameState, rng: GameRNG, queue: List, log: DayLog) -> HourLog:
    """推进一个小时刻度：到达→决策→排队→结账。queue 跨小时延续。"""
    hlog = HourLog(hour=0)
    busy_box = [0.0]

    def try_serve() -> None:
        while queue:
            basket = queue[0]
            svc = _service_minutes(basket.picks)
            if busy_box[0] + svc > 60.0:
                break
            queue.pop(0)
            busy_box[0] += svc
            _checkout(state, basket, log, hlog)

    hour = B.DAY_START_HOUR + len(log.hour_logs)

    # 1) 服务上一小时遗留的排队顾客
    conv0, sat_n0 = log.conversions, len(log.sat_samples)
    try_serve()

    # 2) 本小时到达
    n = traffic.arrivals_for_hour(state, hour, rng)
    hlog.arrivals = n
    log.arrivals += n

    arrivals = [customer_mod.build_customer(
        state, rng, traffic.pick_archetype(hour, rng)) for _ in range(n)]
    arrivals.sort(key=lambda c: rng.random())   # 分钟级随机到达次序

    oos_note: Dict[str, int] = {}
    for cust in arrivals:
        if len(queue) > cust.patience:
            hlog.abandons += 1
            log.abandons += 1
            continue
        basket = customer_mod.shop(cust, state, rng)
        log.total_needs += len(cust.needs)
        log.oos_needs += basket.oos_count
        if basket.oos_count:
            # 记录缺货商品名（需求为商品级），供小时摘要展示
            for item_id, _q in cust.needs:
                if inventory.slot_with_item(state, item_id) is None:
                    oos_note[item_id] = oos_note.get(item_id, 0) + 1
        queue.append(basket)
        try_serve()

    hlog.conversions = log.conversions - conv0
    new_sat = log.sat_samples[sat_n0:]
    if new_sat:
        hlog.sat_hour = sum(new_sat) / len(new_sat)
    if hlog.abandons:
        hlog.notes.append(f"排队放弃 {hlog.abandons} 人")
    if oos_note:
        detail = "、".join(f"{catalog.get(k).name}×{v}"
                           for k, v in oos_note.items())
        hlog.notes.append(f"缺货: {detail}")
    hlog.hour = hour
    return hlog


def iter_day_hours(state: GameState, rng: GameRNG):
    """逐小时生成器（供实时 UI 驱动）：yield (hour, HourLog)；
    耗尽时 StopIteration.value 携带完整 DayLog（含打烊滞留）。"""
    log = DayLog()
    queue: List = []   # 等待结账的购物篮（跨小时延续，打烊清空）
    for _ in range(B.DAY_END_HOUR - B.DAY_START_HOUR):
        hlog = _run_hour(state, rng, queue, log)
        log.hour_logs.append(hlog)
        yield hlog.hour, hlog
    log.lost_at_close = len(queue)
    return log


def run_day(state: GameState, rng: GameRNG) -> DayLog:
    log = DayLog()
    queue: List = []   # 等待结账的购物篮（跨小时延续，打烊清空）
    for _ in range(B.DAY_END_HOUR - B.DAY_START_HOUR):
        log.hour_logs.append(_run_hour(state, rng, queue, log))
    log.lost_at_close = len(queue)
    return log
