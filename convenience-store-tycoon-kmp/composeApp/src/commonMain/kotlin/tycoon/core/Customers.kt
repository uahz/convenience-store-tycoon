package tycoon.core

/** 顾客原型（纯数据）。needs 落到具体商品，避免品类内永远挑最便宜。 */
data class Archetype(
    val id: String,
    val name: String,
    val share: Double,
    val hourWeights: Map<Int, Double>,
    val itemPreferences: Map<String, Double>,
    val budgetRange: ClosedFloatingPointRange<Double>,
    val patienceRange: IntRange,
    val promoSensitivity: Double,
    val initialLoyalty: Double,
)

object Archetypes {
    val ALL: List<Archetype> = listOf(
        Archetype(
            "office", "上班族", 0.45,
            mapOf(8 to 2.0, 9 to 1.6, 12 to 1.6, 13 to 1.2, 18 to 1.4, 19 to 1.2),
            mapOf("cola" to 0.24, "juice" to 0.16, "sandwich" to 0.22,
                  "bread" to 0.16, "noodles" to 0.10, "water" to 0.12),
            18.0..26.0, 4..6, 0.25, 0.35,
        ),
        Archetype(
            "student", "学生", 0.30,
            mapOf(15 to 1.6, 16 to 1.8, 17 to 1.6, 18 to 1.5, 19 to 1.3, 21 to 1.3),
            mapOf("cookie" to 0.30, "gum" to 0.18, "cola" to 0.22,
                  "noodles" to 0.16, "water" to 0.14),
            10.0..18.0, 3..5, 0.45, 0.25,
        ),
        Archetype(
            "senior", "银发族", 0.25,
            mapOf(8 to 1.8, 9 to 1.5, 10 to 1.3),
            mapOf("tissue" to 0.28, "juice" to 0.18, "bread" to 0.20,
                  "water" to 0.20, "noodles" to 0.14),
            8.0..20.0, 6..9, 0.15, 0.50,
        ),
    )

    fun byId(id: String): Archetype = ALL.first { it.id == id }
}
