package tycoon.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import tycoon.core.Balance
import tycoon.core.Catalog
import tycoon.core.Difficulties
import tycoon.core.DayReport
import tycoon.util.Fmt

@Composable
fun SettlementDialog(vm: GameViewModel, report: DayReport) {
    Dialog(onDismissRequest = { vm.afterSettlement() }) {
        Column(
            Modifier
                .clip(RoundedCornerShape(18.dp))
                .background(Theme.Panel)
                .padding(22.dp)
                .width(480.dp),
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    "每日结算 · 第 ${report.day} 天 [${report.weekday}]",
                    fontSize = 17.sp, fontWeight = FontWeight.Bold,
                    modifier = Modifier.weight(1f),
                )
                Text(
                    if (report.net >= 0) "盈利" else "亏损",
                    color = if (report.net >= 0) Theme.Good else Theme.Bad,
                    fontSize = 13.sp, fontWeight = FontWeight.Bold,
                )
            }
            Spacer(Modifier.height(10.dp))

            @Composable
            fun pl(label: String, value: String, color: Color = Theme.Text,
                   big: Boolean = false, bold: Boolean = false,
                   dim: Boolean = false) {
                Row(
                    Modifier.fillMaxWidth().padding(vertical = 4.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Text(label, fontSize = if (big) 13.sp else 12.sp,
                        color = when {
                            bold -> Theme.Text
                            dim -> Theme.Sub
                            else -> Theme.Text
                        },
                        fontWeight = if (big || bold) FontWeight.Bold
                        else FontWeight.Normal,
                        modifier = Modifier.weight(1f))
                    Text(value, fontSize = if (big) 20.sp else 12.sp,
                        fontWeight = if (big || bold) FontWeight.Bold
                        else FontWeight.Normal,
                        color = color)
                }
            }
            pl("营收（${report.conversions} 单 / 进店 ${report.traffic} 人）",
                Fmt.signedMoney(report.revenue), bold = true)
            pl("售出成本", Fmt.signedMoney(-report.cogs), dim = true)
            if (report.spoilage > 0) {
                val names = report.spoilageItems.joinToString("、") { (id, q) ->
                    "${Catalog.get(id).name}×$q"
                }
                pl("报废损失（$names）", Fmt.signedMoney(-report.spoilage),
                    Theme.Bad, dim = true)
            }
            pl("房租", Fmt.signedMoney(-report.rent), dim = true)
            pl("水电", Fmt.signedMoney(-report.utilities), dim = true)
            Spacer(Modifier.height(6.dp))
            pl("今日净利", Fmt.signedMoney(report.net),
                if (report.net >= 0) Theme.Good else Theme.Bad, big = true)

            Spacer(Modifier.height(10.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                Chip("转化率 ${Fmt.pct(report.conversionRate)}")
                Chip("客单价 ${Fmt.money(report.aov)}")
                Chip("缺货率 ${Fmt.pct(report.oosRate)}")
                Chip("周转 ${Fmt.formatDecimal(report.turnover, 2)}")
                Chip("报废率 ${Fmt.pct(report.wasteRate)}")
            }
            Spacer(Modifier.height(8.dp))
            Text(
                "满意度 ${if (report.satAvg > 0) Fmt.formatDecimal(report.satAvg, 0) else "—"}"
                        + " · 声望 ${Fmt.formatDecimal(report.repBefore, 0)} → "
                        + "${Fmt.formatDecimal(report.repAfter, 0)} "
                        + Fmt.stars(report.repAfter),
                fontSize = 12.sp, color = Theme.Sub,
            )
            if (report.abandonRate > Balance.QUEUE_PENALTY_RATE ||
                report.lostAtClose > 0
            ) {
                Spacer(Modifier.height(4.dp))
                Text(
                    "⚠ 排队流失 ${report.abandons} 人，打烊滞留 ${report.lostAtClose} 人"
                            + " → 优化高峰备货",
                    fontSize = 12.sp, color = Theme.Warn,
                )
            }
            if (report.victory) {
                Spacer(Modifier.height(4.dp))
                Text("🏆 达成胜利目标！", fontSize = 15.sp, color = Theme.Good,
                    fontWeight = FontWeight.Bold)
            }
            if (report.bankrupt) {
                Spacer(Modifier.height(4.dp))
                Text("✖ 现金枯竭，门店破产清算……", fontSize = 15.sp, color = Theme.Bad,
                    fontWeight = FontWeight.Bold)
            }
            Spacer(Modifier.height(14.dp))
            Row(horizontalArrangement = Arrangement.End, modifier = Modifier.fillMaxWidth()) {
                Button(
                    onClick = { vm.afterSettlement() },
                    colors = ButtonDefaults.buttonColors(containerColor = Theme.Primary),
                ) {
                    Text(
                        if (report.victory || report.bankrupt) "返回主菜单"
                        else "开始第 ${report.day + 1} 天 →",
                    )
                }
            }
        }
    }
}

