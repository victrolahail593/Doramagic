# Doramagic 多项目提取→组装管线（v1）

> 基于 2026-03-17 极限模拟暴露的 5 个结构性缺口设计
> 与 V5 单项目管线（Stage 0-5）并行，不替代

---

## 定位

单项目管线回答："这个项目的灵魂是什么？"
多项目管线回答："用户想做 X，应该站在哪些前人的肩膀上？"

---

## 完整管线

```
Phase A: 需求理解
  ↓
Phase B: 作业发现（搜索+筛选+推荐）
  ↓
Phase C: 并行灵魂提取（N 路，每路走单项目管线）
  ↓
Phase D: 社区知识采集（ClawHub/教程/用例）
  ↓
Phase E: 知识综合（公约数+打架+独创分析）
  ↓
Phase F: Skill 组装（知识选择+冲突解决+格式编译）
  ↓
Phase G: 质量门控（Validation Gate）
  ↓
Phase H: 交付（SKILL.md + 说明）
```

---

## 各 Phase 详细定义

### Phase A：需求理解

**输入**：用户的自然语言描述（如"我想做一个记录食物卡路里的 skill"）

**处理**：
1. 提取关键词和意图（LLM 理解）
2. 分类需求类型：
   - 功能需求（记录食物、计算卡路里）
   - 场景约束（通过消息渠道使用、中文用户）
   - 质量期望（准确度、响应速度）
3. 生成搜索计划：要搜哪些方向？优先级？

**输出**：`need_profile.json`
```json
{
  "raw_input": "我想做一个记录食物卡路里的 skill",
  "keywords": ["食物", "卡路里", "记录", "追踪"],
  "intent": "构建一个通过消息记录饮食和计算热量的 AI skill",
  "search_directions": [
    {"direction": "AI 食物识别/卡路里计算", "priority": "high"},
    {"direction": "营养数据库/食物成分表", "priority": "high"},
    {"direction": "健康追踪应用架构", "priority": "medium"},
    {"direction": "OpenClaw 社区已有的饮食/健康 skill", "priority": "high"}
  ],
  "constraints": ["OpenClaw 平台", "消息驱动交互", "中文支持"]
}
```

**执行者**：LLM（OpenClaw agent 或主对话）
**工时**：< 1 分钟

---

### Phase B：作业发现

**输入**：`need_profile.json`

**处理**：
1. **搜索**（按 search_directions 并行）：
   - GitHub API 搜索（关键词 + 语言 + stars 排序）
   - ClawHub 搜索（已有 skill 目录）
   - 社区资源搜索（awesome 列表、教程、用例）
2. **粗筛**（好作业快速评估）：
   - Stars > 10（过滤实验性项目）
   - 最近 6 个月有更新（过滤废弃项目）
   - 有 README（过滤不可理解项目）
   - 不在暗雷黑名单中
3. **精筛**（好作业评分）：
   - 与用户需求的相关度（LLM 判断）
   - 项目质量信号（stars/forks/issues 活跃度）
   - 知识互补性（已选项目覆盖了什么，还缺什么）
4. **推荐**（Top 3-5 项目 + 理由）

**输出**：`discovery_result.json`
```json
{
  "candidates": [
    {
      "name": "ai-calorie-counter",
      "url": "https://github.com/open-kbs/ai-calorie-counter",
      "type": "github_repo",
      "relevance": "high",
      "contribution": "AI 食物识别 + 卡路里估算的核心架构",
      "quick_score": 7.2
    },
    {
      "name": "calorie-counter skill",
      "url": "clawhub://cnqso/calorie-counter",
      "type": "community_skill",
      "relevance": "high",
      "contribution": "OpenClaw 原生的卡路里追踪 skill，可直接参考格式",
      "quick_score": 6.8
    }
  ],
  "search_coverage": {
    "AI 食物识别": "covered",
    "营养数据库": "covered",
    "健康追踪架构": "covered",
    "社区 skill": "covered"
  }
}
```

**执行者**：搜索工具 + LLM 判断
**工时**：2-5 分钟

---

### Phase C：并行灵魂提取

**输入**：`discovery_result.json` 中的 GitHub 项目列表

**处理**：对每个 GitHub 项目，走**单项目管线**（Stage 0→1→[1.5]→2→3→3.5→4→5）

**关键约束**：
- 必须走 Stage 0（确定性提取 repo_facts.json）
- 必须走 Stage 3.5（证据绑定，claim 必须有 file:line）
- Stage 1.5（Agentic Loop）视项目规模决定是否启用
- N 路并行，每路独立子代理

**输出**：每个项目一个标准提取包
```
project_name/
├── repo_facts.json          # Stage 0 确定性事实
├── soul_discovery.md        # Stage 1 灵魂发现
├── concept_cards/           # Stage 2 概念卡片
├── workflow_cards/          # Stage 2 工作流卡片
├── decision_rule_cards/     # Stage 3 规则卡片
├── validation_report.json   # Stage 3.5 验证报告
├── expert_narrative.md      # Stage 4 专家叙事
└── CLAUDE.md                # Stage 5 最终输出
```

