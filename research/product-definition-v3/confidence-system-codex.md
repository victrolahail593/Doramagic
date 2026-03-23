# 置信度体系设计研究：从"打分"到"举证"，再到"可执行裁决"

## 1. 我推荐的方案

我推荐**第三方案：Evidence Graph + Policy Verdict（证据图 + 策略裁决）**。

它不是 A/B/C/D，也不是仅有证据标签，而是两层：

1. **证据层（描述事实）**：保留 `[CODE]/[DOC]/[COMMUNITY]/[INFERENCE]` 等原子证据及其溯源。  
2. **裁决层（支持决策）**：由**确定性规则引擎**根据证据图输出机器可执行结论，而不是让 LLM 自打分。

输出不再是 `confidence: B`，而是：
- `evidence_profile`: 证据清单与质量特征
- `verdict`: `SUPPORTED | CONTESTED | WEAK | REJECTED`
- `policy_action`: `ALLOW_CORE | ALLOW_STORY | QUARANTINE`


## 2. 推荐理由（第一性原理）

### 2.1 信息论角度

结论：**A/B/C/D 是高损压缩；证据图是低损表示；证据图+裁决才可计算。**

- 目标变量是“某条知识是否可被下游使用”。它依赖多个独立维度：证据类型、证据数量、来源独立性、时间新鲜度、冲突状态、可复现性。  
- A/B/C/D 把多维证据压成 4 个桶，最大仅约 `log2(4)=2 bit` 可区分信息，无法保留决策所需细节。  
- 纯证据标签保留了信息，但没有统一决策函数，消费端会各自解释，系统行为不一致。  
- 证据图 + 策略裁决把“表示”和“决策”分离：先完整保真，再用可审计函数做压缩，满足可追溯和可操作。

### 2.2 LLM 行为特性角度

结论：**禁止自评，改为“生成-校验-裁决”解耦。**

- LLM 对自身错误没有可靠可观测内部变量；让同一个模型给自己置信度，本质是同源误差复用。  
- 自评分数不可证伪；证据引用可证伪（要么能定位到源码/文档片段，要么不能）。  
- 方案中 LLM只负责“提出 claim + 对齐候选证据”，最终 verdict 由独立规则引擎和确定性检查器给出，降低同源幻觉。

### 2.3 工程可行性角度

结论：**证据图+裁决的实现复杂度可控，且能稳定落到流水线。**

- A/B/C/D 的一致性问题难解：标注员之间会因语义理解差异而漂移。  
- 证据标签可由脚本化提取器大量自动生成（代码/文档可确定性抽取），一致性高。  
- 裁决规则可版本化（`policy_v1`, `policy_v2`），可回放、可 A/B、可审计，便于持续迭代。


## 3. 完整实现设计

### 3.1 判定流程（谁标注、怎么标注、依据是什么）

#### 3.1.1 数据对象

- `Claim`: 一条最小可判定知识（例如“项目默认重试 3 次”）。
- `Evidence`: 可定位来源的证据原子。
- `Edge`: `supports` 或 `contradicts`，连接 `Claim` 与 `Evidence`。
- `Verdict`: 规则引擎输出。

建议结构：

```yaml
claim_id: C123
layer: decision
text: "该项目优先使用乐观重试而非熔断"
evidence_profile:
  - evidence_id: E1
    type: CODE
    source: src/retry/policy.go#L42-L78
    extractor: ast_pattern_v2
    reproducible: true
  - evidence_id: E2
    type: DOC
    source: docs/architecture.md#L120-L146
    extractor: doc_quote_v1
    reproducible: true
  - evidence_id: E3
    type: COMMUNITY
    source: github_issue_348
    extractor: thread_miner_v1
    reproducible: true
verdict: SUPPORTED
policy_action: ALLOW_CORE
policy_version: policy_v1.3
```

#### 3.1.2 标注角色分工

- **确定性提取器（主标注者）**：
  - 代码提取器：AST、调用图、配置解析、测试断言扫描 → `[CODE]`
  - 文档提取器：README/官方 docs/注释解析 → `[DOC]`
  - 社区提取器：Issue/Discussion 去重聚类 → `[COMMUNITY]`
- **LLM（候选生成者，不是裁判）**：
  - 生成候选 `Claim`
  - 将 claim 对齐到候选 evidence（允许失败）
  - 无证据时可标 `[INFERENCE]`
- **规则引擎（唯一裁判）**：
  - 根据 policy 输出 verdict 与消费动作

#### 3.1.3 判定规则（示例）

```text
R1: 若存在 >=1 CODE 或 >=1 DOC 支持，且无高优先级冲突 -> SUPPORTED
R2: 若仅 COMMUNITY 支持，且独立来源 >=2 -> WEAK
R3: 若仅 INFERENCE -> WEAK + QUARANTINE
R4: 若存在 CODE 与 DOC 直接矛盾 -> CONTESTED
R5: 若 claim 被可执行检查反证（如测试失败）-> REJECTED
```

