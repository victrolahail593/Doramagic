# Group A — Single-Pass Soul Extraction: OpenClaw

**Target**: `/tmp/openclaw`
**Method**: Single-pass scan — README, VISION, CLAUDE/AGENTS, SECURITY, CONTRIBUTING, docs/, CHANGELOG, key config files
**Date**: 2026-03-18

---

## WHY 列表（设计哲学 / 架构决策）

### W1. 为什么选 TypeScript 而非更"工程化"的语言
OpenClaw 本质是编排系统（prompts, tools, protocols, integrations），TypeScript 的选择是为了保持"hackable by default"——知名度高、迭代快、容易阅读修改和扩展。
**证据**: `VISION.md:95-97`

### W2. 为什么不把 MCP 内置进 core
MCP 通过外部桥接工具 `mcporter` 接入，而非 core 内建。原因：可以不重启 gateway 就增删 MCP server，保持 core 工具/上下文面精简，减少 MCP 变动对 core 稳定性和安全性的冲击。
**证据**: `VISION.md:74-83`

### W3. 为什么新 skill 必须先发 ClawHub，不进 core
核心 skill 添加要求极高门槛（产品或安全理由），否则发布到 `clawhub.ai`。目的：保持 core 精简，避免功能蔓延。
**证据**: `VISION.md:69-70`, `VISION.md:101`

### W4. 为什么 memory 是"exclusive slot"而不是多个并行插件
Memory 是特殊插件槽，同时只能有一个 memory 插件激活。未来计划收敛到一个推荐默认路径。
**证据**: `VISION.md:63-64`

### W5. 为什么 Gateway 是"控制平面"而非产品本身
Gateway 只是 control plane，产品是 assistant。设计上分离了路由（Gateway）和执行（Node/Agent）。
**证据**: `README.md:22-25`, `SECURITY.md:169-176`

### W6. 为什么安全模型是"单用户个人助手"而非多租户
OpenClaw 的安全模型是 personal assistant（一个 trusted operator，可以有多个 agents），不是 shared multi-tenant bus。如果多用户需要 OpenClaw，用一台 VPS/host per user。
**证据**: `SECURITY.md:92-107`, `docs/gateway/security/index.md:11-24`

### W7. 为什么 exec 默认 sandbox 是 off
`agents.defaults.sandbox.mode` 默认是 `off`，exec host-first。这是有意识的单用户 trusted operator 模型决策，而非设计疏忽。
**证据**: `SECURITY.md:103-106`

### W8. 为什么插件在进程内运行（in-process），不沙箱化
原生插件与 Gateway 在同一进程运行，信任级别等同本地代码。这是架构决策：安装/启用即信任，不是沙箱边界绕过。
**证据**: `SECURITY.md:108-114`, `docs/tools/plugin.md:131-139`

### W9. 为什么 session identifier 不是授权凭证
sessionKey / session ID 是路由控制（routing controls），不是 per-user 授权边界。多人共用一个 session 是预期行为，不是 bug。
**证据**: `SECURITY.md:97-98`

### W10. 为什么"terminal-first"而非 GUI 优先上手
OpenClaw 当前是 terminal-first by design：让用户明确看到 docs、auth、permissions 和 security posture。不希望便捷封装掩盖关键安全决策。
**证据**: `VISION.md:87-91`

### W11. 为什么版本命名用 YYYY.M.D 而非 semver
CalVer 风格（`2026.3.14`），不是 `1.x.x`。反映快速迭代、日期驱动的 cadence。Beta 先于 stable，stable 在 beta 验证后才跟进。
**证据**: `docs/reference/RELEASING.md:18-32`, `package.json:3`

### W12. 为什么不允许 agent-hierarchy 框架（manager of managers）
明确拒绝"nested planner trees as default architecture"和"heavy orchestration layers"。理由：会复制已有 agent/tool 基础设施，增加不必要的复杂度。
**证据**: `VISION.md:106-108`

### W13. 为什么 MEMORY.md 优先于 memory.md（breaking change）
只加载一个 root memory bootstrap 文件。`MEMORY.md` 胜出，`memory.md` 仅在 `MEMORY.md` 不存在时使用。修复了 case-insensitive Docker 挂载上的重复注入问题。
**证据**: `CHANGELOG.md:93`

