# Soul Extraction: OpenNutriTracker

**提取日期**: 2026-03-17
**提取模型**: Claude Sonnet 4.6
**项目路径**: /tmp/OpenNutriTracker

---

## Stage 0: repo_facts

```json
{
  "name": "opennutritracker",
  "description": "Open-Source Calories & Activity Tracker",
  "version": "1.0.0+41",
  "language": "Dart / Flutter",
  "sdk_constraint": ">=3.0.0 <4.0.0",
  "platforms": ["android", "ios"],
  "license": "GPLv3",
  "state_management": "flutter_bloc (BLoC pattern)",
  "local_storage": "Hive (AES-256 encrypted)",
  "remote_backend": "Supabase (for FDC food search mirror)",
  "error_tracking": "Sentry (optional, consent-gated)",
  "food_databases": ["Open Food Facts (OFF)", "Food Data Central (USDA FDC)", "Supabase FDC mirror (sp_fdc)"],
  "di_container": "get_it (service locator)",
  "architecture": "Clean Architecture (data / domain / presentation layers)",
  "feature_modules": [
    "home", "diary", "add_meal", "edit_meal", "meal_detail",
    "add_activity", "activity_detail", "scanner", "onboarding",
    "profile", "settings"
  ],
  "calc_modules": ["bmr_calc", "tdee_calc", "calorie_goal_calc", "macro_calc", "met_calc", "pal_calc", "bmi_calc", "unit_calc"],
  "localization": "flutter_intl (en, de, tr)",
  "key_dependencies": {
    "hive": "2.2.3",
    "flutter_bloc": "8.1.6",
    "mobile_scanner": "6.0.2",
    "supabase_flutter": "2.8.2",
    "sentry_flutter": "8.14.2",
    "envied": "1.0.0"
  },
  "notable_todos": [
    "// TODO lower timeout (OFF 20s timeout)",
    "// TODO GROUP activities in effort categories (light, moderate, vigorous)",
    "// TODO extract correct unit from quantity string",
    "// TODO Make translation keys for FDC measure units"
  ]
}
```

**目录结构摘要**:
```
lib/
  core/
    data/         (data_source, dbo, repository)
    domain/       (entity, usecase)
    presentation/ (main_screen, widgets)
    styles/
    utils/
      calc/       (8 calculation modules — 核心科学引擎)
  features/
    home/         (dashboard + meal type lists)
    diary/        (calendar view + day info)
    add_meal/     (search + barcode)
    edit_meal/
    meal_detail/
    add_activity/ (activity picker)
    activity_detail/
    scanner/      (barcode scanner)
    onboarding/   (5-page user setup flow)
    profile/      (BMI + user stats)
    settings/     (calculations dialog + export/import)
```

---

## Stage 1: 灵魂发现

### 项目灵魂一句话

**"把公开的营养科学公式封装成隐私优先的个人代谢计算器，配上双数据库食物查找和全强度运动追踪，让用户拥有一个不收费、不看广告、不泄隐私的卡路里管家。"**

### 核心价值主张
1. **科学公式的忠实实现** — 4种BMR方程、2种TDEE方程、WHO宏量营养素比例，全部有学术文献引用，不是黑盒估算
2. **隐私作为硬性产品约束** — 所有数据在设备本地AES加密存储，Sentry错误上报需用户显式同意，Supabase仅用于公开食物数据库镜像查询（不含用户数据）
3. **双数据库覆盖策略** — OFF（全球品牌包装食品，支持条码）+ FDC（USDA基础食材，科学级数据），互为补充
4. **运动即卡路里加额度** — 记录运动后每日目标自动上调，不惩罚运动者，鼓励积极生活方式

### 关键设计决策（设计哲学的痕迹）
- 营养数据全部按**每100g/100ml**存储，在计算层按实际摄入量等比换算 — 一致性优于便利性
- TrackedDay对象 — 每天快照一次目标值，避免历史记录受用户资料变更影响
- Supabase镜像 FDC — 原FDC API需要API Key且有速率限制，镜像解决冷启动和免费用量问题
- 条码扫描只走OFF — FDC是基础食材数据库，没有UPC条码；OFF是品牌食品数据库，有条码
- 运动Compendium hard-coded — 2011年Compendium有~75项活动，每项有经过测量的MET值，不依赖用户估算

---

## Stage 2-3: 结构化知识卡片

