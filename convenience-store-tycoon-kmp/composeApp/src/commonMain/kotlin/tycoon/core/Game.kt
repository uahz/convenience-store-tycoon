package tycoon.core

import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import tycoon.PlatformIo

@Serializable
data class SaveEnvelope(
    val formatVersion: Int = 1,
    val appVersion: String = "1.0.0",
    val game: GameState,
)

/** 存档：版本化 JSON、原子性由平台层保证。 */
object Savegame {
    const val FORMAT_VERSION = 1
    const val SAVE_NAME = "autosave"

    private val json = Json {
        prettyPrint = true
        ignoreUnknownKeys = false
    }

    fun save(game: Game): String? {
        if (game.state == null) return "尚未开始游戏，无法保存"
        val envelope = SaveEnvelope(FORMAT_VERSION, "1.0.0", game.state!!)
        return try {
            PlatformIo.writeTextFile(SAVE_NAME, json.encodeToString(envelope))
            null
        } catch (e: Exception) {
            "保存失败：${e.message}"
        }
    }

    fun load(game: Game): String? {
        val text = PlatformIo.readTextFile(SAVE_NAME)
            ?: return "存档不存在"
        return try {
            val envelope = json.decodeFromString<SaveEnvelope>(text)
            if (envelope.formatVersion > FORMAT_VERSION) {
                return "存档版本高于当前游戏，请升级后再读取"
            }
            game.state = envelope.game
            game.lastDaylog = null
            game.lastReport = null
            game.pendingSpoilageCost = 0.0
            game.pendingSpoilageItems = emptyList()
            null
        } catch (e: Exception) {
            "存档损坏：${e.message}"
        }
    }

    fun hasSave(): Boolean = PlatformIo.readTextFile(SAVE_NAME) != null

    fun deleteSave() {
        PlatformIo.deleteFile(SAVE_NAME)
    }
}

/** Game 门面：UI 层唯一接触的核心对象。 */
class Game(seed: Long?) {
    val rng = GameRng(seed)
    var state: GameState? = null
    var lastDaylog: DayLog? = null
    var lastReport: DayReport? = null
    var pendingSpoilageCost = 0.0
    var pendingSpoilageItems: List<Pair<String, Int>> = emptyList()
    private var invStart = 0.0

    fun newGame(difficultyKey: String) {
        val preset = Difficulties.ALL.getValue(difficultyKey)
        val st = GameState(
            difficulty = difficultyKey,
            cash = preset.cash,
            slots = (0 until Balance.SHELF_SLOTS).map {
                ShelfSlot(it, it in Balance.PREMIUM_SLOT_INDEXES)
            }.toMutableList(),
            prices = Catalog.all().associate { it.id to it.refPrice }.toMutableMap(),
            salesHistory = Catalog.all().associate {
                it.id to mutableListOf<Int>()
            }.toMutableMap(),
            archetypeLoyalty = Archetypes.ALL.associate {
                it.id to it.initialLoyalty
            }.toMutableMap(),
        )
        state = st
        lastDaylog = null
        lastReport = null
        pendingSpoilageCost = 0.0
        pendingSpoilageItems = emptyList()
    }

    private fun require(): GameState = state ?: error("尚未开始游戏")

    /** 夜间"结束今天"后调用：日推进 + 过期报废 + 促销计时。 */
    fun startNewDay() {
        val st = require()
        st.day += 1
        val (spoil, dead) = Inventory.ageAndDiscard(st, st.day)
        Pricing.tickPromos(st)
        pendingSpoilageCost = spoil
        pendingSpoilageItems = dead.map { it.itemId to it.qty }
    }

    data class MorningInfo(
        val spoilageItems: List<Pair<String, Int>>,
        val spoilageCost: Double,
        val expiryWarns: List<Triple<String, Int, Int>>,
        val stagnants: List<Pair<String, Double>>,
        val warehouseUsed: Int,
        val warehouseFree: Int,
        val onShelf: Int,
        val slotsFilled: Int,
        val activePromos: Int,
    )

