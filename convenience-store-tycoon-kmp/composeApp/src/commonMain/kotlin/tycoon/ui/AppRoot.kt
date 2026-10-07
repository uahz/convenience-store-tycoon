package tycoon.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ExitToApp
import androidx.compose.material.icons.filled.FastForward
import androidx.compose.material.icons.filled.Pause
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Save
import androidx.compose.material.icons.filled.Storefront
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.delay
import tycoon.core.Balance
import tycoon.core.Difficulties
import tycoon.core.Economy
import tycoon.core.Savegame
import tycoon.util.Fmt

@Composable
fun TycoonAppRoot(vm: GameViewModel, previousCrash: String? = null) {
    if (previousCrash != null && vm.crashText == null) {
        vm.crashText = previousCrash
    }
    MaterialTheme(
        colorScheme = MaterialTheme.colorScheme.copy(
            primary = Theme.Primary,
            background = Theme.Bg,
        ),
    ) {
        // 小时节拍：营业中按流速每 interval 推进一小时
        LaunchedEffect(vm.phase, vm.speed) {
            while (vm.phase == "open" && vm.speed != "pause") {
                delay(vm.hourIntervalMs())
                vm.tickHour()
            }
        }
        DemoHook(vm)
        Column(
            Modifier
                .fillMaxSize()
                .background(Theme.Bg),
        ) {
            TopBar(vm)
            when (vm.phase) {
                "menu" -> MenuScreen(vm)
                else -> Row(
                    Modifier.fillMaxSize().padding(10.dp),
                    horizontalArrangement = Arrangement.spacedBy(10.dp),
                ) {
                    FloorCanvas(
                        vm,
                        Modifier
                            .weight(1.55f)
                            .fillMaxSize()
                            .clip(RoundedCornerShape(12.dp)),
                    )
                    Sidebar(
                        vm,
                        Modifier
                            .width(400.dp)
                            .fillMaxSize()
                            .clip(RoundedCornerShape(14.dp)),
                    )
                }
            }
        }
        if (vm.phase == "settle") {
            vm.settlementReport?.let { SettlementDialog(vm, it) }
        }
        if (vm.difficultyDialog) DifficultyDialog(vm)
        if (vm.showHelp) HelpDialog(vm)
    }
}

