# Soul Extraction: ai-calorie-counter

Extracted: 2026-03-17
Extractor: Doramagic Soul Extractor

---

# repo_facts

- **项目名**: ai-calorie-counter
- **版本**: 0.0.1
- **语言**: JavaScript (Node.js + React 18)
- **规模**: 1 核心 JS 文件（492 行），1 配置 JSON（204 行），1 系统提示 TXT（29 行）
- **平台**: OpenKBS（云端知识库平台，支持 PWA 移动端安装）
- **入口文件**: `index.js`（本地开发服务器启动器，非业务逻辑入口）
- **核心业务模块**: `src/Frontend/contentRender.js`（全部业务逻辑）
- **配置文件**: `app/settings.json`（itemTypes 数据模型 + 服务依赖声明），`app/instructions.txt`（LLM 系统提示）
- **核心依赖**:
  - React 18 + MUI v5（前端 UI）
  - OpenKBS 平台（`openkbs-ui`, `openkbs-chat`, `openkbs-ai-server`, `openkbs-code`）
  - claude-sonnet-4-5（主对话模型，来自 `app/settings.json:6`）
  - IndexedDB（本地搜索引擎，来自 `app/settings.json:8`）
  - Webpack（contentRender 独立打包）
- **数据模型**: 3 个 itemType：food（7 属性）、activity（3 属性）、profile（10 属性）
- **加密策略**: 所有用户数据字段均标注 `"encrypted": true`（唯独 profile.id 例外）

---

# 灵魂发现

**项目本质（1句话）**: 用 LLM 把自然语言/图片描述即时转化为结构化营养记录，让用户不用查表、不用计算，只需描述就能完成健康追踪。

**设计哲学**:
1. **LLM 即解析器**: AI 不是助手，是 ETL 管道——把模糊的食物描述转换成精确的 JSON 数值记录。`app/instructions.txt` 中的 system prompt 直接要求输出 JSON，不要求解释，不要求对话。
2. **聊天消息即数据库记录**: 每条 LLM 回复既是对话消息，也是可编辑的数据表单。`contentRender.js:33` 中 `EditableForm` 直接从消息内容解析 JSON 渲染表单——消息内容和数据库记录是同一份 JSON。
3. **自动保存，用户可改**: `contentRender.js:75-80` 的 `useEffect` 检测到用户有近期活跃（15 秒内），就自动调用 `handleSave`——用户不需要点"添加"，但可以在自动保存前修改数值。
4. **上下文动态注入**: 每次渲染 header 时，`contentRender.js:209-218` 把当日用户数据（profile、已消耗营养、活动记录、剩余配额）拼接进 `instructionSuffix`，让 LLM 下一条回复具备完整当日上下文——无需显式"记忆"系统。
5. **数据完全客户端加密**: 所有业务字段 `encrypted: true`，OpenKBS 平台在传输前加密，服务器看不到用户健康数据。

**心智模型**:
- 用户心智: "我说我吃了什么，手机自动帮我记好了" — 零摩擦记录
- 开发者心智: "聊天记录 = 数据库日志"——每条 AI 消息携带一个 JSON 实体，消息编辑 = 记录更新，消息删除 = 记录删除

---

# concept_cards

## CC-001: LLM-as-Parser（LLM 即解析器）

- **定义**: 使用 LLM 将非结构化食物/活动描述直接转换成预定义 schema 的 JSON，作为确定性 ETL 步骤而非对话步骤
- **是什么**: 系统提示要求 LLM 输出纯 JSON，不输出解释性文字；解析结果直接写入数据库
- **不是什么**: 不是传统"AI 聊天后用户再手工填表"，也不是"AI 给建议用户再决定"
- **证据**:
  - `app/instructions.txt:3-14`: 系统提示完整示例 JSON schema，要求直接输出 JSON
  - `src/Frontend/contentRender.js:8-13`: `parseJSONWithText()` 从消息内容中提取 JSON（支持被文字包围的情况）
  - `src/Frontend/contentRender.js:142-147`: `onRenderChatMessage` 检测到 JSON 就渲染 EditableForm，不渲染原始文本

## CC-002: Message-as-Record（消息即记录）

