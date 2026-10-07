# 临时平衡性推演脚本（非交付物）：模拟"合格玩家"跑 N 天，观察经济曲线。
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core import catalog, inventory
from core.game import Game

DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 14

# 首日铺底（按需求占比的 top-6 选品）
SEED_ORDER = {"cola": 3, "water": 2, "noodles": 3, "bread": 4,
              "juice": 4, "sandwich": 3}
SHELVES = [("cola", 0), ("water", 3), ("noodles", 2),
           ("bread", 1), ("juice", 4), ("sandwich", 5)]
STOCKED = {item_id for item_id, _ in SHELVES}

game = Game(seed=11)
game.new_game("normal")

for day in range(1, DAYS + 1):
    if day > 1:
        game.start_new_day()
    st = game.state
    if day == 1:
        order = dict(SEED_ORDER)
    else:
        order = {}
        for item_id in STOCKED:
            sug = inventory.suggested_order_units(st, item_id)
            cases = math.ceil(sug / catalog.get(item_id).case_size)
            if cases > 0:
                order[item_id] = cases
    while order:
        err = game.confirm_order(order)
        if err is None:
            break
        order = {k: v - 1 for k, v in order.items() if v > 1}  # 缩单重试
    for item_id, slot in SHELVES:
        cur = st.slots[slot].qty if st.slots[slot].item_id == item_id else 0
        if cur < 12:
            err = game.shelve(slot, item_id, None)
            if err:
                print("shelve err:", err)
    rep = game.open_store()
    print(f"D{rep.day:02d} {rep.weekday} "
          f"营收{rep.revenue:7.0f} 净利{rep.net:8.1f} "
          f"客流{rep.traffic:4d} 转化{rep.conversion_rate * 100:5.1f}% "
          f"缺货{rep.oos_rate * 100:5.1f}% 满意{rep.sat_avg:5.1f} "
          f"声望{rep.rep_after:5.1f} 现金{rep.closing_cash:9.0f}")

led = game.state.ledger
print("---- 合计 ----")
print(f"累计营收 {sum(e['revenue'] for e in led):,.0f}  "
      f"累计净利 {sum(e['net'] for e in led):,.0f}  "
      f"净资产 {game.state.cash + inventory.inventory_value(game.state):,.0f}")
