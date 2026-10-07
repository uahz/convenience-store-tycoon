"""库存规则：批次池、FIFO、上架/取下/售出扣减、过期报废。

批次统一存于 state.warehouse 池；货架槽位通过 (batch_id, qty) 分配记录引用批次，
"仓库余量" = 批次总量 − 已上架分配量。售出直接从批次扣减（FIFO 取最旧分配）。
"""

import math
from typing import Dict, List, Optional, Tuple

from config import balance as B
from core import catalog
from core.state import Batch, GameState, ShelfSlot


# ---------- 查询 ----------

def batch_by_id(state: GameState, batch_id: int) -> Optional[Batch]:
    for b in state.warehouse:
        if b.batch_id == batch_id:
            return b
    return None


def allocated_by_batch(state: GameState) -> Dict[int, int]:
    """batch_id → 已上架分配量。"""
    alloc: Dict[int, int] = {}
    for slot in state.slots:
        for bid, q in slot.batches:
            alloc[bid] = alloc.get(bid, 0) + q
    return alloc


def warehouse_units(state: GameState) -> int:
    """未上架、存于仓库的件数（受仓库容量约束的部分）。"""
    alloc = allocated_by_batch(state)
    return sum(max(0, b.qty - alloc.get(b.batch_id, 0)) for b in state.warehouse)


def warehouse_free(state: GameState) -> int:
    return max(0, B.WAREHOUSE_CAPACITY - warehouse_units(state))


def on_shelf_units(state: GameState) -> int:
    return sum(s.qty for s in state.slots if s.item_id)


def item_warehouse_qty(state: GameState, item_id: str) -> int:
    alloc = allocated_by_batch(state)
    return sum(max(0, b.qty - alloc.get(b.batch_id, 0))
               for b in state.warehouse if b.item_id == item_id)


def item_on_shelf_qty(state: GameState, item_id: str) -> int:
    return sum(s.qty for s in state.slots if s.item_id == item_id)


def slot_with_item(state: GameState, item_id: str) -> Optional[ShelfSlot]:
    for s in state.slots:
        if s.item_id == item_id and s.qty > 0:
            return s
    return None


def item_batches_fifo(state: GameState, item_id: str) -> List[Batch]:
    """该商品的可上架批次，先到期先出。"""
    alloc = allocated_by_batch(state)
    batches = [b for b in state.warehouse
               if b.item_id == item_id and b.qty - alloc.get(b.batch_id, 0) > 0]
    return sorted(batches, key=lambda b: (b.expire_day, b.batch_id))


def inventory_value(state: GameState) -> float:
    return sum(b.qty * b.unit_cost for b in state.warehouse)


# ---------- 变更 ----------

def add_batch(state: GameState, item_id: str, qty: int, day: int,
              unit_cost: float) -> Batch:
    item = catalog.get(item_id)
    expire = day + item.shelf_life_days
    if item.shelf_life_days >= B.INFINITE_SHELF_LIFE // 10:
        expire = B.INFINITE_SHELF_LIFE
    batch = Batch(batch_id=state.next_batch_id, item_id=item_id,
                  arrived_day=day, expire_day=expire, qty=qty,
                  unit_cost=unit_cost)
    state.next_batch_id += 1
    state.warehouse.append(batch)
    return batch


def shelve(state: GameState, slot: ShelfSlot, item_id: str,
           qty: int) -> Optional[str]:
    """把 qty 件商品上架到槽位。返回 None 表示成功，否则为错误信息。"""
    if slot.item_id is not None and slot.item_id != item_id:
        return f"槽位 {slot.index + 1} 已被其他商品占用，请先取下"
    remaining_capacity = B.SLOT_CAPACITY - slot.qty
    if qty > remaining_capacity:
        return f"槽位容量不足（剩余 {remaining_capacity} 件）"
    taken: List[Tuple[int, int]] = []
    need = qty
    for b in item_batches_fifo(state, item_id):
        alloc = allocated_by_batch(state)
        avail = b.qty - alloc.get(b.batch_id, 0)
        if avail <= 0:
            continue
        t = min(avail, need)
        taken.append((b.batch_id, t))
        need -= t
        if need == 0:
            break
    if need > 0:
        return "仓库中该商品库存不足"
    for bid, q in taken:
        slot.batches.append([bid, q])
    slot.item_id = item_id
    slot.qty += qty
    return None


