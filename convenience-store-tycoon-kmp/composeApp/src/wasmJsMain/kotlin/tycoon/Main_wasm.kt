@file:OptIn(androidx.compose.ui.ExperimentalComposeUiApi::class)

package tycoon

import androidx.compose.ui.window.CanvasBasedWindow
import tycoon.ui.GameViewModel
import tycoon.ui.TycoonAppRoot

fun main() {
    CanvasBasedWindow(title = "便利店大亨 · Convenience Tycoon",
        canvasElementId = "ComposeTarget") {
        TycoonAppRoot(GameViewModel(null))
    }
}
