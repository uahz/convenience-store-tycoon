# 临时工具（非交付物）：运行真实 GUI 并抓取窗口截图（主菜单 / 营业中 / 结算单）。
import ctypes
import time
from ctypes import wintypes

from PIL import ImageGrab

from ui_gui import dialogs
from core.game import Game
from ui_gui.app import TycoonApp

dialogs.AUTO = False
OUT = r"F:\Administrator\Documents\代码\convenience-store-tycoon\design\ui-shots"

user32 = ctypes.windll.user32


def shot(app, path):
    app.update()
    app.update()
    hwnd = user32.GetParent(app.winfo_id())
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    img = ImageGrab.grab(bbox=(rect.left, rect.top, rect.right, rect.bottom))
    img.save(path)
    print("saved", path)


game = Game(seed=11)
app = TycoonApp(game)
app.geometry("1200x740+60+40")
app.update()
shot(app, OUT + r"\gui_real_1_menu.png")

app.start_new_game("normal")
app.update()
buy = app.sidebar.buy
buy.add_to_cart("cola", 3)
buy.add_to_cart("water", 2)
buy.add_to_cart("noodles", 2)
buy.add_to_cart("bread", 2)
buy.add_to_cart("juice", 3)
buy.add_to_cart("sandwich", 3)
buy.confirm_order()
for item, slot in (("cola", 0), ("water", 3), ("noodles", 2),
                   ("bread", 1), ("juice", 4), ("sandwich", 5)):
    app.game.shelve(slot, item, None)
app.sidebar.nb.select(0)
app.sidebar.refresh_all()
app.update()
app.open_store()
for _ in range(6):
    app._hour_tick()
    app.update()
    time.sleep(0.05)
for _ in range(4):
    app.update()
    time.sleep(0.12)
shot(app, OUT + r"\gui_real_2_open.png")

while app.phase == "open":
    app._hour_tick()
    app.update()
time.sleep(0.3)
app.update()
shot(app, OUT + r"\gui_real_3_settlement.png")
app._after_settlement()
app.update()

app.destroy()
print("done")
