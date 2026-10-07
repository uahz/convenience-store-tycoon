"""结算测试：损益逐项、声望/忠诚更新、破产标记、账本。"""

import unittest

from core import game as game_mod
from core.settlement import settle
from core.simulation import DayLog


def make_game() -> game_mod.Game:
    game = game_mod.Game(seed=1)
    game.new_game("normal")
    game.state.cash = 5000.0
    return game


def make_daylog() -> DayLog:
    log = DayLog()
    log.revenue = 1000.0
    log.cogs = 700.0
    log.arrivals = 100
    log.conversions = 60
    log.oos_needs = 5
    log.total_needs = 100
    log.abandons = 5
    log.sat_samples = [70.0] * 10
    log.items_sold = {"water": 10}
    return log


class TestSettlement(unittest.TestCase):

    def test_profit_and_loss_math(self):
        game = make_game()
        st = game.state
        from core.inventory import add_batch
        add_batch(st, "water", 100, st.day, 1.0)      # 期末库存价值 100
        report = settle(st, make_daylog(), inv_value_start=100.0,
                        spoilage_cost=20.0, spoilage_items=[("bread", 4)])
        # 固定费用 = 250 房租 + (30 + 1000×1.5%) 水电 = 295
        self.assertAlmostEqual(report.rent, 250.0)
        self.assertAlmostEqual(report.utilities, 45.0)
        self.assertAlmostEqual(report.net, 1000 - 700 - 20 - 295)
        # 现金只动"营收 − 固定费用"（采购支出已在下单时扣）
        self.assertAlmostEqual(report.closing_cash, 5000 + 1000 - 295)
        self.assertAlmostEqual(report.net_worth, report.closing_cash + 100)
        # 声望：满意度 70 > 基线 65 → 上涨 0.18×5 = 0.9
        self.assertAlmostEqual(report.rep_after, 60.0 + 0.9, places=6)
        # KPI
        self.assertAlmostEqual(report.conversion_rate, 0.6)
        self.assertAlmostEqual(report.aov, 1000 / 60, places=6)
        self.assertAlmostEqual(report.oos_rate, 0.05)
        self.assertAlmostEqual(report.turnover, 700 / 100.0)
        self.assertFalse(report.bankrupt)
        self.assertFalse(report.victory)
        # 账本
        self.assertEqual(len(st.ledger), 1)
        self.assertEqual(st.ledger[0]["day"], 1)
        self.assertAlmostEqual(st.ledger[0]["net"], report.net, places=6)
        # 采购窗口归档并清零
        self.assertEqual(st.purchases_7d, [0.0])
        self.assertEqual(st.procurement_today, 0.0)
        # 销量历史已记录
        self.assertEqual(st.sales_history["water"], [10])

    def test_bankruptcy_flag(self):
        game = make_game()
        game.state.cash = -3000.0
        report = settle(game.state, make_daylog(), 0.0, 0.0, [])
        self.assertTrue(report.bankrupt)
        self.assertFalse(report.victory)

    def test_queue_penalty_hits_reputation(self):
        game = make_game()
        log = make_daylog()
        log.abandons = 30                      # 放弃率 30% > 8%
        report = settle(game.state, log, 0.0, 0.0, [])
        # 满意度追加扣减 + 声望应明显低于无惩罚情形
        self.assertLess(report.sat_avg, 70.0)
        self.assertLess(report.rep_after, 60.9)

    def test_no_customers_no_rep_change(self):
        game = make_game()
        log = DayLog()                          # 全空日志：没人进店
        report = settle(game.state, log, 0.0, 0.0, [])
        self.assertAlmostEqual(report.rep_after, 60.0)
        self.assertAlmostEqual(report.net, -(250 + 30))


if __name__ == "__main__":
    unittest.main()
