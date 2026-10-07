package tycoon.core

/** 全局平衡数值（唯一数值来源，逻辑代码禁止魔法数字）。 */
object Balance {
    const val DAY_START_HOUR = 8
    const val DAY_END_HOUR = 24
    val DAY_NAMES = listOf("周一", "周二", "周三", "周四", "周五", "周六", "周日")

    const val TRAFFIC_BASE_WEEKDAY = 460.0
    const val TRAFFIC_BASE_WEEKEND = 575.0
    val WEEKEND_DAYS = setOf(5, 6)
    const val BASE_ENTER_RATE = 0.38
    val PEAK_WEIGHTS: Map<Int, Double> = mapOf(
        8 to 1.8, 9 to 1.5, 12 to 1.5, 13 to 1.2, 15 to 1.2, 16 to 1.4,
        17 to 1.5, 18 to 1.6, 19 to 1.4, 21 to 1.3, 22 to 1.2,
    )
    val ATTRACT_WEIGHTS = mapOf(
        "reputation" to 0.40, "display" to 0.25,
        "promo" to 0.20, "assortment" to 0.15,
    )
    const val PREMIUM_SLOT_WEIGHT = 1.5
    const val PROMO_STRENGTH_SCALE = 2.0

    const val INITIAL_CASH = 20000.0
    const val RENT_PER_DAY = 250.0
    const val UTILITY_BASE = 30.0
    const val UTILITY_RATE = 0.015
    const val VICTORY_NET_WORTH = 200000.0
    const val BANKRUPTCY_CASH = 0.0

    const val SHELF_SLOTS = 6
    const val SLOT_CAPACITY = 36
    const val WAREHOUSE_CAPACITY = 300
    val PREMIUM_SLOT_INDEXES = setOf(0, 3)

    val AI_UTILITY_WEIGHTS = mapOf(
        "price" to 0.45, "position" to 0.20, "promo" to 0.20, "stock" to 0.15,
    )
    const val AI_BUY_THRESHOLD = 0.45
    const val AI_PRICE_SCORE_K = 3.0
    const val AI_WTP_JITTER = 0.12
    const val AI_SUBSTITUTE_PROB = 0.35
    const val AI_PREMIUM_POS_SCORE = 1.0
    const val AI_NORMAL_POS_SCORE = 0.6
    const val AI_STOCK_LOW_THRESHOLD = 5
    const val AI_STOCK_LOW_SCORE = 0.7
    val NEEDS_COUNT_WEIGHTS = listOf(1 to 0.55, 2 to 0.40, 3 to 0.05)
    const val SECOND_UNIT_PROB = 0.22
    const val SECOND_UNIT_MAX_REF = 3.5
    const val LOYALTY_ARRIVAL_A = 0.55
    const val LOYALTY_ARRIVAL_B = 0.45

    const val QUEUE_SERVICE_MIN_BASE = 2.6
    const val QUEUE_PER_ITEM_MIN = 0.5
    const val SERVICE_SPEED = 1.0

    const val SAT_NEUTRAL = 70.0
    const val SAT_BASE = 8.0
    const val SAT_OOS_SUB = 1.5
    const val SAT_OOS_NOSUB = 3.0
    const val SAT_PRICE_UNFAIR_COEF = 4.0
    const val QUEUE_PENALTY_RATE = 0.08
    const val SAT_QUEUE_PENALTY_MAX = 5.0
    const val SAT_QUEUE_PENALTY_SLOPE = 30.0
    const val SAT_BASELINE = 65.0
    const val REP_GAIN_COEF = 0.18
    const val REP_DAILY_LIMIT = 3.0
    const val REP_ABANDON_RATE = 0.08
    const val REP_ABANDON_PENALTY_MAX = 3.0
    const val REP_ABANDON_SLOPE = 20.0
    const val LOYALTY_DAILY_GAIN = 0.30
    const val LOYALTY_DAILY_LIMIT = 0.03

    const val EXPIRY_WARN_DAYS = 2
    const val STAGNANT_RATIO = 1.5
    const val TARGET_TURNOVER_DAYS = 3
    const val SUGGEST_COVER_DAYS = 2
    const val INFINITE_SHELF_LIFE = 9999

    const val PROMO_DEFAULT_DAYS = 3
    const val PROMO_MAX_PCT = 50

    const val LEDGER_KEEP_DAYS = 30
    const val SALES_HISTORY_DAYS = 7
    const val WASTE_RATE_WINDOW_DAYS = 7
}

data class DifficultyPreset(
    val key: String,
    val label: String,
    val cash: Double,
    val trafficMult: Double,
    val rentMult: Double,
    val victoryNetWorth: Double,
)

object Difficulties {
    val EASY = DifficultyPreset("easy", "轻松", 25000.0, 1.30, 0.85, 150000.0)
    val NORMAL = DifficultyPreset("normal", "普通", 20000.0, 1.00, 1.00, 200000.0)
    val HARD = DifficultyPreset("hard", "硬核", 15000.0, 0.85, 1.25, 260000.0)
    val ALL = linkedMapOf("easy" to EASY, "normal" to NORMAL, "hard" to HARD)
}
