# FoodYou — Soul Extractor 提取报告

项目路径: `/tmp/FoodYou`
提取时间: 2026-03-18
提取版本: v3.4.5 (DB schema v32)

---

## Stage 0 — repo_facts

### 基本信息

| 字段 | 值 |
|---|---|
| 项目名 | FoodYou |
| 包名 | com.maksimowiczm.foodyou |
| 版本 | 3.4.5 / versionCode 119 |
| DB Schema 版本 | 32 |
| 语言 | Kotlin Multiplatform |
| 目标平台 | Android (minSdk 28, targetSdk 36) |
| UI 框架 | Compose Multiplatform 1.10.1 / Material3 |
| 网络 | Ktor 3.4.0 |
| 数据库 | Room 2.8.4 + SQLite (bundled) |
| DI | Koin 4.1.1 |
| 分发 | F-Droid + GitHub Releases |
| 许可 | GPL v3 |

### 模块结构

```
FoodYou/
  app/                     # 主模块（巨型单模块架构）
    src/commonMain/kotlin/
      food/                # 食物领域（Product/Recipe/Search/USDA/OFF）
      fooddiary/           # 日记领域（Meal/DiaryEntry/Measurement）
      goals/               # 营养目标
      importexport/        # CSV + Swiss DB 导入导出
      settings/            # 用户偏好 / 主屏卡片
      common/              # 跨领域基础类 (NutritionFacts/Measurement/Event Bus)
    src/androidMain/       # Android 平台实现
  shared/
    barcodescanner/        # 条形码扫描（独立模块，因用旧式 XML 布局）
    resources/             # 字符串/图片/字体
```

### 外部食物数据库

| 数据库 | 接入方式 | API 限流 |
|---|---|---|
| Open Food Facts (OFF) | REST API v1(搜索) + v2(条码) | 100 req/min 产品, 10 req/min 搜索 |
| USDA FoodData Central | REST API (需 API Key) | 无明确限制 |
| Swiss Food Composition Database | 本地 CSV 文件导入 | N/A |

### 数据库实体总览（FoodYouDatabase v32）

主要实体: `ProductEntity`, `RecipeEntity`, `RecipeIngredientEntity`, `MealEntity`, `MeasurementEntity`, `DiaryProductEntity`, `DiaryRecipeEntity`, `ManualDiaryEntryEntity`, `MeasurementSuggestionEntity`, `SponsorshipEntity`

FTS 虚表: `ProductFts`（name/brand/note）, `RecipeFts`（name/note）

数据库视图: `RecipeAllIngredientsView`, `LatestMeasurementSuggestion`

---

## Stage 1 — 灵魂发现

### 这个项目真正在解决什么问题？

FoodYou 的核心主张是：**全营养追踪，不妥协隐私，不依赖账号**。大多数食物追踪 App 要么数据不够完整（只有宏量营养素），要么需要注册账号并上传数据到云端，要么是订阅制付费。

FoodYou 的回答是：把外部数据库的能力引进来（OFF/USDA/Swiss），全部存在本地，对用户的隐私链路做到断点。

### 灵魂所在的三条线索

**1. NutrientValue.Complete vs Incomplete 的二元语义**
这是整个 NutritionFacts 系统的根基。每个营养素字段不是 `Double?`，而是 `NutrientValue`（sealed interface）——`Complete` 表示"我知道这个值"，`Incomplete` 表示"这个值可能不存在或来源不完整"。这个设计让系统在累加食谱营养素时能正确传播"不确定性"——如果任意一个 ingredient 的某字段是 Incomplete，合并后的食谱该字段也是 Incomplete。大多数同类应用直接用 nullable 处理，这种二元语义是这个项目的精华。

**2. 本地镜像策略（Local Mirror）**
OFF 和 USDA 的搜索结果通过 RemoteMediator（Paging3）逐页拉取并写入本地 Room 数据库，搜索走本地 FTS4 而不是云端。这个决策（docs/decision-log/0003）明确表达："复制远程数据库的搜索逻辑，让用户体验在 App 内和在浏览器里查同一个数据库一致"。代价是无法真正离线，但换来了速度和一致性。