- **定义**: 聊天消息与数据库记录共享同一个 JSON blob；消息编辑触发记录更新，消息删除触发记录删除
- **是什么**: 消息内容 IS 数据记录，不是数据记录的描述
- **不是什么**: 不是"AI 回复后调用单独 API 创建记录"的两步流程
- **证据**:
  - `src/Frontend/contentRender.js:99-104`: `handleSave` 调用 `chatAPI.chatEditMessage` 把 `itemId` 写回消息内容，记录 ID 和消息内容绑定
  - `src/Frontend/contentRender.js:149-157`: `onDeleteChatMessage` 从消息内容中解析 `itemId` 然后调用 `itemsAPI.deleteItem`——删除消息 = 删除记录
  - `src/Frontend/contentRender.js:33`: `EditableForm` 用 `parseJSONWithText(messages[msgIndex].content)` 初始化表单状态

## CC-003: Weight-as-Multiplier（重量即倍率）

- **定义**: 食物重量字段作为所有其他营养素的比例缩放器；修改重量时，所有 float 字段按比例自动更新
- **是什么**: 重量是营养素密度的"分母"，调整份量不需要用户重新计算每项营养值
- **不是什么**: 不是独立字段各自编辑
- **证据**:
  - `src/Frontend/contentRender.js:59-73`: 监听 `formData.weight` 变化，计算 ratio，对所有 `attrType.startsWith('float')` 且非 weight 的字段乘以 ratio
  - `src/Frontend/contentRender.js:34`: `previousMultiplierFieldRef` 记录上次重量用于计算比例

## CC-004: Dynamic Context Injection（动态上下文注入）

- **定义**: 每次界面渲染时，将当日实时数据（profile + 已消耗营养 + 剩余配额 + 活动列表 + 餐食列表）动态拼接进 LLM 系统提示的 suffix，实现无状态记忆
- **是什么**: 每次对话请求都携带完整当日健康快照，LLM 不需要"记住"，因为每次都被告知
- **不是什么**: 不是独立的记忆系统或向量数据库检索
- **证据**:
  - `src/Frontend/contentRender.js:209-218`: `setRenderSettings` 构建 `instructionSuffix`，拼接 UserProfile、MaxAllowedNutrients、ConsumedNutrients、Activities、Meals
  - `app/instructions.txt:26`: "Use provided user profile data below to accurately adjust calories burned" — 系统提示预留接收 profile 的位置

## CC-005: Mifflin-St Jeor BMR 计算

- **定义**: 应用内置 Mifflin-St Jeor 公式计算基础代谢率（BMR），用于计算"今日可消耗卡路里上限"
- **是什么**: 客户端确定性计算（不依赖 LLM），BMR + 运动消耗 - 卡路里亏缺 = 今日上限
- **证据**:
  - `src/Frontend/contentRender.js:17-19`: `calculateBMR` 函数，男性公式 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
  - `src/Frontend/contentRender.js:199-207`: `maxCalories = BMR + totalActivities.caloriesBurned - calorieDeficit`，再按宏量比例拆分 proteins/carbs/fats 上限

---

# workflow_cards

## WF-001: 食物记录工作流

**步骤**:
1. **用户输入** — 用户用自然语言描述食物（"吃了个苹果"）或上传照片
   - 依据: `app/settings.json:189-194`（optionalServices 包含 speech-to-text）
2. **LLM 解析** — claude-sonnet 按 system prompt schema 返回食物 JSON（name/weight/calories/carbs/proteins/fats/water）
   - 依据: `app/instructions.txt:3-14`
3. **JSON 提取** — `parseJSONWithText()` 从消息中提取 JSON，渲染 `EditableForm`
   - 依据: `src/Frontend/contentRender.js:8-13, 142-147`
4. **自动保存检测** — 若用户在 15 秒内有活跃行为，`useEffect` 触发 `handleSave({ autoCreate: true })`，延迟 1 秒执行（给用户改数值的窗口）
   - 依据: `src/Frontend/contentRender.js:75-80, 100-101`
5. **记录持久化** — `itemsAPI.createItem` 写入数据库，返回 `itemId`
   - 依据: `src/Frontend/contentRender.js:91-98`
6. **消息绑定** — `chatAPI.chatEditMessage` 把 `itemId` 写回聊天消息，实现消息↔记录双向绑定
   - 依据: `src/Frontend/contentRender.js:99-101`
7. **Header 实时更新** — IndexedDB query 响应变化，`StatsProgressBars` 重新计算今日进度条
   - 依据: `src/Frontend/contentRender.js:432-438`

**失败模式**:
- JSON 解析失败：`parseJSONWithText` 返回 null，`onRenderChatMessage` 返回 null，消息以纯文本显示（无表单），记录不创建
- `formData.itemId` 已存在时 `autoCreate` 不再触发（`!formData?.itemId` guard），防止重复创建
  - 依据: `src/Frontend/contentRender.js:76`
