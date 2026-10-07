"""顾客与购物决策管线（DESIGN.md §2.2）。

个体顾客是一次性的（生成→决策→离店），"回头客"以原型级忠诚度均值近似，
逐顾客的长期档案留给 M1。需求为商品级（来自原型 item_preferences），
缺货判定针对具体商品，跨品类替代近似冲动消费。
"""

import math
from dataclasses import dataclass, field
from typing import List, Tuple

from config import balance as B
from core import catalog, inventory, pricing
from core.rng import GameRNG
from core.state import GameState


@dataclass
class Customer:
    archetype_id: str
    name: str
    budget: float
    patience: int                 # 排队耐心（可忍受的排队人数）
    wtp_jitter: float             # 愿付价浮动（作用于参考价）
    needs: List[Tuple[str, int]] = field(default_factory=list)  # (item_id, qty)


@dataclass
class Basket:
    customer: Customer
    picks: List[Tuple[str, int]] = field(default_factory=list)  # (item_id, qty)
    oos_count: int = 0            # 缺货需求数
    sub_count: int = 0            # 其中被替代满足的数


def _sigmoid(x: float) -> float:
    if x < -30:
        return 0.0
    if x > 30:
        return 1.0
    return 1.0 / (1.0 + math.exp(-x))


def build_customer(state: GameState, rng: GameRNG, arch: dict) -> Customer:
    budget = rng.uniform(*arch["budget_range"])
    patience = rng.randint(*arch["patience_range"])
    jitter = rng.uniform(-B.AI_WTP_JITTER, B.AI_WTP_JITTER)
    needs = _sample_needs(arch, rng)
    # M0：忠诚度通过客流引擎（原型均值）生效，个体档案留给 M1
    return Customer(archetype_id=arch["id"], name=arch["name"], budget=budget,
                    patience=patience, wtp_jitter=jitter, needs=needs)


def _sample_needs(arch: dict, rng: GameRNG) -> List[Tuple[str, int]]:
    """抽取 1~3 个互不重复的商品需求。"""
    count = rng.weighted(B.NEEDS_COUNT_WEIGHTS)
    pool = list(arch["item_preferences"].items())
    needs: List[Tuple[str, int]] = []
    while len(needs) < count and pool:
        item_id = rng.weighted(pool)
        pool = [(k, w) for k, w in pool if k != item_id]
        needs.append((item_id, 1))
    return needs


def utility(state: GameState, slot, customer: Customer) -> float:
    """商品效用 = 价格分 + 位置分 + 促销分 + 库存分（权重可配）。"""
    item = catalog.get(slot.item_id)
    price = pricing.effective_price(state, item.id)
    wtp = item.ref_price * (1.0 + customer.wtp_jitter)
    price_score = _sigmoid(B.AI_PRICE_SCORE_K * (wtp / price - 1.0))
    position = (B.AI_PREMIUM_POS_SCORE if slot.premium
                else B.AI_NORMAL_POS_SCORE)
    promo = state.promos.get(item.id)
    promo_score = (promo.discount * _arch_promo_sens(customer)
                   if promo else 0.0)
    stock_score = (1.0 if slot.qty > B.AI_STOCK_LOW_THRESHOLD
                   else B.AI_STOCK_LOW_SCORE)
    w = B.AI_UTILITY_WEIGHTS
    return (w["price"] * price_score + w["position"] * position
            + w["promo"] * promo_score + w["stock"] * stock_score)


def _arch_promo_sens(customer: Customer) -> float:
    from config import customers as customers_cfg
    for arch in customers_cfg.ARCHETYPES:
        if arch["id"] == customer.archetype_id:
            return arch["promo_sensitivity"]
    return 0.0


def shop(customer: Customer, state: GameState, rng: GameRNG) -> Basket:
    """逐需求决策：点名商品缺货→替代；效用达门槛且预算允许→购买。"""
    basket = Basket(customer=customer)
    remaining_budget = customer.budget
    for item_id, qty in customer.needs:
        slot = inventory.slot_with_item(state, item_id)
        if slot is None:
            basket.oos_count += 1
            # 跨品类替代：随机买一件其他在售商品（冲动消费近似）
            if rng.random() < B.AI_SUBSTITUTE_PROB:
                others = [s for s in state.slots if s.item_id and s.qty > 0]
                if others:
                    alt = rng.choice(others)
                    price = pricing.effective_price(state, alt.item_id)
                    if price <= remaining_budget:
                        basket.picks.append((alt.item_id, 1))
                        basket.sub_count += 1
                        remaining_budget -= price
            continue
        if utility(state, slot, customer) < B.AI_BUY_THRESHOLD:
            continue
        item = catalog.get(item_id)
        price = pricing.effective_price(state, item_id)
        buy_qty = qty
        if (item.ref_price <= B.SECOND_UNIT_MAX_REF
                and rng.random() < B.SECOND_UNIT_PROB
                and slot.qty >= buy_qty + 1
                and price * (buy_qty + 1) <= remaining_budget):
            buy_qty += 1
        buy_qty = min(buy_qty, slot.qty)
        if buy_qty <= 0 or price * buy_qty > remaining_budget:
            continue
        basket.picks.append((item_id, buy_qty))
        remaining_budget -= price * buy_qty
    return basket
