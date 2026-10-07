package tycoon

/** 平台 IO：存档目录随平台不同（桌面=exe 旁、安卓=filesDir、网页=localStorage）。 */
expect object PlatformIo {
    fun writeTextFile(name: String, content: String): Boolean
    fun readTextFile(name: String): String?
    fun deleteFile(name: String)
}