**3. 食谱的 unpack 能力**
一份食谱可以整体作为一条日记 entry（Record as Recipe），也可以按某个 Measurement（份数/克重）拆解（unpack）成各自 ingredient 的单独 entry。这个 `UnpackFoodDiaryEntryUseCase` 反映了一种产品哲学：食谱是"快捷方式"，不是不可拆分的黑盒。

---

## Stage 2-3 — 结构化卡片

### Concept Cards

---

**CONCEPT-01: NutrientValue — 带确定性语义的营养值类型**

完整度状态不是 UI 层的显示问题，而是领域模型的核心属性。

每个营养素值是 `NutrientValue`（sealed interface），有两个子类型：
- `Complete(value: Double)` — 确定值，支持完整算术运算
- `Incomplete(value: Double?)` — 不确定值，null 表示数据库中没有该字段

算术规则：Complete + Complete = Complete；Complete + Incomplete = Incomplete；Incomplete + Incomplete = Incomplete（保留 partial sum）

```kotlin
// file: app/src/commonMain/kotlin/com/maksimowiczm/foodyou/common/domain/food/NutrientValue.kt:6
sealed interface NutrientValue {
    val value: Double?
    @JvmInline value class Complete(override val value: Double) : NutrientValue
    @JvmInline value class Incomplete(override val value: Double?) : NutrientValue
    // 运算规则: Complete+Incomplete → Incomplete（不确定性传播）
    operator fun plus(other: NutrientValue): NutrientValue = when (this) {
        is Complete -> when (other) {
            is Complete -> this + other
            is Incomplete -> Incomplete(value + (other.value ?: 0.0))
        }
        ...
    }
}
```

file:line 证据: `app/src/commonMain/kotlin/com/maksimowiczm/foodyou/common/domain/food/NutrientValue.kt:6-78`

---

**CONCEPT-02: Food — 统一的食物抽象（Product 和 Recipe 同质化）**

Product（来自数据库/用户创建）和 Recipe（用户自建食谱）共同实现 `Food` sealed interface，使得日记和搜索系统对两者完全透明。

关键字段：`id: FoodId`（sealed，Product/Recipe 子类型），`nutritionFacts: NutritionFacts`，`isLiquid: Boolean`，`servingWeight: Double?`，`totalWeight: Double?`

`Food.weight(measurement)` 方法委托给 `WeightCalculator`，处理 Gram/Milliliter/Ounce/Package/Serving 五种计量方式。

Recipe 的 `nutritionFacts` 是 lazy 计算的：`ingredients.mapNotNull { it.nutritionFacts }.sum() / totalWeight * 100.0`

```kotlin
// file: app/src/commonMain/kotlin/com/maksimowiczm/foodyou/food/domain/entity/Food.kt:7
sealed interface Food {
    val id: FoodId
    val nutritionFacts: NutritionFacts
    val isLiquid: Boolean
    fun weight(measurement: Measurement): Double?
}
```

file:line 证据:
- `app/src/commonMain/kotlin/com/maksimowiczm/foodyou/food/domain/entity/Food.kt:7-21`
- `app/src/commonMain/kotlin/com/maksimowiczm/foodyou/food/domain/entity/Recipe.kt:32-38`

---

**CONCEPT-03: Measurement — 六种计量单位的统一模型**

Measurement 是一个 sealed interface，表达用户选择的计量方式：
- `Gram(value: Double)` — 克数（默认 100g）
- `Milliliter(value: Double)` — 毫升（默认 100ml）
- `Ounce(value: Double)` — 盎司（默认 1oz）
- `FluidOunce(value: Double)` — 液体盎司（默认 8 fl oz）
- `Package(quantity: Double)` — 整包数量（需要 `packageWeight` 字段）
- `Serving(quantity: Double)` — 份数（需要 `servingWeight` 字段）

ImmutableMeasurement（Gram/Milliliter/Ounce/FluidOunce）有 `.metric` 属性直接返回公制值。Package/Serving 需要 food 的 weight 字段才能换算。

Measurement 支持 `times(Double)` 运算，用于 Recipe.unpack 按比例缩放。

```kotlin
// file: app/src/commonMain/kotlin/com/maksimowiczm/foodyou/common/domain/measurement/Measurement.kt:5
sealed interface Measurement {
    operator fun times(other: Double): Measurement
    sealed interface ImmutableMeasurement : Measurement { val metric: Double }
    data class Package(val quantity: Double) : Measurement {
        fun weight(packageWeight: Double): Double = packageWeight * quantity
    }
    data class Serving(val quantity: Double) : Measurement {
        fun weight(servingWeight: Double): Double = servingWeight * quantity
    }
}
```

