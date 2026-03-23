# Doramagic 补充开发 Brief

> 日期：2026-03-20
> 前置文档：docs/doramagic-product-dev-brief.md（产品背景）、docs/product-design-adjustment.md（架构调整）
> 目标：将初版 CLI 产品改造为 OpenClaw Skill 形态，真实数据验证端到端

---

## 背景：为什么需要补充开发

初版四路开发暴露了 3 个根本性问题：

1. **产品形态错误** — 做成了 `python doramagic.py` CLI 工具，但 Doramagic 是 OpenClaw Skill，入口应该是 SKILL.md + `/dora` 触发
2. **绑死了特定 LLM** — 硬编码 `import anthropic`，但 Doramagic 的用户使用各种大模型。在 OpenClaw/Claude Code/Codex/Gemini 里，AI 自身就是 LLM，不需要调外部 API
3. **没有真实数据验证** — Sonnet/Codex/Gemini 都用 mock 或离线 fallback 跑通，只有 GLM5 真正调了 GitHub API

本次补充开发的目标是修正这 3 个问题，产出一个**真正能用的 Doramagic Skill**。

---

## 核心交付物

每个选手需要交付以下文件（注意文件名带选手标识，避免覆盖）：

```
skills/doramagic-{选手}/
├── SKILL.md                    ← 产品主入口，AI 读取后按指令执行
├── scripts/
│   ├── github_search.py        ← 【已提供，直接复用】搜索+下载
│   ├── extract_facts.py        ← 确定性事实提取（基于已有 stage0/repo_facts）
│   ├── validate_skill.py       ← Skill 质量校验（基于已有 validator）
│   └── assemble_output.py      ← 组装最终输出文件
└── README.md                   ← 安装和使用说明
```

**注意**：`skills/doramagic/scripts/github_search.py` 已由 PM 提供并验证通过，所有选手直接复用，不要重写。

---

## SKILL.md 的设计要求

SKILL.md 是产品的灵魂。它是一份**给 AI 的指令文档**——AI（不管是 Claude、GPT、Gemini 还是 GLM）读了这份文档后，就知道怎么完成"帮用户锻造 Skill"的全流程。

### Frontmatter（必须）

```yaml
---
name: doramagic
description: >
  从开源世界找最好的作业，提取智慧（WHY + UNSAID），
  锻造开袋即食的 OpenClaw Skill。
version: 1.0.0
user-invocable: true
allowed-tools: [exec, read, write]
tags: [doramagic, knowledge-extraction, skill-generation]
metadata:
  openclaw:
    skillKey: dora
    category: builder
    requires:
      bins: [python3, curl, unzip]
    storage_root: ~/clawd/doramagic/
---
```

### 指令结构（SKILL.md 正文）

SKILL.md 正文告诉 AI 怎么做。核心原则：

- **你自己就是 LLM** — 理解需求、分析代码、提取 WHY/UNSAID、综合知识、锻造叙事，这些都由你（AI）直接完成
- **确定性操作用 exec** — 搜索 GitHub、下载代码、提取文件事实、校验输出，通过 `exec python3 scripts/xxx.py` 调用
- **不调外部 LLM API** — 不 import anthropic/openai/google，你自己就是智能

SKILL.md 正文应包含以下 Phase 指令（每个 Phase 清楚写明"AI 做什么"和"exec 做什么"）：

| Phase | AI 做什么 | exec 做什么 |
|-------|---------|-----------|
| A 需求理解 | 将用户一句话解析为关键词、意图、约束 | 可选：将 NeedProfile 写成 JSON |
| B 作业发现 | 从搜索结果中判断哪些项目真正相关 | `exec python3 scripts/github_search.py "关键词" --top 5 --output discovery.json` |
| C 灵魂提取 | 读取项目代码，回答 Q1-Q7（参考 skills/soul-extractor/stages/STAGE-1-essence.md），提取 WHY/UNSAID/设计哲学 | `exec python3 scripts/extract_facts.py <repo_dir> --output facts.json`（确定性事实） |
| D 社区采集 | 从 issue/PR 标题中判断哪些是高价值经验 | `exec` 调 GitHub API 获取 issues 列表 |
| E 知识综合 | 跨项目比较，找共识和冲突，解释 WHY | 可选：调 compare.py/synthesis.py |
| F Skill 锻造 | 撰写 SKILL.md 内容（包含 WHY + UNSAID） | `exec python3 scripts/assemble_output.py` 组装文件 |
| G 质量门控 | 根据校验报告判断是否修补 | `exec python3 scripts/validate_skill.py <skill_dir>` |
| H 交付 | 向用户解释结果和局限 | 将文件写入 ~/clawd/doramagic/runs/<run_id>/ |

