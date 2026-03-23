# LIMITATIONS.md -- 已知限制与暗坑

**Skill**: flight-search v0.1.0
**审查日期**: 2026-03-18

---

## Phase G: 质量门控 (7 项检查)

### 1. Consistency (一致性) -- PASS

**检查项**: SKILL.md 内部逻辑是否自洽

| 检查点 | 结果 | 说明 |
|--------|------|------|
| 参数命名一致 | PASS | 全文统一使用 `origin/destination/depart_date` |
| 数据流完整 | PASS | 意图提取→城市解析→API 搜索→排序→展示，无断裂 |
| 三个流程的参数兼容 | PASS | 流程二/三基于流程一的参数扩展 |
| 代码说事实/AI 说故事 | PASS | Pareto 计算用代码，自然语言解读用 LLM，职责清晰 |
| 默认值一致 | PASS | currency 默认 CNY 全文统一 |

**无冲突发现。**

### 2. Completeness (完整性) -- PASS with notes

**检查项**: 用户需求的每个维度是否被覆盖

| 需求维度 | 覆盖状态 | 说明 |
|----------|---------|------|
| 机票搜索 | 完整覆盖 | 流程一: 单程/往返 |
| 最优路线规划 | 完整覆盖 | 流程二: 多城市 Pareto 优化 |
| 价格比较 | 完整覆盖 | Pareto 排序 + 单维排序 |
| 价格追踪 | 完整覆盖 | 流程三: tracked.json + cron |
| 中文用户支持 | 完整覆盖 | 城市解析层 + CNY 默认 |
| 消息驱动交互 | 部分覆盖 | SKILL.md 定义了触发条件和交互流程，但 Telegram/WhatsApp 适配需平台层实现 |
| 实时数据 | 完整覆盖 | Amadeus 实时 API + 4h 缓存 |

**缺口**: 消息驱动的推送通知（价格告警推送到 Telegram）需要平台层 webhook 支持，超出 Skill 范围。

### 3. Traceability (可追溯性) -- PASS

**检查项**: SKILL.md 中的每个设计决策是否可追溯到知识来源

| SKILL.md 关键决策 | PROVENANCE.md 追溯 | 来源报告引用 |
|-------------------|-------------------|-------------|
| Amadeus + fast-flights 双轨 | 来源 4 (社区) | Section 三/3.2 |
| LLM→API→LLM 架构 | 来源 3 (gpt-flights) | CC-01, CC-03 |
| Pareto 多目标排序 | 来源 2 (travel-planner) | Stage 5.3 |
| 穷举 <=8 / 贪心 >8 | 来源 2 (travel-planner) | UNSAID-02, Stage 5.5 |
| tracked.json 价格追踪 | 来源 4 (社区 FlightClaw) | Section 1 |
| 不替用户订票 | 四方共识 | C-04 |

**100% 可追溯。** 每条知识在 PROVENANCE.md 中有明确来源标注。

### 4. Platform Fit (平台适配) -- PASS

**检查项**: SKILL.md 是否符合 OpenClaw 平台规范

| 规范要求 | 符合度 | 说明 |
|----------|--------|------|
| YAML frontmatter 格式 | 符合 | name, version, description, user-invocable, allowed-tools |
| allowed-tools 声明 | 符合 | Bash, Read, Write, AskUserQuestion |
| 脚本可执行 | 符合 | 所有脚本通过 `python3 {baseDir}/scripts/xxx.py` 调用 |
| 环境变量配置 | 符合 | `AMADEUS_API_KEY/SECRET` 在 metadata.requires.env 中声明 |
| 外部依赖声明 | 符合 | requires.bins: python3, pip |
| 触发描述 | 符合 | description 包含中英文触发词 |

### 5. Conflict Resolution (冲突解决) -- PASS

**检查项**: synthesis_report.md 中的分歧是否全部在 SKILL.md 中有明确解决

| 分歧 | 解决方式 | SKILL.md 位置 |
|------|---------|--------------|
| D-01: 数据源选型 | 双轨方案: Amadeus 主 + fast-flights 备 | 数据源设计 Section |
| D-02: 多城市算法 | 分层: 穷举(<=8) + 贪心(>8) | 流程二 Step 3 |
| D-03: 货币处理 | 固定 CNY + 显式标注 | 参数表 currency 默认值 |

**所有分歧已解决，无遗留。**

### 6. License (许可证) -- PASS

**检查项**: 是否存在许可证合规风险

| 来源 | 许可 | 代码复用 | 风险 |
|------|------|---------|------|
| fast-flights | MIT | 无直接复用 | 无 |
| travel-smart-planner | 未声明 | 无直接复用 | 无 |
| gpt-search-flights | 未声明 | 无直接复用 | 无 |
| 社区 Skills | MIT 为主 | 无直接复用 | 无 |
| Amadeus API | 商业 TOS | API 调用 | 需遵守 TOS |

**无许可证风险。** 所有知识借鉴限于架构模式和算法思路层面。

### 7. Dark Trap Scan (暗坑扫描) -- 6 项发现

以下暗坑已在 SKILL.md "暗坑警告"和"已知限制"中标注:

