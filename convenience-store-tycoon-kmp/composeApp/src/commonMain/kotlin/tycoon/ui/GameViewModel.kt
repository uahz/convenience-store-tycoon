package tycoon.ui

import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import tycoon.core.Balance
import tycoon.core.Catalog
import tycoon.core.DayLog
import tycoon.core.DayReport
import tycoon.core.Difficulties
import tycoon.core.Game
import tycoon.core.GameRng
import tycoon.core.HourLog
import tycoon.core.Savegame

/** 顾客动画代理（纯呈现层，经济真值在 core）。 */
class Agent(
    var x: Float,
    var y: Float,
    val waypoints: List<Offset>,
    val color: Color,
    var bubble: String = "",
) {
    var wi = 0
}

/** 状态机 + 小时节拍驱动。 */
class GameViewModel(seed: Long?) {
    val game = Game(seed)
    var phase by mutableStateOf("menu")          // menu/prep/open/settle/night
    var speed by mutableStateOf("1x")
    var difficultyDialog by mutableStateOf(false)
    var settlementReport by mutableStateOf<DayReport?>(null)
    var showHelp by mutableStateOf(false)
    var frameTick by mutableIntStateOf(0)        // 每帧自增，驱动 Canvas 重绘
    var clockHour by mutableIntStateOf(Balance.DAY_START_HOUR)
    var clockProgress by mutableFloatStateOf(0f)
    var daylogRunning = DayLog()
    var hourTicker: tycoon.core.DaySimulator? = null
    var lastFinishError by mutableStateOf<String?>(null)

    val agents = mutableStateListOf<Agent>()
    val logLines = mutableStateListOf<Pair<String, String>>()  // (text, kind)
    var sidebarBump by mutableIntStateOf(0)   // 任何操作后 +1，驱动侧栏重组
    var sidebarTab by mutableIntStateOf(0)    // 当前侧栏页签
    var autoDemo by mutableStateOf(false)     // 打包冒烟：自动演示并自截画面

    fun poke() {
        sidebarBump += 1
    }

    val state get() = game.state

    fun hourIntervalMs(): Long = when (speed) {
        "2x" -> 2000L
        "4x" -> 1000L
        else -> 4000L
    }

    fun startNewGame(key: String) {
        game.newGame(key)
        phase = "prep"
        agents.clear()
        daylogRunning = DayLog()
        logLines.clear()
        appendLog("开业第一天！先在侧栏进货、定价、陈列，然后开门营业。", "good")
    }

    fun continueGame(): String? {
        val err = Savegame.load(game)
        if (err == null) {
            phase = "night"
            agents.clear()
            daylogRunning = DayLog()
            logLines.clear()
            appendLog("已读取存档：第 ${state?.day} 天结算后。点「结束今天」继续。", "good")
        }
        return err
    }

    fun backToMenu() {
        phase = "menu"
        settlementReport = null
    }

    fun openStore() {
        hourTicker = game.beginDay()
        daylogRunning = DayLog()
        agents.clear()
        phase = "open"
        clockHour = Balance.DAY_START_HOUR
        clockProgress = 0f
        appendLog("开门营业！", "good")
    }

    fun tickHour() {
        val sim = hourTicker ?: return
        val hlog = sim.stepHour() ?: run {
            finishDay(sim.dayLog())
            return
        }
        clockHour = hlog.hour
        clockProgress = 0f
        daylogRunning.revenue += hlog.revenue
        daylogRunning.conversions += hlog.conversions
        daylogRunning.arrivals += hlog.arrivals
        daylogRunning.abandons += hlog.abandons
        if (hlog.served > 0 && hlog.satHour > 0) {
            daylogRunning.satSamples.add(hlog.satHour)
        }
        spawnHourAgents(hlog)
        val hh = hlog.hour.toString().padStart(2, '0')
        for (note in hlog.notes) {
            appendLog(
                "$hh:00  $note",
                if ("缺货" in note || "放弃" in note) "bad" else "dim",
            )
        }
        if (hlog.served > 0) {
            appendLog(
                "$hh:00  到达 ${hlog.arrivals} · 成交 " +
                        "${hlog.conversions} 单 · 营收 ${tycoon.util.Fmt.signedMoney(hlog.revenue)}",
                "good",
            )
        }
    }

    fun finishDay(daylog: DayLog) {
        val report = game.finishDay(daylog)
        phase = "settle"
        Savegame.save(game)
        settlementReport = report
        appendLog("打烊 · 今日净利 ${tycoon.util.Fmt.signedMoney(report.net)}", "good")
    }