- `hasActivity(15)` 检测失败（用户没有互动）：不自动保存，用户必须手动点 Add 按钮

## WF-002: 用户 Profile 设置工作流

**步骤**:
1. **初始状态检测** — `Header` 组件启动时从 IndexedDB 拉取 profile；`profile === null` 时组件返回 null（不渲染）
   - 依据: `src/Frontend/contentRender.js:456-462, 467`
2. **无 profile 时显示表单** — `!profile` 时渲染 `ProfileForm`，默认值预填（目标体重减少、宏量 45/30/25）
   - 依据: `src/Frontend/contentRender.js:324-331, 484`
3. **百分比自动平衡** — 用户修改任一宏量百分比时，第三个字段自动 = 100 - 另外两个
   - 依据: `src/Frontend/contentRender.js:345-350`
4. **保存验证** — 提交前验证所有字段非空且三项百分比加总等于 100
   - 依据: `src/Frontend/contentRender.js:359-368`
5. **写入数据库** — 固定 `itemId: 'profile'`（单例），更新/创建皆可
   - 依据: `src/Frontend/contentRender.js:374`
6. **上下文注入激活** — `profile` 状态更新触发 `StatsProgressBars` 的 `useEffect`，将 profile 数据注入 `instructionSuffix`
   - 依据: `src/Frontend/contentRender.js:209-212`

**失败模式**:
- 三项百分比不等于 100：所有三个字段标红，阻止保存（`contentRender.js:364-367`）
- 任意字段为空：字段标红，阻止保存
- Profile 尚未保存时，Header 仅渲染 ProfileForm，不渲染 StatsProgressBars 也不渲染日期导航（健康数据依赖 profile）

## WF-003: 删除记录工作流

**步骤**:
1. **删除聊天消息** — 用户点击消息删除按钮
2. **解析消息中的 itemType + itemId** — `onDeleteChatMessage` 从消息 content JSON 中读取
   - 依据: `src/Frontend/contentRender.js:149-153`
3. **调用 itemsAPI.deleteItem** — 传入 `itemId`、`itemType`、`KBData`
   - 依据: `src/Frontend/contentRender.js:155`
4. **setBlockingLoading** — 操作期间 UI 阻塞（防止并发修改）
   - 依据: `src/Frontend/contentRender.js:154, 156`

**失败模式**:
- 消息无 `itemType` 或无 `itemId`（如 profile 查询类消息）：`onDeleteChatMessage` 返回 null，不触发删除——消息被删，但没有对应记录需要删

---

# decision_rule_cards

## DR-001: 自动保存触发规则

- **IF** LLM 回复包含有效 JSON（itemType 为 food/activity）
- **AND** 消息中没有 `itemId`（说明尚未保存）
- **AND** `window.openkbs.hasActivity(15)` 返回 true（用户 15 秒内有互动）
- **THEN** 延迟 1000ms 后自动调用 `handleSave({ autoCreate: true })`
- **上下文**: 用于减少用户操作摩擦——不需要点 Add，但 1 秒延迟给了修改窗口
- **证据**: `src/Frontend/contentRender.js:75-80`

## DR-002: 消息渲染模式切换规则

- **IF** 消息 role 为 `assistant`
- **AND** 消息 content 通过 `parseJSONWithText` 解析出有效 JSON
- **THEN** 渲染 `EditableForm` 替代原始文本
- **ELSE** 返回 null（平台默认文本渲染接管）
- **上下文**: 区分"数据回复"和"对话回复"（如建议、问候），只有数据回复显示表单
- **证据**: `src/Frontend/contentRender.js:142-147`

## DR-003: 重量缩放保护规则

- **IF** `formData.weight` 发生变化
- **AND** 新重量 > 0
- **AND** 上次重量不为 undefined
- **THEN** 对所有 `attrType.startsWith('float')` 且 `attrName !== 'weight'` 的字段乘以 `currentWeight / previousWeight`
- **ELSE IF** 上次重量为 undefined（初始加载）: ratio = 1（不缩放）
- **上下文**: 防止用户修改份量时需要手动重算所有营养值；weight=0 时不触发（防止除零）
- **证据**: `src/Frontend/contentRender.js:59-73`

## DR-004: Profile 强制前置规则

- **IF** IndexedDB 中无 profile 记录
- **THEN** Header 仅显示 ProfileForm，隐藏所有营养统计和日期导航
- **IF** Profile 存在
- **THEN** 显示带日期导航的 StatsProgressBars（可切换 Profile 编辑视图）
- **上下文**: BMR 计算和营养上限计算依赖 profile 数据，无 profile 则无法计算任何目标值
- **证据**: `src/Frontend/contentRender.js:467, 476, 484`

