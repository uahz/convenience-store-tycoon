"""Game 门面：UI 层唯一接触的核心对象。组装规则模块，暴露玩家操作。"""

from typing import Dict, List, Optional, Tuple

from config import balance as B
from config import customers as customers_cfg
from core import catalog, economy, inventory, pricing, settlement, simulation
from core.rng import GameRNG
from core.state import GameState, ShelfSlot


class Game:

    def __init__(self, seed: Optional[int] = None):
        self.seed = seed
        self.rng = GameRNG(seed)
        self.state: Optional[GameState] = None
        self.last_daylog = None
        self.last_report: Optional[settlement.DayReport] = None
        self.pending_spoilage_cost = 0.0
        self.pending_spoilage_items: List[Tuple[str, int]] = []
        self._inv_start = 0.0

    # ---------- 生命周期 ----------

    def new_game(self, difficulty_key: str) -> None:
        preset = B.DIFFICULTIES[difficulty_key]
        state = GameState(difficulty=difficulty_key, cash=preset.cash)
        state.slots = [ShelfSlot(index=i, premium=(i in B.PREMIUM_SLOT_INDEXES))
                       for i in range(B.SHELF_SLOTS)]
        state.prices = {item.id: item.ref_price for item in catalog.all_items()}
        state.sales_history = {item.id: [] for item in catalog.all_items()}
        state.archetype_loyalty = {arch["id"]: arch["initial_loyalty"]
                                   for arch in customers_cfg.ARCHETYPES}
        self.state = state
        self.rng = GameRNG(self.seed)
        self.last_daylog = None
        self.last_report = None
        self.pending_spoilage_cost = 0.0
        self.pending_spoilage_items = []

    def start_new_day(self) -> None:
        """夜间"结束今天"后调用：日推进 + 过期报废 + 促销计时。"""
        state = self._require_state()
        state.day += 1
        spoil, dead = inventory.age_and_discard(state, state.day)
        pricing.tick_promos(state)
        self.pending_spoilage_cost = spoil
        self.pending_spoilage_items = [(b.item_id, b.qty) for b in dead]

    # ---------- 晨间信息 ----------

    def morning_info(self) -> dict:
        state = self._require_state()
        return {
            "day": state.day,
            "weekday": B.DAY_NAMES[(state.day - 1) % 7],
            "spoilage_items": list(self.pending_spoilage_items),
            "spoilage_cost": self.pending_spoilage_cost,
            "expiry_warns": inventory.expiry_warnings(state, state.day),
            "stagnants": inventory.stagnant_items(state),
            "warehouse_used": inventory.warehouse_units(state),
            "warehouse_free": inventory.warehouse_free(state),
            "on_shelf": inventory.on_shelf_units(state),
            "slots_filled": sum(1 for s in state.slots if s.item_id),
            "active_promos": len(state.promos),
        }

    # ---------- 玩家操作 ----------

    def confirm_order(self, cart: Dict[str, int]) -> Optional[str]:
        """确认进货单：cart = {item_id: 箱数}。返回 None 成功，否则错误信息。"""
        state = self._require_state()
        if not cart:
            return "订单为空"
        total_cost = 0.0
        total_units = 0
        for item_id, cases in cart.items():
            if cases <= 0:
                return "箱数必须为正整数"
            item = catalog.get(item_id)
            total_cost += item.unit_cost * item.case_size * cases
            total_units += item.case_size * cases
        if total_cost > state.cash:
            return f"资金不足：需 ¥{total_cost:,.0f}，现有 ¥{state.cash:,.0f}"
        if total_units > inventory.warehouse_free(state):
            return (f"仓库容量不足：本次 {total_units} 件 > "
                    f"剩余 {inventory.warehouse_free(state)} 件")
        state.cash -= total_cost
        state.procurement_today += total_cost
        for item_id, cases in cart.items():
            item = catalog.get(item_id)
            inventory.add_batch(state, item_id, item.case_size * cases,
                                state.day, item.unit_cost)
        return None

    def set_price(self, item_id: str, price: float) -> Optional[str]:
        return pricing.set_price(self._require_state(), item_id, price)

    def set_promo(self, item_id: str, pct: float) -> Optional[str]:
        return pricing.set_promo(self._require_state(), item_id, pct,
                                 B.PROMO_DEFAULT_DAYS)

    def shelve(self, slot_idx: int, item_id: str,
               qty: Optional[int] = None) -> Optional[str]:
        state = self._require_state()
        if not (0 <= slot_idx < len(state.slots)):
            return "槽位不存在"
        slot = state.slots[slot_idx]
        if inventory.slot_with_item(state, item_id) not in (None, slot):
            return "该商品已在其他槽位上架"
        if qty is None:
            # 尽可能多上：受槽位容量与仓库余量双重限制
            qty = min(B.SLOT_CAPACITY - slot.qty,
                      inventory.item_warehouse_qty(state, item_id))
            if qty <= 0:
                return "仓库中没有可上架的该商品"
        return inventory.shelve(state, slot, item_id, qty)

    def unshelve(self, slot_idx: int, qty: Optional[int] = None) -> Optional[str]:
        state = self._require_state()
        if not (0 <= slot_idx < len(state.slots)):
            return "槽位不存在"
        slot = state.slots[slot_idx]
        if slot.item_id is None:
            return "该槽位为空"
        inventory.unshelve(state, slot, qty)
        return None

    # ---------- 营业 ----------

    def begin_day(self):
        """开门：返回逐小时生成器（实时 UI 每小时 next 一次）。
        与 finish_day 配对使用；open_store 是两者的同步快捷方式。"""
        state = self._require_state()
        self._inv_start = inventory.inventory_value(state)
        return simulation.iter_day_hours(state, self.rng)

    def finish_day(self, daylog) -> settlement.DayReport:
        """打烊结算（实时 UI 在小时生成器耗尽后调用）。"""
        state = self._require_state()
        report = settlement.settle(state, daylog, self._inv_start,
                                   self.pending_spoilage_cost,
                                   self.pending_spoilage_items)
        self.last_daylog = daylog
        self.last_report = report
        self.pending_spoilage_cost = 0.0
        self.pending_spoilage_items = []
        return report

    def open_store(self) -> settlement.DayReport:
        """开门营业：跑完一日仿真并结算（同步快捷方式，终端模式用）。"""
        state = self._require_state()
        daylog = simulation.run_day(state, self.rng)
        return self.finish_day(daylog)

    # ---------- 工具 ----------

    def _require_state(self) -> GameState:
        if self.state is None:
            raise RuntimeError("尚未开始游戏")
        return self.state
