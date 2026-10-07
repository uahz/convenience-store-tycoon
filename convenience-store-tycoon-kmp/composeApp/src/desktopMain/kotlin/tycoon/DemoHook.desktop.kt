package tycoon.ui

import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import kotlinx.coroutines.delay
import java.awt.Rectangle
import java.awt.Robot
import java.awt.Window
import javax.imageio.ImageIO

/** 桌面端演示钩子：自动完成进货→上架→开门→数小时营业，并自截窗口画面。 */
@Composable
actual fun DemoHook(vm: GameViewModel) {
    if (!vm.autoDemo) return
    LaunchedEffect(Unit) {
        delay(2000)
        vm.startNewGame("normal")
        vm.game.confirmOrder(
            mapOf("cola" to 3, "water" to 2, "noodles" to 2,
                "bread" to 2, "juice" to 3, "sandwich" to 3),
        )
        listOf(0 to "cola", 3 to "water", 2 to "noodles",
            1 to "bread", 4 to "juice", 5 to "sandwich",
        ).forEach { (slot, item) -> vm.game.shelve(slot, item, null) }
        vm.poke()
        delay(800)
        vm.openStore()
        repeat(5) {
            delay(vm.hourIntervalMs())
            vm.tickHour()
        }
        delay(1200)
        runCatching {
            val win = Window.getWindows().firstOrNull() ?: return@runCatching
            // 抬到最上层避免被遮挡（约 1 秒），截完还原
            win.isAlwaysOnTop = true
            delay(700)
            val bounds = win.bounds
            val img = Robot().createScreenCapture(
                Rectangle(bounds.x, bounds.y, bounds.width, bounds.height),
            )
            win.isAlwaysOnTop = false
            ImageIO.write(img, "png", java.io.File("demo_open.png"))
        }
        // 切到进货页签再截一张（实证面板渲染）
        delay(600)
        vm.sidebarTab = 1
        runCatching {
            val win = Window.getWindows().firstOrNull() ?: return@runCatching
            win.isAlwaysOnTop = true
            delay(700)
            val bounds = win.bounds
            val img = Robot().createScreenCapture(
                Rectangle(bounds.x, bounds.y, bounds.width, bounds.height),
            )
            win.isAlwaysOnTop = false
            ImageIO.write(img, "png", java.io.File("demo_buy.png"))
        }
        delay(400)
        runCatching {
            Window.getWindows().forEach { it.dispose() }
        }
    }
}
