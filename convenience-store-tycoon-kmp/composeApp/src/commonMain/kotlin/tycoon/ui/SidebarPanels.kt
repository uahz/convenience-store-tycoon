package tycoon.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Inventory2
import androidx.compose.material.icons.filled.Sell
import androidx.compose.material.icons.filled.ShoppingCart
import androidx.compose.material.icons.filled.Storefront
import androidx.compose.material.icons.filled.TrendingUp
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Slider
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.drawText
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlin.math.ceil
import kotlin.math.roundToInt
import tycoon.core.Balance
import tycoon.core.Catalog
import tycoon.core.Inventory
import tycoon.core.Pricing
import tycoon.util.Fmt

@Composable
fun Sidebar(vm: GameViewModel, modifier: Modifier) {
    val bump = vm.sidebarBump          // 订阅操作信号，操作后整栏刷新
    val tab = vm.sidebarTab
    Column(
        modifier
            .background(Theme.Panel, RoundedCornerShape(14.dp))
            .padding(horizontal = 6.dp, vertical = 6.dp),
    ) {
        Row(
            Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceEvenly,
        ) {
            val tabDefs = listOf(
                Triple("今日", Icons.Filled.TrendingUp, 0),
                Triple("进货", Icons.Filled.ShoppingCart, 1),
                Triple("定价", Icons.Filled.Sell, 2),
                Triple("陈列", Icons.Filled.Storefront, 3),
                Triple("报表", Icons.Filled.Inventory2, 4),
            )
            tabDefs.forEachIndexed { i, (label, icon, _) ->
                val selected = tab == i
                Row(
                    modifier = Modifier
                        .clip(RoundedCornerShape(9.dp))
                        .background(if (selected) Theme.PrimarySoft else Color.Transparent)
                        .clickable { vm.sidebarTab = i }
                        .padding(vertical = 7.dp, horizontal = 8.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.Center,
                ) {
                    Icon(icon, null, tint = if (selected) Theme.Primary else Theme.Sub,
                        modifier = Modifier.size(13.dp))
                    Spacer(Modifier.width(3.dp))
                    Text(label, fontSize = 12.sp,
                        color = if (selected) Theme.Primary else Theme.Sub,
                        fontWeight = if (selected) FontWeight.Bold else FontWeight.Normal)
                }
            }
        }
        when (tab) {
            0 -> TodayPanel(vm)
            1 -> BuyPanel(vm)
            2 -> PricingPanel(vm)
            3 -> DisplayPanel(vm)
            else -> ReportsPanel(vm)
        }
    }
}

@Composable
private fun StatCell(label: String, value: String, valueColor: Color = Theme.Text) {
    Column {
        Text(label, fontSize = 11.sp, color = Theme.Sub)
        Text(value, fontSize = 17.sp, fontWeight = FontWeight.Bold,
            color = valueColor)
    }
}

@Composable
private fun TodayPanel(vm: GameViewModel) {
    val state = vm.state ?: return
    val bump = vm.sidebarBump
    Column(
        Modifier.fillMaxWidth().verticalScroll(rememberScrollState()).padding(12.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        Row(horizontalArrangement = Arrangement.spacedBy(18.dp)) {
            StatCell("今日营收", Fmt.money(vm.daylogRunning.revenue), Theme.Good)
            StatCell("成交", "${vm.daylogRunning.conversions} 单")
            StatCell("客流", "${vm.daylogRunning.arrivals}")
            StatCell("满意度",
                if (vm.daylogRunning.satSamples.isEmpty()) "—"
                else "${vm.daylogRunning.satAvg.toInt()}")
        }
        val info = vm.game.morningInfo()
        Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
            for ((itemId, qty, days) in info.expiryWarns) {
                AlertRow("⚠ 临期：${Catalog.get(itemId).name} ×$qty（剩 $days 天）→ 建议促销",
                    Theme.Warn)
            }
            for ((itemId, _) in info.stagnants) {
                AlertRow("⚠ 滞销：${Catalog.get(itemId).name} → 降价/促销", Theme.Warn)
            }
            if (vm.phase == "open" && vm.daylogRunning.abandons > 0) {
                AlertRow("⚠ 排队流失 ${vm.daylogRunning.abandons} 人", Theme.Bad)
            }
            if (info.expiryWarns.isEmpty() && info.stagnants.isEmpty() &&
                vm.phase != "open"
            ) {
                AlertRow("✓ 一切正常，准备开店吧", Theme.Good)
            }
        }
        Column(
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(10.dp))
                .background(Theme.PanelDim)
                .padding(8.dp),
        ) {
            Text("最近动态", fontSize = 12.sp, fontWeight = FontWeight.Bold)
            Spacer(Modifier.height(4.dp))
            for ((text, kind) in vm.logLines.takeLast(60).asReversed()) {
                Text(
                    text, fontSize = 11.sp,
                    color = when (kind) {
                        "good" -> Theme.Good
                        "bad" -> Theme.Bad
                        "dim" -> Theme.Sub
                        else -> Theme.Text
                    },
                )
            }
        }
    }
}