### Concept Cards

---

**CONCEPT-01: 每日卡路里目标计算链**

这是整个产品的核心算法链，从用户生理参数出发，逐级计算到最终每日目标：

```
用户档案 (性别/年龄/身高/体重/PAL等级)
    ↓
BMR (基础代谢率)     — Schofield 1985 (WHO推荐)
    ↓ × PAL系数
TDEE (总能量消耗)    — IOM 2005公式 (默认使用)
    ↓ ± 目标调整
卡路里基准目标        — 减重:-500kcal / 维持:±0 / 增重:+500kcal
    ↓ + 运动消耗
最终每日卡路里目标    — 随当日运动实时更新
    ↓ − 已摄入
剩余可用卡路里       — 仪表盘圆形进度条显示
```

**文件证据**:
- `lib/core/utils/calc/tdee_calc.dart:12-16` — `getTDEEKcalWHO2001` uses Schofield BMR × PAL
- `lib/core/utils/calc/tdee_calc.dart:27-47` — `getTDEEKcalIOM2005` (实际默认使用的公式)
- `lib/core/utils/calc/calorie_goal_calc.dart:6-8` — `-500/0/+500` kcal 调整常量
- `lib/core/utils/calc/calorie_goal_calc.dart:17-23` — `getTotalKcalGoal` = TDEE + goal_adj + user_adj + activities
- `lib/core/domain/usecase/get_kcal_goal_usecase.dart:16-29` — 汇聚用户数据、配置、当日运动计算最终目标

---

**CONCEPT-02: 食物数据的三层来源架构**

```
Layer 1: Open Food Facts (OFF)
  ├── 用途: 品牌包装食品搜索 + 条码扫描
  ├── 接入: REST API (world.openfoodfacts.org)
  ├── 字段要求: 按需请求特定字段(off_const.dart _returnFields)
  └── 数据质量: 社区贡献，质量参差不齐，nutriments可能为null

Layer 2: USDA FDC (Food Data Central)
  ├── 用途: 基础食材搜索 (Foundation + SR Legacy类型)
  ├── 接入: 官方REST API (api.nal.usda.gov)，需API Key
  ├── 特点: 科学级营养数据，有Atwater能量因子变体
  └── 数据质量: 权威，但无品牌/包装信息，无条码

Layer 3: Supabase FDC Mirror (sp_fdc)
  ├── 用途: FDC基础食材搜索的自托管镜像
  ├── 接入: Supabase PostgreSQL (full-text search)
  ├── 特点: 支持多语言描述(en/de)，无需API Key
  └── 数据质量: 与FDC相同，但检索方式更灵活
```

**关键设计**: 三个数据源在`ProductsRepository`统一封装，向上只暴露`MealEntity`列表，数据源来源标记在`MealSourceEntity`枚举(unknown/custom/off/fdc)。

**文件证据**:
- `lib/features/add_meal/data/repository/products_repository.dart:6-49` — 三数据源统一封装
- `lib/features/add_meal/data/data_sources/off_data_source.dart:13-69` — OFF API调用
- `lib/features/add_meal/data/data_sources/fdc_data_source.dart:11-33` — FDC API调用
- `lib/features/add_meal/data/data_sources/sp_fdc_data_source.dart:11-40` — Supabase镜像调用
- `lib/features/add_meal/domain/entity/meal_entity.dart:186-210` — MealSourceEntity枚举

---

**CONCEPT-03: 营养数据的"per-100"规范化模型**

所有食物的营养数据，无论来源，统一规范化为**每100g/100ml**的形式存储：

```dart
// MealNutrimentsDBO — 存储层
double? energyKcal100;    // kcal per 100g
double? carbohydrates100; // g per 100g
double? fat100;           // g per 100g
double? proteins100;      // g per 100g
// ...

// MealNutrimentsEntity — 域层，提供按单位换算的getter
double? get energyPerUnit => _getValuePerUnit(energyKcal100);
// _getValuePerUnit: return valuePer100 / 100  (per gram/ml)

// IntakeEntity — 摄入量 × 单位值 = 实际摄入
double get totalKcal => amount * (meal.nutriments.energyPerUnit ?? 0);
```

**意图**: `amount`字段存用户输入的实际克数或毫升数，`energyPerUnit`是每克能量，相乘即为实际摄入。这避免了不同包装规格的混乱，所有计算在同一坐标系下进行。

