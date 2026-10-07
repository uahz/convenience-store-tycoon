"""主菜单与难度选择。"""

from ui import console, theme
import save.savegame as savegame


BANNER = r"""
╔══════════════════════════════════════════════════════╗
║            便 利 店 大 亨   Convenience Tycoon        ║
║                  —— 街角生意，日进斗金 ——             ║
╚══════════════════════════════════════════════════════╝"""

ASCII_BANNER = r"""
+======================================================+
|            便 利 店 大 亨   Convenience Tycoon        |
|                  —— 街角生意，日进斗金 ——             |
+======================================================+"""


def run(game) -> str:
    """返回 "new" | "continue" | "quit"。"""
    while True:
        console.clear()
        print(theme.ASCII and ASCII_BANNER or BANNER)
        print(theme.dim(f"  Demo v{__import__('config').APP_VERSION}"
                        "  ·  单人终端经营模拟\n"))
        options = [("1", "开始新游戏（选择难度）")]
        if savegame.has_save():
            options.append(("2", "继续游戏（读取自动存档）"))
        options += [("3", "玩法说明"), ("0", "退出")]
        key = console.menu("", options)
        if key == "1":
            diff = _choose_difficulty()
            if diff:
                game.new_game(diff)
                return "new"
        elif key == "2":
            try:
                meta = savegame.load(game, "autosave")
            except savegame.SaveError as exc:
                print(theme.bad(f"读取失败：{exc}"))
                console.pause()
                continue
            print(theme.good(
                f"已读取存档：第 {meta['day']} 天 · "
                f"现金 {console.money(meta['cash'])} · "
                f"{console.stars(meta['reputation'])}"))
            console.pause()
            return "continue"
        elif key == "3":
            from ui.screens import help_screen
            help_screen.run()
        elif key == "0":
            return "quit"


def _choose_difficulty():
    from config import balance as B
    console.clear()
    print(theme.strong("选择难度\n"))
    options = []
    for i, preset in enumerate(B.DIFFICULTIES.values(), start=1):
        options.append((str(i), (
            f"{preset.label} · 初始资金 {console.money(preset.cash)} · "
            f"客流×{preset.traffic_mult:.2f} · 房租×{preset.rent_mult:.2f} · "
            f"胜利线 {console.money(preset.victory_net_worth)}")))
    options.append(("0", "返回"))
    key = console.menu("", options)
    if key == "0":
        return None
    keys = list(B.DIFFICULTIES.keys())
    return keys[int(key) - 1]