file:line 证据: `app/src/commonMain/kotlin/com/maksimowiczm/foodyou/common/domain/measurement/Measurement.kt:5-89`

---

**CONCEPT-04: NutritionFacts — 43 字段的全营养素模型**

`NutritionFacts` 是一个 data class，持有 43 个营养素字段，全部是 `NutrientValue`，默认值为 `Incomplete(null)`。

字段分类：
- 宏量营养素（4）: energy, proteins, fats, carbohydrates
- 脂肪细分（6）: saturatedFats, transFats, monounsaturatedFats, polyunsaturatedFats, omega3, omega6
- 碳水细分（5）: sugars, addedSugars, dietaryFiber, solubleFiber, insolubleFiber
- 其他（3）: salt, cholesterol, caffeine
- 维生素（13）: A, B1-B12, C, D, E, K
- 矿物质（12）: Mn, Mg, K, Ca, Cu, Zn, Na, Fe, P, Se, I, Cr

支持算术运算（+, *, /），用于食谱营养素聚合。`sum()` 扩展函数用于 `Iterable<NutritionFacts>` 的折叠。

file:line 证据: `app/src/commonMain/kotlin/com/maksimowiczm/foodyou/common/domain/food/NutritionFacts.kt:4-48`

---

**CONCEPT-05: Recipe.unpack — 食谱原子化拆解**

Recipe 可以按指定重量拆解为 ingredient 列表，每个 ingredient 的 measurement 按比例缩放。这使得"食谱"可以既作为整体记录，也可以拆成原料单独记录。

拆解算法: `fraction = weight / totalWeight`，每个 ingredient 的 measurement 乘以 fraction。

`flatIngredients()` 提供递归展平，处理嵌套食谱（recipe 作为另一个 recipe 的 ingredient）。

```kotlin
// file: app/src/commonMain/kotlin/com/maksimowiczm/foodyou/food/domain/entity/Recipe.kt:71
fun unpack(weight: Double): List<RecipeIngredient> {
    val fraction = weight / totalWeight
    return ingredients.map { (food, measurement) ->
        RecipeIngredient(food = food, measurement = measurement * fraction)
    }
}
```

file:line 证据: `app/src/commonMain/kotlin/com/maksimowiczm/foodyou/food/domain/entity/Recipe.kt:52-78`

---

**CONCEPT-06: MacronutrientGoal — 两种目标设定模式**

`MacronutrientGoal` 是 sealed interface，支持两种设定模式：
- `Manual` — 直接指定能量(kcal)和三大营养素的克重
- `Distribution` — 指定总能量和三大营养素的百分比，克重自动计算（用 `NutrientsHelper` 的 4/4/9 kcal/g 系数）

这让用户可以按"我要吃 2000kcal，蛋白质 20%"或"我每天吃 150g 蛋白质"两种方式设目标，系统在内部统一为克重表达。

file:line 证据: `app/src/commonMain/kotlin/com/maksimowiczm/foodyou/goals/domain/entity/MacronutrientGoal.kt:6-47`

---

### Workflow Cards

---

**WORKFLOW-01: 食物搜索流程（本地 FTS + Remote Mediator 双路）**

```
用户输入查询词
      ↓
FoodSearchUseCase
      ↓
判断输入类型
  ├── 条码 → 本地先查 barcode 字段 + OFF barcode API
  └── 文字 → 本地 FTS4 查询（ProductFts MATCH query||'*'）
                 ↓
         Room PagingSource（Paging3）
                 ↓（并行触发）
         RemoteMediator（OFF/USDA）
           ├── 检查 RateLimiter（OFF: 10 req/min 搜索, 100/min 产品）
           ├── 拉取远端分页数据（PAGE_SIZE=50）
           ├── 通过 OpenFoodFactsProductMapper 转换为 RemoteProduct
           ├── 通过 RemoteProductMapper 转换为 domain Product
           └── insertUniqueProduct（检查 name+brand+barcode+source 四元组去重）
                 ↓
         本地 FTS4 结果实时更新
```

去重规则：`ProductDao.insertUniqueProduct` 在同一事务内 SELECT EXISTS → INSERT，避免远端重复拉取写入相同数据。

