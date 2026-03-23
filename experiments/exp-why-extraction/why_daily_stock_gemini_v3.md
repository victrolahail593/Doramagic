# WHY 提取报告：daily_stock_analysis（Gemini v3 — Stage 0 v2）

- why_id: W001
  type: selection
  claim: "选择 LiteLLM 统一管理多样的 LLM，是为了在 CI/CD 环境中通过 YAML 配置实现灵活的、可动态切换的模型路由与回滚策略。"
  reasoning_chain: "项目需要支持多种 LLM (Gemini, OpenAI, Claude等) → 直接管理多套 SDK 和 API Key 会使 CI/CD 流程复杂化 → LiteLLM 提供了统一接口 → 更重要的是，它支持通过 YAML (`LITELLM_CONFIG_YAML`) 进行高级配置 → 这使得在 GitHub Actions 中可以动态注入模型、设置回滚和负载均衡策略，而无需修改代码，极大提升了运维灵活性。"
  evidence:
    - type: CODE
      source: "requirements.txt:L47-L49"
    - type: CODE
      source: ".github/workflows/daily_analysis.yml:L101-L103"
    - type: DOC
      source: "README.md:L49, L88"
  contrast: "不使用 LiteLLM，而是为每个 LLM (Gemini, OpenAI, Claude) 编写独立的适配层。这将导致在 CI 脚本中需要编写大量 `if/else` 逻辑来根据 `secrets` 的存在与否选择 `base_url` 和 `api_key`，并且难以实现跨供应商的自动回滚或负载均衡，每次模型策略调整都可能需要修改 Python 或 Shell 脚本。"

- why_id: W002
  type: architecture
  claim: "系统核心功能（如数据获取、机器人平台）采用基于抽象基类（ABC）的插件化架构，以实现高内聚、低耦合的扩展性。"
  reasoning_chain: "系统需要对接多种外部服务，如不同的数据源 (Akshare, YFinance) 和机器人平台 (飞书, 钉钉) → 将每个服务的具体实现硬编码在主逻辑中会违反开闭原则，导致维护困难 → 通过定义 `BaseFetcher` 和 `BotPlatform` 等抽象基类，强制规定了插件的接口 → 核心逻辑仅与抽象接口交互，新服务的集成只需添加新的子类实现，无需改动核心代码。"
  evidence:
    - type: CODE
      source: "data_provider/base.py:L2081-L2099"
    - type: CODE
      source: "bot/platforms/base.py:L4-L44"
    - type: CODE
      source: "data_provider/akshare_fetcher.py:L148"
  contrast: "采用非插件化的过程式设计，在数据管理或机器人消息分发模块中使用巨大的 `if/elif/else` 结构来判断数据源或平台类型。这种做法会导致每次增加新的数据源或平台时，都必须修改这个核心模块，增加代码冲突的风险，并使单元测试变得异常复杂。"

- why_id: W003
  type: architecture
  claim: "项目被设计为以 GitHub Actions 为核心的“无服务器”应用，旨在最大程度地降低用户的部署和维护成本。"
  reasoning_chain: "个人或小团队用户通常没有专门的服务器资源，也缺乏 24/7 运维能力 → 要求用户部署一个持续运行的服务（如 Docker 容器或 VM）会构成很高的使用门槛 → GitHub Actions 提供了免费的、基于事件（如 `cron` 定时）的计算资源 → 因此，项目将核心业务逻辑封装在可以在 Actions 环境中运行的脚本中，并完全通过 Secrets 和 `workflow_dispatch` 进行配置和控制，实现了零成本、免运维的自动化运行。"
  evidence:
    - type: CODE
      source: ".github/workflows/daily_analysis.yml:L5-7"
    - type: DOC
      source: "README.md:L69-L72"
    - type: INFERENCE
      source: "项目的配置方式（`secrets.*`, `vars.*`）和触发机制（`schedule`, `workflow_dispatch`）完全是围绕 GitHub Actions 的特性设计的。"
  contrast: "将项目设计成一个需要持久化运行的 Web 服务器或后台服务。这种方式虽然更传统，但要求用户自行解决服务器购买/租赁、环境配置、进程守护、日志管理、网络安全等一系列运维问题，对于目标用户群体来说门槛过高。该项目舍弃了实时性（只能定时运行），换取了极低的部署成本。"

