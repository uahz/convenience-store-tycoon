package tycoon.core

import kotlin.math.roundToLong

/** 财务口径：净资产与破产判定。 */
object Economy {
    fun netWorth(state: GameState): Double =
        state.cash + Inventory.inventoryValue(state)

    fun isBankrupt(state: GameState): Boolean =
        state.cash < Balance.BANKRUPTCY_CASH
}

/** 每日结算（纯函数式）：状态 + DayLog → DayReport + 更新状态 + KPI 账本。 */
object Settlement {

    private fun round2(v: Double): Double = (v * 100).roundToLong() / 100.0
    private fun round4(v: Double): Double = (v * 10000).roundToLong() / 10000.0
    private fun round1(v: Double): Double = (v * 10).roundToLong() / 10.0

    fun settle(state: GameState, daylog: DayLog, invValueStart: Double,
               spoilageCost: Double,
               spoilageItems: List<Pair<String, Int>>): DayReport {
        val preset = Difficulties.ALL.getValue(state.difficulty)
        val weekday = Balance.DAY_NAMES[(state.day - 1) % 7]
        val r = DayReport(day = state.day, weekday = weekday)
        r.revenue = daylog.revenue
        r.cogs = daylog.cogs
        r.spoilage = spoilageCost
        r.spoilageItems = spoilageItems
        r.rent = Balance.RENT_PER_DAY * preset.rentMult
        r.utilities = Balance.UTILITY_BASE + Balance.UTILITY_RATE * daylog.revenue

        val fixed = r.rent + r.utilities
        r.net = daylog.revenue - daylog.cogs - spoilageCost - fixed

        r.openingCash = state.cash
        state.cash += daylog.revenue - fixed
        r.closingCash = state.cash
        r.netWorth = Economy.netWorth(state)

        r.traffic = daylog.arrivals
        r.conversions = daylog.conversions
        r.conversionRate = if (daylog.arrivals > 0)
            daylog.conversions.toDouble() / daylog.arrivals else 0.0
        r.aov = if (daylog.conversions > 0)
            daylog.revenue / daylog.conversions else 0.0
        r.oosRate = if (daylog.totalNeeds > 0)
            daylog.oosNeeds.toDouble() / daylog.totalNeeds else 0.0
        r.abandonRate = if (daylog.arrivals > 0)
            daylog.abandons.toDouble() / daylog.arrivals else 0.0
        r.abandons = daylog.abandons
        r.lostAtClose = daylog.lostAtClose
        val invValueEnd = Inventory.inventoryValue(state)
        val avgInv = (invValueStart + invValueEnd) / 2.0
        r.turnover = if (avgInv > 0) daylog.cogs / avgInv else 0.0
        val purchasesTotal = state.purchases7d.sum()
        r.wasteRate = if (purchasesTotal > 0) spoilageCost / purchasesTotal else 0.0
        r.itemsSold = daylog.itemsSold.toMap()

        r.repBefore = state.reputation
        if (daylog.satSamples.isNotEmpty()) {
            var satAvg = daylog.satAvg.coerceIn(0.0, 100.0)
            if (r.abandonRate > Balance.QUEUE_PENALTY_RATE) {
                satAvg -= minOf(
                    Balance.SAT_QUEUE_PENALTY_MAX,
                    (r.abandonRate - Balance.QUEUE_PENALTY_RATE) *
                            Balance.SAT_QUEUE_PENALTY_SLOPE,
                )
            }
            r.satAvg = satAvg
            val repDelta = (Balance.REP_GAIN_COEF * (satAvg - Balance.SAT_BASELINE))
                .coerceIn(-Balance.REP_DAILY_LIMIT, Balance.REP_DAILY_LIMIT)
            state.reputation = (state.reputation + repDelta).coerceIn(0.0, 100.0)
            val loyaltyDelta = (Balance.LOYALTY_DAILY_GAIN *
                    (satAvg - Balance.SAT_BASELINE) / Balance.SAT_BASELINE)
                .coerceIn(-Balance.LOYALTY_DAILY_LIMIT, Balance.LOYALTY_DAILY_LIMIT)
            for (k in state.archetypeLoyalty.keys) {
                state.archetypeLoyalty[k] =
                    (state.archetypeLoyalty[k]!! + loyaltyDelta).coerceIn(0.0, 1.0)
            }
        } else if (r.abandonRate > Balance.REP_ABANDON_RATE) {
            state.reputation = maxOf(
                0.0,
                state.reputation - minOf(
                    Balance.REP_ABANDON_PENALTY_MAX,
                    (r.abandonRate - Balance.REP_ABANDON_RATE) * Balance.REP_ABANDON_SLOPE,
                ),
            )
        }
        r.repAfter = state.reputation

        for (item in Catalog.all()) {
            val hist = state.salesHistory.getOrPut(item.id) { mutableListOf() }
            hist.add(daylog.itemsSold[item.id] ?: 0)
            while (hist.size > Balance.SALES_HISTORY_DAYS) hist.removeAt(0)
        }
        state.purchases7d.add(state.procurementToday)
        while (state.purchases7d.size > Balance.WASTE_RATE_WINDOW_DAYS) {
            state.purchases7d.removeAt(0)
        }
        state.procurementToday = 0.0

        state.ledger.add(
            mapOf(
                "day" to state.day.toDouble(),
                "revenue" to round2(r.revenue),
                "cogs" to round2(r.cogs),
                "spoilage" to round2(r.spoilage),
                "fixed" to round2(fixed),
                "net" to round2(r.net),
                "traffic" to r.traffic.toDouble(),
                "conversions" to r.conversions.toDouble(),
                "convRate" to round4(r.conversionRate),
                "aov" to round2(r.aov),
                "oosRate" to round4(r.oosRate),
                "turnover" to round4(r.turnover),
                "wasteRate" to round4(r.wasteRate),
                "sat" to round1(r.satAvg),
                "rep" to round1(state.reputation),
                "cash" to round2(state.cash),
                "netWorth" to round2(r.netWorth),
            ),
        )
        while (state.ledger.size > Balance.LEDGER_KEEP_DAYS) state.ledger.removeAt(0)

        r.bankrupt = state.cash < Balance.BANKRUPTCY_CASH
        r.victory = !r.bankrupt && r.netWorth >= preset.victoryNetWorth
        return r
    }
}
