"""陈列指数与门店吸引力：客流引擎的输入。"""

from config import balance as B
from core import catalog, inventory
from core.state import GameState


def display_index(state: GameState) -> float:
    """陈列指数 0~1：满架率的加权平均（黄金位权重更高）。"""
    total_weight = 0.0
    weighted_fill = 0.0
    for slot in state.slots:
        weight = B.PREMIUM_SLOT_WEIGHT if slot.premium else 1.0
        total_weight += weight
        weighted_fill += weight * (min(slot.qty, B.SLOT_CAPACITY) / B.SLOT_CAPACITY)
    if total_weight <= 0:
        return 0.0
    return weighted_fill / total_weight


def assortment_ratio(state: GameState) -> float:
    """在售品类数 / 目录品类总数。"""
    on_shelf_categories = {catalog.get(s.item_id).category
                           for s in state.slots if s.item_id and s.qty > 0}
    if not catalog.CATEGORIES:
        return 0.0
    return len(on_shelf_categories) / len(catalog.CATEGORIES)


def promo_strength(state: GameState) -> float:
    """促销力度 0~1：在售商品的平均折扣 × 缩放系数。"""
    on_shelf_items = {s.item_id for s in state.slots if s.item_id and s.qty > 0}
    if not on_shelf_items:
        return 0.0
    total_discount = sum(state.promos[i].discount
                         for i in on_shelf_items if i in state.promos)
    return min(1.0, total_discount / len(on_shelf_items) * B.PROMO_STRENGTH_SCALE)


def attractiveness(state: GameState) -> float:
    """门店吸引力 0~1：客流引擎用它合成进店率。"""
    w = B.ATTRACT_WEIGHTS
    return (w["reputation"] * state.reputation / 100.0
            + w["display"] * display_index(state)
            + w["promo"] * promo_strength(state)
            + w["assortment"] * assortment_ratio(state))


def avg_loyalty(state: GameState) -> float:
    if not state.archetype_loyalty:
        return 0.0
    return sum(state.archetype_loyalty.values()) / len(state.archetype_loyalty)