**文件证据**:
- `lib/core/data/dbo/meal_nutriments_dbo.dart:10-17` — 存储层字段定义
- `lib/features/add_meal/domain/entity/meal_nutriments_entity.dart:19-25` — perUnit getter
- `lib/features/add_meal/domain/entity/meal_nutriments_entity.dart:132-138` — `_getValuePerUnit` = value / 100
- `lib/core/domain/entity/intake_entity.dart:33-41` — totalKcal = amount × energyPerUnit

---

**CONCEPT-04: 运动消耗的MET模型**

运动热量消耗使用2011 Compendium of Physical Activities的MET值：

```
燃烧卡路里 = MET × 体重(kg) × 时长(小时)
```

~75种运动被硬编码在`PhysicalActivityDataSource`中，每种活动携带Compendium的标准代码（如`"12150"` = running general, MET=8.0）。用户记录一次运动后，当日卡路里目标自动增加该次燃烧量，等效于"挣得额外食物配额"。

**文件证据**:
- `lib/core/utils/calc/met_calc.dart:10-13` — 公式: `mets × weightKG × durationMin / 60`
- `lib/core/data/data_source/physical_activity_data_source.dart:7-309` — 75项活动及MET值硬编码
- `lib/core/domain/entity/physical_activity_entity.dart:11-15` — PhysicalActivityEntity含mets字段
- `lib/features/home/presentation/bloc/home_bloc.dart:104-105` — 当日运动kcal累加入TDEE目标

---

**CONCEPT-05: TrackedDay — 历史快照解耦机制**

`TrackedDay`实体每天持久化存储当日的目标和实际追踪值，独立于用户当前的资料设置：

```dart
class TrackedDayDBO {
  DateTime day;
  double calorieGoal;     // 快照：当日计算的目标
  double caloriesTracked; // 实际已追踪卡路里
  double? carbsGoal;      // 宏量目标快照
  double? carbsTracked;   // 宏量实际追踪
  // fat, protein同上...
}
```

**为什么重要**: 如果用户后来更改了体重或目标，历史日期的记录不会被回算修改。这是一个不显眼但正确的设计决策，保证了日历视图中的历史数据准确性。

**文件证据**:
- `lib/core/data/dbo/tracked_day_dbo.dart:9-57` — TrackedDayDBO结构
- `lib/core/domain/usecase/add_tracked_day_usecase.dart:8-73` — 增/减/更新追踪值的所有操作
- `lib/features/home/presentation/bloc/home_bloc.dart:165-218` — 删除/编辑摄入时同步更新TrackedDay

---

### Workflow Cards

---

**WORKFLOW-01: 食物记录完整流程**

```
用户操作                         代码路径
─────────────────────────────────────────────────────────
1. 点击 "+" 添加早餐             → AddMealScreen (NavigationOptions.addMealRoute)
2. 输入食物名称/扫描条码          → AddMealBloc / ScannerBloc
3a. 文字搜索                     → SearchProductsUsecase
   ├─ OFF: OFFDataSource.fetchSearchWordResults
   ├─ FDC: FDCDataSource.fetchSearchWordResults
   └─ SP: SpFdcDataSource.fetchSearchWordResults
3b. 条码扫描                     → SearchProductByBarcodeUsecase
   └─ OFF: OFFDataSource.fetchBarcodeResults (仅OFF有UPC)
4. 选择食物 → 进入MealDetailScreen
5. 输入摄入量(克/毫升)            → MealDetailBloc
6. 确认记录                      → AddIntakeUsecase
   ├─ IntakeDataSource.addIntake (Hive)
   └─ AddTrackedDayUsecase.addDayCaloriesTracked (更新TrackedDay)
7. HomeBloc.LoadItemsEvent重新加载 → 仪表盘数据刷新
```

**关键约束**: 摄入量的单位判断依赖`MealEntity.isLiquid` / `isSolid` getter，通过检测`mealUnit`是否在`liquidUnits`/`solidUnits`集合中决定。

**文件证据**:
- `lib/features/add_meal/data/repository/products_repository.dart:14-48` — 搜索路由
- `lib/core/domain/usecase/add_intake_usecase.dart` — 记录摄入
- `lib/features/home/presentation/bloc/home_bloc.dart:52-136` — LoadItemsEvent聚合所有当日数据
- `lib/features/add_meal/domain/entity/meal_entity.dart:14-21,45-48` — 液体/固体单位集合