---

## 暗坑详细清单

### DT-01: Amadeus 测试环境返回模拟数据

**严重度**: 高
**来源**: Amadeus 官方文档 + 社区经验
**影响**: 开发阶段看到的价格全部是假数据，切换生产环境后价格可能完全不同。开发者可能基于假数据调优算法参数，导致生产环境表现失准。
**缓解**: SKILL.md 健康检查标注当前环境（test/production），结果展示标注数据来源。
**在 SKILL.md 中的位置**: 暗坑警告 #1

### DT-02: fast-flights 的 multi-city 是假功能

**严重度**: 高
**来源**: fast-flights extraction CC-03, DR-03, UNSAID-03
**影响**: `trip="multi-city"` 不报错但结果未定义。如果开发者误以为可以用单次调用搜索多城市，会得到错误或空结果。
**缓解**: SKILL.md 流程二明确拆成多个单程查询，不使用 multi-city trip type。
**在 SKILL.md 中的位置**: 暗坑警告 #2, 备用数据源限制说明

### DT-03: 同城多机场导致结果遗漏

**严重度**: 中
**来源**: 社区空白分析 (Section 4.2)
**影响**: 用户说"上海飞东京"，如果只搜 PVG→NRT，会漏掉 SHA→NRT、PVG→HND、SHA→HND 三个组合，其中可能有更便宜的选项。
**缓解**: SKILL.md 城市解析层返回所有候选机场，多城市矩阵搜索覆盖全部组合。
**在 SKILL.md 中的位置**: 暗坑警告 #3, 城市解析 Step 2

### DT-04: Google Flights 协议变更导致备用数据源静默失效

**严重度**: 中（有主数据源兜底）
**来源**: fast-flights UNSAID-01, INFERENCE-2
**影响**: Protobuf field numbers 变更 → 服务器解读错误字段 → 返回错误结果而非报错。JS 数据路径变更 → parse 异常或数据错位。两者都可能返回看似正常但实际错误的数据。
**缓解**: 健康检查层用已知查询定期验证 fast-flights 输出。主数据源 Amadeus 不受影响。
**在 SKILL.md 中的位置**: 限制 #4, 健康检查设计

### DT-05: 多目标权重的用户期望错位

**严重度**: 中
**来源**: 综合分析
**影响**: 用户说"最便宜"但可能不接受 3 次中转和 20 小时飞行时间。权重公式 `alpha=0.8, beta=0.1, gamma=0.1` 在极端情况下可能推荐用户不满意的方案。"最便宜"对不同用户含义不同——有人指绝对最低价，有人指"合理范围内最低价"。
**缓解**: Pareto 前沿展示多个方案而非单一"最优"，让用户自己选择。告知用户默认权重，允许调整。
**在 SKILL.md 中的位置**: 流程二 Step 3 权重表, 产品原则"给工具不做决策"

### DT-06: 价格缓存期内的大幅波动

**严重度**: 低
**来源**: 综合分析
**影响**: 4 小时缓存窗口内，特价票可能已售罄或价格已上涨。多城市矩阵搜索中，不同城市对的缓存新鲜度不同，可能导致组合方案的总价与实际不一致。
**缓解**: 结果展示标注"查询时间"，提醒价格为估算值。关键路线方案用户确认后可触发"刷新价格"强制跳过缓存。
**在 SKILL.md 中的位置**: 限制 #1, 缓存策略说明

---

## 未覆盖的能力边界

以下功能明确不在 v0.1.0 范围内:

| 不做的功能 | 原因 | 未来可能性 |
|-----------|------|-----------|
| 预订/出票 | 产品红线: "不替用户做事" | 低 -- 永远不做 |
| 行李/退改签查询 | 因航司和票价类别而异，数据复杂度过高 | 中 -- v0.3+ 可考虑 |
| 酒店/地面交通 | 超出 Skill 范围 | 中 -- 独立 Skill |
| 签证/证件提醒 | 超出 Skill 范围 | 低 -- 参考 travel-manager |
| 价格预测 ("再等几天") | 需要大量历史数据 + ML 模型 | 高 -- v0.2+ 基于 price_history 可做简单趋势 |
| 时差评分 | 有意义但 v0.1 不优先 | 中 -- 参考 Aerobase 思路 |
| 儿童友好航班过滤 | 需要额外规则引擎 | 中 -- 参考 openclaw-travel-planner |

---

## 部署前检查清单

- [ ] Amadeus API Key 已配置且为生产环境
- [ ] `city_iata_map.json` 已加载，覆盖主要中文城市
- [ ] `python3` >= 3.10 已安装
- [ ] `pip install amadeus fast-flights` 已执行
- [ ] 健康检查通过: `python3 scripts/healthcheck.py`
- [ ] 首次搜索测试: 已知路线（如 PVG→NRT）返回合理结果
- [ ] 缓存目录可写: `~/.flight-search/cache/`
- [ ] 可选: BrightData API Key 已配置（启用 fast-flights 备用通道）

---

*质量门控完成。7 项检查: 6 PASS + 1 PASS with notes。6 个暗坑已标注。*