- why_id: W004
  type: implementation
  claim: "在数据处理入口处强制对股票代码进行“归一化”，以保证所有下游的数据获取器（Fetcher）接收到的都是格式统一、干净的数据。"
  reasoning_chain: "用户输入的股票代码格式多样（如 'sh600519', '600519.SH', 'AAPL'）→ 如果每个数据获取器都自行处理这些格式，会产生大量重复代码且容易出错 → 项目在 `data_provider/base.py` 中定义了一个 `normalize_stock_code` 函数 → 该函数被设计在数据获取的管理器（Manager）层面统一调用 → 从而确保任何一个具体的 Fetcher 实现（如 Akshare, YFinance）都无需关心代码格式的预处理，只需处理标准化的代码，降低了 Fetcher 的实现复杂度和潜在错误。"
  evidence:
    - type: CODE
      source: "data_provider/base.py:L1968-L2001"
    - type: DOC
      source: "data_provider/base.py:L1995-L1998"
  contrast: "将代码归一化的责任下放给每一个具体的 `BaseFetcher` 子类。这会导致 `normalize_stock_code` 的逻辑在 `AkshareFetcher`, `TushareFetcher` 等多个文件中被重复实现。一旦归一化规则需要变更（例如，支持新的交易所代码），就需要修改所有相关文件，增加了维护成本和引入不一致性的风险。"

- why_id: W005
  type: constraint
  claim: "主动将 `tiktoken` 库的版本上限锁定在 `0.12.0` 以下，是为防止其新版本的插件注册机制破坏依赖环境的稳定性。"
  reasoning_chain: "项目依赖 `tiktoken` 进行 token 计算 → 某个新版本（`0.12.0` 及以上）引入了破坏性变更（插件注册机制）→ 这导致了实际的运行时问题（记录在 Issue #537）→ 为保证在自动化环境（如 GitHub Actions）中的可靠运行，必须避免这种不可预见的上游依赖破环 → 因此，在 `requirements.txt` 中明确添加了 `<0.12.0` 的版本约束，并附上注释说明原因，以牺牲新特性为代价换取系统的稳定性。"
  evidence:
    - type: CODE
      source: "requirements.txt:L48"
    - type: DOC
      source: "`requirements.txt:L48` 的注释 `(pin <0.12 to avoid plugin registration issues, #537)`"
  contrast: "遵循常规的依赖管理方式，只设置最低版本或一个宽松的版本范围，如 `tiktoken>=0.8.0`。这将自动拉取最新版本的 `tiktoken`，虽然能享受到新功能和修复，但也使项目暴露在上游库引入破坏性变更的风险之下，可能导致 CI/CD 流程在没有代码改动的情况下突然失败。"

- why_id: W006
  type: architecture
  claim: "基本面数据获取流程采用“尽力而为”的软超时（Fail-Open）设计，是为了优先保障核心报告的生成与送达，即便部分补充数据缺失。"
  reasoning_chain: "基本面数据（如估值、增长率）依赖多个第三方 API，这些 API 的稳定性不可控 → 如果采用严格的硬超时或失败即终止（Fail-Closed）策略，任何一个辅助 API 的延迟或失败都会导致整个分析任务中断，用户将收不到任何报告 → 项目的核心价值是每日推送“决策仪表盘” → 因此，架构选择牺牲数据的完整性来换取系统的可用性。当基本面数据获取超时，流程会降级并继续执行核心的技术面和 AI 分析，确保主报告总能生成。"
  evidence:
    - type: DOC
      source: "README.md:L163-L167"
    - type: CODE
      source: "README.md:L157-L162"
  contrast: "采用“全有或全无”（Fail-Closed）的硬超时策略。在该策略下，一旦获取基本面数据的子任务失败，整个分析流程将立即终止并报错。这种设计保证了每份成功生成的报告都包含完整的数据，但大大降低了系统的健壮性和用户体验，因为任何一个非核心依赖的抖动都可能导致核心功能的“雪崩式”失败。"
