package tycoon.util

import kotlin.math.abs
import kotlin.math.pow
import kotlin.math.roundToLong

/** 与区域设置无关的数字/货币格式化（commonMain 可用，不依赖 java.text）。 */
object Fmt {
    fun money(v: Double): String {
        val neg = v < 0
        val a = abs(v)
        val text = if (a - a.toLong().toDouble() < 0.005) {
            group(a.toLong().toString())
        } else {
            val intPart = a.toLong()
            val frac = ((a - intPart) * 100).roundToLong().toString()
                .padStart(2, '0')
            group(intPart.toString()) + "." + frac
        }
        return (if (neg) "-¥" else "¥") + text
    }

    fun signedMoney(v: Double): String =
        (if (v >= 0) "+" else "-") + money(abs(v))

    fun pct(v: Double, digits: Int = 1): String =
        formatDecimal(v * 100, digits) + "%"

    fun formatDecimal(v: Double, digits: Int): String {
        val factor = 10.0.pow(digits)
        val rounded = (v * factor).roundToLong()
        val scaled = if (rounded < 0) -rounded else rounded
        val intPart = scaled / factor.toLong()
        var frac = (scaled % factor.toLong()).toString()
        while (frac.length < digits) frac = "0$frac"
        val sign = if (rounded < 0) "-" else ""
        return sign + group(intPart.toString()) +
                (if (digits > 0) "." + frac else "")
    }

    private fun group(digits: String): String {
        val sb = StringBuilder()
        var count = 0
        for (i in digits.length - 1 downTo 0) {
            sb.append(digits[i])
            count += 1
            if (count % 3 == 0 && i > 0) sb.append(',')
        }
        return sb.reverse().toString()
    }

    fun stars(rep: Double): String {
        val filled = (rep / 20).toInt().coerceIn(0, 5)
        return "★".repeat(filled) + "☆".repeat(5 - filled)
    }
}