### W14. 为什么 Pi session transcripts 用 parentId DAG 而非线性 JSONL
transcript 是 `parentId` chain/DAG，不能直接 append raw JSONL。缺失 `parentId` 会截断 leaf path，破坏 compaction/history。必须通过 `SessionManager.appendMessage()` 写入。
**证据**: `src/gateway/server-methods/AGENTS.md:3`

### W15. 为什么 ACP bridge 不支持 per-session MCP servers
ACP bridge 是 Gateway-backed 桥接，不是 ACP-native editor runtime。per-session MCP 请求被明确 reject，而非静默忽略，让 IDE 客户端看到明确的桥接限制。
**证据**: `docs.acp.md:37`, `CHANGELOG.md:348`

### W16. 为什么 plugin 安装只接受 registry-only npm spec，拒绝 git/url/file/semver range
只接受 package name + exact version 或 dist-tag，拒绝 git/URL/file spec 和 semver range。目的：控制供应链风险，确保 plugin 来源可审计。
**证据**: `docs/tools/plugin.md:41-45`

### W17. 为什么 discovery + config validation 必须在不执行 plugin 代码的情况下工作
设计边界：manifest/schema metadata 层面的 discovery 和 config validation 不应执行 plugin 代码。这让 OpenClaw 在完整运行时激活前就能 validate config、解释缺失/禁用的 plugin、构建 UI/schema hint。
**证据**: `docs/tools/plugin.md:81-86`

### W18. 为什么 commit 用 `scripts/committer` 而非手动 `git add/commit`
保持 staging 范围严格。避免意外包含无关文件。
**证据**: `CLAUDE.md:155`

### W19. 为什么有多套 vitest 配置文件而不是一个统一的
按测试类型分离（unit/e2e/channels/extensions/gateway/live/scoped），支持独立运行不同 profile，允许不同的 pool/worker 配置。
**证据**: 根目录有 `vitest.config.ts`, `vitest.channels.config.ts`, `vitest.e2e.config.ts`, `vitest.unit.config.ts`, `vitest.live.config.ts`, `vitest.extensions.config.ts`, `vitest.gateway.config.ts`

### W20. 为什么 CI 有 docs-scope 探测步骤
docs-only 变更跳过重量级 job（test、build、Windows、macOS、Android），节省 CI 资源。fail-safe：探测失败则运行全部 job。
**证据**: `.github/workflows/ci.yml:14-46`

### W21. 为什么 Swabble 用 Apple Speech.framework 而非 whisper.cpp
macOS 26 的 SpeechAnalyzer + SpeechTranscriber 是 on-device，无网络调用。不需要维护 whisper 模型，利用 Apple 原生 API 提供更好的系统集成。
**证据**: `Swabble/docs/spec.md:3-4`

### W22. 为什么 OpenClaw 有三个历史名字（Warelay→Clawdbot→Moltbot→OpenClaw）
Warelay 是 WhatsApp gateway，Clawdbot 因 Anthropic 商标要求更名（2026年1月），Moltbot 过渡，最终 January 30, 2026 定名 OpenClaw。
**证据**: `docs/start/lore.md:14-24`

### W23. 为什么 CODEOWNERS 使用 last-match-wins 语义需要特别警惕
GitHub CODEOWNERS last-match-wins：新增 overlapping rules 如果不包含 `@openclaw/secops`，会静默移除 secops 的必须审核。
**证据**: `.github/CODEOWNERS:4-7`

### W24. 为什么 PR merge 强制要求"bug-fix truthfulness gate"
禁止仅基于 issue 文本、PR 文本或 AI 理由合并 bug-fix PR。要求：symptom evidence + root cause in code + fix touches implicated path + regression test（或手动验证证明）。防止幻觉修复进入主线。
**证据**: `CLAUDE.md:34-42`, `.pi/prompts/reviewpr.md:0-30`

---

## UNSAID 列表（暗坑 / 陷阱 / 文档未明说但很重要的事）

### U1. sandbox.mode 默认 off，exec 实际在 gateway host 运行
`tools.exec.host` 默认路由到 sandbox，但如果 sandbox runtime 没激活，exec 会 fallback 到 gateway host 运行。这是 silent fallback，不会报错。
**证据**: `SECURITY.md:103-106`

### U2. 插件"世界级可写"目录会触发 plugin blocks，根因是权限问题
macOS Tahoe fresh install 上 root-installed tgz 可能因 `extensions/*` world-writable 触发 plugin loading blocks。这是安装路径问题，与 gateway 健康无关，但日志看起来像 gateway 故障。
**证据**: `CLAUDE.md:223`

