package tycoon

import java.nio.file.Files
import java.nio.file.Path

actual object PlatformIo {
    private fun dir(): Path = Path.of(System.getProperty("user.dir"), "saves")

    actual fun writeTextFile(name: String, content: String): Boolean = runCatching {
        Files.createDirectories(dir())
        val target = dir().resolve("$name.json")
        val tmp = dir().resolve("$name.json.tmp")
        Files.writeString(tmp, content)
        Files.move(tmp, target, java.nio.file.StandardCopyOption.REPLACE_EXISTING)
        true
    }.getOrDefault(false)

    actual fun readTextFile(name: String): String? = runCatching {
        Files.readString(dir().resolve("$name.json"))
    }.getOrNull()

    actual fun deleteFile(name: String) {
        runCatching { Files.deleteIfExists(dir().resolve("$name.json")) }
    }
}
