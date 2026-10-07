"""顾客原型（纯数据）。M0 实现三类；字段与 DESIGN.md §2.2.1 对应。

hour_weights：该原型在各小时的到访倾向倍率（未列出 = 1.0）。
item_preferences：购物篮需求的商品级抽取权重（需求落到具体商品，
避免"品类内永远挑最便宜"导致客单价塌陷）。
"""

ARCHETYPES = [
    dict(id="office", name="上班族", share=0.45,
         hour_weights={8: 2.0, 9: 1.6, 12: 1.6, 13: 1.2, 18: 1.4, 19: 1.2},
         item_preferences={"cola": 0.24, "juice": 0.16, "sandwich": 0.22,
                           "bread": 0.16, "noodles": 0.10, "water": 0.12},
         budget_range=(18.0, 26.0), patience_range=(4, 6),
         promo_sensitivity=0.25, initial_loyalty=0.35),
    dict(id="student", name="学生", share=0.30,
         hour_weights={15: 1.6, 16: 1.8, 17: 1.6, 18: 1.5, 19: 1.3, 21: 1.3},
         item_preferences={"cookie": 0.30, "gum": 0.18, "cola": 0.22,
                           "noodles": 0.16, "water": 0.14},
         budget_range=(10.0, 18.0), patience_range=(3, 5),
         promo_sensitivity=0.45, initial_loyalty=0.25),
    dict(id="senior", name="银发族", share=0.25,
         hour_weights={8: 1.8, 9: 1.5, 10: 1.3},
         item_preferences={"tissue": 0.28, "juice": 0.18, "bread": 0.20,
                           "water": 0.20, "noodles": 0.14},
         budget_range=(8.0, 20.0), patience_range=(6, 9),
         promo_sensitivity=0.15, initial_loyalty=0.50),
]
