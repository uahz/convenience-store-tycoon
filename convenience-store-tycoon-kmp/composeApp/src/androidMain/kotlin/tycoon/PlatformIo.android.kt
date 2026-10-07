package tycoon

import android.content.Context

/** 安卓平台 IO：写入应用私有目录 filesDir/saves/。 */
actual object PlatformIo {
    private var context: Context? = null

    fun init(ctx: Context) {
        context = ctx.applicationContext
    }

    private fun dir(): java.io.File {
        val d = java.io.File(context!!.filesDir, "saves")
        if (!d.exists()) d.mkdirs()
        return d
    }

    actual fun writeTextFile(name: String, content: String): Boolean = runCatching {
        val tmp = java.io.File(dir(), "$name.json.tmp")
        tmp.writeText(content, Charsets.UTF_8)
        val target = java.io.File(dir(), "$name.json")
        if (!tmp.renameTo(target)) {
            target.writeText(content, Charsets.UTF_8)
            tmp.delete()
        }
        true
    }.getOrDefault(false)

    actual fun readTextFile(name: String): String? = runCatching {
        val f = java.io.File(dir(), "$name.json")
        if (f.exists()) f.readText(Charsets.UTF_8) else null
    }.getOrNull()

    actual fun deleteFile(name: String) {
        java.io.File(dir(), "$name.json").delete()
    }
}