> “高优先级冲突”按来源优先级：`runtime-observed CODE > static CODE > DOC > COMMUNITY > INFERENCE`。

### 3.2 冲突处理（同条知识不同标注怎么办）

#### 3.2.1 冲突类型

- `Type-A`: 同源冲突（同类证据互相矛盾，如两个代码路径）。
- `Type-B`: 跨源冲突（文档说 A，代码做 B）。
- `Type-C`: 时间冲突（旧讨论与新版本代码不一致）。

#### 3.2.2 仲裁流程

1. 先按 `repo_snapshot_sha` 锁定版本，所有证据必须绑定同一快照。  
2. 再按来源优先级和时间戳排序。  
3. 若冲突仍未消除，打 `CONTESTED`，并进入“可执行验证”：生成最小复现实验/测试脚本。  
4. 验证通过的一侧升权，另一侧降为背景证据。  
5. 无法验证时保留冲突态，不进入 `ALLOW_CORE`。

### 3.3 消费端处理（Knowledge Compiler 与最终 Skill）

#### 3.3.1 Knowledge Compiler 路由策略

- `ALLOW_CORE`：可进入能力规则、关键决策、默认行为。  
- `ALLOW_STORY`：只进入“踩坑经验/背景解释”，不驱动关键执行路径。  
- `QUARANTINE`：不注入主 Skill，仅存档或进入待验证队列。

建议矩阵：

- 事实/操作层：只接收 `SUPPORTED`。
- 经验层：接收 `SUPPORTED` + 部分 `WEAK`（需显式“社区经验，未官方确认”）。
- 设计哲学/隐性知识：允许 `WEAK`，但必须伴随证据脚注与反例提示。

#### 3.3.2 最终 Skill 呈现规范

每条关键知识附最小证据脚注：

```markdown
- 默认采用指数退避重试（来源：CODE: `src/retry.go:42`；DOC: `docs/ops.md:88`）
- 社区反馈该策略在高并发下可能放大尾延迟（来源：COMMUNITY: issue #348，未官方确认）
```

这样消费模型看到的是“结论 + 可追溯证据 + 状态”，而不是一个不可解释字母分级。

### 3.4 验证方法（验证标注系统本身准确性）

#### 3.4.1 离线基准

构建 `Gold Claims Set`（高星/低星项目各半），人工给出真值标签与证据对齐。

评估指标：
- `Evidence Precision/Recall`：证据是否找对、找全。  
- `Verdict Accuracy`：`SUPPORTED/CONTESTED/WEAK/REJECTED` 是否正确。  
- `Conflict F1`：冲突识别能力。  
- `Inter-annotator kappa`：人工一致性基线。

#### 3.4.2 可证伪测试

- **删证据单调性**：移除强证据后 verdict 不能升高。  
- **注入伪证据鲁棒性**：加入低质量社区噪声不应把 `WEAK` 提升为 `SUPPORTED`。  
- **跨版本回放**：同一规则在历史快照可重放得到一致结果。

#### 3.4.3 在线效果

对比实验：`A/B/C/D` vs `证据标签` vs `证据图+裁决`。

看 4 个终局指标：
- Skill 任务成功率
- 幻觉触发率
- 用户纠错次数
- 每次编译成本（token + 时延）


### 3.5 高 Star vs 低 Star 项目适配

同一框架可适用，但策略阈值不同。

#### 高 Star（记忆污染风险高）

- 强制“**仓库内证据闭环**”：关键 claim 必须有当前快照 `CODE/DOC`，否则最多 `WEAK`。  
- LLM 预训练记忆只能作为候选，不可直接入库。  
- 提高反证检查权重（优先跑最小复现实验）。

#### 低 Star（外部证据稀缺）

- 允许更多 `INFERENCE` 进入 `ALLOW_STORY`，但禁止进入 `ALLOW_CORE`。  
- 增加代码结构证据挖掘深度（调用链、测试行为、配置分支）。  
- 用“待验证队列”累积后续真实运行反馈，逐步把 `WEAK -> SUPPORTED`。

核心点：**框架统一，阈值自适应；不因项目热度改变真值定义，只改变可接受风险边界。**


## 4. 风险和局限

- 初期工程成本高于字母分级，需要建设证据存储、规则引擎、回放工具链。  
- 部分高层语义（设计哲学）难以被确定性证据完全覆盖，仍会保留 `WEAK` 区域。  
- 社区证据存在从众偏差与时间漂移，需持续去噪和版本化。  
- 可执行验证并非总能自动构造（依赖环境、外部服务权限）。  
- 若规则写得过硬，会提高假阴性；写得过松，会提高幻觉泄露，需要通过在线指标持续校准。


## 5. 一句话总结

**把“可信度”从 LLM 主观分数改为“可追溯证据 + 可执行裁决”，才能同时满足第一性原理下的可证伪性、工程可操作性和下游可消费性。**
