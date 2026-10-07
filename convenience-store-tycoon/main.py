"""《便利店大亨》入口。

用法：
    python main.py                 # 窗口版（默认）
    python main.py --cli           # 终端纯文本版（保留）
    python main.py --seed N        # 固定随机种子（复现/调试）
    python main.py --selftest      # 运行 GUI 自检后退出
    python main.py --ascii         # 仅 --cli 模式：纯 ASCII 渲染
"""

import argparse
import os
import sys
import traceback

from config import APP_VERSION


def setup_console() -> None:
    if os.name == "nt":
        os.system("")                       # 启用 Windows 10+ 的 ANSI 转义序列
        os.system("chcp 65001 >nul 2>&1")   # 切到 UTF-8 代码页（尽力而为）
        for stream in (sys.stdout, sys.stderr, sys.stdin):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (AttributeError, OSError):
                pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="便利店大亨（实时窗口版）")
    parser.add_argument("--cli", action="store_true",
                        help="使用终端纯文本模式（默认为窗口版）")
    parser.add_argument("--ascii", action="store_true",
                        help="--cli 模式下使用纯 ASCII 字符渲染")
    parser.add_argument("--seed", type=int, default=None,
                        help="固定随机种子（复现/调试）")
    parser.add_argument("--selftest", action="store_true",
                        help="运行 GUI 自检后退出（打包冒烟用）")
    parser.add_argument("--version", action="version",
                        version=f"convenience-store-tycoon {APP_VERSION}")
    return parser.parse_args()


def run_cli(args) -> int:
    from core.game import Game
    from ui import theme
    from ui.screens import main_menu, night, open_view, prep
    from ui.screens import settlement as settlement_screen

    theme.init(args.ascii)
    game = Game(seed=args.seed)
    phase = "menu"
    try:
        while True:
            if phase == "menu":
                action = main_menu.run(game)
                if action == "quit":
                    break
                phase = "prep" if action == "new" else "night"
            elif phase == "prep":
                action = prep.run(game)
                if action != "open":
                    phase = "menu"
                    continue
                report = game.open_store()
                open_view.run(game, report)
                settlement_screen.run(game, report)
                try:
                    savegame_save(game)
                except OSError as exc:
                    print(f"自动存档失败：{exc}")
                if report.victory or report.bankrupt:
                    from ui.screens import ending
                    (ending.victory if report.victory
                     else ending.bankrupt)(game, report)
                    phase = "menu"
                else:
                    phase = "night"
            elif phase == "night":
                action = night.run(game)
                if action == "next":
                    game.start_new_day()
                    phase = "prep"
                else:
                    phase = "menu"
    except (KeyboardInterrupt, EOFError):
        print("\n（中断）再见，老板！")
    return 0


def savegame_save(game):
    import save.savegame as savegame
    savegame.save(game, "autosave")


def main() -> int:
    args = parse_args()
    setup_console()
    if args.selftest:
        from ui_gui.app import run_selftest
        return 0 if run_selftest(seed=args.seed) else 1
    if args.cli:
        return run_cli(args)
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)   # 高分屏清晰渲染
        except (OSError, AttributeError):
            pass
    try:
        from ui_gui.app import run_gui
        return run_gui(seed=args.seed)
    except Exception:
        # 窗口程序无控制台，崩溃信息落盘便于排查
        try:
            from save.savegame import _app_dir
            log = _app_dir() / "crash.log"
            log.write_text(traceback.format_exc(), encoding="utf-8")
        except OSError:
            pass
        raise


if __name__ == "__main__":
    sys.exit(main())