@Composable
private fun AlertRow(text: String, color: Color) {
    Row(verticalAlignment = Alignment.CenterVertically) {
        Icon(Icons.Filled.Warning, null, tint = color, modifier = Modifier.size(13.dp))
        Spacer(Modifier.width(5.dp))
        Text(text, fontSize = 11.5.sp, color = color)
    }
}

@Composable
private fun BuyPanel(vm: GameViewModel) {
    val state = vm.state ?: return
    val bump = vm.sidebarBump
    var cart by remember { mutableStateOf(linkedMapOf<String, Int>()) }
    Column(
        Modifier.fillMaxWidth().verticalScroll(rememberScrollState()).padding(12.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Text("商品目录（按整箱进货 · 当日早到货）", fontSize = 12.sp,
            color = Theme.Sub)
        for (item in Catalog.all()) {
            val have = Inventory.itemWarehouseQty(state, item.id) +
                    Inventory.itemOnShelfQty(state, item.id)
            val avg = Inventory.avgDailySales(state, item.id)
            val sug = Inventory.suggestedOrderUnits(state, item.id)
            val sugCases = if (sug > 0) ceil(sug.toDouble() / item.caseSize).toInt() else 0
            val inCart = cart[item.id] ?: 0
            Row(
                modifier = Modifier.fillMaxWidth()
                    .clip(RoundedCornerShape(9.dp))
                    .background(if (inCart > 0) Theme.Select else Theme.PanelDim)
                    .padding(8.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Column(Modifier.weight(1f)) {
                    Text(item.name, fontSize = 12.5.sp, fontWeight = FontWeight.Bold)
                    Text(
                        "进价 ¥${item.unitCost} · 保质 ${item.shelfLifeDays} 天 · "
                                + "箱规 ${item.caseSize} · 库存 $have · 均销 $avg",
                        fontSize = 10.sp, color = Theme.Sub,
                    )
                }
                if (sugCases > 0) {
                    Text("建议 ${sugCases}箱", fontSize = 10.sp, color = Theme.Warn)
                    Spacer(Modifier.width(6.dp))
                }
                Text("+1 箱", fontSize = 12.sp, color = Theme.Primary,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier
                        .clip(RoundedCornerShape(7.dp))
                        .background(Theme.PrimarySoft)
                        .clickable {
                            cart[item.id] = (cart[item.id] ?: 0) + 1
                            vm.poke()
                        }
                        .padding(horizontal = 10.dp, vertical = 5.dp))
            }
        }
        if (cart.isNotEmpty()) {
            Column(
                Modifier.fillMaxWidth().clip(RoundedCornerShape(10.dp))
                    .background(Theme.PanelDim).padding(10.dp),
            ) {
                Text("订单车", fontSize = 12.5.sp, fontWeight = FontWeight.Bold)
                var totalCost = 0.0
                var totalUnits = 0
                for ((itemId, cases) in cart) {
                    val item = Catalog.get(itemId)
                    val cost = item.unitCost * item.caseSize * cases
                    totalCost += cost
                    totalUnits += item.caseSize * cases
                    Row(Modifier.fillMaxWidth().padding(top = 4.dp),
                        verticalAlignment = Alignment.CenterVertically) {
                        Text("${item.name} ×$cases 箱", fontSize = 12.sp,
                            modifier = Modifier.weight(1f))
                        Text(Fmt.money(cost), fontSize = 12.sp)
                        Text("✕", fontSize = 11.sp, color = Theme.Bad,
                            modifier = Modifier
                                .padding(start = 8.dp)
                                .clickable { cart.remove(itemId); vm.poke() })
                    }
                }
                val free = Inventory.warehouseFree(state)
                Text(
                    "合计 ${Fmt.money(totalCost)} · 共 $totalUnits 件" +
                            (if (totalUnits > free) " ⚠ 超容量" else "") +
                            "（仓库剩余 $free 件）",
                    fontSize = 11.5.sp, color = Theme.Sub,
                    modifier = Modifier.padding(top = 4.dp),
                )
            }
            androidx.compose.material3.Button(
                onClick = {
                    val err = vm.game.confirmOrder(cart)
                    if (err == null) {
                        cart = linkedMapOf()
                        vm.poke()
                        vm.appendLog("✓ 订单已确认，货已到仓", "good")
                    } else {
                        vm.appendLog("下单失败：$err", "bad")
                    }
                },
                modifier = Modifier.fillMaxWidth(),
                colors = androidx.compose.material3.ButtonDefaults.buttonColors(
                    containerColor = Theme.Primary),
            ) {
                Icon(Icons.Filled.ShoppingCart, null, modifier = Modifier.size(16.dp))
                Spacer(Modifier.width(6.dp))
                Text("✓ 确认下单（当日到仓）")
            }
        }
    }
}

@Composable
private fun PricingPanel(vm: GameViewModel) {
    val state = vm.state ?: return
    var selected by remember { mutableStateOf<String?>(null) }
    Column(
        Modifier.fillMaxWidth().verticalScroll(rememberScrollState()).padding(12.dp),
        verticalArrangement = Arrangement.spacedBy(6.dp),
    ) {
        Text("定价与促销（售价贴近参考价好卖；过高会赶客）", fontSize = 12.sp,
            color = Theme.Sub)
        for (item in Catalog.all()) {
            val price = state.prices[item.id] ?: item.refPrice
            val margin = Pricing.marginRate(state, item.id)
            val promo = state.promos[item.id]
            val eff = Pricing.effectivePrice(state, item.id)
            val selectedNow = selected == item.id
            Column(
                Modifier.fillMaxWidth()
                    .clip(RoundedCornerShape(9.dp))
                    .background(if (selectedNow) Theme.Select else Theme.PanelDim)
                    .clickable { selected = item.id }
                    .padding(8.dp),
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Filled.Sell, null, tint = Theme.Primary,
                        modifier = Modifier.size(13.dp))
                    Spacer(Modifier.width(6.dp))
                    Text(item.name, fontSize = 12.5.sp, fontWeight = FontWeight.Bold,
                        modifier = Modifier.weight(1f))
                    if (promo != null) {
                        Text("−${(promo.discount * 100).toInt()}% · 剩${promo.daysLeft}天",
                            fontSize = 10.sp, color = Theme.Warn)
                    }
                }
                Text(
                    "现售价 ${Fmt.money(price)} · 参考价 ${Fmt.money(item.refPrice)}"
                            + " · 毛利率 ${(margin * 100).toInt()}% · 生效价 ${Fmt.money(eff)}",
                    fontSize = 10.5.sp, color = Theme.Sub,
                )
                if (selectedNow) {
                    var sliderP by remember(item.id) {
                        mutableStateOf(price.toFloat())
                    }
                    Slider(
                        value = sliderP,
                        onValueChange = { sliderP = it },
                        onValueChangeFinished = {
                            vm.game.setPrice(item.id, sliderP.toDouble())
                        },
                        valueRange = (item.unitCost.toFloat() * 1.1f)..
                                (item.refPrice.toFloat() * 2f),
                    )
                    Text(
                        "拖动设置售价：¥" + Fmt.formatDecimal(sliderP.toDouble(), 2),
                        fontSize = 11.sp, color = Theme.Primary,
                        fontWeight = FontWeight.Bold,
                    )
                    var promoP by remember(item.id) {
                        mutableStateOf(
                            ((promo?.discount ?: 0.0) * 100).roundToInt().toFloat(),
                        )
                    }
                    Slider(
                        value = promoP,
                        onValueChange = { promoP = it },
                        onValueChangeFinished = {
                            vm.game.setPromo(item.id, promoP.roundToInt().toDouble())
                        },
                        valueRange = 0f..Balance.PROMO_MAX_PCT.toFloat(),
                    )
                    Text(
                        if (promoP < 0.5f) "促销：未设置" else "促销 −${promoP.roundToInt()}%"
                                + "（持续 ${Balance.PROMO_DEFAULT_DAYS} 天）",
                        fontSize = 11.sp, color = Theme.Warn,
                    )
                }
            }
        }
    }
}

