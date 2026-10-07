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
        // 崩溃自诊断：上次启动的异常堆栈写入本地，供界面显示
        val previousCrash = PlatformIo.readTextFile("crash")
        PlatformIo.deleteFile("crash")
        Thread.setDefaultUncaughtExceptionHandler { _, e ->
            val sb = StringBuilder()
            sb.append(e.javaClass.name).append(": ").append(e.message).append('\n')
            for (frame in e.stackTrace.take(30)) {
                sb.append("  at ").append(frame.toString()).append('\n')
            }
            e.cause?.let { c ->
                sb.append("Caused by: ").append(c.javaClass.name).append(": ")
                    .append(c.message).append('\n')
                for (frame in c.stackTrace.take(15)) {
                    sb.append("  at ").append(frame.toString()).append('\n')
                }
            }
            PlatformIo.writeTextFile("crash", sb.toString())
        }
        setContent {
            TycoonAppRoot(GameViewModel(null), previousCrash)
        }
    }
}
