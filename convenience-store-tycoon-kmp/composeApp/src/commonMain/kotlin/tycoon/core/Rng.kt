package tycoon.core

import kotlin.math.exp
import kotlin.random.Random

/** 可播种、可复现的随机源（对应终端版的 GameRNG）。 */
class GameRng(seed: Long?) {
    val random: Random = if (seed != null) Random(seed) else Random.Default

    fun next(): Double = random.nextDouble()

    /** 含两端，等价 Python randint。 */
    fun randInt(a: Int, b: Int): Int = a + random.nextInt(b - a + 1)

    fun uniform(a: Double, b: Double): Double = a + (b - a) * random.nextDouble()

    fun <T> choice(seq: List<T>): T = seq[random.nextInt(seq.size)]

    fun <T> weighted(pairs: List<Pair<T, Double>>): T {
        val total = pairs.sumOf { it.second }
        var roll = random.nextDouble() * total
        for ((value, w) in pairs) {
            roll -= w
            if (roll <= 0) return value
        }
        return pairs.last().first
    }

    /** Knuth 泊松采样。 */
    fun poisson(lam: Double): Int {
        val threshold = exp(-lam)
        var k = 0
        var p = 1.0
        while (true) {
            p *= random.nextDouble()
            if (p <= threshold) return k
            k += 1
        }
    }
}