---

**WORKFLOW-02: 用户初始化（Onboarding）流程**

```
页面1: 欢迎介绍
页面2: 输入生日 (用于计算年龄)
页面3: 输入身高、体重、选择性别
页面4: 选择PAL等级 (sedentary/lowActive/active/veryActive)
       选择体重目标 (减重/维持/增重)
       选择单位制 (公制/英制)
预览页: 实时显示计算出的:
       - 每日卡路里目标
       - 碳水/脂肪/蛋白质目标 (克)
       此处使用默认宏量比例: carbs 60% / fat 25% / protein 15%
页面5: 隐私政策确认 + 匿名数据收集(可选)

保存: OnboardingBloc.saveOnboardingData()
  ├─ AddUserUsecase.addUser(userEntity)
  ├─ AddConfigUsecase.setConfigHasAcceptedAnonymousData()
  └─ AddConfigUsecase.setConfigUsesImperialUnits()
```

**文件证据**:
- `lib/features/onboarding/presentation/bloc/onboarding_bloc.dart:29-75` — 保存逻辑 + 预览计算
- `lib/core/utils/calc/macro_calc.dart:11-13` — 默认宏量比例常量
- `lib/features/onboarding/domain/entity/user_data_mask_entity.dart` — 收集中间状态

---

**WORKFLOW-03: 运动记录流程**

```
1. 进入AddActivityScreen
   ├─ ActivitiesBloc: 加载全部~75种活动（按类别分组）
   └─ RecentActivitiesBloc: 加载最近20条去重活动
2. 用户选择活动 → ActivityDetailScreen
3. 输入时长(分钟)
4. 确认记录 → AddUserActivityUsecase
   ├─ burnedKcal = METCalc.getTotalBurnedKcal(user, activity, durationMin)
   ├─ UserActivityDataSource.addUserActivity (Hive)
   └─ AddTrackedDayUsecase.increaseDayCalorieGoal(day, burnedKcal)
       同时增加宏量目标配额 (MacroCalc按燃烧量反算)
5. HomeBloc刷新: 仪表盘"已燃烧"数字更新，卡路里目标上调
```

**文件证据**:
- `lib/core/utils/calc/met_calc.dart:4-14` — MET计算
- `lib/core/domain/usecase/add_user_activity_usercase.dart` — 添加活动
- `lib/features/home/presentation/bloc/home_bloc.dart:102-105` — 当日运动kcal累加
- `lib/core/data/data_source/physical_activity_data_source.dart:8-309` — 活动库

---

### Decision Rule Cards

---

**RULE-01: 卡路里目标选用IOM 2005，不用WHO 2001**

系统存在两个TDEE计算实现：
- `TDEECalc.getTDEEKcalWHO2001` (Schofield BMR × PAL)
- `TDEECalc.getTDEEKcalIOM2005` (IOM 2005 EER公式)

`CalorieGoalCalc.getTdee()` 硬连接到 `getTDEEKcalIOM2005`，Settings界面显示"IOM 2006 (Recommended)"，下拉框被禁用（`onChanged: null`）。

**推断规则**: 提供公式选项是为了将来可扩展性，但作者认为IOM公式更准确（它直接使用PA系数而非简单乘以PAL，并按性别差异化处理），所以当前版本锁定了IOM公式，保留了UI占位以示"可以有多种选择"。

**文件证据**:
- `lib/core/utils/calc/calorie_goal_calc.dart:14-15` — `getTdee` → `getTDEEKcalIOM2005`
- `lib/features/settings/presentation/widgets/calculations_dialog.dart:102-108` — dropdown被禁用
- `lib/core/utils/calc/tdee_calc.dart:27-47` — IOM 2005公式实现

---

**RULE-02: 宏量比例调整时保持总和100%的算法**

当用户在Settings中拖动一个宏量滑块时，其余两个自动按比例调整，且任何值不低于5%。算法如下：

```
调整碳水时:
  delta = 新碳水值 - 旧碳水值
  蛋白质减少量 = delta × (蛋白质 / (蛋白质+脂肪))
  脂肪减少量 = delta × (脂肪 / (蛋白质+脂肪))
  任何值 < 5% 时，溢出量转移给另一个
最终通过_normalizeMacros()确保三值之和精确等于100
```