## DR-005: 宏量上限计算规则

- **IF** profile 存在（含 gender/age/weight/height/calorieDeficit/carbPercentage/proteinPercentage/fatPercentage）
- **THEN**:
  - BMR = Mifflin-St Jeor 公式（`contentRender.js:17-19`）
  - maxCalories = BMR + caloriesBurned_today - calorieDeficit
  - maxProteins = maxCalories × proteinPercentage% ÷ 4（蛋白质 4kcal/g）
  - maxCarbs = maxCalories × carbPercentage% ÷ 4（碳水 4kcal/g）
  - maxFats = maxCalories × fatPercentage% ÷ 9（脂肪 9kcal/g）
- **上下文**: 热量守恒定律客户端实现；运动加分机制（运动后可多吃）
- **证据**: `src/Frontend/contentRender.js:198-207`

## DR-006: LLM 上下文注入触发规则

- **IF** profile 数据存在
- **AND** `renderSettings.instructionSuffix` 中尚不包含 `'\nUserProfile:\n'`（防重复注入）
- **THEN** 将 UserProfile + MaxAllowedNutrients + ConsumedNutrients + Activities + Meals 全部序列化为 JSON 追加至 instructionSuffix
- **上下文**: 确保每次对话 LLM 都知道用户的今日状态；用字符串包含检测防止 profile 变更时重复追加
- **证据**: `src/Frontend/contentRender.js:209-218`

---

# UNSAID（暗坑）

## UNSAID-001: JSON 解析对 LLM 输出格式极度脆弱
- **描述**: `parseJSONWithText` 用正则 `/(.*?)`?`?`?\s*([\{\[].*?[\}\]])\s*`?`?`?(.*)/s` 提取 JSON；若 LLM 输出多个 JSON 对象、嵌套数组、或 JSON 中有换行的注释，正则 match 可能失败或提取错误块
- **暗坑**: 系统提示没有要求"仅输出 JSON，不要输出任何其他文字"，而是说"generate as a valid JSON string"——LLM 完全可以在 JSON 前后加解释性文字；`parseJSONWithText` 虽然处理了这种情况，但 JSON 内部注释剥除（`replace(/\/\/.*|\/\*[\s\S]*?\*\//g, '')`）可能误删 food name 中的 `//`
- **发现来源**: `src/Frontend/contentRender.js:9-11` + `app/instructions.txt:14`（JSON 示例中有结尾逗号，是非法 JSON）

## UNSAID-002: instructionSuffix 无限增长 + 防重复检测错误
- **描述**: `instructionSuffix` 用 `includes('\nUserProfile:\n')` 防止重复追加，但这个检测只在首次触发时有效；若用户更新 profile，`setRenderSettings` 的 `prev =>` 函数里的 `suffix` 来自 `prev.instructionSuffix`，仍包含旧 UserProfile——旧数据不会被清除，新数据追加到末尾，导致 LLM 看到两份 UserProfile
- **暗坑**: 今日营养数据每次渲染都可能追加新版本（虽然有 `includes` 检测拦住了 UserProfile，但 MaxAllowedNutrients 也是同一个 `includes` 检测）——实际上只要 suffix 里有 `\nUserProfile:\n` 就全部跳过，所以今日营养**不会随进食更新**
- **发现来源**: `src/Frontend/contentRender.js:209-220`

## UNSAID-003: autoCreate 的 1 秒延迟窗口与用户感知不匹配
- **描述**: 自动保存在 1000ms 后执行（`setTimeout(..., autoCreate ? 1000 : 0)`），用户在这 1 秒内可以修改数值；但 UI 没有倒计时或任何提示，用户不知道"我还有 1 秒可以改"——实际上多数用户修改时间超过 1 秒，autoCreate 会在用户还没改完时保存脏数据
- **暗坑**: 保存后 `handleSave` 调用 `chatAPI.chatEditMessage` 同步消息，这时即使用户继续在表单里改值，`setMessages` 也会把消息内容更新回已保存的值——用户的修改会被覆盖
- **发现来源**: `src/Frontend/contentRender.js:75-80, 99-104`