file:line 证据:
- `app/src/commonMain/kotlin/com/maksimowiczm/foodyou/food/search/infrastructure/openfoodfacts/OpenFoodFactsRemoteMediator.kt:41-150`
- `app/src/commonMain/kotlin/com/maksimowiczm/foodyou/food/infrastructure/room/ProductDao.kt:64-78`
- `app/src/commonMain/kotlin/com/maksimowiczm/foodyou/food/search/infrastructure/room/FoodSearchDao.kt:85-120`

---

**WORKFLOW-02: 食物记录入日记流程**

```
用户从搜索结果选中某 Food
      ↓
AddEntryScreen — 选择 Meal + Date + Measurement
      ↓
AddEntryViewModel.save()
      ↓
CreateFoodDiaryEntryUseCase
      ├── 判断 food 类型：Product → DiaryProductEntity
      │                   Recipe  → DiaryRecipeEntity + DiaryRecipeIngredientEntity（快照）
      └── 写入 Measurement 表（mealId, epochDay, productId/recipeId, type, quantity）
              ↓（EventBus 发布）
      FoodDiaryEntryCreatedEvent
              ↓
      FoodDiaryEntryCreatedEventHandler（food 模块）
      └── 写入 MeasurementSuggestion（记录该 food 的最近使用 measurement）
```

日记快照机制：`DiaryRecipeEntity` + `DiaryRecipeIngredientEntity` 存储快照，防止后续修改食谱影响历史记录。（与 `RecipeEntity` 通过 recipe 名+时间点区分）

file:line 证据:
- `app/src/commonMain/kotlin/com/maksimowiczm/foodyou/fooddiary/infrastructure/room/MeasurementEntity.kt:22-37`
- `app/src/commonMain/kotlin/com/maksimowiczm/foodyou/food/domain/event/FoodDiaryEntryCreatedEventHandler.kt`（间接推断）

---

**WORKFLOW-03: Recipe unpack 到日记流程**

```
用户在日记中找到一条 recipe entry，选择"解包"
      ↓
UnpackFoodDiaryEntryUseCase.unpack(id, measurement, mealId, date)
      ↓
事务中:
  1. observeEntry(id) 确认存在且是 DiaryFoodRecipe 类型
  2. delete 原 recipe entry
  3. recipe.unpack(measurement 对应的克重) → List<RecipeIngredient>
  4. 对每个 ingredient 插入新的 DiaryEntry（保留原 createdAt）
```

这个功能允许用户在记录了"今天做了这道菜"之后，回头拆解成原料，用于更精细的营养分析。

file:line 证据: `app/src/commonMain/kotlin/com/maksimowiczm/foodyou/fooddiary/domain/usecase/UnpackFoodDiaryEntryUseCase.kt:33-98`

---

**WORKFLOW-04: Swiss Food Composition Database 导入流程**

```
用户进入 Settings → Database → Swiss Food Composition Database
      ↓
选择语言（DE/FR/IT 等）
      ↓
ImportSwissFoodCompositionDatabaseUseCase.import(languages)
      ↓
SwissFoodCompositionDatabaseRepository.readCsvFile(language)
      ↓（流式处理）
ImportCsvProductUseCase.import(mapper=order, stream, source=SwissFCD, skipHeader=true)
      ↓（逐行）
解析 CSV → 按 order 映射到 ProductField → 创建 Product → insertUniqueProduct
      ↓
emit count（实时进度）
```

Swiss DB 的 CSV 字段顺序硬编码在 `ImportSwissFoodCompositionDatabaseUseCaseImpl` 的 `order` 列表中（43 个字段映射）。

file:line 证据: `app/src/commonMain/kotlin/com/maksimowiczm/foodyou/importexport/swissfoodcompositiondatabase/domain/ImportSwissFoodCompositionDatabaseUseCase.kt:15-83`

---

### Decision Rule Cards

---

**RULE-01: 所有营养素值在 DB 中按物理单位分列存储，统一以克为内部单位**

`ProductEntity` 嵌入三个结构体：`Nutrients`（能量/宏量）、`Vitamins`（各维生素）、`Minerals`（各矿物质）。数据库列名带单位后缀（`cholesterolMilli`、`vitaminAMicro`、`sodiumMilli`）。

