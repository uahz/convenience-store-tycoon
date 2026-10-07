# 便利店大亨 · Convenience Tycoon（Kotlin 多平台版）

**一套 Kotlin 代码（JetBrains Compose Multiplatform），三端运行：**

| 端 | 形态 | 状态 |
|---|---|---|
| **PC** | 免安装包（jar + 内置 JRE），双击「启动游戏.bat」 | ✅ 已验证 |
| **网页** | Kotlin/Wasm 编译，浏览器直接玩 | ✅ 可构建（见下） |
| **安卓** | Gradle 标准 APK（minSdk 24） | ✅ 构建配置就绪 |

界面为全新设计的实时经营视图：左侧店铺地板实时呈现顾客进店/选购/排队/离店，
右侧五页签常驻侧栏（今日/进货/定价/陈列/报表），顶部随时暂停或 2×/4× 加速。
经营仿真核心（顾客 AI、批次保质期、FIFO、满意度→声望→客流）与 Python 版
逻辑一致，数值全部集中在 `composeApp/src/commonMain/kotlin/tycoon/core/Balance.kt`。

## 运行方式

### PC（免安装包）
```
dist-pc/ConvenienceTycoon/启动游戏.bat
```
- 自带 JRE，无需安装任何环境。
- 存档保存在程序目录 `saves/autosave.json`。
- 应用图标：`composeApp/icons/game.ico`。

### 网页
```bash
# 开发版（无需 binaryen 优化器）
gradle :composeApp:wasmJsBrowserDevelopmentExecutableDistribution
# 产物在 composeApp/build/dist/wasmJs/developmentExecutable/
# 本地预览：python -m http.server -d <产物目录> 8080
```
- 正式优化版需要 `wasmJsBrowserDistribution`（会从 GitHub 下载 binaryen，
  国内网络受阻时用开发版即可，仅体积更大）。
- 存档保存在浏览器 localStorage。

### 安卓 APK
```bash
gradle :composeApp:assembleDebug
# 产物 composeApp/build/outputs/apk/debug/ComposeTycoon.apk
```
- 需要 ANDROID SDK（platforms;android-34 + build-tools）并写入 `local.properties`。
- 启动器图标为自适应图标（`res/drawable/ic_launcher_foreground.xml`）。

## 操作说明（与设计稿一致）

1. **备货（暂停状态）**：进货页签下订单 → 定价页签拖滑条设价/促销 →
   陈列页签点槽位上架（★ 黄金位 1、4 号槽曝光更高）。
2. **开门营业**：「今日」页签大按钮启动时钟；顾客实时进店选购、排队结账；
   缺货顾客变红离开。
3. **营业中随时经营**：切页签补货调价，时间照跑；或点 ⏸ / 2× / 4×。
4. **24:00 打烊** → 结算单 → 下一天。每日结算后自动存档。

## 项目结构

```
composeApp/src/
├── commonMain/kotlin/tycoon/
│   ├── core/          # 游戏核心（Balance/Catalog/Customers/State/Rng/Inventory/
│   │                  #  Pricing/Display/Customer/Traffic/Simulation/
│   │                  #  Settlement/Economy/Game/Savegame）
│   ├── ui/            # Compose 界面（GameViewModel/AppRoot/FloorCanvas/
│   │                  #  SidebarPanels/Dialogs/Theme）
│   ├── util/Fmt.kt    # 跨平台格式化（无 java.text 依赖）
│   └── PlatformIo.kt  # expect：存档 IO
├── desktopMain/       # PC 入口 + 文件存档 actual + 演示自截钩子
├── androidMain/       # MainActivity + filesDir 存档 actual + 自适应图标
└── wasmJsMain/        # CanvasBasedWindow 入口 + localStorage actual
```

## 设计资产

- 游戏主图标：`art/icons.html`（512px 主图标 + 8 枚游戏内小图标集），
  渲染产物 `art/renders/`，Windows 图标 `composeApp/icons/game.ico`，
  安卓自适应图标 `androidMain/res/drawable/ic_launcher_foreground.xml`。
- 界面设计稿与实拍：见 `../convenience-store-tycoon/design/ui-shots/`。