@Composable
private fun DisplayPanel(vm: GameViewModel) {
    val state = vm.state ?: return
    var selectedSlot by remember { mutableIntStateOf(-1) }
    Column(
        Modifier.fillMaxWidth().verticalScroll(rememberScrollState()).padding(12.dp),
        verticalArrangement = Arrangement.spacedBy(6.dp),
    ) {
        Text("货架陈列（每槽 ${Balance.SLOT_CAPACITY} 件 · ★ 黄金位曝光更高）",
            fontSize = 12.sp, color = Theme.Sub)
        Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
            for (slot in state.slots) {
                val selectedNow = selectedSlot == slot.index
                Column(
                    Modifier
                        .weight(1f)
                        .clip(RoundedCornerShape(9.dp))
                        .background(
                            if (selectedNow) Theme.Select else Theme.PanelDim,
                        )
                        .clickable { selectedSlot = slot.index }
                        .padding(6.dp),
                ) {
                    Text(
                        (if (slot.premium) "★" else "") + "${slot.index + 1}",
                        fontSize = 11.sp, fontWeight = FontWeight.Bold,
                        color = if (slot.premium) Theme.Gold else Theme.Sub,
                    )
                    Text(
                        slot.itemId?.let { Catalog.get(it).name } ?: "（空）",
                        fontSize = 11.sp,
                        color = if (slot.itemId != null) Theme.Text else Theme.Sub,
                    )
                    Text("${slot.qty}/${Balance.SLOT_CAPACITY}", fontSize = 10.sp,
                        color = Theme.Sub)
                }
            }
        }
        Text("仓库（未上架）—— 点「上架」放入选中槽位", fontSize = 12.sp,
            color = Theme.Sub)
        for (item in Catalog.all()) {
            val qty = Inventory.itemWarehouseQty(state, item.id)
            if (qty <= 0) continue
            val batches = state.warehouse.filter { it.itemId == item.id }
            val soonest = batches.minOfOrNull { it.expireDay - state.day }
            Row(
                Modifier.fillMaxWidth().clip(RoundedCornerShape(9.dp))
                    .background(Theme.PanelDim).padding(8.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Column(Modifier.weight(1f)) {
                    Text(item.name, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                    Text(
                        "仓库 $qty 件 · " + (if (soonest != null) "最早到期 剩${soonest}天"
                        else "长期"),
                        fontSize = 10.5.sp, color = Theme.Sub,
                    )
                }
                Text("上架", fontSize = 12.sp, color = Theme.Primary,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier
                        .clip(RoundedCornerShape(7.dp))
                        .background(Theme.PrimarySoft)
                        .clickable {
                            if (selectedSlot >= 0) {
                                vm.game.shelve(selectedSlot, item.id, null)
                                vm.poke()
                            }
                        }
                        .padding(horizontal = 10.dp, vertical = 5.dp))
            }
        }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            androidx.compose.material3.OutlinedButton(
                onClick = {
                    if (selectedSlot >= 0) vm.game.unshelve(selectedSlot, null)
                    vm.poke()
                },
            ) { Text("⬇ 取下选中槽") }
            androidx.compose.material3.OutlinedButton(
                onClick = {
                    for (slot in state.slots) {
                        if (slot.itemId != null) {
                            vm.game.shelve(slot.index, slot.itemId!!, null)
                        }
                    }
                    vm.poke()
                },
            ) { Text("⚡ 一键补满") }
        }
        Text("已选槽位：${if (selectedSlot >= 0) selectedSlot + 1 else "未选择"}",
            fontSize = 11.sp, color = Theme.Sub)
    }
}

