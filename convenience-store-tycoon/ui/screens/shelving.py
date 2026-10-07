"""货架陈列界面。"""

from config import balance as B
from core import catalog, inventory
from ui import console, theme


def run(game) -> None:
    state = game.state
    while True:
        console.clear()
        print(console.hr())
        print(theme.strong(" 货架陈列   （★ 黄金位：顾客更容易注意到）"))
        print(console.hr())
        slot_rows = []
        for slot in state.slots:
            name = catalog.get(slot.item_id).name if slot.item_id else "(空)"
            slot_rows.append([
                f"{slot.index + 1}{'★' if slot.premium else ''}",
                name, f"{slot.qty}/{B.SLOT_CAPACITY}",
                str(len(slot.batches)),
            ])
        console.table(["槽", "商品", "数量/容量", "批次数"], slot_rows,
                      right={2, 3})

        print()
        print(theme.dim(" 仓库（未上架）："))
        wh_rows = []
        for i, item in enumerate(catalog.all_items(), start=1):
            qty = inventory.item_warehouse_qty(state, item.id)
            if qty <= 0:
                continue
            batches = [b for b in state.warehouse if b.item_id == item.id]
            soonest = min((b.expire_day - state.day for b in batches),
                          default=None)
            expire_text = f"剩{soonest}天" if soonest is not None else "-"
            wh_rows.append([str(i), item.name, str(qty), expire_text])
        if wh_rows:
            console.table(["序", "商品", "仓库件数", "最早到期"], wh_rows,
                          right={2, 3})
        else:
            print("  （仓库为空，先去进货）")

        print()
        raw = console.ask_line(
            "[槽号 商品序号 (数量)] 上架 · [x槽号 (数量)] 取下 · 回车返回: ").strip()
        if not raw:
            return
        low = raw.lower()
        parts = low.split()
        try:
            if parts[0].startswith("x"):
                slot_idx = int(parts[0][1:]) - 1
                qty = int(parts[1]) if len(parts) > 1 else None
                err = game.unshelve(slot_idx, qty)
            else:
                slot_idx = int(parts[0]) - 1
                item_idx = int(parts[1]) - 1
                qty = int(parts[2]) if len(parts) > 2 else None
                item = catalog.all_items()[item_idx]
                err = game.shelve(slot_idx, item.id, qty)
        except (ValueError, IndexError):
            print(theme.warn("格式: 1 3 或 1 3 12 / x1 或 x1 5"))
            console.pause()
            continue
        if err:
            print(theme.bad(err))
        else:
            print(theme.good("✓ 已更新陈列"))
        console.pause()
