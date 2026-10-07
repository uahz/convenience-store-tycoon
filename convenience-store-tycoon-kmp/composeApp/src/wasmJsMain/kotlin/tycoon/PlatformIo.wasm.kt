package tycoon

import kotlinx.browser.window

/** 网页平台 IO：localStorage。 */
actual object PlatformIo {
    private const val PREFIX = "ctycoon_"

    actual fun writeTextFile(name: String, content: String): Boolean = try {
        window.localStorage.setItem(PREFIX + name, content)
        true
    } catch (e: Throwable) {
        false
    }

    actual fun readTextFile(name: String): String? =
        window.localStorage.getItem(PREFIX + name)

    actual fun deleteFile(name: String) {
        window.localStorage.removeItem(PREFIX + name)
    }
}
