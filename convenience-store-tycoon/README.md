# 便利店大亨（Convenience Tycoon）· Demo v0.1

**实时窗口版**便利店经营模拟：左侧店铺地板里顾客实时进店、选购、排队结账，
右侧常驻侧栏完成进货/定价/陈列/报表，顶部随时暂停或 2×/4× 加速。
零第三方依赖（界面为 Python 自带 Tkinter），`python main.py` 或双击 exe 即可开玩。
设计文档见 [DESIGN.md](DESIGN.md)，界面设计稿见 [design/ui-shots/](design/ui-shots/)。

> 当前为 **M0+ 实时闭环 Demo**：完整的日循环（备货 → 营业 → 结算 → 次日），
> 可连续多日经营，含存/读档。事件系统、贷款、店铺升级、雇员等按里程碑逐步加入。

## 运行

### 方式一：独立程序（exe，推荐）

双击 `dist/ConvenienceTycoon.exe`（Windows 10+，单文件，无需安装 Python）。

- 存档自动生成在 **exe 同目录**的 `saves/autosave.json`，把 exe 拷到任何位置存档都跟着走。
- 首次运行可能被 Windows SmartScreen 提示（未签名程序），点"更多信息 → 仍要运行"。
- 重新打包：`python -m PyInstaller --onefile --noconsole --clean --noconfirm --name ConvenienceTycoon main.py`（或 `python -m PyInstaller ConvenienceTycoon.spec`）。

### 方式二：源码运行

要求：Python 3.10+（仅标准库，无 pip 依赖）。

```bash
python main.py             # 窗口版（默认）
python main.py --cli       # 终端纯文本模式（保留的老玩法）
python main.py --seed 42   # 固定随机种子（可复现，用于调试与对比）
python main.py --selftest  # 运行 GUI 自检后退出（打包冒烟用）
```

## 怎么玩（实时日循环）

1. **备货阶段（时间暂停）**：右侧侧栏 →
   **进货**页签按"箱"下订单（当日早到货，注意仓库容量 300 件与现金）；
   **定价**页签设售价（贴近参考价好卖，远高于参考价会赶客）与促销；
   **陈列**页签把商品上架（每槽 36 件，★黄金位 1、4 号槽曝光更高）。
2. **开门营业**：点"今日"页签的大按钮，时钟开始流动——
   顾客实时进店、走到货架、排队结账；缺货的顾客变红直接离开。
3. **营业中随时经营**：切到进货/定价页签补货调价，时间照跑；
   想从容操作就点顶部 **⏸ 暂停**，或开 **2×/4×** 加速（一天约 1~4 分钟）。
4. **24:00 打烊** → 结算单弹窗（净利、KPI、声望变化）→ 开始下一天。
   每日结算后自动存档；"今日"页签可手动保存。
5. 满意度均值决定声望涨跌 → 影响次日客流；**结算后现金为负即破产**；
   普通难度净资产 ¥200,000 达成胜利。

操作约定：全部鼠标点选；确认类操作有弹窗校验，非法输入不会崩溃。

## 目录结构

```
convenience-store-tycoon/
├── main.py            # 入口（默认窗口版；--cli 终端版；--selftest 自检）
├── config/            # ★ 全部可调数值（balance / items / customers）
├── core/              # ★ 纯仿真：零 IO，与界面严格分离
│   ├── game.py        #   Game 门面（begin_day/finish_day/open_store）
│   ├── simulation.py  #   日仿真引擎（iter_day_hours 逐小时生成器）
│   ├── settlement.py  #   每日结算（纯函数）+ KPI 账本
│   ├── customer.py    #   顾客 AI 决策管线（商品级需求）
│   ├── inventory.py   #   批次/FIFO/保质期/报废
│   └── ...            #   traffic / pricing / display / economy / state / rng
├── ui_gui/            # ★ 实时窗口界面（Tkinter）
│   ├── app.py         #   主窗口/状态机/小时节拍驱动
│   ├── floorview.py   #   实时地板画布（30FPS 顾客动画）
│   ├── sidebar.py     #   五页签侧栏（今日/进货/定价/陈列/报表）
│   └── dialogs.py     #   结算单/难度/改价/促销弹窗
├── ui/                # 终端界面（--cli 备用模式）
├── save/savegame.py   # 版本化 JSON 存档（原子写入 + 迁移链）
└── tests/             # 21 个测试（含 GUI 自检与端到端成交验收）
```

## 主要可调参数（config/balance.py）

改完即生效；逻辑代码中不出现魔法数字，所有数值以本表与 config 为准。