USDA API 返回的值是 mg 或 µg，`USDAMapper.normalize()` 统一换算为克：
```kotlin
private fun normalize(unitName: String?, amount: Double?): Double? {
    val from = UnitType.fromString(unitName) ?: return null
    return amount * multiplier(UnitType.GRAMS, from)
}
```

这样做的原因：NutritionFacts 领域模型统一使用克，避免在应用层做单位换算。

file:line 证据:
- `app/src/commonMain/kotlin/com/maksimowiczm/foodyou/food/infrastructure/usda/USDAMapper.kt:240-246`
- `app/src/commonMain/kotlin/com/maksimowiczm/foodyou/common/infrastructure/room/Nutrients.kt:3-22`

---

**RULE-02: 远端产品去重规则 — name + brand + barcode + sourceType 四元组唯一**

`ProductDao.insertUniqueProduct` 在同一事务内检查：
```sql
SELECT EXISTS (
    SELECT 1 FROM Product
    WHERE name = :name
    AND (:brand IS NULL OR brand = :brand)
    AND (:barcode IS NULL OR barcode = :barcode)
    AND :source = sourceType
)
```
只有当四元组不存在时才插入，否则返回 null（表示已存在，不计入 history）。

这个规则防止重复搜索同一词时数据库膨胀，但也意味着同名同品牌产品的营养数据更新不会自动同步（需要用户手动编辑）。

file:line 证据: `app/src/commonMain/kotlin/com/maksimowiczm/foodyou/food/infrastructure/room/ProductDao.kt:38-77`

---

**RULE-03: OFF 搜索限速规则 — 产品 100/min，搜索 10/min**

`OpenFoodFactsRateLimiter` 维护两个独立的 `RateLimiter` 实例：
- 产品请求（barcode 查询）: 100 req/min
- 搜索请求（关键词查询）: 10 req/min

限速说明来自 OFF 官方 API 文档，直接写在注释里：
```
// 10 req/min for all search queries; don't use it for a search-as-you-type feature
```

触发限速时，RemoteMediator 返回 `MediatorResult.Error(RateLimitException)`，不崩溃，UI 层展示错误卡片。

file:line 证据: `app/src/commonMain/kotlin/com/maksimowiczm/foodyou/food/infrastructure/openfoodfacts/OpenFoodFactsRateLimiter.kt:7-24`

---

**RULE-04: FTS4 搜索用 prefix 匹配，unicode61 tokenizer，移除变音符号**

```kotlin
// ProductFts 定义
@Fts4(
    contentEntity = ProductEntity::class,
    tokenizer = FtsOptions.TOKENIZER_UNICODE61,
    tokenizerArgs = ["remove_diacritics=2"],
)
```

查询时用 `MATCH :query || '*'`（prefix query），支持实时搜索（输入"appl"能找到"apple"）。

`remove_diacritics=2` 使得 "café" 能匹配 "cafe"，支持欧洲语言。另有 `FoodSearchFtsCyrillicMigration`（schema v32），专门为西里尔字母（俄语等）添加 tokenizer 支持。

file:line 证据:
- `app/src/commonMain/kotlin/com/maksimowiczm/foodyou/food/infrastructure/room/ProductFts.kt:7-13`
- `app/src/commonMain/kotlin/com/maksimowiczm/foodyou/food/search/infrastructure/room/FoodSearchDao.kt:89-91`
- `app/src/commonMain/kotlin/com/maksimowiczm/foodyou/app/infrastructure/room/migration/FoodSearchFtsMigration.kt:1-147`

---

**RULE-05: 最近使用的 Measurement 作为搜索结果的默认建议值**

`LatestMeasurementSuggestion` 是一个数据库视图（window function ROW_NUMBER），对每个 product/recipe 取最近一次使用的 measurement type 和 value：

```sql
SELECT id, productId, recipeId, type, value, epochSeconds
FROM (
    SELECT ms.*, ROW_NUMBER() OVER (
        PARTITION BY productId, recipeId ORDER BY epochSeconds DESC
    ) AS rn
    FROM MeasurementSuggestion AS ms
)
WHERE rn = 1
```

搜索结果 `FoodSearch` 中包含 `measurementType` 和 `measurementValue` 字段（30天内有记录则填充）。这样用户选择"100g 牛奶"后，下次打开搜索，牛奶默认就是 100ml 而不是 1 serving。