### 关键：提取的核心是 WHY 和 UNSAID

SKILL.md 中必须明确指导 AI 怎么提取 WHY 和 UNSAID。参考 `skills/soul-extractor/stages/STAGE-1-essence.md` 的 7 问框架：

- Q1-Q5（WHAT 层）：项目做什么、用什么技术、数据怎么流、存在哪、有什么接口
- Q6（WHY 层）：为什么选择这个技术/架构/存储方式，有没有替代方案被否决
- Q7（UNSAID 层）：社区踩过什么坑、文档没写但用过才知道的事

**如果输出的 Skill 只有 WHAT 没有 WHY，就跟 GitHub 搜索没区别，产品没有价值。**

---

## 参考资产

### 直接复用

| 资产 | 位置 | 用法 |
|------|------|------|
| GitHub 搜索脚本 | `skills/doramagic/scripts/github_search.py` | PM 已验证，直接 exec 调用 |
| Soul Extractor 提取框架 | `skills/soul-extractor/stages/STAGE-*.md` | AI 参考这些 prompt 做知识提取 |
| Validator | `packages/platform_openclaw/.../validator.py` | 改成 exec 可调的脚本 |
| Contracts | `packages/contracts/` | 数据模型参考 |
| auto-Doraemon 参考 | Mac mini `~/Documents/auto-Doraemon/` | 参考其 LLM 多供应商抽象和知识卡片设计 |

### 初版代码参考

| 选手 | 文件 | 值得参考的点 |
|------|------|------------|
| S1 Sonnet | `doramagic_sonnet.py` (1501行) | Phase A-H 内联实现最完整 |
| S2 Codex | `packages/doramagic_product/` (2328行) | 离线降级路径设计好 |
| S3 Gemini | `doramagic_gemini.py` (454行) | 最精简，最大化复用 |
| S4 GLM5 | Mac mini `doramagic_glm5.py` (1104行) | 唯一真实调通 GitHub API |

---

## 验证方法

### 第一层：自身 CLI 环境测试

在你自己的 AI 编码环境中（Claude Code / Codex / Gemini / GLM5 CLI）：

1. 加载你写的 SKILL.md（按各平台方式：Claude Code 放 `skills/doramagic-{选手}/`）
2. 输入 `/dora 我想做一个管理家庭菜谱的 skill`
3. 观察 AI 是否按 Phase A-H 执行
4. 确认最终输出了 SKILL.md + PROVENANCE.md + LIMITATIONS.md
5. 确认输出中包含 WHY 和 UNSAID 内容

### 第二层：跑一个不同的需求验证泛化性

1. 输入 `/dora 帮我做一个管理 WiFi 密码的工具`
2. 确认 GitHub 搜索到了相关项目（不是菜谱项目）
3. 确认输出适配了新需求

---

## 分步骤要求

### 步骤 1：创建 SKILL.md（核心）

写好 `skills/doramagic-{选手}/SKILL.md`，包含完整的 Phase A-H 指令。这是本次补充开发最重要的交付物。

### 步骤 2：适配 exec 脚本

- 复用 `skills/doramagic/scripts/github_search.py`（已提供）
- 创建 `extract_facts.py`：包装已有的 `stage0.py` 或 `extract_repo_facts.py`，使其可通过 exec 调用
- 创建 `validate_skill.py`：包装已有的 `validator.py`，使其可通过 exec 调用
- 创建 `assemble_output.py`：组装最终的 SKILL.md + PROVENANCE.md + LIMITATIONS.md 到指定目录

### 步骤 3：自身环境验证

在你自己的 CLI 环境里测试 `/dora "需求"`，确保真实调 GitHub API、真实分析代码、真实输出 Skill。

### 步骤 4：准备 OpenClaw 部署

写一个 `README.md` 说明如何将 Skill 安装到 OpenClaw 和 Mac mini。

---

## 评分维度

| 维度 | 权重 | 说明 |
|------|------|------|
| SKILL.md 质量 | 30% | 指令是否清晰、AI 能否按指令完成全流程 |
| WHY/UNSAID 提取效果 | 25% | 输出的 Skill 是否包含真正有价值的 WHY 和 UNSAID |
| 真实数据验证 | 20% | 是否用真实 GitHub 项目跑通，不接受 mock |
| 已有资产复用 | 15% | 是否充分利用 github_search.py + Soul Extractor + validator |
| 跨平台兼容 | 10% | SKILL.md 是否不绑定特定 LLM，任何 AI 都能执行 |