| 参数 | 默认值 | 作用 |
|---|---|---|
| `INITIAL_CASH` | 20000 | 初始资金 |
| `RENT_PER_DAY` | 250 | Lv1 日房租（固定成本大头） |
| `UTILITY_BASE` / `UTILITY_RATE` | 30 / 1.5% | 水电 = 基数 + 营收×比例 |
| `SHELF_SLOTS` / `SLOT_CAPACITY` | 6 / 36 | 货架槽数 / 单槽容量（件） |
| `WAREHOUSE_CAPACITY` | 300 | 仓库容量（未上架部分，件） |
| `TRAFFIC_BASE_WEEKDAY` / `WEEKEND` | 460 / 575 | 路过人流基数（进店≈基数×进店率） |
| `BASE_ENTER_RATE` | 0.38 | 基准进店率系数（随声望/陈列/促销浮动） |
| `PEAK_WEIGHTS` | 8点1.8 … | 各小时客流倍率 |
| `AI_UTILITY_WEIGHTS` | 价.45/位.20/促.20/货.15 | 顾客购买效用权重 |
| `AI_BUY_THRESHOLD` | 0.45 | 效用购买门槛（调大→顾客更挑剔） |
| `AI_WTP_JITTER` | 0.12 | 个人愿付价浮动（±，相对参考价） |
| `AI_SUBSTITUTE_PROB` | 0.35 | 缺货时被"顺手买别的"替代的概率 |
| `QUEUE_SERVICE_MIN_BASE` / `PER_ITEM` | 2.6 / 0.5 分钟 | 收银速度（决定排队压力） |
| `SAT_NEUTRAL` / `SAT_BASE` | 70 / +8 | 单顾客满意度中性值 / 成交基础增量 |
| `SAT_OOS_SUB` / `SAT_OOS_NOSUB` | −1.5 / −3 | 缺货满意度扣减（有替代/无替代） |
| `SAT_PRICE_UNFAIR_COEF` | 4 | 定价超过参考价的满意度惩罚斜率 |
| `REP_GAIN_COEF` / `REP_DAILY_LIMIT` | 0.18 / ±3 | 声望日变化系数 / 单日幅度上限 |
| `LOYALTY_ARRIVAL` | 0.55+0.45×忠诚 | 忠诚度对回头率的乘数 |
| `EXPIRY_WARN_DAYS` | 2 | 剩余保质期警告阈值 |
| `STAGNANT_RATIO` / `TARGET_TURNOVER_DAYS` | 1.5 / 3 | 滞销判定 |
| `SUGGEST_COVER_DAYS` | 2 | 进货建议量的覆盖天数 |
| `PROMO_DEFAULT_DAYS` / `PROMO_MAX_PCT` | 3 / 50% | 促销时长 / 折扣上限 |
| `DIFFICULTIES` | 轻松/普通/硬核 | 初始资金、客流与房租乘数、胜利线 |
| `VICTORY_NET_WORTH`（普通） | 200000 | 胜利净资产目标 |

商品目录（进价/参考价/保质期/箱规）在 `config/items.py`；顾客原型
（时段、预算、耐心、商品偏好、促销敏感度）在 `config/customers.py`。

## 存档

- 位置：**exe（或项目根目录）旁的 `saves/autosave.json`**（UTF-8 JSON，含 RNG 状态，读档后随机序列无缝延续）。
- 每日结算后自动保存；夜间菜单可手动覆盖保存。
- 版本化（`format_version`）：旧档沿迁移链升级；高版本档拒绝读取；原子写入防损坏。
- 破产结局会清除自动存档。

## 测试与开发工具

```bash
python -m unittest discover -s tests   # 21 个测试：库存FIFO/顾客AI/结算/存档/端到端/GUI自检
python _balance_check.py 14            # 无头推演 14 天（脚本化"合格玩家"），观察经济曲线
python _gui_shots.py                   # 运行真实 GUI 并抓取三张截图
```

基准推演（seed=11）：14 天累计净利约 +1,300，声望 60→90，第 1 天微利、
第 2 周起日净利 100~170，验证"首日紧、随后正反馈"的难度曲线。

## 与设计文档的数值差异（M0 调参结果）

实测校准后以下数值与 DESIGN.md 不同，**以 config 为准**：
房租 400→250、水电 60+2%→30+1.5%、单槽容量 30→36、需求从"品类级"细化为
"商品级偏好"、满意度改为"中性 70 ± 增量"的绝对值口径（修复声望死亡螺旋）。

## 路线图（若 Demo 获得通过）

| 里程碑 | 内容 |
|---|---|
| **M0+（本 Demo）** | 实时窗口版一日闭环 + 顾客动画 + 五页签侧栏 + 存档 |
| M1 | 客服事件弹窗、6 类顾客原型与个体忠诚档案、临期区深化 |
| M2 | 随机事件引擎（14 事件表）、贷款/信用/破产缓冲、店铺升级 Lv1-5、设备与雇员 |
| M3 | 报表打磨、难度平衡、多存档槽、README 终稿 |
