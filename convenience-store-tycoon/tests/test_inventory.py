"""库存规则测试：FIFO 售出、上架取下、过期报废。"""

import unittest

from config import balance as B
from core import game as game_mod
from core import inventory


def make_game() -> game_mod.Game:
    game = game_mod.Game(seed=1)
    game.new_game("normal")
    return game


class TestInventory(unittest.TestCase):

    def test_shelve_and_consume_fifo(self):
        game = make_game()
        st = game.state
        game.confirm_order({"water": 1})          # 批次1：24 件
        game.confirm_order({"water": 1})          # 批次2：24 件
        b1, b2 = [b for b in st.warehouse if b.item_id == "water"]
        b1.unit_cost, b2.unit_cost = 1.0, 1.2     # b1 批次号更小 → FIFO 先出

        err = game.shelve(0, "water", 30)
        self.assertIsNone(err)
        self.assertEqual(inventory.item_on_shelf_qty(st, "water"), 30)
        self.assertEqual(inventory.warehouse_units(st), 18)

        slot = st.slots[0]
        consumed = inventory.consume(st, slot, 30)
        self.assertEqual(consumed, [(24, 1.0), (6, 1.2)])  # 先卖旧批次
        self.assertEqual(slot.qty, 0)
        self.assertIsNone(slot.item_id)
        self.assertEqual([b.qty for b in st.warehouse if b.item_id == "water"],
                         [18])                    # 批次1 已耗尽被清理

    def test_unshelve_returns_to_warehouse(self):
        game = make_game()
        st = game.state
        game.confirm_order({"noodles": 3})        # 36 件
        self.assertIsNone(game.shelve(1, "noodles", 20))
        self.assertIsNone(game.unshelve(1))       # 全部取下
        self.assertIsNone(st.slots[1].item_id)
        self.assertEqual(st.slots[1].qty, 0)
        self.assertEqual(inventory.item_warehouse_qty(st, "noodles"), 36)

    def test_expiry_discard_including_shelf(self):
        game = make_game()
        st = game.state
        game.confirm_order({"paper": 2})          # 晚报：保质期 1 天
        game.shelve(2, "paper", 10)
        self.assertEqual(st.day, 1)
        # 到了第 2 天早晨：expire_day = 1+1 = 2 <= 2 → 报废
        spoil, dead = inventory.age_and_discard(st, 2)
        self.assertGreater(spoil, 0)
        self.assertEqual(len(dead), 1)
        self.assertEqual(inventory.item_warehouse_qty(st, "paper"), 0)
        self.assertIsNone(st.slots[2].item_id)
        self.assertEqual(inventory.item_on_shelf_qty(st, "paper"), 0)

    def test_warehouse_capacity_enforced(self):
        game = make_game()
        st = game.state
        err = game.confirm_order({"water": 20})   # 480 件 > 300 容量
        self.assertIsNotNone(err)
        self.assertEqual(st.cash, B.INITIAL_CASH)  # 未扣款

    def test_suggested_order(self):
        game = make_game()
        st = game.state
        st.sales_history["water"] = [24, 24, 24, 24, 24, 24, 24]
        # 目标持有 = 24×2 = 48，现有 0 → 建议 2 箱（48 件）
        self.assertEqual(inventory.suggested_order_units(st, "water"), 48)


if __name__ == "__main__":
    unittest.main()
