"""商品目录：config 中的纯数据 → 只读 ItemDef。"""

from dataclasses import dataclass
from typing import Tuple

from config import items as items_cfg


@dataclass(frozen=True)
class ItemDef:
    id: str
    name: str
    category: str
    unit_cost: float
    ref_price: float
    shelf_life_days: int
    storage: str
    case_size: int
    popularity: float
    elasticity: float
    suppliers: Tuple[str, ...]


CATALOG = {d["id"]: ItemDef(**d) for d in items_cfg.ITEMS}
CATEGORIES = sorted({item.category for item in CATALOG.values()})


def get(item_id: str) -> ItemDef:
    return CATALOG[item_id]


def all_items():
    """目录稳定顺序（按 config 声明顺序）。"""
    return list(CATALOG.values())
