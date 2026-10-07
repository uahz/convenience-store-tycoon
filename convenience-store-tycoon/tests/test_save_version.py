"""存档测试：往返一致、RNG 序列延续、前向版本拒绝、损坏检测。"""

import json
import tempfile
import unittest
from pathlib import Path

import save.savegame as savegame
from core import game as game_mod


class TestSaveVersion(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self._orig_dir = savegame._SAVES_DIR
        savegame._SAVES_DIR = Path(self.tmp.name)

    def tearDown(self):
        savegame._SAVES_DIR = self._orig_dir
        self.tmp.cleanup()

    def test_round_trip_and_rng_continuity(self):
        game = game_mod.Game(seed=123)
        game.new_game("normal")
        game.confirm_order({"water": 2})
        game.shelve(0, "water", 20)
        game.set_price("cola", 3.8)
        game.state.reputation = 66.5

        consumed = [game.rng.random() for _ in range(5)]  # 消耗随机序列
        savegame.save(game, "autosave")                   # 保存当前 RNG 状态
        continuation = [game.rng.random() for _ in range(5)]  # 原局的后续序列

        game2 = game_mod.Game()
        meta = savegame.load(game2, "autosave")
        s1, s2 = game.state, game2.state
        self.assertEqual(s2.day, s1.day)
        self.assertAlmostEqual(s2.cash, s1.cash)
        self.assertAlmostEqual(s2.reputation, 66.5)
        self.assertEqual(len(s2.warehouse), len(s1.warehouse))
        self.assertEqual(s2.slots[0].qty, 20)
        self.assertAlmostEqual(s2.prices["cola"], 3.8)
        self.assertEqual(meta["day"], s1.day)
        # RNG 序列无缝延续：读档后的随机序列 == 原局保存点之后的序列
        after = [game2.rng.random() for _ in range(5)]
        self.assertEqual(after, continuation)

    def test_future_version_rejected(self):
        game = game_mod.Game(seed=1)
        game.new_game("normal")
        savegame.save(game, "autosave")
        path = savegame.slot_path("autosave")
        data = json.loads(path.read_text(encoding="utf-8"))
        data["format_version"] = 99
        path.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(savegame.SaveError):
            savegame.load(game_mod.Game(), "autosave")

    def test_corrupt_file_rejected(self):
        Path(savegame.slot_path("autosave")).write_text(
            "{not json", encoding="utf-8")
        with self.assertRaises(savegame.SaveError):
            savegame.load(game_mod.Game(), "autosave")

    def test_missing_file_rejected(self):
        with self.assertRaises(savegame.SaveError):
            savegame.load(game_mod.Game(), "autosave")


if __name__ == "__main__":
    unittest.main()