    fun morningInfo(): MorningInfo {
        val st = require()
        return MorningInfo(
            spoilageItems = pendingSpoilageItems,
            spoilageCost = pendingSpoilageCost,
            expiryWarns = Inventory.expiryWarnings(st, st.day),
            stagnants = Inventory.stagnantItems(st),
            warehouseUsed = Inventory.warehouseUnits(st),
            warehouseFree = Inventory.warehouseFree(st),
            onShelf = Inventory.onShelfUnits(st),
            slotsFilled = st.slots.count { it.itemId != null },
            activePromos = st.promos.size,
        )
    }

    /** 确认进货单：cart = itemId 到 箱数。返回 null 成功。 */
    fun confirmOrder(cart: Map<String, Int>): String? {
        val st = require()
        if (cart.isEmpty()) return "订单为空"
        var totalCost = 0.0
        var totalUnits = 0
        for ((itemId, cases) in cart) {
            if (cases <= 0) return "箱数必须为正整数"
            val item = Catalog.get(itemId)
            totalCost += item.unitCost * item.caseSize * cases
            totalUnits += item.caseSize * cases
        }
        if (totalCost > st.cash) {
            return "资金不足：需 $totalCost，现有 ${st.cash}"
        }
        if (totalUnits > Inventory.warehouseFree(st)) {
            return "仓库容量不足：本次 $totalUnits 件 > 剩余 " +
                    "${Inventory.warehouseFree(st)} 件"
        }
        st.cash -= totalCost
        st.procurementToday += totalCost
        for ((itemId, cases) in cart) {
            val item = Catalog.get(itemId)
            Inventory.addBatch(st, itemId, item.caseSize * cases, st.day,
                item.unitCost)
        }
        return null
    }

    fun setPrice(itemId: String, price: Double): String? =
        Pricing.setPrice(require(), itemId, price)

    fun setPromo(itemId: String, pct: Double): String? =
        Pricing.setPromo(require(), itemId, pct)

    fun shelve(slotIdx: Int, itemId: String, qty: Int? = null): String? {
        val st = require()
        if (slotIdx !in st.slots.indices) return "槽位不存在"
        val slot = st.slots[slotIdx]
        val existing = Inventory.slotWithItem(st, itemId)
        if (existing != null && existing != slot) return "该商品已在其他槽位上架"
        val q = qty ?: run {
            val n = minOf(
                Balance.SLOT_CAPACITY - slot.qty,
                Inventory.itemWarehouseQty(st, itemId),
            )
            if (n <= 0) return "仓库中没有可上架的该商品"
            n
        }
        return Inventory.shelve(st, slot, itemId, q)
    }

    fun unshelve(slotIdx: Int, qty: Int? = null): String? {
        val st = require()
        if (slotIdx !in st.slots.indices) return "槽位不存在"
        val slot = st.slots[slotIdx]
        if (slot.itemId == null) return "该槽位为空"
        Inventory.unshelve(st, slot, qty)
        return null
    }

    /** 同步完成一天（冒烟测试用）。 */
    fun openStore(): DayReport {
        val st = require()
        invStart = Inventory.inventoryValue(st)
        val daylog = Simulation.runDay(st, rng)
        return finishDay(daylog)
    }

    /** 实时 UI：开门，返回可逐步推进的一天模拟器。 */
    fun beginDay(): DaySimulator {
        val st = require()
        invStart = Inventory.inventoryValue(st)
        return DaySimulator(st, rng)
    }

    fun finishDay(daylog: DayLog): DayReport {
        val st = require()
        val report = Settlement.settle(st, daylog, invStart,
            pendingSpoilageCost, pendingSpoilageItems)
        lastDaylog = daylog
        lastReport = report
        pendingSpoilageCost = 0.0
        pendingSpoilageItems = emptyList()
        return report
    }
}
