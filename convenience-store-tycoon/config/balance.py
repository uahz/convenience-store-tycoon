"""全局平衡数值（唯一数值来源，逻辑代码禁止出现魔法数字）。

单位约定：金额=元；时间=小时/分钟；概率与比率=0~1。
每个常量注释说明"调大/调小"的经营后果，便于调参。
"""

from dataclasses import dataclass

# ---------- 营业时间 ----------
DAY_START_HOUR = 8                 # 开门时刻（含）
DAY_END_HOUR = 24                  # 打烊时刻（不含）
DAY_NAMES = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

# ---------- 客流 ----------
TRAFFIC_BASE_WEEKDAY = 460.0       # 工作日路过人流基数；调大→整体客流量上升
TRAFFIC_BASE_WEEKEND = 575.0       # 周末路过人流基数
WEEKEND_DAYS = (5, 6)              # DAY_NAMES 索引：周六/周日
BASE_ENTER_RATE = 0.38             # 基准进店率系数（attractiveness=0.5、忠诚度中位时约 0.27）
PEAK_WEIGHTS = {8: 1.8, 9: 1.5, 12: 1.5, 13: 1.2, 15: 1.2, 16: 1.4,
                17: 1.5, 18: 1.6, 19: 1.4, 21: 1.3, 22: 1.2}   # 各小时客流倍率，未列出=1.0
ATTRACT_WEIGHTS = {"reputation": 0.40, "display": 0.25,
                   "promo": 0.20, "assortment": 0.15}           # 门店吸引力合成权重
PREMIUM_SLOT_WEIGHT = 1.5          # 黄金位在陈列指数中的权重；调大→黄金位更值钱
PROMO_STRENGTH_SCALE = 2.0         # 促销力度 = 在售商品平均折扣 × 该系数

# ---------- 财务 ----------
INITIAL_CASH = 20000.0             # 初始资金
RENT_PER_DAY = 250.0               # Lv1 日房租
UTILITY_BASE = 30.0                # 水电基数
UTILITY_RATE = 0.015               # 水电浮动部分 = 营收 × 比例
VICTORY_NET_WORTH = 200000.0       # 普通难度胜利净资产
BANKRUPTCY_CASH = 0.0              # 结算后现金低于该值 → 破产

# ---------- 门店容量（Lv1） ----------
SHELF_SLOTS = 6                    # 货架槽位数
SLOT_CAPACITY = 36                 # 单槽容量（件）
WAREHOUSE_CAPACITY = 300           # 仓库容量（件，未上架部分）
PREMIUM_SLOT_INDEXES = (0, 3)      # 黄金位槽号（曝光加成）

# ---------- 顾客 AI ----------
AI_UTILITY_WEIGHTS = {"price": 0.45, "position": 0.20,
                      "promo": 0.20, "stock": 0.15}             # 商品效用权重
AI_BUY_THRESHOLD = 0.45            # 效用购买门槛；调大→顾客更挑剔
AI_PRICE_SCORE_K = 3.0             # 价格分数 sigmoid 陡度
AI_WTP_JITTER = 0.12               # 个人愿付价浮动幅度（±）
AI_SUBSTITUTE_PROB = 0.35          # 缺货时跨品类替代购买概率
AI_PREMIUM_POS_SCORE = 1.0         # 黄金位位置分
AI_NORMAL_POS_SCORE = 0.6          # 普通位位置分
AI_STOCK_LOW_THRESHOLD = 5         # 槽内余量 ≤ 该值时视为"零散"
AI_STOCK_LOW_SCORE = 0.7           # 零散商品的库存分
NEEDS_COUNT_WEIGHTS = [(1, 0.55), (2, 0.40), (3, 0.05)]         # 每位顾客需求个数分布
SECOND_UNIT_PROB = 0.22            # 便宜商品多买一件的概率
SECOND_UNIT_MAX_REF = 3.5          # 参考价 ≤ 该值视为"便宜商品"
LOYALTY_ARRIVAL = (0.55, 0.45)     # 回头率乘数 = a + b×忠诚度

