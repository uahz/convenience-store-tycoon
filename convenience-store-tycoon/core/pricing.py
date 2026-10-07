"""定价规则：生效售价（含促销）、毛利计算、价格校验。"""

from typing import Optional

from core import catalog
from core.state import GameState, Promo


def effective_price(state: GameState, item_id: str) -> float:
    """顾客实际成交价 = 当前售价 × (1 − 促销折扣)。"""
    price = state.prices.get(item_id, catalog.get(item_id).ref_price)
    promo = state.promos.get(item_id)
    if promo and promo.discount > 0:
        price *= (1.0 - promo.discount)
    return price


def margin_rate(state: GameState, item_id: str) -> float:
    """当前售价（不含促销）对进价的毛利率。"""
    price = state.prices.get(item_id, catalog.get(item_id).ref_price)
    cost = catalog.get(item_id).unit_cost
    if price <= 0:
        return 0.0
    return (price - cost) / price


def set_price(state: GameState, item_id: str, price: float) -> Optional[str]:
    """校验并设置售价。返回 None 成功，否则错误信息。"""
    if item_id not in catalog.CATALOG:
        return "未知商品"
    if price <= 0:
        return "售价必须大于 0"
    state.prices[item_id] = round(float(price), 2)
    return None


def set_promo(state: GameState, item_id: str, pct: float,
              days: int) -> Optional[str]:
    """设置促销折扣（pct 为百分数，0 = 取消促销）。"""
    from config import balance as B
    if item_id not in catalog.CATALOG:
        return "未知商品"
    if pct == 0:
        state.promos.pop(item_id, None)
        return None
    if not (0 < pct <= B.PROMO_MAX_PCT):
        return f"折扣需在 0~{B.PROMO_MAX_PCT}% 之间"
    state.promos[item_id] = Promo(item_id=item_id, discount=pct / 100.0,
                                  days_left=days)
    return None


def tick_promos(state: GameState) -> None:
    """每日晨间：促销剩余天数 −1，到期移除。"""
    expired = [k for k, p in state.promos.items() if p.days_left - 1 <= 0]
    for k in expired:
        del state.promos[k]
    for p in state.promos.values():
        p.days_left -= 1
