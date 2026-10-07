package tycoon.core

/** 日仿真引擎：逐小时推进（供实时 UI 驱动），产出 DayLog。 */
object Simulation {

    private fun serviceMinutes(picks: List<Pair<String, Int>>): Double {
        val totalItems = picks.sumOf { it.second }
        return Balance.QUEUE_SERVICE_MIN_BASE + Balance.QUEUE_PER_ITEM_MIN * totalItems
    }

    private fun checkout(state: GameState, basket: Basket, log: DayLog,
                         hlog: HourLog) {
        var revenue = 0.0
        var sat = Balance.SAT_NEUTRAL + Balance.SAT_BASE
        for ((itemId, qty) in basket.picks) {
            var q = qty
            val slot = Inventory.slotWithItem(state, itemId) ?: continue
            if (slot.qty < q) q = slot.qty
            if (q <= 0) continue
            val price = Pricing.effectivePrice(state, itemId)
            revenue += price * q
            val consumed = Inventory.consume(state, slot, q)
            log.cogs += consumed.sumOf { (c, cost) -> c * cost }
            log.itemsSold[itemId] = (log.itemsSold[itemId] ?: 0) + q
            val ref = Catalog.get(itemId).refPrice
            val unfair = if (ref > 0) (price / ref - 1.0).coerceIn(0.0, 1.0) else 1.0
            sat -= Balance.SAT_PRICE_UNFAIR_COEF * unfair
        }
        sat -= Balance.SAT_OOS_SUB * basket.subCount
        sat -= Balance.SAT_OOS_NOSUB * (basket.oosCount - basket.subCount)
        log.revenue += revenue
        hlog.revenue += revenue
        log.satSamples.add(sat)
        if (basket.picks.isNotEmpty()) log.conversions += 1
        log.served += 1
        hlog.served += 1
    }

    /** 推进一个小时刻度：到达→决策→排队→结账。queue 跨小时延续。 */
    fun runHour(state: GameState, rng: GameRng, queue: ArrayDeque<Basket>,
                log: DayLog): HourLog {
        val hlog = HourLog()
        var busy = 0.0
        fun tryServe() {
            while (queue.isNotEmpty()) {
                val basket = queue.first()
                val svc = serviceMinutes(basket.picks)
                if (busy + svc > 60.0) break
                queue.removeFirst()
                busy += svc
                checkout(state, basket, log, hlog)
            }
        }

        val hour = Balance.DAY_START_HOUR + log.hourLogs.size
        val conv0 = log.conversions
        val satN0 = log.satSamples.size
        tryServe()

        val n = Traffic.arrivalsForHour(state, hour, rng)
        hlog.arrivals = n
        log.arrivals += n
        val arrivals = List(n) {
            CustomerAi.buildCustomer(state, rng, Traffic.pickArchetype(hour, rng))
        }.sortedBy { rng.next() }

        val oosNote = linkedMapOf<String, Int>()
        for (cust in arrivals) {
            if (queue.size > cust.patience) {
                hlog.abandons += 1
                log.abandons += 1
                continue
            }
            val basket = CustomerAi.shop(cust, state, rng)
            log.totalNeeds += cust.needs.size
            log.oosNeeds += basket.oosCount
            if (basket.oosCount > 0) {
                for ((itemId, _) in cust.needs) {
                    if (Inventory.slotWithItem(state, itemId) == null) {
                        oosNote[itemId] = (oosNote[itemId] ?: 0) + 1
                    }
                }
            }
            queue.addLast(basket)
            tryServe()
        }

        hlog.conversions = log.conversions - conv0
        val newSat = log.satSamples.drop(satN0)
        if (newSat.isNotEmpty()) hlog.satHour = newSat.average()
        if (hlog.abandons > 0) hlog.notes.add("排队放弃 ${hlog.abandons} 人")
        if (oosNote.isNotEmpty()) {
            val detail = oosNote.entries.joinToString("、") {
                "${Catalog.get(it.key).name}×${it.value}"
            }
            hlog.notes.add("缺货: $detail")
        }
        hlog.hour = hour
        return hlog
    }

    /** 逐小时生成器（同步跑完一整天，onHour 每小时回调一次）。 */
    fun iterDayHours(state: GameState, rng: GameRng,
                     onHour: (HourLog) -> Unit): DayLog {
        val log = DayLog()
        val queue = ArrayDeque<Basket>()
        for (i in 0 until Balance.DAY_END_HOUR - Balance.DAY_START_HOUR) {
            val hlog = runHour(state, rng, queue, log)
            log.hourLogs.add(hlog)
            onHour(hlog)
        }
        log.lostAtClose = queue.size
        return log
    }

    fun runDay(state: GameState, rng: GameRng): DayLog {
        val log = DayLog()
        val queue = ArrayDeque<Basket>()
        for (i in 0 until Balance.DAY_END_HOUR - Balance.DAY_START_HOUR) {
            log.hourLogs.add(runHour(state, rng, queue, log))
        }
        log.lostAtClose = queue.size
        return log
    }
}

/** 有状态的一天模拟器：实时 UI 每次调用 [stepHour] 推进一个游戏小时。 */
class DaySimulator(val state: GameState, val rng: GameRng) {
    private val log = DayLog()
    private val queue = ArrayDeque<Basket>()
    private val totalHours = Balance.DAY_END_HOUR - Balance.DAY_START_HOUR
    private var closed = false

    val hoursDone: Int get() = log.hourLogs.size
    val isDone: Boolean get() = log.hourLogs.size >= totalHours

    /** 推进一个小时；一天走完后再调用返回 null（含打烊滞留统计）。 */
    fun stepHour(): HourLog? {
        if (log.hourLogs.size >= totalHours) {
            if (!closed) {
                log.lostAtClose = queue.size
                closed = true
            }
            return null
        }
        val hlog = Simulation.runHour(state, rng, queue, log)
        log.hourLogs.add(hlog)
        if (log.hourLogs.size == totalHours) log.lostAtClose = queue.size
        return hlog
    }

    fun dayLog(): DayLog = log
}