file:line 证据:
- `app/src/commonMain/kotlin/com/maksimowiczm/foodyou/food/infrastructure/room/LatestMeasurementSuggestion.kt:7-27`
- `app/src/commonMain/kotlin/com/maksimowiczm/foodyou/food/search/infrastructure/room/FoodSearchDao.kt:181-225`（30天窗口: `epochSeconds >= :nowEpochSeconds - 2592000`）

---

**RULE-06: 食谱搜索时自动排除循环引用（RecipeAllIngredientsView）**

`RecipeAllIngredientsView` 是一个递归视图，追踪所有嵌套 ingredient 关系。搜索时使用：

```sql
(:excludedRecipeId IS NULL OR NOT EXISTS (
    SELECT 1 FROM RecipeAllIngredientsView rai
    WHERE rai.targetRecipeId = r.id
    AND rai.ingredientId = :excludedRecipeId
))
```

当用户在编辑 recipe A 时搜索 ingredient，不会看到"包含 A 作为 ingredient 的其他 recipe B"，防止循环依赖。

file:line 证据: `app/src/commonMain/kotlin/com/maksimowiczm/foodyou/food/search/infrastructure/room/FoodSearchDao.kt:42-52`

---

**RULE-07: 巨型单模块策略（反多模块决策）**

文档 `docs/development/decision-log/0002-minimize-gradle-modules.md` 记录：作者从多模块架构主动合并为单 `app` 模块，原因是"模块带来的 overhead 远大于收益，拖慢了开发速度"。

只有两种情况单独成模块：①barcodescanner（旧式 XML 布局，技术原因隔离）②resources（静态资源）。

这个决策直接影响了代码组织方式：所有业务代码在 `app` 模块内按包名（`food/`, `fooddiary/`, `goals/` 等）组织，而非 Gradle 模块边界。

file:line 证据: `docs/development/decision-log/0002-minimize-gradle-modules.md`

---

## Stage 3.5 — INFERENCE（无直接代码证据的推断）

**INFERENCE-01: 无服务器端，无用户账号，无遥测**
README 明确"No account required, all data stored locally"。代码中 `SponsorshipEntity` 和 `SponsorsNetworkDataSource` 表明有一个赞助信息展示功能（从远端拉取），但无用户标识。INFERENCE: 该网络请求不携带任何设备标识符，纯拉取操作。

**INFERENCE-02: 日记快照的真实动机**
`DiaryRecipeEntity` + `DiaryRecipeIngredientEntity` 存储了日记中食谱条目的快照。代码注释没有直接解释原因。INFERENCE: 这是为了保证历史日记数据的不变性——用户修改食谱后，过去的记录不受影响。这是正确的数据设计，但对性能有一定影响（Recipe 变更不自动传播）。

**INFERENCE-03: v4 与 v3 的根本架构差异**
Decision Log 0005 提到"v3.x.x 有若干根本性设计决策被证明是次优的"，并在 2026-03-02 宣布 v3 只做 bug fix。结合 DB 迁移记录（FoodYou3Migration）推断：v3 → v4 的核心重构包括 Diary 从 Food 解耦（`UnlinkDiaryMigration`）和删除已使用食物事件（`DeleteUsedFoodEvent`）。v3 的 diary 和 food 可能直接通过 FK 绑定，v4 改为快照模式。

**INFERENCE-04: 本地镜像策略的隐患**
Decision Log 0003 提到"这会限制离线访问能力，因为本地镜像需要网络来搜索食物"。代码中没有看到任何 offline fallback 实现。INFERENCE: 当前版本如果断网，搜索 OFF/USDA 的结果仅限于之前缓存过的本地数据，没有明确的 UI 提示告知用户"当前是离线模式"。

**INFERENCE-05: 营养素默认目标值来源**
`DailyGoal.defaultGoals` 中硬编码了详细的维生素矿物质推荐值（如 VitaminD 0.00002g/day = 20µg/day）。这些值与 EU/WHO 推荐摄入量基本一致，但没有任何注释说明来源。INFERENCE: 作者参考了欧盟或 WHO 的 RDA 数据，但未记录参考来源，可能存在版本/地区差异问题。

---

## UNSAID — 未言明的设计意图

