"""财务口径：净资产、破产判定。（贷款/利息在 M2 扩展于此模块）"""

from config import balance as B
from core import inventory
from core.state import GameState


def net_worth(state: GameState) -> float:
    """净资产 = 现金 + 库存价值（按进价计）。"""
    return state.cash + inventory.inventory_value(state)


def is_bankrupt(state: GameState) -> bool:
    return state.cash < B.BANKRUPTCY_CASH
