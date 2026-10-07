"""核心数据模型（Game / 门店状态）。只描述数据与序列化，不含规则。"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Batch:
    """库存最小单位。所有批次统一存于 GameState.warehouse 池，
    货架槽位仅持有 (batch_id, 数量) 的分配记录；售出即从批次扣减。"""
    batch_id: int
    item_id: str
    arrived_day: int
    expire_day: int          # 到期日：早于等于当日晨间 → 报废
    qty: int
    unit_cost: float

    def to_save(self) -> dict:
        return {"batch_id": self.batch_id, "item_id": self.item_id,
                "arrived_day": self.arrived_day, "expire_day": self.expire_day,
                "qty": self.qty, "unit_cost": self.unit_cost}

    @classmethod
    def from_save(cls, d: dict) -> "Batch":
        return cls(batch_id=int(d["batch_id"]), item_id=str(d["item_id"]),
                   arrived_day=int(d["arrived_day"]), expire_day=int(d["expire_day"]),
                   qty=int(d["qty"]), unit_cost=float(d["unit_cost"]))


@dataclass
class Promo:
    item_id: str
    discount: float          # 折扣深度 0~1（0.2 = 八折）
    days_left: int

    def to_save(self) -> dict:
        return {"item_id": self.item_id, "discount": self.discount,
                "days_left": self.days_left}

    @classmethod
    def from_save(cls, d: dict) -> "Promo":
        return cls(item_id=str(d["item_id"]), discount=float(d["discount"]),
                   days_left=int(d["days_left"]))


@dataclass
class ShelfSlot:
    index: int
    premium: bool                              # 黄金位
    item_id: Optional[str] = None              # 每槽一种商品
    qty: int = 0
    batches: List = field(default_factory=list)  # [(batch_id, qty)]，FIFO 顺序

    def to_save(self) -> dict:
        return {"index": self.index, "premium": self.premium,
                "item_id": self.item_id, "qty": self.qty,
                "batches": [[bid, q] for bid, q in self.batches]}

    @classmethod
    def from_save(cls, d: dict) -> "ShelfSlot":
        slot = cls(index=int(d["index"]), premium=bool(d["premium"]),
                   item_id=d["item_id"], qty=int(d["qty"]))
        slot.batches = [[int(bid), int(q)] for bid, q in d["batches"]]
        return slot


@dataclass
class GameState:
    day: int = 1
    difficulty: str = "normal"
    cash: float = 0.0
    reputation: float = 60.0                  # 0~100，显示为 ★
    warehouse: List[Batch] = field(default_factory=list)
    slots: List[ShelfSlot] = field(default_factory=list)
    prices: Dict[str, float] = field(default_factory=dict)    # item_id → 当前售价
    promos: Dict[str, Promo] = field(default_factory=dict)
    archetype_loyalty: Dict[str, float] = field(default_factory=dict)
    sales_history: Dict[str, List[int]] = field(default_factory=dict)  # item_id → 近7日销量
    purchases_7d: List[float] = field(default_factory=list)    # 近7日采购金额（报废率分母）
    ledger: List[dict] = field(default_factory=list)           # 近N日结算摘要（KPI 账本）
    next_batch_id: int = 1
    procurement_today: float = 0.0             # 当日采购支出（结算时归档后清零）

    def to_save(self) -> dict:
        return {
            "day": self.day, "difficulty": self.difficulty,
            "cash": self.cash, "reputation": self.reputation,
            "warehouse": [b.to_save() for b in self.warehouse],
            "slots": [s.to_save() for s in self.slots],
            "prices": dict(self.prices),
            "promos": [p.to_save() for p in self.promos.values()],
            "archetype_loyalty": dict(self.archetype_loyalty),
            "sales_history": {k: list(v) for k, v in self.sales_history.items()},
            "purchases_7d": list(self.purchases_7d),
            "ledger": [dict(e) for e in self.ledger],
            "next_batch_id": self.next_batch_id,
            "procurement_today": self.procurement_today,
        }

    @classmethod
    def from_save(cls, d: dict) -> "GameState":
        state = cls(
            day=int(d["day"]), difficulty=str(d["difficulty"]),
            cash=float(d["cash"]), reputation=float(d["reputation"]),
            prices={str(k): float(v) for k, v in d["prices"].items()},
            archetype_loyalty={str(k): float(v) for k, v in d["archetype_loyalty"].items()},
            sales_history={str(k): [int(x) for x in v]
                           for k, v in d["sales_history"].items()},
            purchases_7d=[float(x) for x in d["purchases_7d"]],
            ledger=[dict(e) for e in d["ledger"]],
            next_batch_id=int(d["next_batch_id"]),
            procurement_today=float(d["procurement_today"]),
        )
        state.warehouse = [Batch.from_save(b) for b in d["warehouse"]]
        state.slots = [ShelfSlot.from_save(s) for s in d["slots"]]
        state.promos = {p["item_id"]: Promo.from_save(p) for p in d["promos"]}
        return state