    fun afterSettlement() {
        val report = settlementReport
        if (report != null && (report.victory || report.bankrupt)) {
            if (report.bankrupt) Savegame.deleteSave()
            backToMenu()
            return
        }
        phase = "night"
        agents.clear()
    }

    fun nextDay() {
        if (phase != "night") return
        game.startNewDay()
        phase = "prep"
        agents.clear()
        daylogRunning = DayLog()
        appendLog("—— 第 ${state?.day} 天开始 ——", "dim")
    }

    fun appendLog(text: String, kind: String) {
        logLines.add(text to kind)
        while (logLines.size > 150) logLines.removeAt(0)
    }

    /** 把刚结束的一个游戏小时呈现为顾客动画。 */
    private fun spawnHourAgents(hlog: HourLog) {
        val st = state ?: return
        val rng = GameRng((hlog.hour * 31 + st.day).toLong())
        val archColors = listOf(
            ArchColor("office", Theme.ArchOffice),
            ArchColor("student", Theme.ArchStudent),
            ArchColor("senior", Theme.ArchSenior),
        )
        val shelfTargets = st.slots.filter { it.itemId != null }
            .map { FloorLayout.shelfCenter(it.index) }
            .ifEmpty { listOf(Offset(200f, 200f)) }
        val served = minOf(hlog.served, 14)
        repeat(served) { k ->
            val (archId, color) = archColors[k % archColors.size]
            val (sx, sy) = rng.choice(shelfTargets)
            val queueSlot = k % 5
            val waypoints = listOf(
                Offset(FloorLayout.door.x + 10f, FloorLayout.door.y + 30f),
                Offset(sx, sy + 40f),
                Offset(
                    FloorLayout.counter.x - 40f - queueSlot * 26f,
                    FloorLayout.counter.y - 6f + (k % 4) * 12f,
                ),
                Offset(FloorLayout.door.x + 10f, FloorLayout.door.y + 30f),
            )
            agents.add(
                Agent(
                    FloorLayout.door.x + 10f, FloorLayout.door.y + 30f,
                    waypoints, color,
                    bubble = if (k % 3 == 0) "结账" else "",
                ),
            )
        }
        val abandonNote = hlog.notes.firstOrNull { "缺货" in it } != null
        repeat(minOf(hlog.abandons, 8)) {
            val mid = Offset(
                rng.uniform(120.0, 420.0).toFloat(),
                rng.uniform(220.0, 400.0).toFloat(),
            )
            agents.add(
                Agent(
                    FloorLayout.door.x + 10f, FloorLayout.door.y + 30f,
                    listOf(mid, Offset(FloorLayout.door.x + 10f, FloorLayout.door.y + 30f)),
                    Theme.ArchGone,
                    bubble = if (abandonNote) "缺货走了…" else "排队走了…",
                ),
            )
        }
    }

    fun stepAgents(distPx: Float) {
        for (a in agents) {
            if (a.wi >= a.waypoints.size) continue
            val t = a.waypoints[a.wi]
            val dx = t.x - a.x
            val dy = t.y - a.y
            val d = kotlin.math.hypot(dx.toDouble(), dy.toDouble()).toFloat()
            if (d <= distPx) {
                a.x = t.x
                a.y = t.y
                a.wi += 1
            } else {
                a.x += dx / d * distPx
                a.y += dy / d * distPx
            }
        }
        agents.removeAll { it.wi >= it.waypoints.size }
        if (agents.size > 40) {
            while (agents.size > 40) agents.removeAt(0)
        }
        frameTick += 1
    }

    fun shelfStockText(slotIndex: Int): Pair<String, Float> {
        val st = state ?: return "" to 0f
        val slot = st.slots[slotIndex]
        return (slot.itemId?.let { Catalog.get(it).name } ?: "（空槽位）") to
                (slot.qty.toFloat() / Balance.SLOT_CAPACITY)
    }
}

data class ArchColor(val id: String, val color: Color)

/** 地板逻辑坐标系（660×560，绘制时按画布尺寸缩放）。 */
object FloorLayout {
    const val W = 660f
    const val H = 560f
    val shelfPos = listOf(
        Offset(28f, 46f), Offset(216f, 46f), Offset(404f, 46f),
        Offset(28f, 152f), Offset(216f, 152f), Offset(404f, 152f),
    )
    const val SHELF_W = 166f
    const val SHELF_H = 60f
    val door = Offset(10f, 430f)
    val counter = Offset(452f, 468f)

    fun shelfCenter(index: Int): Offset =
        Offset(shelfPos[index].x + SHELF_W / 2, shelfPos[index].y + SHELF_H / 2)
}
