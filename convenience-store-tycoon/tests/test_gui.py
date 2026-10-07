"""GUI 自检测试：无头驱动完整一日流程（需要桌面环境；CI 无显示器时跳过）。"""

import unittest

try:
    import tkinter  # noqa: F401
    HAS_TK = True
except Exception:
    HAS_TK = False


@unittest.skipUnless(HAS_TK, "tkinter 不可用")
class TestGuiSelftest(unittest.TestCase):

    def test_full_day_flow(self):
        from ui_gui.app import run_selftest
        self.assertTrue(run_selftest(seed=7))


if __name__ == "__main__":
    unittest.main()
