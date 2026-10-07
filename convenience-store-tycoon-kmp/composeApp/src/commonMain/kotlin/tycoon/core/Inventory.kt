package tycoon.core

import kotlin.math.ceil

/** 库存规则：批次池、FIFO、上架/取下/售出扣减、过期报废。 */
object Inventory {

    fun batchById(state: GameState, batchId: Int): Batch? =
        state.warehouse.firstOrNull { it.batchId == batchId }

    fun allocatedByBatch(state: GameState): Map<Int, Int> {
        val m = mutableMapOf<Int, Int>()
        for (slot in state.slots) {
            for (rec in slot.batches) m[rec[0]] = (m[rec[0]] ?: 0) + rec[1]
        }
        return m
    }

    /** 未上架、存于仓库的件数。 */
    fun warehouseUnits(state: GameState): Int {
        val alloc = allocatedByBatch(state)
        return state.warehouse.sumOf { b ->
            maxOf(0, b.qty - (alloc[b.batchId] ?: 0))
        }
    }

    fun warehouseFree(state: GameState): Int =
        maxOf(0, Balance.WAREHOUSE_CAPACITY - warehouseUnits(state))

    fun onShelfUnits(state: GameState): Int =
        state.slots.sumOf { if (it.itemId != null) it.qty else 0 }

    fun itemWarehouseQty(state: GameState, itemId: String): Int {
        val alloc = allocatedByBatch(state)
        return state.warehouse.filter { it.itemId == itemId }.sumOf { b ->
            maxOf(0, b.qty - (alloc[b.batchId] ?: 0))
        }
    }

    fun itemOnShelfQty(state: GameState, itemId: String): Int =
        state.slots.filter { it.itemId == itemId }.sumOf { it.qty }

    fun slotWithItem(state: GameState, itemId: String): ShelfSlot? =
        state.slots.firstOrNull { it.itemId == itemId && it.qty > 0 }

    fun itemBatchesFifo(state: GameState, itemId: String): List<Batch> {
        val alloc = allocatedByBatch(state)
        return state.warehouse
            .filter { it.itemId == itemId && it.qty - (alloc[it.batchId] ?: 0) > 0 }
            .sortedBy { it.expireDay * 1_000_000 + it.batchId }
    }

    fun inventoryValue(state: GameState): Double =
        state.warehouse.sumOf { it.qty * it.unitCost }

    fun addBatch(state: GameState, itemId: String, qty: Int, day: Int,
                 unitCost: Double): Batch {
        val item = Catalog.get(itemId)
        val expire = if (item.shelfLifeDays >= Balance.INFINITE_SHELF_LIFE / 10) {
            Balance.INFINITE_SHELF_LIFE
        } else {
            day + item.shelfLifeDays
        }
        val batch = Batch(state.nextBatchId++, itemId, day, expire, qty, unitCost)
        state.warehouse.add(batch)
        return batch
    }

    /** 上架。返回 null 成功，否则错误信息。 */
    fun shelve(state: GameState, slot: ShelfSlot, itemId: String,
               qty: Int): String? {
        if (slot.itemId != null && slot.itemId != itemId) {
            return "槽位 ${slot.index + 1} 已被其他商品占用，请先取下"
        }
        val remaining = Balance.SLOT_CAPACITY - slot.qty
        if (qty > remaining) return "槽位容量不足（剩余 $remaining 件）"
        val alloc = allocatedByBatch(state)
        val taken = mutableListOf<Pair<Int, Int>>()
        var need = qty
        for (b in itemBatchesFifo(state, itemId)) {
            val avail = b.qty - (alloc[b.batchId] ?: 0)
            if (avail <= 0) continue
            val t = minOf(avail, need)
            taken.add(b.batchId to t)
            need -= t
            if (need == 0) break
        }
        if (need > 0) return "仓库中该商品库存不足"
        for ((bid, q) in taken) slot.batches.add(listOf(bid, q))
        slot.itemId = itemId
        slot.qty += qty
        return null
    }