### U3. MEMORY.md 和 memory.md 共存时，只有 MEMORY.md 被注入（breaking change in 历史版本）
如果你同时保留了 MEMORY.md 和 memory.md 并依赖两个文件都被注入，升级后必须合并。文档未在主线显眼位置警告这个 breaking change。
**证据**: `CHANGELOG.md:93`

### U4. ACP shared session 多客户端时，event 和 cancel routing 是 best-effort，不是严格隔离
多个 ACP 客户端共享同一 Gateway session key 时，event 和 cancel routing 是 best-effort。如果需要干净的 editor-local turns，必须使用默认的隔离 `acp:<uuid>` session。
**证据**: `docs.acp.md:47-50`

### U5. 插件 npm 安装时，runtime deps 必须在 `dependencies`，不能用 `workspace:*`
plugin npm install 时运行 `npm install --omit=dev`，`workspace:*` 在 `dependencies` 会导致 npm install 失败。应该把 `openclaw` 放在 `devDependencies` 或 `peerDependencies`。
**证据**: `CLAUDE.md:50-51`

### U6. 动态 import 和静态 import 混用同一模块会产生 [INEFFECTIVE_DYNAMIC_IMPORT] warning
在同一生产代码路径中，不能混用 `await import("x")` 和 `import ... from "x"`。需要创建专用 `*.runtime.ts` 边界，从 lazy callers 动态导入该边界，而非原始模块。
**证据**: `CLAUDE.md:115-118`

### U7. prototype mutation 被明确禁止，但很多现有测试还在用它
不能通过 prototype mutation 共享 class 行为。现有测试若要用 prototype 级 patching，必须明确注释原因。这是一个现存的技术债坑。
**证据**: `CLAUDE.md:117-119`

### U8. 多个 agents 共用 agentDir 会导致 auth/session 冲突，但配置层面没有强制阻止
文档说"never reuse agentDir across agents"，但配置文件本身不会校验这个约束。错误配置后症状是 auth/session 碰撞，难以诊断。
**证据**: `docs/concepts/multi-agent.md:26-28`

### U9. 远程 Gateway 时，workspace 文件在 gateway host 而非本地机器
macOS app 连接远程 Gateway 时，workspace 文件和 bootstrapping 文件在远程机器上。直觉上容易以为文件在本地。
**证据**: `docs/start/bootstrapping.md:29-35`

### U10. session transcript 必须通过 SessionManager.appendMessage() 写入，直接 JSONL append 会破坏 compaction
如果绕过 API 直接 append JSONL，缺少 `parentId` 会截断 leaf path，breaking compaction/history。这个约束只在一个小文件中记录，没有在 plugin SDK 文档中显眼说明。
**证据**: `src/gateway/server-methods/AGENTS.md:3`

### U11. `prlctl exec` 在 Linux 上会 reap detached child processes，background gateway 不可信
Linux Parallels 上 background `openclaw gateway run` 通过 prlctl exec 启动后，子进程会被 reap。不能用这个路径做 smoke path，需要从 interactive guest shell 手动启动。
**证据**: `CLAUDE.md:241-243`

### U12. Windows guest 中，bare `npm`/`openclaw` 可能命中 .ps1 shim 在受限执行策略下失败
Windows PowerShell 环境中，必须显式调用 `.cmd` shim（`npm.cmd`, `openclaw.cmd`），而非 bare `npm`/`openclaw`。这个坑只在 Windows smoke playbook 中记录，没有在 Windows 安装文档主线中说明。
**证据**: `CLAUDE.md:228-230`

### U13. `pnpm test` 有包装配置，不能用 `pnpm vitest run ...` 直接替代
`pnpm test` 走包装器 config/profile/pool routing，raw `pnpm vitest run` 会绕过这些设置。测试结果可能不同。
**证据**: `CLAUDE.md:138-139`

### U14. GitHub GHSA API：`severity` 和 `cvss_vector_string` 不能在同一 PATCH 请求中设置
需要分两次调用。单次 PATCH 包含两者时，即使返回 200，部分字段可能不持久化。
**证据**: `CLAUDE.md:196`