@Composable
fun Chip(text: String) {
    Text(
        text,
        fontSize = 11.sp,
        color = Theme.Text,
        modifier = Modifier
            .clip(RoundedCornerShape(7.dp))
            .background(Theme.Select)
            .padding(horizontal = 8.dp, vertical = 3.dp),
    )
}

@Composable
fun DifficultyDialog(vm: GameViewModel) {
    Dialog(onDismissRequest = { vm.difficultyDialog = false }) {
        Column(
            Modifier
                .clip(RoundedCornerShape(18.dp))
                .background(Theme.Panel)
                .padding(22.dp)
                .width(460.dp),
        ) {
            Text("选择难度", fontSize = 17.sp, fontWeight = FontWeight.Bold)
            Text("三种开局强度，胜利线与经营压力不同", fontSize = 12.sp,
                color = Theme.Sub)
            Spacer(Modifier.height(12.dp))
            for ((key, preset) in Difficulties.ALL) {
                Button(
                    onClick = {
                        vm.difficultyDialog = false
                        vm.startNewGame(key)
                    },
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Theme.Primary),
                    modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
                ) {
                    Column(Modifier.fillMaxWidth()) {
                        Text(preset.label, fontWeight = FontWeight.Bold)
                        Text(
                            "初始资金 ${Fmt.money(preset.cash)} · 客流 ×" +
                                    Fmt.formatDecimal(preset.trafficMult, 2) +
                                    " · 房租 ×" +
                                    Fmt.formatDecimal(preset.rentMult, 2) +
                                    " · 胜利线 ${Fmt.money(preset.victoryNetWorth)}",
                            fontSize = 11.sp,
                        )
                    }
                }
            }
            Spacer(Modifier.height(8.dp))
            Button(
                onClick = { vm.difficultyDialog = false },
                colors = ButtonDefaults.buttonColors(containerColor = Theme.PanelDim),
                modifier = Modifier.fillMaxWidth(),
            ) { Text("返回", color = Theme.Text) }
        }
    }
}

@Composable
fun HelpDialog(vm: GameViewModel) {
    Dialog(onDismissRequest = { vm.showHelp = false }) {
        Column(
            Modifier
                .clip(RoundedCornerShape(18.dp))
                .background(Theme.Panel)
                .padding(22.dp)
                .width(520.dp),
        ) {
            Text("玩法说明", fontSize = 17.sp, fontWeight = FontWeight.Bold)
            Spacer(Modifier.height(8.dp))
            Text(
                "目标：滚动经营，净资产达到难度胜利线即胜利；结算后现金为负即破产。\n\n" +
                        "一天循环：\n" +
                        "  1. 备货（时间暂停）：进货订货 → 定价/促销 → 货架陈列\n" +
                        "  2. 开门营业：时间流动，顾客实时进店选购、排队结账\n" +
                        "  3. 营业中随时切侧栏补货/改价/促销（想从容操作就先暂停）\n" +
                        "  4. 24:00 打烊 → 结算单 → 开始下一天\n\n" +
                        "关键规则：\n" +
                        "  · 售价贴近参考价好卖；远高于参考价（>1.25×）明显赶客\n" +
                        "  · 保质期：到期批次晨间自动报废（报纸 1 天、面包 3 天！）\n" +
                        "  · 缺货：顾客买不到会不满离开，连续缺货拉低声望\n" +
                        "  · 黄金位（1、4 号槽）曝光更高，放高周转商品\n" +
                        "  · 排队过长顾客会放弃购买 → 高峰期前把畅销品备足\n\n" +
                        "所有数值都可在 config 中调整（见 README 参数表）。",
                fontSize = 12.sp, lineHeight = 19.sp,
            )
            Spacer(Modifier.height(12.dp))
            Button(
                onClick = { vm.showHelp = false },
                colors = ButtonDefaults.buttonColors(containerColor = Theme.Primary),
                modifier = Modifier.align(Alignment.End),
            ) { Text("知道了") }
        }
    }
}