def unshelve(state: GameState, slot: ShelfSlot, qty: Optional[int]) -> int:
    """取下 qty 件（None=全部）回仓库：仅清除分配记录。返回实际取下数量。"""
    if qty is None or qty >= slot.qty:
        removed = slot.qty
        slot.batches = []
        slot.qty = 0
        slot.item_id = None
        return removed
    removed = 0
    while removed < qty and slot.batches:
        bid, q = slot.batches[-1]
        t = min(q, qty - removed)
        q -= t
        removed += t
        if q <= 0:
            slot.batches.pop()
        else:
            slot.batches[-1] = [bid, q]
    slot.qty -= removed
    if slot.qty <= 0:
        slot.batches = []
        slot.qty = 0
        slot.item_id = None
    return removed


def consume(state: GameState, slot: ShelfSlot,
            qty: int) -> List[Tuple[int, float]]:
    """售出 qty 件：按槽内 FIFO 批次扣减。返回 [(数量, 批次进价), ...] 供 COGS。"""
    out: List[Tuple[int, float]] = []
    remaining = qty
    i = 0
    while remaining > 0 and i < len(slot.batches):
        bid, q = slot.batches[i]
        t = min(q, remaining)
        batch = batch_by_id(state, bid)
        if batch is None:  # 不应发生：防御性跳过
            slot.batches.pop(i)
            continue
        batch.qty -= t
        q -= t
        remaining -= t
        out.append((t, batch.unit_cost))
        if q <= 0:
            slot.batches.pop(i)
        else:
            slot.batches[i] = [bid, q]
            i += 1
    slot.qty -= qty - remaining
    if slot.qty <= 0:
        slot.batches = []
        slot.qty = 0
        slot.item_id = None
    # 清理空批次
    state.warehouse = [b for b in state.warehouse if b.qty > 0]
    return out


def age_and_discard(state: GameState, day: int) -> Tuple[float, List[Batch]]:
    """晨间过期清理：到期批次（含已上架部分）整体报废。
    返回 (报废成本, 报废批次列表)。"""
    dead = [b for b in state.warehouse if b.expire_day <= day]
    if not dead:
        return 0.0, []
    dead_ids = {b.batch_id for b in dead}
    spoil = sum(b.qty * b.unit_cost for b in dead)
    state.warehouse = [b for b in state.warehouse if b.batch_id not in dead_ids]
    for slot in state.slots:
        if any(bid in dead_ids for bid, _ in slot.batches):
            slot.batches = [[bid, q] for bid, q in slot.batches
                            if bid not in dead_ids]
            slot.qty = sum(q for _, q in slot.batches)
            if slot.qty <= 0:
                slot.item_id = None
    return spoil, dead


# ---------- 辅助 ----------

def avg_daily_sales(state: GameState, item_id: str) -> float:
    hist = state.sales_history.get(item_id, [])
    if not hist:
        return 0.0
    return sum(hist) / len(hist)


def suggested_order_units(state: GameState, item_id: str) -> int:
    """建议持有量 = 近7日均销 × 覆盖天数 − 现有量（下限 0）。"""
    target = avg_daily_sales(state, item_id) * B.SUGGEST_COVER_DAYS
    have = item_warehouse_qty(state, item_id) + item_on_shelf_qty(state, item_id)
    return max(0, math.ceil(target - have))


def stagnant_items(state: GameState) -> List[Tuple[str, float]]:
    """滞销商品列表 [(item_id, 周转倍率)]：库存天数 > 目标周转天数 × 阈值。
    仅在开Day≥3 后开始判定，避免开局误报。"""
    result = []
    if state.day < 3:
        return result
    for item in catalog.all_items():
        have = item_warehouse_qty(state, item.id) + item_on_shelf_qty(state, item.id)
        if have <= 0:
            continue
        avg = avg_daily_sales(state, item.id)
        if avg <= 0:
            ratio = float("inf")
        else:
            ratio = (have / avg) / B.TARGET_TURNOVER_DAYS
        if ratio > B.STAGNANT_RATIO:
            result.append((item.id, min(ratio, 9.9)))
    return result


def expiry_warnings(state: GameState, day: int) -> List[Tuple[str, int, int]]:
    """临期警告 [(item_id, 剩余件数, 最少剩余天数)]。"""
    warns: Dict[str, List[int]] = {}
    for b in state.warehouse:
        if b.qty <= 0:
            continue
        remaining = b.expire_day - day
        if 0 < remaining <= B.EXPIRY_WARN_DAYS:
            warns.setdefault(b.item_id, [0, remaining])
            warns[b.item_id][0] += b.qty
            warns[b.item_id][1] = min(warns[b.item_id][1], remaining)
    return [(k, v[0], v[1]) for k, v in sorted(warns.items())]