    /** 取下（null = 全部），返回实际取下数量。 */
    fun unshelve(state: GameState, slot: ShelfSlot, qty: Int?): Int {
        if (qty == null || qty >= slot.qty) {
            val removed = slot.qty
            slot.batches.clear()
            slot.qty = 0
            slot.itemId = null
            return removed
        }
        var removed = 0
        while (removed < qty && slot.batches.isNotEmpty()) {
            val rec = slot.batches.last()
            val t = minOf(rec[1], qty - removed)
            val newQ = rec[1] - t
            removed += t
            if (newQ <= 0) slot.batches.removeAt(slot.batches.size - 1)
            else slot.batches[slot.batches.size - 1] = listOf(rec[0], newQ)
        }
        slot.qty -= removed
        if (slot.qty <= 0) {
            slot.batches.clear()
            slot.qty = 0
            slot.itemId = null
        }
        return removed
    }

    /** 售出（FIFO 扣减），返回 [(数量, 批次进价)]。 */
    fun consume(state: GameState, slot: ShelfSlot, qty: Int):
            List<Pair<Int, Double>> {
        val out = mutableListOf<Pair<Int, Double>>()
        var remaining = qty
        var i = 0
        while (remaining > 0 && i < slot.batches.size) {
            val rec = slot.batches[i]
            val t = minOf(rec[1], remaining)
            val batch = batchById(state, rec[0])
            if (batch == null) {
                slot.batches.removeAt(i)
                continue
            }
            batch.qty -= t
            val newQ = rec[1] - t
            remaining -= t
            out.add(t to batch.unitCost)
            if (newQ <= 0) slot.batches.removeAt(i) else {
                slot.batches[i] = listOf(rec[0], newQ)
                i += 1
            }
        }
        slot.qty -= qty - remaining
        if (slot.qty <= 0) {
            slot.batches.clear()
            slot.qty = 0
            slot.itemId = null
        }
        state.warehouse.removeAll { it.qty <= 0 }
        return out
    }

    /** 晨间过期清理。返回 (报废成本, 报废批次)。 */
    fun ageAndDiscard(state: GameState, day: Int): Pair<Double, List<Batch>> {
        val dead = state.warehouse.filter { it.expireDay <= day }
        if (dead.isEmpty()) return 0.0 to emptyList()
        val deadIds = dead.map { it.batchId }.toSet()
        val spoil = dead.sumOf { it.qty * it.unitCost }
        state.warehouse.removeAll { it.batchId in deadIds }
        for (slot in state.slots) {
            if (slot.batches.any { it[0] in deadIds }) {
                slot.batches.removeAll { it[0] in deadIds }
                slot.qty = slot.batches.sumOf { it[1] }
                if (slot.qty <= 0) slot.itemId = null
            }
        }
        return spoil to dead
    }

    fun avgDailySales(state: GameState, itemId: String): Double {
        val hist = state.salesHistory[itemId] ?: return 0.0
        if (hist.isEmpty()) return 0.0
        return hist.average()
    }

    fun suggestedOrderUnits(state: GameState, itemId: String): Int {
        val target = avgDailySales(state, itemId) * Balance.SUGGEST_COVER_DAYS
        val have = itemWarehouseQty(state, itemId) + itemOnShelfQty(state, itemId)
        val raw = ceil(target - have).toInt()
        return maxOf(0, raw)
    }

    /** 滞销商品 [(item_id, 周转倍率)]。 */
    fun stagnantItems(state: GameState): List<Pair<String, Double>> {
        val result = mutableListOf<Pair<String, Double>>()
        if (state.day < 3) return result
        for (item in Catalog.all()) {
            val have = itemWarehouseQty(state, item.id) + itemOnShelfQty(state, item.id)
            if (have <= 0) continue
            val avg = avgDailySales(state, item.id)
            val ratio = if (avg <= 0) Double.POSITIVE_INFINITY
            else (have / avg) / Balance.TARGET_TURNOVER_DAYS
            if (ratio > Balance.STAGNANT_RATIO) {
                result.add(item.id to minOf(ratio, 9.9))
            }
        }
        return result
    }

    /** 临期警告 [(item_id, 剩余件数, 最少剩余天数)]。 */
    fun expiryWarnings(state: GameState, day: Int):
            List<Triple<String, Int, Int>> {
        val warns = linkedMapOf<String, Pair<Int, Int>>()
        for (b in state.warehouse) {
            if (b.qty <= 0) continue
            val remaining = b.expireDay - day
            if (remaining in 1..Balance.EXPIRY_WARN_DAYS) {
                val cur = warns[b.itemId] ?: (0 to remaining)
                warns[b.itemId] = (cur.first + b.qty) to minOf(cur.second, remaining)
            }
        }
        return warns.map { Triple(it.key, it.value.first, it.value.second) }
    }
}
