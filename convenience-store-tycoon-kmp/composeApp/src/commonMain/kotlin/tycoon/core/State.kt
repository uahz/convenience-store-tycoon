package tycoon.core

import kotlinx.serialization.Serializable

@Serializable
data class Batch(
    val batchId: Int,
    val itemId: String,
    val arrivedDay: Int,
    val expireDay: Int,
    var qty: Int,
    val unitCost: Double,
)

@Serializable
data class Promo(val itemId: String, val discount: Double, var daysLeft: Int)

@Serializable
data class ShelfSlot(
    val index: Int,
    val premium: Boolean,
    var itemId: String? = null,
    var qty: Int = 0,
    val batches: MutableList<List<Int>> = mutableListOf(),  // [batchId, qty]
)

@Serializable
data class GameState(
    var day: Int = 1,
    var difficulty: String = "normal",
    var cash: Double = 0.0,
    var reputation: Double = 60.0,
    val warehouse: MutableList<Batch> = mutableListOf(),
    val slots: MutableList<ShelfSlot> = mutableListOf(),
    val prices: MutableMap<String, Double> = mutableMapOf(),
    val promos: MutableMap<String, Promo> = mutableMapOf(),
    val archetypeLoyalty: MutableMap<String, Double> = mutableMapOf(),
    /** item_id -> 近7日销量（用于均销/建议订货）。 */
    val salesHistory: MutableMap<String, MutableList<Int>> = mutableMapOf(),
    val purchases7d: MutableList<Double> = mutableListOf(),
    val ledger: MutableList<Map<String, Double>> = mutableListOf(),
    var nextBatchId: Int = 1,
    var procurementToday: Double = 0.0,
)

@Serializable
data class DayReport(
    val day: Int,
    val weekday: String,
    var revenue: Double = 0.0,
    var cogs: Double = 0.0,
    var spoilage: Double = 0.0,
    var spoilageItems: List<Pair<String, Int>> = emptyList(),
    var rent: Double = 0.0,
    var utilities: Double = 0.0,
    var net: Double = 0.0,
    var openingCash: Double = 0.0,
    var closingCash: Double = 0.0,
    var netWorth: Double = 0.0,
    var traffic: Int = 0,
    var conversions: Int = 0,
    var conversionRate: Double = 0.0,
    var aov: Double = 0.0,
    var oosRate: Double = 0.0,
    var turnover: Double = 0.0,
    var wasteRate: Double = 0.0,
    var abandonRate: Double = 0.0,
    var abandons: Int = 0,
    var lostAtClose: Int = 0,
    var satAvg: Double = 0.0,
    var repBefore: Double = 0.0,
    var repAfter: Double = 0.0,
    var itemsSold: Map<String, Int> = emptyMap(),
    var victory: Boolean = false,
    var bankrupt: Boolean = false,
)

data class HourLog(
    var hour: Int = 0,
    var arrivals: Int = 0,
    var served: Int = 0,
    var conversions: Int = 0,
    var revenue: Double = 0.0,
    var abandons: Int = 0,
    var satHour: Double = 0.0,
    val notes: MutableList<String> = mutableListOf(),
)

data class DayLog(
    val hourLogs: MutableList<HourLog> = mutableListOf(),
    var revenue: Double = 0.0,
    var cogs: Double = 0.0,
    var arrivals: Int = 0,
    var served: Int = 0,
    var conversions: Int = 0,
    var abandons: Int = 0,
    var lostAtClose: Int = 0,
    var oosNeeds: Int = 0,
    var totalNeeds: Int = 0,
    val itemsSold: MutableMap<String, Int> = mutableMapOf(),
    val satSamples: MutableList<Double> = mutableListOf(),
) {
    val satAvg: Double
        get() = if (satSamples.isEmpty()) 0.0 else satSamples.average()
}