### U15. detect-secrets 的 baseline 文件需要定期更新，否则 CI 会对新增 secret patterns 误报
baseline 文件 `.secrets.baseline` 是增量式的，需要手动 `detect-secrets scan --baseline .secrets.baseline` 更新。项目文档没有说明何时/如何更新 baseline。
**证据**: `SECURITY.md:283-291`, `.secrets.baseline` 文件存在

### U16. 多 agent 时，如果想共享 credentials，必须手动 copy auth-profiles.json
Agent 间 credentials 默认不共享。要共享，必须把 `auth-profiles.json` 复制到目标 agent 的 agentDir。没有内置的 credential sharing 机制。
**证据**: `docs/concepts/multi-agent.md:26-28`

### U17. `sessions_spawn` 的 sandbox 参数默认是 `inherit`，不是 `require`
sub-agent delegation 时，spawn 的 sandbox 默认继承父 session 设置，不是强制沙箱。如果父 session 是 unsandboxed，子 agent 也是 unsandboxed，除非显式传 `sandbox: "require"`。
**证据**: `SECURITY.md:226-229`

### U18. Control UI 的 gateway 认证如果禁用（dangerouslyDisableDeviceAuth），是 loopback-only 的 break-glass 设计，不是正常功能
`gateway.controlUi.dangerouslyDisableDeviceAuth` 不是一个普通配置项，是 break-glass。在非 local 部署中使用会被 `openclaw security audit` 标记为 dangerous。
**证据**: `SECURITY.md:239-241`

### U19. 暗中的历史包袱：项目经历过三次大改名，大量遗留 alias 和 migration 代码
Warelay→Clawdbot→Moltbot→OpenClaw。代码库中存在大量 legacy alias、migration 路径（config 字段别名、legacy cron storage 格式等），文档大多只提最新名字，不解释历史。
**证据**: `docs/start/lore.md:14-24`, `CHANGELOG.md` 多处 "legacy" 条目

### U20. bootstrap files 截断后不会告知 model 原始长度，只加一个 marker
大文件按 `agents.defaults.bootstrapMaxChars`（默认 20000 chars）截断，加 marker 提示 model 读完整文件，但 model 不知道截断了多少内容。容易漏掉关键 context。
**证据**: `docs/reference/token-use.md:21`, `docs/concepts/agent.md:36-38`

### U21. cli committer 脚本用于 staging 范围控制，但 agent 文档中没有提醒 merge commit 和 fix commit 的消息格式区别
landpr 流程中，final merge commit 必须包含 PR number + thanks，中间 fix commit 不应包含 PR number/thanks。混淆后会产生格式问题。
**证据**: `.pi/prompts/landpr.md:46-49`

### U22. Node.js 版本要求是 22.12.0+（不只是 22+），因为特定 CVE 修复
文档通常说 "Node 22+"，但实际要求是 `22.12.0+`，包含 CVE-2025-59466 和 CVE-2026-21636 的修复。不升到具体小版本会有安全漏洞。
**证据**: `SECURITY.md:254-258`

---

## 统计

| 指标 | 数量 |
|------|------|
| WHY 条目总数 | 24 |
| UNSAID 条目总数 | 22 |
| 有 file:line 或 file 名证据的 WHY 条目 | 24 / 24 (100%) |
| 有 file:line 或 file 名证据的 UNSAID 条目 | 22 / 22 (100%) |
| 总计有证据条目 | 46 / 46 (100%) |

---

## 方法说明

扫描路径（按优先级）：
1. `VISION.md` — 产品哲学和不做什么
2. `CLAUDE.md` / `AGENTS.md` — 工程操作规范
3. `SECURITY.md` — 安全/信任模型设计决策
4. `README.md` — 产品定位
5. `CONTRIBUTING.md` — 团队结构
6. `docs.acp.md` — ACP bridge 架构
7. `docs/concepts/agent.md`, `docs/concepts/multi-agent.md`
8. `docs/gateway/security/index.md`
9. `docs/tools/plugin.md`
10. `docs/start/lore.md` — 历史背景
11. `docs/reference/token-use.md`, `docs/reference/RELEASING.md`
12. `.github/CODEOWNERS`, `.github/pull_request_template.md`
13. `.pi/prompts/landpr.md`, `.pi/prompts/reviewpr.md`
14. `src/gateway/server-methods/AGENTS.md`
15. `CHANGELOG.md` 头部 (breaking changes / security fixes)
16. `Swabble/docs/spec.md`
17. `.github/workflows/ci.yml`
18. `.env.example`
19. `package.json`
