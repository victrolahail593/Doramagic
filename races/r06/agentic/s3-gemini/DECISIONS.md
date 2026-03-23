# Design Decisions - Stage 1.5 Agentic Extraction (S3-Gemini)

## 1. Agent 循环设计
我们采用了基于“假说驱动”的循环逻辑。每个假说作为一个独立探索单元，分配固定的探索步数（默认为 5 步），以防止 Agent 在单个假说上陷入死循环或过度消耗 Token。

## 2. 工具集定义
- **工具化结论**: 引入了 `finalize_hypothesis` 工具，让 LLM 主动宣告探索结束并提交 Claim。这比解析 LLM 的自然语言回复更稳定。
- **真实代码访问**: `read_file`, `search_repo`, `list_tree` 直接操作 `repo_local_path`。
- **行号支持**: `read_file` 返回带有行号的内容，方便 LLM 在生成 `ClaimRecord` 时提供精确的 `EvidenceRef`。

## 3. 模型无关性实现
- 严格遵守不直接导入特定厂商 SDK 的原则。
- 仅通过 `LLMAdapter` 及其 `generate_with_tools` 接口进行交互。
- 使用 `CapabilityRouter` 进行 Stage 级别的模型能力路由，确保选择了具备 `tool_calling` 能力的模型。

## 4. 证据绑定策略
- Confirmed Claim 必须通过 `finalize_hypothesis` 工具显式绑定证据。
- 探索过程中产生的观察结果会被记录在 `ExplorationLogEntry` 中，形成完整的证据链。

## 5. 预算与终止控制
- 全局预算：通过 `ctx` 跟踪全局 `tool_calls` 和 `prompt_tokens`。
- 局部控制：单假说最大步数控制。
- 终止原因：所有假说解决或达到全局预算上限。
