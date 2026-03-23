---
name: skill-forge
description: >
  Skill Forge（技能锻造师）：理解你的真实需求，从开源世界提取智慧，为你量身定制一款 AI 技能。
  输入：一句话描述你需要什么。
  输出：一套即用的自定义 skill（SKILL.md + stages/）。
  Triggers on: "我需要", "帮我做一个skill", "我想要一个skill", "build me a skill", "create a skill", "forge a skill", "制作一个skill".
version: 1.0.0
user-invocable: true
tags: [skill-generation, meta-skill, needs-discovery, doramagic]
metadata:
  openclaw:
    category: generation
    requires:
      bins: ["git"]
---

# Skill Forge — 技能锻造师

用户说"我需要 xxx"，我帮你从开源世界提炼智慧，锻造一个量身定制的 AI 技能。

**炼制流程（5 个阶段）**：
1. **需求挖掘** — Socratic 对话，提炼真实需求（不是功能列表，是问题本质）
2. **开源发现** — 找出最相关的开源项目或开源项目组合
3. **灵魂提取** — 从项目中提取设计哲学、心智模型、核心知识
4. **社区智慧** — 合成该领域的社区踩坑经验和最佳实践
5. **技能锻造** — 生成量身定制的完整 skill 包

每个阶段完成后向用户汇报进展，然后继续下一阶段。

## 初始化

在开始前，先确定输出目录：

```
output_dir = /tmp/skill-forge-<需求关键词>/
```

创建该目录结构：
```
<output>/
├── discovery/        # Stage 1-2 产出
├── soul/             # Stage 3-4 产出
└── skill-output/     # Stage 5 最终 skill
```

然后告诉用户："明白了，开始为你量身定制技能，共 5 个阶段。"

## Stage 1: 需求挖掘

读取并执行 `{baseDir}/stages/STAGE-1-discovery.md` 中的指令。

深度理解用户的真实需求——通过 Socratic 对话提炼问题本质。

## Stage 2: 开源发现

读取并执行 `{baseDir}/stages/STAGE-2-search.md` 中的指令。

找出与用户需求最相关的 3-5 个开源项目，说明为什么选它们。

## Stage 3: 灵魂提取

读取并执行 `{baseDir}/stages/STAGE-3-extract.md` 中的指令。

从开源项目中提取设计哲学、心智模型和核心知识，合成为解决方案灵魂。

## Stage 4: 社区智慧

读取并执行 `{baseDir}/stages/STAGE-4-community.md` 中的指令。

合成该领域的社区集体经验——踩坑模式、最佳实践、演化故事。

## Stage 5: 技能锻造

读取并执行 `{baseDir}/stages/STAGE-5-generate.md` 中的指令。

将所有洞察合成为一个完整的、即用的自定义 skill 包，并询问用户保存位置。