@Composable
private fun TopBar(vm: GameViewModel) {
    val state = vm.state
    Row(
        Modifier
            .fillMaxWidth()
            .background(Theme.PrimaryDeep)
            .padding(horizontal = 16.dp, vertical = 9.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Icon(Icons.Filled.Storefront, null, tint = Color.White,
            modifier = Modifier.size(20.dp))
        Spacer(Modifier.width(8.dp))
        Text(
            state?.let { "第 ${it.day} 天 [${Balance.DAY_NAMES[(it.day - 1) % 7]}]" }
                ?: "便利店大亨",
            color = Color.White, fontWeight = FontWeight.Bold, fontSize = 14.sp,
        )
        Spacer(Modifier.width(14.dp))
        if (vm.phase == "open") {
            SpeedButton(vm, "pause", Icons.Filled.Pause, "暂停")
            SpeedButton(vm, "1x", Icons.Filled.PlayArrow, "1×")
            SpeedButton(vm, "2x", Icons.Filled.FastForward, "2×")
            SpeedButton(vm, "4x", Icons.Filled.FastForward, "4×")
        }
        Spacer(Modifier.weight(1f))
        if (state != null) {
            TopChip("💵 现金 " + Fmt.money(state.cash))
            Spacer(Modifier.width(8.dp))
            TopChip("声望 " + Fmt.stars(state.reputation) + " " +
                    Fmt.formatDecimal(state.reputation, 0))
            Spacer(Modifier.width(8.dp))
            TopChip("净资产 " + Fmt.money(Economy.netWorth(state)))
            Spacer(Modifier.width(8.dp))
            TopChip("目标 " + Fmt.money(
                Difficulties.ALL.getValue(state.difficulty).victoryNetWorth,
            ))
        }
    }
}

@Composable
private fun SpeedButton(vm: GameViewModel, key: String,
                        icon: androidx.compose.ui.graphics.vector.ImageVector,
                        label: String) {
    val selected = vm.speed == key
    Button(
        onClick = { vm.speed = key },
        colors = ButtonDefaults.buttonColors(
            containerColor = if (selected) Theme.Amber else Color(0x33FFFFFF),
            contentColor = if (selected) Theme.PrimaryDeep else Color.White,
        ),
        contentPadding = androidx.compose.foundation.layout.PaddingValues(
            horizontal = 10.dp, vertical = 2.dp),
        modifier = Modifier.padding(horizontal = 3.dp).height(30.dp),
    ) {
        Icon(icon, null, modifier = Modifier.size(13.dp))
        Spacer(Modifier.width(3.dp))
        Text(label, fontSize = 11.sp, fontWeight = FontWeight.Bold)
    }
}

@Composable
private fun TopChip(text: String) {
    Text(
        text,
        color = Color.White, fontSize = 12.sp,
        modifier = Modifier
            .clip(RoundedCornerShape(8.dp))
            .background(Color(0x26FFFFFF))
            .padding(horizontal = 10.dp, vertical = 5.dp),
    )
}

@Composable
private fun MenuScreen(vm: GameViewModel) {
    Box(
        Modifier.fillMaxSize().background(Theme.Bg),
        contentAlignment = Alignment.Center,
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            vm.crashText?.let { crash ->
                Column(
                    Modifier
                        .width(560.dp)
                        .clip(RoundedCornerShape(12.dp))
                        .background(Color(0xFFFDECEB))
                        .padding(12.dp),
                ) {
                    Text("⚠ 上次启动异常（请将以下内容截图反馈）",
                        fontSize = 12.sp, fontWeight = FontWeight.Bold,
                        color = Theme.Bad)
                    Text(
                        crash.take(1200),
                        fontSize = 10.sp, color = Theme.Bad,
                        lineHeight = 14.sp,
                        modifier = Modifier.padding(top = 6.dp),
                    )
                }
                Spacer(Modifier.height(16.dp))
            }
            Icon(
                Icons.Filled.Storefront, null,
                tint = Theme.Primary, modifier = Modifier.size(56.dp),
            )
            Text("便 利 店 大 亨", fontSize = 30.sp, fontWeight = FontWeight.Bold,
                modifier = Modifier.padding(top = 8.dp))
            Text("街角生意 · 日进斗金 —— 实时经营模拟", fontSize = 13.sp,
                color = Theme.Sub, modifier = Modifier.padding(top = 4.dp))
            Spacer(Modifier.height(30.dp))
            Button(
                onClick = { vm.difficultyDialog = true },
                colors = ButtonDefaults.buttonColors(containerColor = Theme.Primary),
                modifier = Modifier.width(260.dp).height(46.dp),
            ) {
                Text("▶ 开始新游戏", fontSize = 15.sp)
            }
            Spacer(Modifier.height(10.dp))
            Button(
                onClick = {
                    val err = vm.continueGame()
                    if (err != null) vm.appendLog(err, "bad")
                },
                colors = ButtonDefaults.buttonColors(containerColor = Theme.Panel),
                modifier = Modifier.width(260.dp).height(46.dp),
            ) {
                Icon(Icons.Filled.Save, null, modifier = Modifier.size(16.dp))
                Spacer(Modifier.width(6.dp))
                Text("继续游戏（自动存档）", fontSize = 14.sp, color = Theme.Text)
            }
            Spacer(Modifier.height(10.dp))
            Button(
                onClick = { vm.showHelp = true },
                colors = ButtonDefaults.buttonColors(containerColor = Theme.Panel),
                modifier = Modifier.width(260.dp).height(46.dp),
            ) {
                Text("📖 玩法说明", fontSize = 14.sp, color = Theme.Text)
            }
            Spacer(Modifier.height(10.dp))
            Button(
                onClick = { vm.appendLog("演示版请直接关闭窗口退出", "dim") },
                colors = ButtonDefaults.buttonColors(containerColor = Theme.Panel),
                modifier = Modifier.width(260.dp).height(46.dp),
            ) {
                Icon(Icons.Filled.ExitToApp, null, modifier = Modifier.size(16.dp),
                    tint = Theme.Bad)
                Spacer(Modifier.width(6.dp))
                Text("✕ 退出", fontSize = 14.sp, color = Theme.Bad)
            }
            Spacer(Modifier.height(18.dp))
            Text("存档位于程序目录 saves/ 下", fontSize = 11.sp, color = Theme.Sub)
        }
    }
}
