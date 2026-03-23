# Exp-UNSAID-01: LLM Seed Baseline 测试结果

## 实验设计
- **Ground truth**: python-dotenv 21 张 UNSAID 卡片（DR-100 ~ DR-120）
- **测试模型**: Sonnet 4.6 + Gemini 2.5 Pro
- **Prompt**: "列出 python-dotenv 所有 undocumented gotchas / hidden traps / unintuitive behaviors"
- **约束**: 纯训练集知识，不允许搜索或读文件

## 逐条对照评分

| DR-ID | Ground Truth 概要 | Sonnet | Gemini |
|-------|-------------------|--------|--------|
| DR-100 | Docker Compose 与 python-dotenv 对同一 .env 文件解析结果不同（引号/插值语义差异） | ⚠️ 提到 Docker 但未涉及 Compose 解析差异 | ⚠️ 类似，提到 Docker env_file 优先级 |
| DR-101 | find_dotenv() 从调用文件目录向上搜索（sys._getframe()），不是从 cwd | ❌ **方向说反了**（说从 cwd 搜索） | ⚠️ 说"从调用脚本位置"，方向对但不精确 |
| DR-102 | override=False 默认行为，已有环境变量静默优先 | ✅ | ✅ |
| DR-103 | 多行值 load_dotenv() 截断但 dotenv_values() 正确返回 | ⚠️ 提到多行截断但未提两个 API 差异 | ⚠️ 类似 |
| DR-104 | 旧版本用系统 locale 编码（GBK/CP1252），非 UTF-8 | ✅ | ❌ 未提到 |
| DR-105 | .env 缺失时静默返回 False，不抛异常 | ✅ | ✅ |
| DR-106 | 未引用值中 # 被当做行内注释，静默截断 URL/密码 | ✅ | ❌ **说反了**（说行内注释不被剥离） |
| DR-107 | 单引号保留字面量，双引号处理转义序列 | ✅ | ❌ 只提到引号剥离，未提转义差异 |
| DR-108 | 只有 ${VAR} 触发插值，裸 $VAR 保留字面量（不同于 Bash） | ❌ 未提到此具体行为 | ❌ 未提到 |
| DR-109 | 无类型转换，一切为字符串，if os.getenv('DEBUG') 永远为 True | ❌ 未提到 | ✅ |
| DR-110 | 模块顶层 load_dotenv() 导致 .env 值泄漏到测试环境 | ✅ | ⚠️ 提到 pytest 但角度不同（时序问题） |
| DR-111 | 生产环境不要用 .env，用 secrets manager，PYTHON_DOTENV_DISABLED | ❌ 未提到此最佳实践 | ❌ 未提到 |
| DR-112 | pip install python-dotenv vs dotenv（PyPI 上有同名不同包） | ✅ | ✅ |
| DR-113 | Flask 自动加载 .env，手动 load_dotenv() 导致双重加载 | ⚠️ 提到 Flask 但角度不同 | ✅ |
| DR-114 | set_key() 默认用单引号包裹，写入的转义序列读回时不解释 | ❌ 未提到 | ❌ 未提到 |
| DR-115 | 无缓存，每次调用重新读取解析文件 | ✅ | ⚠️ 提到 I/O 开销但未明确说"无缓存" |
| DR-116 | dotenv_values() 对无值 key 返回 None，load_dotenv() 跳过 | ⚠️ 部分提到 | ⚠️ 提到空值 vs 未定义但不精确 |
| DR-117 | 必须 .gitignore .env，提交 .env.example | ✅ | ✅ |
| DR-118 | override=False 时 ${VAR} 插值先解析 os.environ，级联影响 | ❌ 未提到此具体级联 | ⚠️ 提到插值顺序依赖 |
| DR-119 | Docker 中 WORKDIR 与调用文件目录不同，静默找不到 .env | ⚠️ 在 Docker 条目中部分覆盖 | ⚠️ 在 Docker 条目中部分覆盖 |
| DR-120 | load_dotenv() 污染全局 os.environ，推荐 dotenv_values() | ⚠️ 提到差异但未给明确建议 | ❌ 未提到 |

## 统计汇总

| 评级 | Sonnet | Gemini |
|------|--------|--------|
| ✅ 完全命中 | 9 | 6 |
| ⚠️ 部分命中 | 5 | 7 |
| ❌ 未命中 | 6 | 6 |
| ❌ **说错（hallucination）** | **1** (DR-101 方向反了) | **2** (DR-106 行为反了 + 声称 find_dotenv 有缓存) |
| **总计** | 21 | 21 |

## 覆盖率计算

| 计算方式 | Sonnet | Gemini | 平均 |
|---------|--------|--------|------|
| 严格（只算 ✅） | 9/21 = **43%** | 6/21 = **29%** | **36%** |
| 宽松（✅ + ⚠️） | 14/21 = **67%** | 13/21 = **62%** | **64%** |

## LLM 额外产出（ground truth 之外）

| | Sonnet 独有发现 | Gemini 独有发现 |
|---|---|---|
| 有效 | 空白字符处理差异、export 前缀处理、find_dotenv 返回空字符串、exhausted stream、内存中明文 secrets、无 hot-reload | export 前缀处理、find_dotenv 返回值类型 |
| 存疑 | — | find_dotenv 缓存（可能是 hallucination） |

## 关键发现

### 1. "60-70%" 估计惊人地准确
宽松覆盖率 64% 几乎完美验证了调研文档的估计。LLM 训练集确实覆盖了大部分 UNSAID。

### 2. LLM 盲区有清晰的模式
两个模型都没命中的 UNSAID（真正的信息增量）：

| DR-ID | 内容 | 为什么 LLM 不知道 |
|-------|------|-----------------|
| DR-108 | ${VAR} vs $VAR 插值语法差异 | 太具体，需要读源码 |
| DR-111 | PYTHON_DOTENV_DISABLED 环境变量 | 文档角落的功能 |
| DR-114 | set_key() 单引号默认包裹行为 | 非常规 API，用的人少 |

共同特征：**越是"角落"的行为，LLM 越不知道**。这正是社区数据的价值——Issues 里报告的恰恰是这些边界情况。

### 3. LLM 会给出错误信息
- Sonnet 把 find_dotenv() 的搜索方向说反了
- Gemini 把 # 行内注释行为说反了（影响更严重）
- Gemini 编造了 find_dotenv() 缓存机制

这意味着：**LLM seed 不能直接用，必须经过社区证据验证**。这反过来证明了 Evidence chain 的必要性。
