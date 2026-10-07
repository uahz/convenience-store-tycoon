"""端到端验收：进货 → 陈列 → 开门营业 → 端到端成交 → 结算数字自洽。"""

import unittest

from core import game as game_mod


class TestEndToEndDay(unittest.TestCase):

    def test_full_day_produces_real_transactions(self):
        game = game_mod.Game(seed=7)
        game.new_game("normal")
        cash_after_order = None

        # 1) 进货（一批全品类）
        cart = {"water": 2, "cola": 2, "noodles": 2, "bread": 2, "cookie": 2,
                "gum": 1, "tissue": 1, "juice": 1, "sandwich": 1, "paper": 1}
        self.assertIsNone(game.confirm_order(cart))
        cash_after_order = game.state.cash
        self.assertLess(cash_after_order, 20000.0)

        # 2) 陈列（黄金位放高周转的饮料）
        plan = [("water", 0, 30), ("cola", 3, 30), ("bread", 1, 12),
                ("noodles", 2, 24), ("cookie", 4, 20), ("sandwich", 5, 6)]
        for item_id, slot_idx, qty in plan:
            self.assertIsNone(game.shelve(slot_idx, item_id, qty))

        # 3) 开门营业 → 必须产生真实交易
        report = game.open_store()
        self.assertGreater(report.traffic, 30)
        self.assertGreaterEqual(report.conversions, 1)
        self.assertGreater(report.revenue, 0.0)
        self.assertGreater(report.cogs, 0.0)
        self.assertGreater(sum(game.last_daylog.items_sold.values()), 0)

        # 4) 结算数字自洽
        self.assertAlmostEqual(
            report.net,
            report.revenue - report.cogs - report.spoilage
            - report.rent - report.utilities, places=6)
        self.assertAlmostEqual(report.closing_cash,
                               cash_after_order + report.revenue
                               - report.rent - report.utilities, places=6)
        self.assertEqual(len(game.state.ledger), 1)
        self.assertFalse(report.bankrupt)
        self.assertFalse(report.victory)

        # 5) 次日推进：过期报废 + 账本保留
        game.start_new_day()
        self.assertEqual(game.state.day, 2)

    def test_empty_store_means_no_sales(self):
        game = game_mod.Game(seed=7)
        game.new_game("normal")
        report = game.open_store()
        self.assertEqual(report.revenue, 0.0)
        self.assertEqual(report.conversions, 0)
        # 空店仍要付房租水电
        self.assertLess(report.net, 0.0)


if __name__ == "__main__":
    unittest.main()