## UNSAID-004: profile 为单例但 IndexedDB 没有强制唯一约束
- **描述**: ProfileForm 用固定 `itemId: 'profile'` 创建/更新 profile，依赖 `itemsAPI.updateItem` 的 upsert 语义；但 `indexedDB.db['profile'].toItems()` 取第一条（`[0]`），若平台行为导致出现两条 profile（如 itemId 冲突），只有第一条被使用，第二条静默忽略
- **发现来源**: `src/Frontend/contentRender.js:458, 374`

## UNSAID-005: 卡路里亏缺（calorieDeficit）无上下限约束
- **描述**: ProfileForm 允许用户输入任意 `calorieDeficit` 值；若输入值大于 BMR + 运动消耗，`maxCalories` 会变为负数，所有进度条会显示 0% 或 NaN，LLM 收到的 `MaxAllowedNutrients` 也会是负值——LLM 可能产生不合理建议
- **发现来源**: `src/Frontend/contentRender.js:199-207`（没有 Math.max(0, ...) 保护）

## UNSAID-006: 全数据 encrypted 但 embeddingModel 为 none
- **描述**: `app/settings.json:7` 设置 `"embeddingModel": "none"`，即不做向量嵌入；`embeddingTemplate` 定义了但从不使用。这意味着 IndexedDB 只能做时间范围查询（`where('updatedAt').between(...)`），无法做语义搜索。历史数据只能按日期浏览，不能搜索"我上次吃苹果是什么时候"
- **发现来源**: `app/settings.json:7-8` + `src/Frontend/contentRender.js:432-438`

---

# 对"食物卡路里 skill"的贡献

## 可复用知识列表

**K-001: LLM 系统提示 JSON Schema 设计模式**
- 完整可复用的食物营养 JSON schema（name/weight/calories/carbs/proteins/fats/water）
- 活动记录 JSON schema（name/caloriesBurned/durationInMinutes）
- 来源: `app/instructions.txt:3-24`

**K-002: 混合文本+JSON 的 LLM 输出解析技术**
- `parseJSONWithText` 正则模式：支持 JSON 被 markdown 代码块或解释性文字包围
- JSON 内注释清洗：`replace(/\/\/.*|\/\*[\s\S]*?\*\//g, '')`
- 来源: `src/Frontend/contentRender.js:8-13`

**K-003: 重量缩放营养素计算**
- 实现思路：监听 weight 字段变化，用 ratio = new/old 缩放所有 float 属性
- 边界处理：初始加载（ratio=1）、重量为 0（跳过）
- 来源: `src/Frontend/contentRender.js:59-73`

**K-004: Mifflin-St Jeor BMR 公式（客户端实现）**
- 男性: 88.362 + (13.397 × 体重kg) + (4.799 × 身高cm) - (5.677 × 年龄)
- 女性: 447.593 + (9.247 × 体重kg) + (3.098 × 身高cm) - (4.330 × 年龄)
- 每日上限 = BMR + 运动消耗 - 卡路里亏缺
- 宏量换算: 蛋白质/碳水 4kcal/g，脂肪 9kcal/g
- 来源: `src/Frontend/contentRender.js:17-19, 202-207`

**K-005: 聊天消息与数据库记录双向绑定架构**
- 模式：LLM 输出 JSON → 渲染表单 → 保存时将 itemId 写回消息内容 → 删除消息时从消息内容读 itemId 删记录
- 优势：无需额外"记录关联"数据结构，消息内容即是记录的完整状态
- 来源: `src/Frontend/contentRender.js:87-111, 149-157`

**K-006: 动态 LLM 上下文注入（instructionSuffix 模式）**
- 模式：在 UI 层将实时计算数据（今日营养、剩余配额）序列化追加至系统提示 suffix
- 格式参考: UserProfile → MaxAllowedNutrientsToday → ConsumedNutrientsToday → ActivitiesToday → MealsToday
- 无需独立记忆系统，前端状态即上下文
- 来源: `src/Frontend/contentRender.js:209-218`

**K-007: 宏量百分比自动平衡 UI 模式**
- 三字段联动：修改任一值时，第三个字段 = 100 - 另两个；配合总和验证（≠100 则阻止保存）
- 来源: `src/Frontend/contentRender.js:345-350, 364-367`

**K-008: 暗坑警告——JSON Schema 中的非法结尾逗号**
- `app/instructions.txt:14` 的示例 JSON 有结尾逗号（`"water": 156,`），这是非法 JSON，真实 LLM 可能照抄格式导致 `JSON.parse` 失败
- 建议: 系统提示中的示例 JSON 必须是合法 JSON，或在解析前额外做 trailing comma 清洗
- 来源: `app/instructions.txt:14`（INFERENCE + 代码验证）
