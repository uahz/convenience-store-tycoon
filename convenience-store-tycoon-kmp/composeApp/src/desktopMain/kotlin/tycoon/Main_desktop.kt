package tycoon

import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Window
import androidx.compose.ui.window.application
import androidx.compose.ui.window.rememberWindowState
import tycoon.ui.GameViewModel
import tycoon.ui.TycoonAppRoot

fun main() = application {
    val autoDemo = System.getenv("CTYCOON_DEMO") == "1"
    Window(
        onCloseRequest = ::exitApplication,
        title = "便利店大亨 · Convenience Tycoon",
        state = rememberWindowState(width = 1200.dp, height = 740.dp,
            position = androidx.compose.ui.window.WindowPosition(60.dp, 40.dp)),
    ) {
        val vm = GameViewModel(null)
        if (autoDemo) vm.autoDemo = true
        TycoonAppRoot(vm)
    }
}
