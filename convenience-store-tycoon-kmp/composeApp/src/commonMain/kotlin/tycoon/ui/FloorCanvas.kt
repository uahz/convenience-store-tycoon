package tycoon.ui

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.translate
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.drawText
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.rememberTextMeasurer
import androidx.compose.ui.unit.IntSize
import androidx.compose.ui.unit.sp
import androidx.compose.ui.layout.onSizeChanged
import kotlinx.coroutines.delay

private const val BASE_WALK = 150f   // 逻辑像素/秒（1× 基准）

private fun two(n: Int): String = n.toString().padStart(2, '0')

/** 实时地板画布：30FPS 重绘（货架/顾客/收银队列/时钟）。 */
@Composable
fun FloorCanvas(vm: GameViewModel, modifier: Modifier) {
    val textMeasurer = rememberTextMeasurer()
    var canvasSize = remember { IntSize(660, 560) }

    fun scale(): Float = minOf(
        canvasSize.width / FloorLayout.W,
        canvasSize.height / FloorLayout.H,
    )

    LaunchedEffect(Unit) {
        val clock = kotlin.time.TimeSource.Monotonic
        var lastMark = clock.markNow()
        while (true) {
            delay(33)
            val dt = lastMark.elapsedNow().inWholeMilliseconds / 1000f
                .coerceAtMost(0.1f)
            lastMark = clock.markNow()
            if (vm.phase == "open" && vm.speed != "pause") {
                val mult = when (vm.speed) {
                    "2x" -> 2f
                    "4x" -> 4f
                    else -> 1f
                }
                vm.stepAgents(BASE_WALK * dt * mult)
                vm.clockProgress = (vm.clockProgress + dt * 1000f /
                        vm.hourIntervalMs()).coerceAtMost(1f)
            }
        }
    }

    Canvas(modifier.fillMaxSize().onSizeChanged { canvasSize = it }) {
        val s = scale()
        val dx = (size.width - FloorLayout.W * s) / 2f
        val dy = (size.height - FloorLayout.H * s) / 2f
        translate(dx, dy) {
            drawScaled(s, textMeasurer, vm)
        }
    }
}

private fun DrawScope.drawScaled(
    s: Float,
    textMeasurer: androidx.compose.ui.text.TextMeasurer,
    vm: GameViewModel,
) {
    fun p(x: Float, y: Float) = Offset(x * s, y * s)
    fun r(w: Float, h: Float) = Size(w * s, h * s)

    // 地板与墙
    drawRoundRect(Theme.FloorBase, cornerRadius = CornerRadius(10 * s),
        topLeft = Offset.Zero, size = Size(FloorLayout.W * s, FloorLayout.H * s))
    var gx = 0f
    var gy = 16f
    var row = 0
    while (gy < FloorLayout.H - 36) {
        gx = if (row % 2 == 0) 0f else 18f
        while (gx < FloorLayout.W - 16 - 36) {
            drawRect(Theme.FloorTile,
                topLeft = p(gx, gy), size = r(18f, 18f))
            gx += 36f
        }
        gy += 36f
        row += 1
    }
    drawRect(Theme.Wall, topLeft = Offset(0f, 0f),
        size = Size(FloorLayout.W * s, 16 * s))
    drawRect(Color(0xFF8A7864), topLeft = Offset(FloorLayout.W * s - 16 * s, 0f),
        size = Size(16 * s, FloorLayout.H * s))
    // 门
    val door = FloorLayout.door
    drawRect(Color.White, topLeft = p(door.x, door.y), size = r(14f, 56f))
    drawRect(Theme.Primary, topLeft = p(door.x, door.y), size = r(14f, 56f),
        style = androidx.compose.ui.graphics.drawscope.Stroke(2 * s))
    drawText(textMeasurer, "入", p(door.x - 2f, door.y + 18f), TextStyle(
        fontSize = 11.sp, color = Theme.Primary, fontWeight = FontWeight.Bold))
    // 收银台
    val c = FloorLayout.counter
    drawRoundRect(Theme.Counter, topLeft = p(c.x, c.y),
        size = r(150f, 30f), cornerRadius = CornerRadius(4 * s))
    drawText(textMeasurer, "🧾 收银台", p(c.x + 28f, c.y + 6f), TextStyle(
        fontSize = 11.sp, color = Color.White))
    // 货架
    val st = vm.state
    if (st != null) {
        for (slot in st.slots) {
            drawShelf(s, textMeasurer, vm, slot.index, slot.premium,
                slot.itemId, slot.qty)
        }
    }
    // 顾客
    for (a in vm.agents) {
        drawCircle(a.color, radius = 7 * s, center = p(a.x, a.y))
        if (a.bubble.isNotEmpty()) {
            val tw = a.bubble.length * 11f + 14f
            drawRoundRect(
                Color.White, topLeft = p(a.x - tw / 2, a.y - 30f),
                size = r(tw, 20f), cornerRadius = CornerRadius(6 * s),
            )
            drawText(textMeasurer, a.bubble, p(a.x - tw / 2 + 6f, a.y - 26f),
                TextStyle(fontSize = 10.sp, color = Theme.Text))
        }
    }
    // 时钟芯片
    drawRoundRect(Color.White, topLeft = p(FloorLayout.W - 104f, 24f),
        size = r(88f, 26f), cornerRadius = CornerRadius(6 * s))
    val txt = when (vm.phase) {
        "open" -> {
            val minute = (vm.clockProgress * 59).toInt()
            two(vm.clockHour) + ":" + two(minute)
        }
        "prep" -> "备货中"
        "night" -> "已打烊"
        else -> "--:--"
    }
    drawText(textMeasurer, txt, p(FloorLayout.W - 84f, 30f), TextStyle(
        fontSize = 13.sp, color = Theme.Text, fontWeight = FontWeight.Bold))
    if (vm.phase != "open") {
        drawText(textMeasurer, "休业中",
            p(FloorLayout.W / 2 - 40f, FloorLayout.H / 2 - 14f), TextStyle(
                fontSize = 22.sp, color = Color(0x33808080),
                fontWeight = FontWeight.Bold))
    }
}