**设计原则**: 零和约束（总和=100%）+ 最小值保护（≥5%）+ 按现有比例分摊变化，保证用户体验直觉自然。

**文件证据**:
- `lib/features/settings/presentation/widgets/calculations_dialog.dart:147-173` — 碳水滑块onChange
- `lib/features/settings/presentation/widgets/calculations_dialog.dart:295-334` — `_normalizeMacros()`

---

**RULE-03: 数据加密始终开启，用户无法关闭**

Hive数据库在初始化时强制使用AES-CBC-PKCS7加密，密钥存储在设备的安全存储区（iOS Keychain / Android EncryptedSharedPreferences）。这是硬编码的行为，没有配置开关。

**推断规则**: 作者视隐私为产品的核心差异化点（README中"Privacy Focused"排在Key Features第一位），而不是可选功能。加密无条件开启，保证即使设备被物理访问，用户营养数据也不可读取。

**文件证据**:
- `lib/core/utils/hive_db_provider.dart:32-63` — `initHiveDB`强制传入encryptionCypher
- `lib/core/utils/secure_app_storage_provider.dart:23-35` — 密钥首次使用时生成并存入安全存储
- `lib/core/utils/hive_db_provider.dart:51-60` — 所有5个Hive Box均使用加密

---

**RULE-04: 条码扫描仅路由至OFF，FDC不参与**

`SearchProductByBarcodeUsecase`只调用`OFFDataSource.fetchBarcodeResults`，没有FDC或Supabase的备选分支。

**推断规则**: FDC基础食品数据库（Foundation + SR Legacy类型）是原始农业/科学食材数据，不含商业UPC条码。条码标识的是品牌包装食品，这是OFF的数据域。两个数据库各司其职，在条码路径上没有争议。

**文件证据**:
- `lib/features/scanner/domain/usecase/search_product_by_barcode_usecase.dart` — 只调用OFF
- `lib/features/add_meal/data/repository/products_repository.dart:44-48` — `getOFFProductByBarcode`
- `lib/features/add_meal/data/dto/fdc/fdc_const.dart:13-25` — FDC只查Foundation+SR Legacy类型

---

**RULE-05: 删除运动时减少卡路里目标，不减少已追踪量**

```
deleteUserActivityItem:
  ├─ 删除UserActivity记录
  └─ reduceDayCalorieGoal(day, burnedKcal)  ← 减少目标
      (不调用 removeDayCaloriesTracked)     ← 不改变已追踪摄入
```

vs. 删除摄入记录时：
```
deleteIntakeItem:
  ├─ 删除Intake记录
  └─ removeDayCaloriesTracked(day, kcal)   ← 减少已追踪量
      (不调用 reduceDayCalorieGoal)         ← 不改变目标
```

**推断规则**: 运动决定"你今天可以吃多少"（目标），摄入决定"你实际已经吃了多少"（实绩）。两个维度独立变化，删除操作也在各自维度上回滚，保持语义一致性。

**文件证据**:
- `lib/features/home/presentation/bloc/home_bloc.dart:190-218` — deleteIntakeItem vs deleteUserActivityItem的不同处理

---

## Stage 3.5: INFERENCE 标记

以下知识无直接代码证据，为基于代码结构的推断：

**INFERENCE-01**: Supabase FDC镜像的存在原因很可能是FDC官方API有速率限制（免费key是有限的），而且FDC不原生支持全文搜索的多语言描述。镜像允许项目无API Key消耗、支持德语搜索。

**INFERENCE-02**: 条码扫描20秒超时注释`// TODO lower timeout`说明作者知道这个超时过长，但可能是为了在网络慢时不让用户失望而设置的保守值。

**INFERENCE-03**: `PhysicalActivityEffort`枚举（light/moderate/vigorous）被定义但未被任何生产代码使用（仅有TODO注释），表明强度分类是计划中的功能，尚未实现。

**INFERENCE-04**: 营养数据中的`sugars100`、`saturatedFat100`、`fiber100`虽然被存储，但在主要计算（卡路里目标、宏量目标）中不参与，它们仅在餐食详情页展示。作者将这些视为"信息字段"而非"计算字段"。

---

## UNSAID (未言说洞察)

