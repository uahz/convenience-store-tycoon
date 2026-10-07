"""顾客 AI 测试：效用购买门槛、缺货替代、价格敏感性、黄金位加成。"""

import unittest

from core.customer import Customer, build_customer, shop
from core.game import Game
from core.rng import GameRNG
from core import traffic


def make_game() -> Game:
    game = Game(seed=42)
    game.new_game("normal")
    return game


def stock(game, item_id: str, slot_idx: int, qty: int) -> None:
    game.confirm_order({item_id: 2})   # 2 箱，确保 ≥ 单槽容量
    game.shelve(slot_idx, item_id, qty)


def office_arch() -> dict:
    return {"id": "office", "name": "上班族", "share": 1.0,
            "hour_weights": {}, "item_preferences": {"water": 1.0},
            "budget_range": (18.0, 26.0), "patience_range": (4, 6),
            "promo_sensitivity": 0.25, "initial_loyalty": 0.35}


class TestCustomerAI(unittest.TestCase):

    def test_buys_at_reference_price(self):
        game = make_game()
        stock(game, "water", 0, 30)
        st = game.state
        rng = GameRNG(7)
        buys = 0
        for _ in range(12):
            cust = build_customer(st, rng, office_arch())
            basket = shop(cust, st, rng)
            if basket.picks:
                buys += 1
        self.assertGreaterEqual(buys, 9)   # 参考价下几乎全部成交（含第二件）

    def test_price_gouging_kills_demand(self):
        game = make_game()
        stock(game, "water", 0, 30)
        st = game.state
        game.set_price("water", 4.0)   # 2 倍参考价
        rng = GameRNG(7)
        buys = 0
        for _ in range(12):
            cust = build_customer(st, rng, office_arch())
            basket = shop(cust, st, rng)
            if basket.picks:
                buys += 1
        self.assertLess(buys, 3)       # 宰客几乎无人问津

    def test_oos_and_substitution(self):
        game = make_game()
        stock(game, "cookie", 0, 10)   # 货架只有饼干，顾客想要可乐
        st = game.state
        rng = GameRNG(3)
        cust = Customer(archetype_id="office", name="上班族", budget=100.0,
                        patience=5, wtp_jitter=0.0,
                        needs=[("cola", 1)])
        basket = shop(cust, st, rng)
        self.assertEqual(basket.oos_count, 1)
        # 35% 概率被其他在售商品替代；不替代则无购买
        self.assertIn(len(basket.picks), (0, 1))
        if basket.picks:
            self.assertEqual(basket.sub_count, 1)
            self.assertEqual(basket.picks[0][0], "cookie")

    def test_premium_slot_boosts_utility(self):
        game = make_game()
        stock(game, "cola", 1, 30)      # 先放普通位槽 1
        st = game.state
        game.set_price("cola", 4.2)     # 1.2 倍参考价：普通位不买，黄金位买
        cust = Customer(archetype_id="office", name="上班族", budget=50.0,
                        patience=5, wtp_jitter=0.0, needs=[("cola", 1)])
        rng = GameRNG(11)
        normal_basket = shop(cust, st, rng)
        self.assertEqual(normal_basket.picks, [])
        game.unshelve(1)                # 移到黄金位槽 0
        game.shelve(0, "cola", 30)
        premium_basket = shop(cust, st, rng)
        self.assertEqual([p[0] for p in premium_basket.picks], ["cola"])

    def test_archetype_pool_covers_config(self):
        """traffic.pick_archetype 返回的配置能被 build_customer 消费。"""
        game = make_game()
        rng = GameRNG(5)
        for hour in range(8, 24):
            arch = traffic.pick_archetype(hour, rng)
            cust = build_customer(game.state, rng, arch)
            self.assertTrue(1 <= len(cust.needs) <= 3)
            for item_id, qty in cust.needs:
                self.assertIn(item_id, arch["item_preferences"])
                self.assertEqual(qty, 1)


if __name__ == "__main__":
    unittest.main()