private fun DrawScope.drawShelf(
    s: Float,
    textMeasurer: androidx.compose.ui.text.TextMeasurer,
    vm: GameViewModel,
    index: Int,
    premium: Boolean,
    itemId: String?,
    qty: Int,
) {
    fun p(x: Float, y: Float) = Offset(x * s, y * s)
    fun r(w: Float, h: Float) = Size(w * s, h * s)
    val pos = FloorLayout.shelfPos[index]
    val (x, y) = pos
    val cap = tycoon.core.Balance.SLOT_CAPACITY
    if (itemId != null) {
        val item = tycoon.core.Catalog.get(itemId)
        val price = tycoon.core.Pricing.effectivePrice(vm.state!!, itemId)
        val promo = vm.state!!.promos[itemId]
        var name = item.name
        if (name.length > 7) name = name.take(7) + "…"
        val priceTxt = "¥" + tycoon.util.Fmt.formatDecimal(price, 2) +
                (if (promo != null) " (−${(promo.discount * 100).toInt()}%)" else "")
        val fill = Theme.Shelf
        drawRoundRect(fill, topLeft = p(x, y), size = r(FloorLayout.SHELF_W,
            FloorLayout.SHELF_H), cornerRadius = CornerRadius(7 * s))
        drawRoundRect(
            if (premium) Theme.Amber else Theme.ShelfDark,
            topLeft = p(x, y), size = r(FloorLayout.SHELF_W, FloorLayout.SHELF_H),
            cornerRadius = CornerRadius(7 * s),
            style = androidx.compose.ui.graphics.drawscope.Stroke(2 * s),
        )
        if (premium) {
            drawRoundRect(Theme.GoldBg, topLeft = p(x + FloorLayout.SHELF_W - 52f,
                y - 8f), size = r(52f, 15f), cornerRadius = CornerRadius(5 * s))
            drawText(textMeasurer, "★ 黄金位",
                p(x + FloorLayout.SHELF_W - 48f, y - 6f), TextStyle(
                    fontSize = 9.sp, color = Theme.Gold,
                    fontWeight = FontWeight.Bold))
        }
        var dispName = name
        if (dispName.length > 7) dispName = dispName.take(7) + "…"
        drawText(textMeasurer, dispName, p(x + 8f, y + 7f), TextStyle(
            fontSize = 11.sp, color = Color.White, fontWeight = FontWeight.Bold))
        drawText(textMeasurer, "$qty/$cap", p(x + FloorLayout.SHELF_W - 40f,
            y + 8f), TextStyle(fontSize = 9.sp, color = Color(0xFFF2F2F2)))
        drawText(textMeasurer, priceTxt, p(x + 8f, y + 23f), TextStyle(
            fontSize = 9.sp, color = Color(0xFFF0F0F0)))
        val barW = FloorLayout.SHELF_W - 16f
        drawRoundRect(Color(0xFF123C2E), topLeft = p(x + 8f, y + 46f),
            size = r(barW, 7f), cornerRadius = CornerRadius(3 * s))
        val ratio = (qty.toFloat() / cap).coerceIn(0f, 1f)
        if (ratio > 0f) {
            drawRoundRect(
                if (ratio > 0.33f) Color(0xFF8FE3C0) else Theme.Amber,
                topLeft = p(x + 8f, y + 46f),
                size = r(barW * ratio, 7f), cornerRadius = CornerRadius(3 * s),
            )
        }
    } else {
        drawRoundRect(Theme.ShelfEmpty, topLeft = p(x, y),
            size = r(FloorLayout.SHELF_W, FloorLayout.SHELF_H),
            cornerRadius = CornerRadius(7 * s))
        drawText(textMeasurer, "（空槽位）", p(x + 8f, y + 8f), TextStyle(
            fontSize = 11.sp, color = Color(0xFF5B6A79)))
        drawText(textMeasurer, "从侧栏「陈列」上架", p(x + 8f, y + 26f),
            TextStyle(fontSize = 9.sp, color = Color(0xFF8A97A4)))
    }
}