# ---------- 排队 / 收银 ----------
QUEUE_SERVICE_MIN_BASE = 2.6       # 每位顾客基础收银时长（分钟）；调大→排队压力增大
QUEUE_PER_ITEM_MIN = 0.5           # 每件商品附加收银时长
SERVICE_SPEED = 1.0                # 服务速度系数（雇员/设备后续可提升）

# ---------- 满意度 / 声望 / 忠诚 ----------
SAT_NEUTRAL = 70.0                 # 单顾客满意度中性值（绝对值口径 0~100）
SAT_BASE = 8.0                     # 成交基础满意度增量
SAT_OOS_SUB = 1.5                  # 缺货但有替代 → 扣减
SAT_OOS_NOSUB = 3.0                # 缺货无替代 → 扣减
SAT_PRICE_UNFAIR_COEF = 4.0        # 定价惩罚 = 系数 × clamp(售价/参考价 − 1, 0, 1)
QUEUE_PENALTY_RATE = 0.08          # 排队放弃率超过该值开始惩罚满意度
SAT_QUEUE_PENALTY_MAX = 5.0        # 满意度追加扣减上限
SAT_QUEUE_PENALTY_SLOPE = 30.0     # 满意度惩罚 = (放弃率−阈值) × 斜率
SAT_BASELINE = 65.0                # 满意度中性线（低于则声望下滑）
REP_GAIN_COEF = 0.18               # 声望日变化 = 系数 × (满意度 − 中性线)
REP_DAILY_LIMIT = 3.0              # 声望单日变化幅度上限（防死亡螺旋）
REP_ABANDON_RATE = 0.08            # 声望惩罚的放弃率阈值
REP_ABANDON_PENALTY_MAX = 3.0      # 声望单日惩罚上限
REP_ABANDON_SLOPE = 20.0           # 声望惩罚 = (放弃率−阈值) × 斜率
LOYALTY_DAILY_GAIN = 0.30          # 忠诚度日变化 = 系数 × (满意度 − 中性线) / 中性线
LOYALTY_DAILY_LIMIT = 0.03         # 忠诚度单日变化幅度上限

# ---------- 库存 ----------
EXPIRY_WARN_DAYS = 2               # 剩余保质期 ≤ 该值 → 临期警告
STAGNANT_RATIO = 1.5               # 库存天数 / 目标周转天数 超过 → 滞销
TARGET_TURNOVER_DAYS = 3           # 品类目标周转天数
SUGGEST_COVER_DAYS = 2             # 进货界面建议订货量的覆盖天数
INFINITE_SHELF_LIFE = 9999         # "无限"保质期的内部到期日表示

# ---------- 促销 ----------
PROMO_DEFAULT_DAYS = 3             # 新促销默认持续天数
PROMO_MAX_PCT = 50                 # 最大折扣百分比

# ---------- 结算 / 账本 ----------
LEDGER_KEEP_DAYS = 30              # 账本保留天数（明细粒度）
SALES_HISTORY_DAYS = 7             # 分商品销量历史保留天数（用于均销/建议订货）
WASTE_RATE_WINDOW_DAYS = 7         # 报废率的采购额滚动窗口

# ---------- 难度 ----------
@dataclass(frozen=True)
class DifficultyPreset:
    key: str
    label: str
    cash: float                    # 初始资金
    traffic_mult: float            # 客流乘数
    rent_mult: float               # 房租乘数
    victory_net_worth: float       # 胜利净资产线


DIFFICULTIES = {
    "easy":   DifficultyPreset("easy",   "轻松", 25000.0, 1.30, 0.85, 150000.0),
    "normal": DifficultyPreset("normal", "普通", 20000.0, 1.00, 1.00, 200000.0),
    "hard":   DifficultyPreset("hard",   "硬核", 15000.0, 0.85, 1.25, 260000.0),
}