**UNSAID-01: NutrientValue.Incomplete 是产品差异化的核心**
当你记录一份"薯条"时，所有来自 OFF 的数据几乎都是 Incomplete（omega3/omega6/每种矿物质几乎都缺）。显示"不完整"比显示"0"诚实得多——用户知道"这个 App 没有数据"和"这个食物真的没有这个营养素"是两件事。大多数竞品（MyFitnessPal、Cronometer 免费版）要么不展示微量营养素，要么把缺失显示为 0。FoodYou 的 Incomplete 语义让用户可以主动发现"我今天碘的摄入情况未知，不是零"。

**UNSAID-02: Meal 的时间窗口暗示了行为设计**
`Meal` 实体有 `from`/`to` 两个 `LocalTime` 字段（不只是名字）。这暗示系统可以根据当前时间自动推荐应该记录到哪个 meal 里。UI 中的 `ChipsMealPicker` 组件利用这个信息做了默认选中。这是一个没有宣传的"智能"特性——用户不需要每次都手动选 meal。

**UNSAID-03: 本地镜像策略是隐私设计的一部分，但没有明说**
Decision Log 写的理由是"一致性"，但本地镜像的另一个效果是：用户的搜索词不会被反复发送给远端服务器。一旦一个食物被缓存，后续搜索完全本地完成。这种设计实际上减少了查询追踪风险，但项目从未把这当成卖点对外宣传。

**UNSAID-04: CSV 导出格式的 header 是 interop 暗语**
`CsvHeaders.kt` 里所有字段都用英文标准名（`Proteins (g)`, `Vitamin B12 (g)`）。这不是随机命名——这个格式与 Cronometer/MyFitnessPal 导出格式部分兼容，用户可以从其他应用导出数据后导入 FoodYou，或反向操作。作者没有明说这个兼容意图，但字段命名的选择暗示了此意。

**UNSAID-05: 赞助系统是生存策略，不是功能**
`SponsorshipEntity` + `SponsorsNetworkDataSource` 存在于代码库中，表明 App 内有赞助商展示功能（推测是 Ko-fi/加密货币支持者的感谢展示）。README 提到"不接受代码贡献，因为 App 产生一些收入"。这透露了一个独立开发者的生存现实：这个 App 是单人维护的商业产品（不是纯公益项目），赞助功能是收入来源的一部分，这解释了为何关闭代码贡献（避免 GPL 授权的贡献者条款复杂化）。

---

## 贡献列表（对 Doramagic SIM-2 卡路里项目的参考价值）

| # | 知识点 | 可借鉴方向 |
|---|---|---|
| 1 | `NutrientValue.Complete/Incomplete` 二元语义 | 设计"营养数据完整度评分"，区分"缺失"和"零值"，给用户诚实的数据质量信号 |
| 2 | 43 字段 `NutritionFacts` 数据模型 | 完整的营养素字段集（含维生素矿物质），可直接参考作为标准 schema |
| 3 | OFF + USDA + Swiss DB 三源融合策略 | 多数据库来源聚合的实现路径，OFF API 字段选择（6 个字段减少带宽） |
| 4 | RemoteMediator + PagingSource 本地镜像 | 搜索缓存策略：远端数据写本地 DB，搜索走本地 FTS，减少重复 API 调用 |
| 5 | FTS4 unicode61 + prefix query | 搜索实现参考，diacritics 支持对多语言场景重要 |
| 6 | 四元组去重（name+brand+barcode+source）| 多源数据防重复写入的严谨规则 |
| 7 | 最近使用 Measurement 作为默认建议 | 个性化体验设计：用户习惯记忆，降低重复输入摩擦 |
| 8 | MacronutrientGoal.Distribution（百分比模式）| 营养目标设定的"比例模式"vs"克重模式"，两种 UX 路径 |
| 9 | Recipe.unpack 食谱原子化 | 食谱的"用完即拆"设计模式，应用于卡路里 App 的复杂餐食分析 |
| 10 | 单模块巨型 app 策略（反教条）| 独立开发者/小团队的实用架构选择，Gradle 模块 overhead 的真实教训 |
| 11 | 营养素默认 RDA 值（DailyGoal.defaultGoals）| 完整的推荐每日摄入量数值，可直接参考作为默认目标 |
| 12 | 隐私优先（本地存储 + 无账号）作为产品差异化 | 对标 Doramagic 隐私定位的具体实现模式 |
