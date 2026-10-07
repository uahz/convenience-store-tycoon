package tycoon.core

import kotlin.math.exp

/** 顾客个体与购物决策管线。 */
data class Customer(
    val archetypeId: String,
    val name: String,
    val budget: Double,
    val patience: Int,
    val wtpJitter: Double,
    val needs: MutableList<Pair<String, Int>>,   // (item_id, 数量)
)

data class Basket(
    val customer: Customer,
    val picks: MutableList<Pair<String, Int>> = mutableListOf(),
    var oosCount: Int = 0,
    var subCount: Int = 0,
)

private fun sigmoid(x: Double): Double = 1.0 / (1.0 + exp(-x))

object CustomerAi {

    fun buildCustomer(state: GameState, rng: GameRng, arch: Archetype): Customer {
        val needs = sampleNeeds(arch, rng)
        return Customer(
            archetypeId = arch.id, name = arch.name,
            budget = rng.uniform(arch.budgetRange.start, arch.budgetRange.endInclusive),
            patience = rng.randInt(arch.patienceRange.first, arch.patienceRange.last),
            wtpJitter = rng.uniform(-Balance.AI_WTP_JITTER, Balance.AI_WTP_JITTER),
            needs = needs,
        )
    }

    private fun sampleNeeds(arch: Archetype, rng: GameRng): MutableList<Pair<String, Int>> {
        val count = rng.weighted(Balance.NEEDS_COUNT_WEIGHTS)
        val pool = arch.itemPreferences.entries.map { it.key to it.value }
        val needs = mutableListOf<Pair<String, Int>>()
        val used = mutableSetOf<String>()
        var guard = 0
        while (needs.size < count && guard++ < 20) {
            val item = rng.weighted(pool)
            if (item in used) continue
            used.add(item)
            needs.add(item to 1)
        }
        return needs
    }

    fun utility(state: GameState, slot: ShelfSlot, customer: Customer): Double {
        val item = Catalog.get(slot.itemId!!)
        val price = Pricing.effectivePrice(state, item.id)
        val wtp = item.refPrice * (1.0 + customer.wtpJitter)
        val priceScore = sigmoid(Balance.AI_PRICE_SCORE_K * (wtp / price - 1.0))
        val position = if (slot.premium) Balance.AI_PREMIUM_POS_SCORE
        else Balance.AI_NORMAL_POS_SCORE
        val promo = state.promos[item.id]
        val arch = Archetypes.byId(customer.archetypeId)
        val promoScore = if (promo != null) promo.discount * arch.promoSensitivity
        else 0.0
        val stockScore = if (slot.qty > Balance.AI_STOCK_LOW_THRESHOLD) 1.0
        else Balance.AI_STOCK_LOW_SCORE
        val w = Balance.AI_UTILITY_WEIGHTS
        return w.getValue("price") * priceScore +
                w.getValue("position") * position +
                w.getValue("promo") * promoScore +
                w.getValue("stock") * stockScore
    }

    /** 逐需求决策：点名商品缺货→替代；效用达门槛且预算允许→购买。 */
    fun shop(customer: Customer, state: GameState, rng: GameRng): Basket {
        val basket = Basket(customer)
        var remaining = customer.budget
        for ((itemId, qty) in customer.needs) {
            val slot = Inventory.slotWithItem(state, itemId)
            if (slot == null) {
                basket.oosCount += 1
                if (rng.next() < Balance.AI_SUBSTITUTE_PROB) {
                    val others = state.slots.filter { it.itemId != null && it.qty > 0 }
                    if (others.isNotEmpty()) {
                        val alt = rng.choice(others)
                        val price = Pricing.effectivePrice(state, alt.itemId!!)
                        if (price <= remaining) {
                            basket.picks.add(alt.itemId!! to 1)
                            basket.subCount += 1
                            remaining -= price
                        }
                    }
                }
                continue
            }
            if (utility(state, slot, customer) < Balance.AI_BUY_THRESHOLD) continue
            val item = Catalog.get(itemId)
            val price = Pricing.effectivePrice(state, itemId)
            var buyQty = qty
            if (item.refPrice <= Balance.SECOND_UNIT_MAX_REF &&
                rng.next() < Balance.SECOND_UNIT_PROB &&
                slot.qty >= buyQty + 1 &&
                price * (buyQty + 1) <= remaining
            ) buyQty += 1
            buyQty = minOf(buyQty, slot.qty)
            if (buyQty <= 0 || price * buyQty > remaining) continue
            basket.picks.add(itemId to buyQty)
            remaining -= price * buyQty
        }
        return basket
    }
}

/** 客流引擎：进店人数合成与原型抽取。 */
object Traffic {

    fun dailyArrivalMean(state: GameState): Double {
        val preset = Difficulties.ALL.getValue(state.difficulty)
        val weekday = (state.day - 1) % 7
        val base = if (weekday in Balance.WEEKEND_DAYS) Balance.TRAFFIC_BASE_WEEKEND
        else Balance.TRAFFIC_BASE_WEEKDAY
        val enterRate = Balance.BASE_ENTER_RATE *
                (0.5 + Display.attractiveness(state)) *
                (Balance.LOYALTY_ARRIVAL_A + Balance.LOYALTY_ARRIVAL_B *
                        Display.avgLoyalty(state))
        return base * enterRate * preset.trafficMult
    }

    fun hoursWeightsSum(): Double {
        var total = 0.0
        for (h in Balance.DAY_START_HOUR until Balance.DAY_END_HOUR) {
            total += Balance.PEAK_WEIGHTS[h] ?: 1.0
        }
        return total
    }

    fun arrivalsForHour(state: GameState, hour: Int, rng: GameRng): Int {
        val w = Balance.PEAK_WEIGHTS[hour] ?: 1.0
        return rng.poisson(dailyArrivalMean(state) * w / hoursWeightsSum())
    }

    fun pickArchetype(hour: Int, rng: GameRng): Archetype {
        val pairs = Archetypes.ALL.map {
            it to (it.share * (it.hourWeights[hour] ?: 1.0))
        }
        return rng.weighted(pairs)
    }
}