**UNSAID-01: 宏量的"脂肪悖论"**
代码里默认脂肪占卡路里25%（`_defaultFatsPercentageGoal = 0.25`），热量系数9kcal/g。但产品没有明确说明：如果用户调低脂肪目标，实际上最难达成——因为脂肪热量密度最高，少量食物就能超标。软件追踪的是"目标克数"，但用户心理模型可能是"少吃脂肪=健康"。这中间有一个认知落差，产品从未解释脂肪的克数目标与热量占比之间的换算逻辑。

**UNSAID-02: 运动卡路里的MET单一性问题**
MET（代谢当量）是群体平均值，对个体的误差可能在20-30%。跑步8.0 MET假设的是"一般跑步"，但一个70kg成人跑步速度从8km/h到12km/h，实际能量消耗差异很大。产品使用MET是行业惯例，但从未告知用户这是估算而非精确测量。用户可能把"燃烧了350kcal"当成精确数字来决定是否多吃一块蛋糕。

**UNSAID-03: 历史数据可能随用户改变体重而失真**
`TrackedDay`快照当日卡路里目标——这是个聪明的设计，防止历史目标随用户资料变更而改变。但是，摄入的营养数据是按当时记录的`amount`和每100g值计算的，并没有问题。然而，运动燃烧卡路里（`UserActivity`）是按**当时**的用户体重计算后存储的`burnedKcal`——这意味着即使用户后来减轻了体重，历史运动记录依然显示减重前体重计算出来的较高消耗值。日历视图的历史热量平衡因此可能失真。

**UNSAID-04: Supabase引入了产品对外依赖**
项目强调隐私优先和本地数据，但Supabase FDC查询在每次食物搜索时都向自托管的Supabase发送查询请求。用户在搜索"apple"时，Supabase服务器会记录该请求（尽管不含用户身份）。项目README的隐私声明未提及这一点。OFF和FDC的API调用同样存在此问题——每次查询对方服务器都知道你在搜索什么食物。

**UNSAID-05: 食物数据质量问题是最大的精度瓶颈**
整个卡路里追踪体系的计算精度，取决于最薄弱的环节——食物数据库里的营养值是否准确。OFF是社区贡献，数据质量高度不一致。`meal.nutriments.energyPerUnit ?? 0`的fallback（能量未知时当0处理）会导致某些食物的卡路里被计为零，用户完全不知情。产品有一个disclaimer（README中"All data provided is not validated"），但在用户界面中没有任何数据质量指标或警告。

---

## 贡献列表（对 Doramagic sim2 实验的贡献）

| 贡献类型 | 内容 | 参考文件 |
|---------|------|---------|
| 算法实现参考 | 4种BMR方程代码实现（含学术引用） | `lib/core/utils/calc/bmr_calc.dart` |
| 算法实现参考 | IOM 2005 TDEE公式（含PA系数性别差异） | `lib/core/utils/calc/tdee_calc.dart` |
| 算法实现参考 | MET卡路里燃烧公式 | `lib/core/utils/calc/met_calc.dart` |
| 算法实现参考 | 宏量换算（carbs/fat/protein kcal/g系数） | `lib/core/utils/calc/macro_calc.dart` |
| 运动数据库 | 75种标准活动及MET值（2011 Compendium） | `lib/core/data/data_source/physical_activity_data_source.dart` |
| 数据架构模式 | per-100g规范化 + perUnit换算getter | `lib/features/add_meal/domain/entity/meal_nutriments_entity.dart` |
| 数据架构模式 | TrackedDay历史快照解耦机制 | `lib/core/data/dbo/tracked_day_dbo.dart` |
| 双数据库策略 | OFF(品牌+条码) vs FDC(基础食材)职责分工 | `lib/features/add_meal/data/repository/products_repository.dart` |
| 隐私架构模式 | AES加密Hive + 安全存储密钥管理 | `lib/core/utils/hive_db_provider.dart`, `secure_app_storage_provider.dart` |
| 目标计算逻辑 | 运动增加卡路里配额（而非减少剩余额度） | `lib/features/home/presentation/bloc/home_bloc.dart` |
| 可扩展性坑点 | 公式选项UI已有但被禁用（锁定IOM 2005） | `lib/features/settings/presentation/widgets/calculations_dialog.dart:102-108` |
| 用户体验细节 | 宏量滑块零和约束算法 | `lib/features/settings/presentation/widgets/calculations_dialog.dart:147-334` |
