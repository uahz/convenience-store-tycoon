package tycoon.core

import kotlin.math.roundToLong

/** 定价规则：生效售价（含促销）、毛利计算、校验。 */
object Pricing {

    fun effectivePrice(state: GameState, itemId: String): Double {
        val price = state.prices[itemId] ?: Catalog.get(itemId).refPrice
        val promo = state.promos[itemId]
        return if (promo != null && promo.discount > 0) {
            price * (1.0 - promo.discount)
        } else price
    }

    fun marginRate(state: GameState, itemId: String): Double {
        val price = state.prices[itemId] ?: Catalog.get(itemId).refPrice
        val cost = Catalog.get(itemId).unitCost
        return if (price <= 0) 0.0 else (price - cost) / price
    }

    fun setPrice(state: GameState, itemId: String, price: Double): String? {
        if (price <= 0) return "售价必须大于 0"
        state.prices[itemId] = (price * 100).roundToLong() / 100.0
        return null
    }

    fun setPromo(state: GameState, itemId: String, pct: Double): String? {
        if (pct == 0.0) {
            state.promos.remove(itemId)
            return null
        }
        if (pct <= 0 || pct > Balance.PROMO_MAX_PCT) {
            return "折扣需在 0~${Balance.PROMO_MAX_PCT}% 之间"
        }
        state.promos[itemId] = Promo(itemId, pct / 100.0, Balance.PROMO_DEFAULT_DAYS)
        return null
    }

    /** 每日晨间：促销剩余天数 -1，到期移除。 */
    fun tickPromos(state: GameState) {
        val expired = state.promos.filterValues { it.daysLeft - 1 <= 0 }.keys
        for (k in expired) state.promos.remove(k)
        for (p in state.promos.values) p.daysLeft -= 1
    }
}

/** 陈列指数与门店吸引力。 */
object Display {

    fun displayIndex(state: GameState): Double {
        var totalWeight = 0.0
        var weightedFill = 0.0
        for (slot in state.slots) {
            val weight = if (slot.premium) Balance.PREMIUM_SLOT_WEIGHT else 1.0
            totalWeight += weight
            weightedFill += weight * (minOf(slot.qty, Balance.SLOT_CAPACITY)
                    .toDouble() / Balance.SLOT_CAPACITY)
        }
        return if (totalWeight <= 0) 0.0 else weightedFill / totalWeight
    }

    fun assortmentRatio(state: GameState): Double {
        val cats = state.slots
            .filter { it.itemId != null && it.qty > 0 }
            .map { Catalog.get(it.itemId!!).category }
            .toSet()
        return if (Catalog.CATEGORIES.isEmpty()) 0.0
        else cats.size.toDouble() / Catalog.CATEGORIES.size
    }

    fun promoStrength(state: GameState): Double {
        val onShelf = state.slots
            .filter { it.itemId != null && it.qty > 0 }
            .map { it.itemId!! }
            .toSet()
        if (onShelf.isEmpty()) return 0.0
        val total = onShelf.sumOf { state.promos[it]?.discount ?: 0.0 }
        return minOf(1.0, total / onShelf.size * Balance.PROMO_STRENGTH_SCALE)
    }

    fun attractiveness(state: GameState): Double {
        val w = Balance.ATTRACT_WEIGHTS
        return w.getValue("reputation") * state.reputation / 100.0 +
                w.getValue("display") * displayIndex(state) +
                w.getValue("promo") * promoStrength(state) +
                w.getValue("assortment") * assortmentRatio(state)
    }

    fun avgLoyalty(state: GameState): Double {
        if (state.archetypeLoyalty.isEmpty()) return 0.0
        return state.archetypeLoyalty.values.average()
    }
}