@Composable
private fun ReportsPanel(vm: GameViewModel) {
    val state = vm.state ?: return
    Column(
        Modifier.fillMaxWidth().verticalScroll(rememberScrollState()).padding(12.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        Text("近 14 日营收", fontSize = 12.5.sp, fontWeight = FontWeight.Bold)
        RevenueChart(state.ledger.takeLast(14).map { (it["day"] ?: 0.0) to (it["revenue"] ?: 0.0) })
        Text("KPI（今日 / 7 日均值）", fontSize = 12.5.sp, fontWeight = FontWeight.Bold)
        val ledger = state.ledger
        if (ledger.isNotEmpty()) {
            val last = ledger.last()
            val week = ledger.takeLast(7)
            fun wavg(key: String): Double = week.mapNotNull { it[key] }.average()
            val rows = listOf(
                "营收" to (Fmt.money(last["revenue"] ?: 0.0) to Fmt.money(wavg("revenue"))),
                "净利" to (Fmt.signedMoney(last["net"] ?: 0.0) to
                        Fmt.signedMoney(wavg("net"))),
                "转化率" to (Fmt.pct(last["convRate"] ?: 0.0) to
                        Fmt.pct(wavg("convRate"))),
                "客单价" to (Fmt.money(last["aov"] ?: 0.0) to Fmt.money(wavg("aov"))),
                "缺货率" to (Fmt.pct(last["oosRate"] ?: 0.0) to
                        Fmt.pct(wavg("oosRate"))),
                "满意度" to (
                        "${((last["sat"] ?: 0.0)).toInt()}" to
                                "${wavg("sat").toInt()}"),
            )
            for ((kpi, pair) in rows) {
                Row(Modifier.fillMaxWidth()) {
                    Text(kpi, fontSize = 12.sp, color = Theme.Sub,
                        modifier = Modifier.width(60.dp))
                    Text(pair.first, fontSize = 12.sp, fontWeight = FontWeight.Bold,
                        modifier = Modifier.weight(1f))
                    Text(pair.second, fontSize = 12.sp, color = Theme.Sub)
                }
            }
        } else {
            Text("（暂无数据）", fontSize = 12.sp, color = Theme.Sub)
        }
        Text("销售排行（近 7 日）", fontSize = 12.5.sp, fontWeight = FontWeight.Bold)
        val ranks = Catalog.all().map { item ->
            Triple(item.name,
                state.salesHistory[item.id]?.sum() ?: 0,
                Inventory.itemOnShelfQty(state, item.id)
                        + Inventory.itemWarehouseQty(state, item.id))
        }.sortedByDescending { it.second }
        for ((name, total, stock) in ranks) {
            Row(Modifier.fillMaxWidth()) {
                Text(name, fontSize = 12.sp, modifier = Modifier.weight(1f))
                Text("$total 件 · 库存 $stock", fontSize = 12.sp, color = Theme.Sub)
            }
        }
    }
}

@Composable
private fun RevenueChart(data: List<Pair<Double, Double>>) {
    val textMeasurer = androidx.compose.ui.text.rememberTextMeasurer()
    androidx.compose.foundation.Canvas(Modifier.fillMaxWidth().height(140.dp)) {
        if (data.isEmpty()) return@Canvas
        val maxV = data.maxOf { it.second }.coerceAtLeast(1.0)
        val n = data.size
        val gap = size.width / n
        val barW = minOf(34f, gap * 0.6f)
        val baseY = size.height - 22f
        drawLine(Theme.Border, Offset(0f, baseY), Offset(size.width, baseY), 2f)
        data.forEachIndexed { i, (day, v) ->
            val h = (v / maxV * (baseY - 20f)).toFloat()
            val x = i * gap + (gap - barW) / 2
            drawRoundRect(
                Theme.Primary,
                topLeft = Offset(x, baseY - h),
                size = androidx.compose.ui.geometry.Size(barW, h),
                cornerRadius = CornerRadius(6f, 6f),
            )
            drawText(
                textMeasurer = textMeasurer,
                text = "D${day.toInt()}",
                topLeft = Offset(x, baseY + 4f),
                style = TextStyle(fontSize = 9.sp, color = Theme.Sub),
            )
        }
    }
}
