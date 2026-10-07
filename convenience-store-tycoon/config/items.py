"""商品目录（纯数据，M0 共 10 种、全部常温存储；冷藏品类与设备留给 M1）。

字段：id、名称、品类、进价、参考价、保质期(天)、存储条件、最小进货箱规、
品类热度、价格弹性、供应商列表。
"""

ITEMS = [
    dict(id="water", name="矿泉水", category="饮料", unit_cost=1.0, ref_price=2.0,
         shelf_life_days=180, storage="常温", case_size=24, popularity=0.95,
         elasticity=1.1, suppliers=("标准供货",)),
    dict(id="cola", name="可乐", category="饮料", unit_cost=1.8, ref_price=3.5,
         shelf_life_days=180, storage="常温", case_size=24, popularity=0.90,
         elasticity=1.2, suppliers=("标准供货",)),
    dict(id="juice", name="鲜榨果汁1L", category="饮料", unit_cost=3.0, ref_price=6.0,
         shelf_life_days=7, storage="常温", case_size=6, popularity=0.55,
         elasticity=1.3, suppliers=("标准供货",)),
    dict(id="noodles", name="红烧牛肉面", category="方便食品", unit_cost=2.2, ref_price=4.0,
         shelf_life_days=180, storage="常温", case_size=12, popularity=0.85,
         elasticity=0.9, suppliers=("标准供货",)),
    dict(id="bread", name="全麦面包", category="烘焙", unit_cost=2.5, ref_price=4.5,
         shelf_life_days=3, storage="常温", case_size=6, popularity=0.70,
         elasticity=1.0, suppliers=("标准供货",)),
    dict(id="sandwich", name="金枪鱼三明治", category="烘焙", unit_cost=4.5, ref_price=9.0,
         shelf_life_days=2, storage="常温", case_size=6, popularity=0.60,
         elasticity=1.1, suppliers=("标准供货",)),
    dict(id="cookie", name="曲奇饼干", category="零食", unit_cost=2.8, ref_price=5.5,
         shelf_life_days=120, storage="常温", case_size=10, popularity=0.60,
         elasticity=0.9, suppliers=("标准供货",)),
    dict(id="gum", name="薄荷口香糖", category="零食", unit_cost=1.2, ref_price=3.0,
         shelf_life_days=365, storage="常温", case_size=20, popularity=0.50,
         elasticity=0.8, suppliers=("标准供货",)),
    dict(id="paper", name="城市晚报", category="报刊", unit_cost=0.8, ref_price=2.0,
         shelf_life_days=1, storage="常温", case_size=10, popularity=0.40,
         elasticity=1.4, suppliers=("标准供货",)),
    dict(id="tissue", name="抽纸", category="日用品", unit_cost=2.0, ref_price=4.5,
         shelf_life_days=999, storage="常温", case_size=20, popularity=0.55,
         elasticity=0.7, suppliers=("标准供货",)),
]