**执行者**：N 个并行子代理（Sonnet/Opus）
**工时**：每个项目 5-15 分钟，并行执行

---

### Phase D：社区知识采集

**输入**：`discovery_result.json` 中的社区 skill / 教程 / 用例

**处理**：对每个社区资源，执行**轻量提取**（不走完整 Stage 0-5）：
1. 读取 SKILL.md / 教程内容
2. 提取：核心功能、触发条件、工具调用、数据格式、存储路径
3. 转化为结构化知识卡片

**与 Phase C 的区别**：
- Phase C 提取的是"代码项目的灵魂"（深度，Stage 0-5）
- Phase D 提取的是"已有 skill 的经验"（宽度，轻量读取）

**输出**：`community_knowledge.json`
```json
{
  "skills": [
    {
      "name": "calorie-counter",
      "source": "clawhub://cnqso/calorie-counter",
      "capabilities": ["追踪每日卡路里和蛋白质", "设置目标", "记录日志"],
      "storage_pattern": "~/clawd/memory/YYYY-MM-DD.md",
      "cron_pattern": "8AM/1PM/7PM 三餐提醒",
      "reusable_knowledge": ["存储路径标准", "提醒时间", "日志格式"]
    }
  ],
  "tutorials": [...],
  "use_cases": [...]
}
```

**执行者**：1 个子代理（Sonnet）
**工时**：2-5 分钟

---

### Phase E：知识综合

**输入**：Phase C 的 N 个提取包 + Phase D 的社区知识

**处理**：
1. **公约数提取**：所有来源的共识知识
2. **打架分析**：来源之间的分歧和冲突
3. **独创标注**：每个来源独有的知识
4. **与用户需求匹配**：哪些知识直接服务于 `need_profile.json` 中的需求

**输出**：`synthesis_report.md`
- 共识知识列表（标注支持来源数和独立性）
- 冲突列表（标注冲突类型和各方立场）
- 独创知识列表（标注来源和采纳建议）
- 知识选择建议（哪些纳入最终 skill，哪些排除，为什么）

**执行者**：Opus 子代理（需要深度理解和权衡）
**工时**：3-5 分钟

---

### Phase F：Skill 组装

**输入**：`synthesis_report.md` + `need_profile.json`

**处理**：
1. **知识选择**：从综合报告中选择纳入 skill 的知识
2. **冲突解决**：
   - 事实冲突 → 选择证据更强的
   - 路线冲突 → 展示选项让用户选，或选择与需求更匹配的
3. **格式编译**：把选中的知识编译为 OpenClaw SKILL.md 格式
   - frontmatter（name / version / description / allowed-tools）
   - 工作流定义（触发条件 → 步骤 → 输出）
   - 数据存储设计（文件路径、格式）
   - AI prompt 契约（输入输出 JSON schema）
   - 人格配置（如有）
   - cron 提醒（如有）

**输出**：`SKILL.md`（可直接部署到 OpenClaw 的 skill 文件）

**执行者**：LLM + 确定性模板
**工时**：3-5 分钟

---

### Phase G：质量门控

**输入**：`SKILL.md` + `synthesis_report.md`

**检查项**（从 StitchCraft Validation Gate 扩展）：

| # | 检查项 | 说明 | 阻断？ |
|---|--------|------|--------|
| 1 | **Consistency** | skill 内部知识是否一致（无自相矛盾） | 是 |
| 2 | **Completeness** | 用户需求中的每个功能是否都被覆盖 | 是 |
| 3 | **Traceability** | 每条知识是否可追溯到来源项目 | 是 |
| 4 | **Platform Fit** | 是否符合 OpenClaw SKILL.md 格式规范 | 是 |
| 5 | **Conflict Resolution** | 所有冲突是否已解决（无未处理冲突） | 是 |
| 6 | **License** | 所有来源的许可证是否兼容 | 警告 |
| 7 | **Dark Trap Scan** | 是否引入了已知暗雷（Top 10 暗雷扫描） | 警告 |

**输出**：`validation_report.json`（PASS / REVISE / BLOCKED）

**执行者**：确定性检查 + LLM 辅助
**工时**：1-2 分钟

---

### Phase H：交付

**输入**：通过门控的 `SKILL.md`

**处理**：
1. 输出 SKILL.md 给用户
2. 附带使用说明（怎么安装、怎么触发、有什么功能）
3. 附带知识溯源摘要（"这个 skill 的知识来自哪些项目"）
4. 附带已知限制（从暗坑警告中提取）

**输出**：交付包
```
delivery/
├── SKILL.md                 # 可运行的 skill
├── README.md                # 使用说明
├── PROVENANCE.md            # 知识溯源（来自哪些项目）
└── LIMITATIONS.md           # 已知限制和暗坑
```

---

## 与单项目管线的关系

```
单项目管线（V5 已有）：
  Stage 0 → 1 → [1.5] → 2 → 3 → 3.5 → 4 → 5 → CLAUDE.md

多项目管线（本文档新增）：
  Phase A → B → C（调用单项目管线×N） + D → E → F → G → H → SKILL.md
                   ↑
             单项目管线作为子组件
```

多项目管线**调用**单项目管线，不替代它。
