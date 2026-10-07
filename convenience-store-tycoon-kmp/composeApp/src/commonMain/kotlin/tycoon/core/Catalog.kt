package tycoon.core

import kotlinx.serialization.Serializable

@Serializable
data class ItemDef(
    val id: String,
    val name: String,
    val category: String,
    val unitCost: Double,
    val refPrice: Double,
    val shelfLifeDays: Int,
    val storage: String,
    val caseSize: Int,
    val popularity: Double,
    val elasticity: Double,
)

object Catalog {
    val ITEMS: List<ItemDef> = listOf(
        ItemDef("water", "矿泉水", "饮料", 1.0, 2.0, 180, "常温", 24, 0.95, 1.1),
        ItemDef("cola", "可乐", "饮料", 1.8, 3.5, 180, "常温", 24, 0.90, 1.2),
        ItemDef("juice", "鲜榨果汁1L", "饮料", 3.0, 6.0, 7, "常温", 6, 0.55, 1.3),
        ItemDef("noodles", "红烧牛肉面", "方便食品", 2.2, 4.0, 180, "常温", 12, 0.85, 0.9),
        ItemDef("bread", "全麦面包", "烘焙", 2.5, 4.5, 3, "常温", 6, 0.70, 1.0),
        ItemDef("sandwich", "金枪鱼三明治", "烘焙", 4.5, 9.0, 2, "常温", 6, 0.60, 1.1),
        ItemDef("cookie", "曲奇饼干", "零食", 2.8, 5.5, 120, "常温", 10, 0.60, 0.9),
        ItemDef("gum", "薄荷口香糖", "零食", 1.2, 3.0, 365, "常温", 20, 0.50, 0.8),
        ItemDef("paper", "城市晚报", "报刊", 0.8, 2.0, 1, "常温", 10, 0.40, 1.4),
        ItemDef("tissue", "抽纸", "日用品", 2.0, 4.5, 999, "常温", 20, 0.55, 0.7),
    )
    val BY_ID: Map<String, ItemDef> = ITEMS.associateBy { it.id }
    val CATEGORIES: List<String> = ITEMS.map { it.category }.distinct().sorted()

    fun get(itemId: String): ItemDef = BY_ID.getValue(itemId)
    fun all(): List<ItemDef> = ITEMS
}
