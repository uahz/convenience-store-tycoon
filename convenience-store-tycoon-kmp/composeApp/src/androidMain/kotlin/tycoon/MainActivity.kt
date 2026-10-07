package tycoon

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import tycoon.ui.GameViewModel
import tycoon.ui.TycoonAppRoot

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        PlatformIo.init(this)
        setContent {
            TycoonAppRoot(GameViewModel(null))
        }
    }
}
