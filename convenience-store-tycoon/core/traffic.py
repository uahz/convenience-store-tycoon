"""客流引擎：合成每日进店人数，按时段分配并挑选顾客原型。"""

from config import balance as B
from config import customers as customers_cfg
from core import display
from core.rng import GameRNG
from core.state import GameState


def daily_arrival_mean(state: GameState) -> float:
    """当日预计进店总人数的期望值。"""
    preset = B.DIFFICULTIES[state.difficulty]
    weekday = (state.day - 1) % 7
    base = (B.TRAFFIC_BASE_WEEKEND if weekday in B.WEEKEND_DAYS
            else B.TRAFFIC_BASE_WEEKDAY)
    enter_rate = (B.BASE_ENTER_RATE
                  * (0.5 + display.attractiveness(state))
                  * (B.LOYALTY_ARRIVAL[0] + B.LOYALTY_ARRIVAL[1]
                     * display.avg_loyalty(state)))
    return base * enter_rate * preset.traffic_mult


def _hour_weight(hour: int) -> float:
    return B.PEAK_WEIGHTS.get(hour, 1.0)


def hours_weights_sum() -> float:
    total = 0.0
    for hour in range(B.DAY_START_HOUR, B.DAY_END_HOUR):
        total += _hour_weight(hour)
    return total


def arrivals_for_hour(state: GameState, hour: int, rng: GameRNG) -> int:
    lam = daily_arrival_mean(state) * _hour_weight(hour) / hours_weights_sum()
    return rng.poisson(lam)


def pick_archetype(hour: int, rng: GameRNG) -> dict:
    """按 原型基础占比 × 时段倾向 抽取一位顾客的原型配置。"""
    pairs = [(arch, arch["share"] * arch["hour_weights"].get(hour, 1.0))
             for arch in customers_cfg.ARCHETYPES]
    return rng.weighted(pairs)
